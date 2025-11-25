# SQLModel Tutorial - Todo List API

This tutorial explains how to build a FastAPI application using **SQLModel**, a powerful library that combines SQLAlchemy (ORM) and Pydantic (validation) into a single, elegant solution.

## Table of Contents

1. [What is SQLModel?](#1-what-is-sqlmodel)
2. [Why Use SQLModel?](#2-why-use-sqlmodel)
3. [Installation](#3-installation)
4. [Project Structure](#4-project-structure)
5. [Understanding the Code](#5-understanding-the-code)
6. [Key Concepts](#6-key-concepts)
7. [Comparison: SQLModel vs Raw SQLite](#7-comparison-sqlmodel-vs-raw-sqlite)
8. [Running the Server](#8-running-the-server)
9. [API Endpoints](#9-api-endpoints)
10. [Best Practices](#10-best-practices)

---

## 1. What is SQLModel? ⭐ Required

**SQLModel** is a library created by Sebastian Ramirez (creator of FastAPI) that combines:
- **SQLAlchemy** - Python's most popular ORM (Object-Relational Mapping)
- **Pydantic** - Data validation using Python type annotations

### The Problem It Solves

**Before SQLModel:**
```python
# You had to define models twice:

# 1. Pydantic model for API validation
class TodoItem(BaseModel):
    id: int
    title: str
    completed: bool

# 2. SQLAlchemy model for database
class Todo(Base):
    __tablename__ = "todos"
    id = Column(Integer, primary_key=True)
    title = Column(String)
    completed = Column(Boolean)
```

**With SQLModel:**
```python
# One model for both!
class Todo(SQLModel, table=True):
    id: Optional[int] = Field(primary_key=True)
    title: str
    completed: bool
```

**One model = Database table + API validation!** 🎉

---

## 2. Why Use SQLModel? ⭐ Required

### Advantages

1. **Less Code** - Define models once, use everywhere
2. **Type Safety** - Full IDE support and type checking
3. **Automatic Validation** - Pydantic validates all data
4. **Database Agnostic** - Works with SQLite, PostgreSQL, MySQL, etc.
5. **FastAPI Integration** - Built by the same creator, perfect fit
6. **Less Boilerplate** - No manual SQL queries needed

### When to Use SQLModel

✅ **Use SQLModel when:**
- Building FastAPI applications
- Need database + API validation
- Want type safety
- Working with complex data models
- Need relationships between tables

❌ **Don't use SQLModel when:**
- Simple scripts with minimal database needs
- Performance-critical applications (raw SQL might be faster)
- Very simple CRUD (might be overkill)

---

## 3. Installation ⭐ Required

### Install SQLModel

```bash
pip install sqlmodel
```

### Required Dependencies

SQLModel requires:
- `sqlalchemy` - ORM library
- `pydantic` - Validation library
- `fastapi` - Web framework (if using with FastAPI)

All are installed automatically with SQLModel.

---

## 4. Project Structure

```
server_sqlmodel/
├── main_sqlmodel.py    # Main application file
├── README.md           # This tutorial
└── todos_db.sqlite     # SQLite database (created automatically)
```

---

## 5. Understanding the Code

Let's break down the key components of `main_sqlmodel.py`:

### 5.1 Database Engine

```python
DATABASE_URL = "sqlite:///server_sqlmodel/todos_db.sqlite"
engine = create_engine(DATABASE_URL, echo=False)
```

**Explanation:**
- `DATABASE_URL` - Connection string for SQLite
- `create_engine()` - Creates a connection pool to the database
- `echo=False` - Set to `True` to see all SQL queries in console (debugging)

**Other Database URLs:**
```python
# PostgreSQL
DATABASE_URL = "postgresql://user:password@localhost/dbname"

# MySQL
DATABASE_URL = "mysql://user:password@localhost/dbname"
```

### 5.2 SQLModel Models

```python
class TodoBase(SQLModel):
    """Base model with common fields"""
    title: str
    description: Optional[str] = None
    completed: bool = False

class Todo(TodoBase, table=True):
    """Database table model"""
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: Optional[str] = Field(default_factory=lambda: datetime.now().isoformat())
    updated_at: Optional[str] = Field(default_factory=lambda: datetime.now().isoformat())
```

**Explanation:**
- `TodoBase` - Shared fields (not a table, just inheritance)
- `Todo` - Actual database table (`table=True`)
- `Field()` - SQLModel field with options (primary_key, default, etc.)
- `default_factory` - Function to generate default value

**Model Types:**
- `Todo` (table=True) - Database table
- `TodoCreate` - For POST requests (no id/timestamps)
- `TodoUpdate` - For PUT requests (all optional)
- `TodoRead` - For GET responses (includes all fields)

### 5.3 Database Session

```python
def get_session():
    """Dependency for database sessions"""
    with Session(engine) as session:
        yield session
```

**Explanation:**
- `Session` - SQLAlchemy session (database connection)
- `Depends(get_session)` - FastAPI dependency injection
- `yield` - Session is closed automatically after request

**Why Sessions?**
- Manage database connections
- Handle transactions
- Automatic cleanup

### 5.4 Querying Data

```python
# Get all todos
statement = select(Todo)
todos = session.exec(statement).all()

# Get with filter
statement = select(Todo).where(Todo.completed == True)
todos = session.exec(statement).all()

# Get by ID
todo = session.get(Todo, todo_id)
```

**Explanation:**
- `select()` - Type-safe query builder
- `.where()` - Add conditions
- `.exec()` - Execute query
- `.all()` - Get all results
- `.first()` - Get first result
- `session.get()` - Get by primary key

### 5.5 Creating Data

```python
db_todo = Todo(
    title=todo.title,
    description=todo.description,
    completed=todo.completed
)

session.add(db_todo)
session.commit()
session.refresh(db_todo)  # Get generated ID
```

**Explanation:**
- Create model instance
- `session.add()` - Add to session
- `session.commit()` - Save to database
- `session.refresh()` - Reload from database (get auto-generated ID)

### 5.6 Updating Data

```python
todo = session.get(Todo, todo_id)
todo.title = "New Title"
session.add(todo)
session.commit()
```

**Explanation:**
- Get existing record
- Modify attributes
- Add to session and commit

### 5.7 Deleting Data

```python
todo = session.get(Todo, todo_id)
session.delete(todo)
session.commit()
```

**Explanation:**
- Get record
- Delete from session
- Commit changes

---

## 6. Key Concepts

### 6.1 Model Inheritance

```python
class TodoBase(SQLModel):
    # Common fields
    title: str
    completed: bool

class Todo(TodoBase, table=True):
    # Database-specific fields
    id: Optional[int] = Field(primary_key=True)
```

**Benefits:**
- Reuse common fields
- Separate concerns (API vs Database)
- Easier maintenance

### 6.2 Field Types

```python
# Required field
title: str

# Optional field
description: Optional[str] = None

# Field with default
completed: bool = False

# Primary key
id: Optional[int] = Field(default=None, primary_key=True)

# Field with default factory
created_at: str = Field(default_factory=lambda: datetime.now().isoformat())
```

### 6.3 Type Safety

SQLModel provides full type safety:

```python
# IDE knows todo.title is a string
todo = session.get(Todo, 1)
print(todo.title.upper())  # IDE autocomplete works!

# Type checking catches errors
todo.completed = "yes"  # Error! Should be bool
```

### 6.4 Automatic Validation

Pydantic validates all data automatically:

```python
# This will fail validation
todo = TodoCreate(title="")  # Error: title cannot be empty

# This will pass
todo = TodoCreate(title="Learn SQLModel", completed=True)
```

---

## 7. Comparison: SQLModel vs Raw SQLite

### Raw SQLite (from server_sqlite)

```python
# Manual SQL queries
conn = sqlite3.connect(DB_FILE)
cursor = conn.cursor()
cursor.execute("SELECT * FROM todos WHERE completed = ?", (1,))
rows = cursor.fetchall()
conn.close()

# Manual conversion
todos = [row_to_dict(row) for row in rows]
```

### SQLModel

```python
# Type-safe queries
with Session(engine) as session:
    statement = select(Todo).where(Todo.completed == True)
    todos = session.exec(statement).all()
    # todos is already a list of Todo objects!
```

### Comparison Table

| Feature | Raw SQLite | SQLModel |
|---------|-----------|----------|
| Type Safety | ❌ | ✅ |
| Validation | ❌ | ✅ |
| IDE Support | ❌ | ✅ |
| Boilerplate | High | Low |
| Learning Curve | Low | Medium |
| Performance | Fast | Fast (with caching) |
| Database Agnostic | ❌ | ✅ |

---

## 8. Running the Server

### Install Dependencies

```bash
pip install sqlmodel fastapi uvicorn
```

### Run from Root Directory

```bash
uvicorn server_sqlmodel.main_sqlmodel:app --reload --port 8002
```

### Run from server_sqlmodel Directory

```bash
cd server_sqlmodel
uvicorn main_sqlmodel:app --reload --port 8002
```

### Run Directly

```bash
python server_sqlmodel/main_sqlmodel.py
```

The server will run on `http://localhost:8002`

---

## 9. API Endpoints

All endpoints are the same as the SQLite version:

### GET `/`
Root endpoint

### GET `/todos`
Get all todos
- Query param: `completed` (bool, optional)

### GET `/todos/{todo_id}`
Get specific todo by ID

### POST `/todos`
Create new todo
- Body: `TodoCreate` model

### PUT `/todos/{todo_id}`
Update existing todo
- Body: `TodoUpdate` model (all fields optional)

### DELETE `/todos/{todo_id}`
Delete specific todo

### DELETE `/todos`
Delete all todos

### POST `/todos/upload-csv`
Upload CSV file and import todos

---

## 10. Best Practices

### 10.1 Use Separate Models for Different Purposes

```python
# Database model
class Todo(SQLModel, table=True):
    id: int
    title: str

# Create model (no id)
class TodoCreate(SQLModel):
    title: str

# Update model (all optional)
class TodoUpdate(SQLModel):
    title: Optional[str] = None
```

### 10.2 Use Dependency Injection for Sessions

```python
def get_session():
    with Session(engine) as session:
        yield session

@app.get("/todos")
def get_todos(session: Session = Depends(get_session)):
    # Session automatically closed after request
    pass
```

### 10.3 Use Transactions

```python
try:
    session.add(todo)
    session.commit()
except Exception:
    session.rollback()
    raise
```

### 10.4 Use Type Hints

```python
# Good
def get_todo(todo_id: int, session: Session) -> Todo:
    return session.get(Todo, todo_id)

# Bad
def get_todo(todo_id, session):
    return session.get(Todo, todo_id)
```

### 10.5 Handle Errors

```python
todo = session.get(Todo, todo_id)
if not todo:
    raise HTTPException(status_code=404, detail="Todo not found")
```

### 10.6 Use Select Statements for Complex Queries

```python
# Good - type-safe
statement = select(Todo).where(Todo.completed == True)
todos = session.exec(statement).all()

# Avoid - not type-safe
todos = session.query(Todo).filter(Todo.completed == True).all()
```

---

## Common Patterns

### Pattern 1: Pagination

```python
@app.get("/todos")
def get_todos(
    skip: int = 0,
    limit: int = 10,
    session: Session = Depends(get_session)
):
    statement = select(Todo).offset(skip).limit(limit)
    todos = session.exec(statement).all()
    return todos
```

### Pattern 2: Sorting

```python
from sqlmodel import select, col

statement = select(Todo).order_by(col(Todo.created_at).desc())
todos = session.exec(statement).all()
```

### Pattern 3: Relationships (Advanced)

```python
class User(SQLModel, table=True):
    id: Optional[int] = Field(primary_key=True)
    name: str
    todos: List["Todo"] = Relationship(back_populates="user")

class Todo(SQLModel, table=True):
    id: Optional[int] = Field(primary_key=True)
    title: str
    user_id: int = Field(foreign_key="user.id")
    user: User = Relationship(back_populates="todos")
```

---

## Troubleshooting

### Issue: "Table already exists"
**Solution:** Delete the database file and restart

### Issue: "Session is closed"
**Solution:** Make sure you're using `Depends(get_session)` correctly

### Issue: "Type error"
**Solution:** Check your type hints match the model definitions

### Issue: "Validation error"
**Solution:** Check that your request body matches the model schema

---

## Next Steps

1. **Add Relationships** - Connect multiple tables
2. **Add Authentication** - Secure your API
3. **Add Migrations** - Use Alembic for schema changes
4. **Add Testing** - Write unit tests
5. **Deploy** - Deploy to production

---

## Resources

- [SQLModel Documentation](https://sqlmodel.tiangolo.com/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [Pydantic Documentation](https://docs.pydantic.dev/)

---

## Summary

SQLModel combines the best of SQLAlchemy and Pydantic:
- ✅ One model definition for database and API
- ✅ Automatic validation
- ✅ Type safety
- ✅ Less boilerplate
- ✅ Perfect FastAPI integration

**Use SQLModel when building FastAPI applications with databases!** 🚀

