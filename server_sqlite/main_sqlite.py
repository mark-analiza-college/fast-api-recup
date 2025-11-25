from fastapi import FastAPI, HTTPException, Request, UploadFile, File
from pydantic import BaseModel
import sqlite3
import os
from datetime import datetime
import uvicorn
import csv
import io

app = FastAPI(title="Todo List API (SQLite)", version="1.0.0")

# Custom middleware with print statement
@app.middleware("http")
def print_middleware(request: Request, call_next):
    print(f"Request: {request.method} {request.url.path}")
    response = call_next(request)
    return response

# Database file path
DB_FILE = "server_sqlite/todos_db.sqlite"

# Pydantic models
class TodoItem(BaseModel):
    id: int | None = None
    title: str
    description: str | None = None
    completed: bool = False
    created_at: str | None = None
    updated_at: str | None = None

class TodoUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    completed: bool | None = None

# Database initialization
def init_db():
    """Initialize database and create tables if they don't exist"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    # Create todos table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS todos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT,
            -- SQLite doesn't have a native BOOLEAN type. It uses INTEGER where 0 = False and 1 = True.
            -- This is a common pattern in SQLite. We convert it back to bool in Python using bool(row['completed']).
            completed INTEGER NOT NULL DEFAULT 0,
            created_at TEXT,
            updated_at TEXT
        )
    """)
    
    conn.commit()
    conn.close()

# Initialize database on startup
init_db()

# Helper functions for database operations
def get_db_connection():
    """Get database connection"""
    conn = sqlite3.connect(DB_FILE)
    # row_factory = sqlite3.Row converts each row from a tuple to a Row object that allows
    # column access by name (row['id']) instead of by index (row[0]). This makes code more readable.
    conn.row_factory = sqlite3.Row
    return conn

# SQLite doesn't have a built-in function to convert rows to dictionaries.
# However, sqlite3.Row objects have a .keys() method and can be converted using dict(row).
# But we need custom logic to convert INTEGER (0/1) to bool, so a custom function is better here.
def row_to_dict(row):
    """Convert SQLite row to dictionary"""
    # Alternative: dict(row) would work, but we need to convert completed INTEGER to bool
    return {
        'id': row['id'],
        'title': row['title'],
        'description': row['description'],
        'completed': bool(row['completed']),  # Convert INTEGER to bool
        'created_at': row['created_at'],
        'updated_at': row['updated_at']
    }

def read_todos(completed: bool | None = None) -> list[dict]:
    """Read todos from database"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    if completed is not None:
        cursor.execute("SELECT * FROM todos WHERE completed = ?", (1 if completed else 0,))
    else:
        cursor.execute("SELECT * FROM todos")
    
    rows = cursor.fetchall()
    conn.close()
    
    return [row_to_dict(row) for row in rows]

def get_todo_by_id(todo_id: int) -> dict | None:
    """Get a single todo by ID"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM todos WHERE id = ?", (todo_id,))
    row = cursor.fetchone()
    conn.close()
    
    if row:
        return row_to_dict(row)
    return None

def create_todo_in_db(todo: TodoItem) -> dict:
    """Create a new todo in database"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Set timestamps
    now = datetime.now().isoformat()
    
    # Always let SQLite auto-increment the ID - we don't include 'id' in the INSERT statement.
    # SQLite will automatically generate the next ID using AUTOINCREMENT.
    # Using RETURNING clause (SQLite 3.35.0+) to get the inserted row atomically.
    # This is safer than cursor.lastrowid because it returns the actual row that was inserted,
    # eliminating any race condition concerns between INSERT and SELECT.
    # Parameterized queries (using ? placeholders) protect against SQL injection.
    cursor.execute("""
        INSERT INTO todos (title, description, completed, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?)
        RETURNING *
    """, (todo.title, todo.description, 1 if todo.completed else 0, now, now))
    
    # Fetch the row that was just inserted (RETURNING clause returns it directly)
    row = cursor.fetchone()
    
    conn.commit()
    conn.close()
    
    # Convert the returned row to dictionary
    return row_to_dict(row)

def update_todo_in_db(todo_id: int, todo_update: TodoUpdate) -> dict:
    """Update an existing todo in database"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Check if todo exists
    cursor.execute("SELECT * FROM todos WHERE id = ?", (todo_id,))
    row = cursor.fetchone()
    
    if not row:
        conn.close()
        return None
    
    # Build update query dynamically based on provided fields
    update_data = todo_update.model_dump(exclude_unset=True)
    
    if not update_data:
        conn.close()
        return get_todo_by_id(todo_id)
    
    # Build SET clause
    set_clauses = []
    values = []
    
    if 'title' in update_data:
        set_clauses.append("title = ?")
        values.append(update_data['title'])
    
    if 'description' in update_data:
        set_clauses.append("description = ?")
        values.append(update_data['description'])
    
    if 'completed' in update_data:
        set_clauses.append("completed = ?")
        values.append(1 if update_data['completed'] else 0)
    
    # Always update updated_at
    set_clauses.append("updated_at = ?")
    values.append(datetime.now().isoformat())
    
    values.append(todo_id)  # For WHERE clause
    
    # query = "UPDATE todos SET title = ?, description = ?, completed = ?, updated_at = ? WHERE id = ?"
    # values = [title, description, completed, datetime.now().isoformat(), todo_id]
    query = f"UPDATE todos SET {', '.join(set_clauses)} WHERE id = ?"
    cursor.execute(query, values)
    
    conn.commit()
    conn.close()
    
    return get_todo_by_id(todo_id)

def delete_todo_from_db(todo_id: int) -> bool:
    """Delete a todo from database"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Check if todo exists
    cursor.execute("SELECT id FROM todos WHERE id = ?", (todo_id,))
    if not cursor.fetchone():
        conn.close()
        return None
    
    cursor.execute("DELETE FROM todos WHERE id = ?", (todo_id,))
    conn.commit()
    conn.close()
    
    return True

def delete_all_todos_from_db():
    """Delete all todos from database"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("DELETE FROM todos")
    conn.commit()
    conn.close()

def import_csv_to_db(csv_content: bytes) -> dict:
    """Import CSV content and append rows to todos table. CSV file is not stored."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Read CSV content
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
            completed = 1 if str(row.get('completed', '0')).strip().lower() in ('1', 'true', 'yes') else 0
            
            cursor.execute("""
                INSERT INTO todos (title, description, completed, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?)
            """, (title, description, completed, now, now))
            imported_count += 1
        
        conn.commit()
        
        return {
            "message": f"Successfully imported {imported_count} todos from CSV",
            "imported_count": imported_count,
            "uploaded_at": now
        }
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=400, detail=f"Error importing CSV: {str(e)}")
    finally:
        conn.close()

# API Endpoints

@app.get("/")
def read_root():
    """Root endpoint"""
    return {"message": "Welcome to Todo List API", "version": "1.0.0"}

@app.get("/todos", response_model=list[TodoItem])
def get_all_todos(completed: bool | None = None):
    """Get all todos, optionally filtered by completed status"""
    todos = read_todos(completed)
    return todos

@app.get("/todos/{todo_id}", response_model=TodoItem)
def get_todo(todo_id: int):
    """Get a specific todo by ID"""
    todo = get_todo_by_id(todo_id)
    if todo is None:
        raise HTTPException(status_code=404, detail="Todo not found")
    return todo

@app.post("/todos", response_model=TodoItem, status_code=201)
def create_todo(todo: TodoUpdate):
    """Create a new todo"""
    return create_todo_in_db(todo)

@app.put("/todos/{todo_id}", response_model=TodoItem)
def update_todo(todo_id: int, todo_update: TodoUpdate):
    """Update an existing todo"""
    updated_todo = update_todo_in_db(todo_id, todo_update)
    if updated_todo is None:
        raise HTTPException(status_code=404, detail="Todo not found")
    return updated_todo

@app.delete("/todos/{todo_id}", status_code=204)
def delete_todo(todo_id: int):
    """Delete a todo"""
    deleted = delete_todo_from_db(todo_id)
    if deleted is None:
        raise HTTPException(status_code=404, detail="Todo not found")
    return None

@app.delete("/todos", status_code=204)
def delete_all_todos():
    """Delete all todos"""
    delete_all_todos_from_db()
    return None

@app.post("/todos/upload-csv")
async def upload_csv(file: UploadFile = File(...)):
    """Upload a CSV file and append all rows to the todos table. Only appends to todos - CSV file is not stored."""
    # Validate file type
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="File must be a CSV file")
    
    # Read file content
    contents = await file.read()
    
    # Import CSV and store in database
    result = import_csv_to_db(contents)
    
    return result

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001)

# Run the server from root directory:
# uvicorn server_sqlite.main_sqlite:app --reload --port 8001
#
# Or from server_sqlite directory:
# uvicorn main_sqlite:app --reload --port 8001