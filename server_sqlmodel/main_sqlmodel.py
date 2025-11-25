"""
Todo List API using SQLModel

SQLModel is a library that combines SQLAlchemy (ORM) and Pydantic (validation).
It allows you to define models that work both as database tables and API schemas.

Key Benefits:
- Single model definition for both database and API
- Automatic validation
- Type safety
- Less boilerplate code
- Better IDE support
"""

from fastapi import FastAPI, HTTPException, Request, UploadFile, File, Depends
from sqlmodel import SQLModel, Field, Session, create_engine, select
from contextlib import asynccontextmanager
from datetime import datetime
import uvicorn
import csv
import io

# ============================================================================
# Database Configuration
# ============================================================================

# SQLite database URL
DATABASE_URL = "sqlite:///server_sqlmodel/todos_db.sqlite"

# Create engine - this manages database connections
# echo=True logs all SQL queries (useful for debugging)
engine = create_engine(DATABASE_URL, echo=False)

# ============================================================================
# SQLModel Models
# ============================================================================

class TodoBase(SQLModel):
    """Base model with common fields (not a table, just for inheritance)"""
    title: str
    description: str | None = None
    completed: bool = False


class Todo(TodoBase, table=True):
    """
    Todo model - represents the todos table in the database.
    
    table=True tells SQLModel this is a database table.
    Inherits from TodoBase to get common fields.
    """
    id: int | None = Field(default=None, primary_key=True)
    created_at: str | None = Field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str | None = Field(default_factory=lambda: datetime.now().isoformat())


class TodoCreate(TodoBase):
    """Model for creating todos (API request body)"""
    pass


class TodoUpdate(SQLModel):
    """Model for updating todos (all fields optional)"""
    title: str | None = None
    description: str | None = None
    completed: bool | None = None


class TodoRead(TodoBase):
    """Model for reading todos (API response)"""
    id: int
    created_at: str
    updated_at: str


# ============================================================================
# Database Initialization
# ============================================================================

def init_db():
    """Create all tables in the database"""
    SQLModel.metadata.create_all(engine)


# ============================================================================
# Dependency: Database Session
# ============================================================================

def get_session():
    """
    Dependency function that provides a database session.
    FastAPI will call this for each request that needs database access.
    The session is automatically closed after the request.
    """
    with Session(engine) as session:
        yield session


# ============================================================================
# Helper (Controller) Functions for Database Operations
# ============================================================================

def read_todos(session: Session, completed: bool | None = None) -> list[Todo]:
    """Read todos from database"""
    statement = select(Todo)
    
    if completed is not None:
        statement = statement.where(Todo.completed == completed)
    
    todos = session.exec(statement).all()
    return todos


def get_todo_by_id(session: Session, todo_id: int) -> Todo | None:
    """Get a single todo by ID"""
    return session.get(Todo, todo_id)


def create_todo_in_db(session: Session, todo: TodoCreate) -> Todo:
    """Create a new todo in database"""
    # Create Todo instance from TodoCreate
    db_todo = Todo(
        title=todo.title,
        description=todo.description,
        completed=todo.completed,
        created_at=datetime.now().isoformat(),
        updated_at=datetime.now().isoformat()
    )
    
    # Add to session and commit
    session.add(db_todo)
    session.commit()
    session.refresh(db_todo)  # Refresh to get the generated ID
    
    return db_todo


def update_todo_in_db(session: Session, todo_id: int, todo_update: TodoUpdate) -> Todo:
    """Update an existing todo in database"""
    todo = session.get(Todo, todo_id)
    if not todo:
        raise HTTPException(status_code=404, detail="Todo not found")
    
    # Get only the fields that were provided
    update_data = todo_update.model_dump(exclude_unset=True)
    
    # Update fields
    for field, value in update_data.items():
        setattr(todo, field, value)
    
    # Update timestamp
    todo.updated_at = datetime.now().isoformat()
    
    session.add(todo)
    session.commit()
    session.refresh(todo)
    
    return todo


def delete_todo_from_db(session: Session, todo_id: int) -> bool:
    """Delete a todo from database"""
    todo = session.get(Todo, todo_id)
    if not todo:
        raise HTTPException(status_code=404, detail="Todo not found")
    
    session.delete(todo)
    session.commit()
    return True


def delete_all_todos_from_db(session: Session):
    """Delete all todos from database"""
    statement = select(Todo)
    todos = session.exec(statement).all()
    
    for todo in todos:
        session.delete(todo)
    
    session.commit()


def import_csv_to_db(session: Session, csv_content: bytes) -> dict:
    """Import CSV content and append rows to todos table. CSV file is not stored."""
    try:
        # Parse CSV
        csv_text = csv_content.decode('utf-8')
        csv_reader = csv.DictReader(io.StringIO(csv_text))
        
        imported_count = 0
        now = datetime.now().isoformat()
        
        # Append rows to todos table
        for row in csv_reader:
            title = row.get('title', '').strip()
            if not title:  # Skip rows without title
                continue
            
            description = row.get('description', '').strip() or None
            completed = str(row.get('completed', '0')).strip().lower() in ('1', 'true', 'yes')
            
            # Create Todo using SQLModel
            todo = Todo(
                title=title,
                description=description,
                completed=completed,
                created_at=now,
                updated_at=now
            )
            
            session.add(todo)
            imported_count += 1
        
        session.commit()
        
        return {
            "message": f"Successfully imported {imported_count} todos from CSV",
            "imported_count": imported_count,
            "uploaded_at": now
        }
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=400, detail=f"Error importing CSV: {str(e)}")


# ============================================================================
# Lifespan Events
# ============================================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for FastAPI.
    Handles startup and shutdown events.
    In this case we initialize the database on startup and close all connections to it on shutdown.
    """
    # Startup: Initialize database
    init_db()
    yield
    # Shutdown: Close database engine
    engine.dispose()


# ============================================================================
# FastAPI App
# ============================================================================

app = FastAPI(
    title="Todo List API (SQLModel)",
    version="2.0.0",
    description="Todo API using SQLModel - combines SQLAlchemy ORM with Pydantic validation",
    lifespan=lifespan
)

# Custom middleware
@app.middleware("http")
def print_middleware(request: Request, call_next):
    print(f"Request: {request.method} {request.url.path}")
    response = call_next(request)
    return response


# ============================================================================
# API Endpoints
# ============================================================================

@app.get("/")
def read_root():
    """Root endpoint"""
    return {
        "message": "Welcome to Todo List API",
        "version": "2.0.0",
        "framework": "SQLModel"
    }


@app.get("/todos", response_model=list[TodoRead])
def get_all_todos(
    completed: bool | None = None,
    session: Session = Depends(get_session)
):
    """Get all todos, optionally filtered by completed status"""
    todos = read_todos(session, completed)
    return todos


@app.get("/todos/{todo_id}", response_model=TodoRead)
def get_todo(todo_id: int, session: Session = Depends(get_session)):
    """Get a specific todo by ID"""
    todo = get_todo_by_id(session, todo_id)
    if todo is None:
        raise HTTPException(status_code=404, detail="Todo not found")
    return todo


@app.post("/todos", response_model=TodoRead, status_code=201)
def create_todo(todo: TodoCreate, session: Session = Depends(get_session)):
    """Create a new todo"""
    return create_todo_in_db(session, todo)


@app.put("/todos/{todo_id}", response_model=TodoRead)
def update_todo(
    todo_id: int,
    todo_update: TodoUpdate,
    session: Session = Depends(get_session)
):
    """Update an existing todo"""
    return update_todo_in_db(session, todo_id, todo_update)


@app.delete("/todos/{todo_id}", status_code=204)
def delete_todo(todo_id: int, session: Session = Depends(get_session)):
    """Delete a todo"""
    delete_todo_from_db(session, todo_id)
    return None


@app.delete("/todos", status_code=204)
def delete_all_todos(session: Session = Depends(get_session)):
    """Delete all todos"""
    delete_all_todos_from_db(session)
    return None


@app.post("/todos/upload-csv")
async def upload_csv(
    file: UploadFile = File(...),
    session: Session = Depends(get_session)
):
    """Upload a CSV file and append all rows to the todos table. Only appends to todos - CSV file is not stored."""
    # Validate file type
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="File must be a CSV file")
    
    # Read file content
    contents = await file.read()
    
    # Import CSV and store in database
    result = import_csv_to_db(session, contents)
    
    return result


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8002)

# Run the server from root directory:
# uvicorn server_sqlmodel.main_sqlmodel:app --reload --port 8002
#
# Or from server_sqlmodel directory:
# uvicorn main_sqlmodel:app --reload --port 8002

