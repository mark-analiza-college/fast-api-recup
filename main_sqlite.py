from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel
import sqlite3
import os
from datetime import datetime
import uvicorn

app = FastAPI(title="Todo List API (SQLite)", version="1.0.0")

# Custom middleware with print statement
@app.middleware("http")
def print_middleware(request: Request, call_next):
    print(f"Request: {request.method} {request.url.path}")
    response = call_next(request)
    return response

# Database file path
DB_FILE = "todos_db"

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
    """Initialize database and create table if it doesn't exist"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS todos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT,
            -- TODO: Can we make this into boolean True / False?
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
    # TODO: Explain this and explain why I dont see row_factory anywhere else in the code.
    conn.row_factory = sqlite3.Row  # This allows column access by name
    return conn

# TODO: Isn't there an sqlite built in function for this?
def row_to_dict(row):
    """Convert SQLite row to dictionary"""
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
    
    # Check if ID already exists (if provided)
    if todo.id is not None:
        cursor.execute("SELECT id FROM todos WHERE id = ?", (todo.id,))
        if cursor.fetchone():
            conn.close()
            raise HTTPException(status_code=400, detail="Todo with this ID already exists")
    
    # Set timestamps
    now = datetime.now().isoformat()
    
    # TODO: Explain this protects us from SQL injection
    if todo.id is not None:
        # Insert with specific ID
        cursor.execute("""
            INSERT INTO todos (id, title, description, completed, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (todo.id, todo.title, todo.description, 1 if todo.completed else 0, now, now))
    else:
        # Let SQLite auto-increment the ID
        cursor.execute("""
            INSERT INTO todos (title, description, completed, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?)
        """, (todo.title, todo.description, 1 if todo.completed else 0, now, now))
        # TODO: Explain this
        todo.id = cursor.lastrowid
    
    conn.commit()
    conn.close()
    
    # Return the created todo
    return get_todo_by_id(todo.id)

def update_todo_in_db(todo_id: int, todo_update: TodoUpdate) -> dict:
    """Update an existing todo in database"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Check if todo exists
    cursor.execute("SELECT * FROM todos WHERE id = ?", (todo_id,))
    row = cursor.fetchone()
    
    if not row:
        conn.close()
        raise HTTPException(status_code=404, detail="Todo not found")
    
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
        raise HTTPException(status_code=404, detail="Todo not found")
    
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
def create_todo(todo: TodoItem):
    """Create a new todo"""
    return create_todo_in_db(todo)

@app.put("/todos/{todo_id}", response_model=TodoItem)
def update_todo(todo_id: int, todo_update: TodoUpdate):
    """Update an existing todo"""
    return update_todo_in_db(todo_id, todo_update)

@app.delete("/todos/{todo_id}", status_code=204)
def delete_todo(todo_id: int):
    """Delete a todo"""
    delete_todo_from_db(todo_id)
    return None

@app.delete("/todos", status_code=204)
def delete_all_todos():
    """Delete all todos"""
    delete_all_todos_from_db()
    return None

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001)

