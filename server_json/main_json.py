from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel
import json
import os
from datetime import datetime
import uvicorn

app = FastAPI(title="Todo List API", version="1.0.0")

# Custom middleware with print statement
@app.middleware("http")
def print_middleware(request: Request, call_next):
    print(f"Request: {request.method} {request.url.path}")
    response = call_next(request)
    return response

# JSON file path
JSON_FILE = "todos.json"

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

# Helper functions for JSON file operations
def read_todos() -> list[dict]:
    """Read todos from JSON file"""
    if not os.path.exists(JSON_FILE):
        return []
    try:
        with open(JSON_FILE, 'r') as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        return []

def write_todos(todos: list[dict]) -> None:
    """Write todos to JSON file"""
    with open(JSON_FILE, 'w') as f:
        json.dump(todos, f, indent=2)

def get_next_id(todos: list[dict]) -> int:
    """Get the next available ID"""
    if not todos:
        return 1
    return max(todo.get('id', 0) for todo in todos) + 1

# API Endpoints

@app.get("/")
def read_root():
    """Root endpoint"""
    return {"message": "Welcome to Todo List API", "version": "1.0.0"}

# @app.get("/todos", response_model=list[TodoItem])
# def get_all_todos():
#     """Get all todos"""
#     todos = read_todos()
#     return todos

# /todos?completed=true"
# /todos?completed=false"
# /todos
@app.get("/todos", response_model=list[TodoItem])
def get_all_todos(completed: bool | None = None):
    """Get all todos, optionally filtered by completed status"""
    todos = read_todos()
    if completed is not None:
        todos = [todo for todo in todos if todo.get('completed') == completed]
    return todos

@app.get("/todos/{todo_id}", response_model=TodoItem)
def get_todo(todo_id: int):
    """Get a specific todo by ID"""
    todos = read_todos()
    todo = next((t for t in todos if t.get('id') == todo_id), None)
    if todo is None:
        raise HTTPException(status_code=404, detail="Todo not found")
    return todo

@app.post("/todos", response_model=TodoItem, status_code=201)
def create_todo(todo: TodoItem):
    """Create a new todo"""
    todos = read_todos()
    
    # Generate ID if not provided
    if todo.id is None:
        todo.id = get_next_id(todos)
    
    # Check if ID already exists
    if any(t.get('id') == todo.id for t in todos):
        raise HTTPException(status_code=400, detail="Todo with this ID already exists")
    
    # Set timestamps
    now = datetime.now().isoformat()
    todo_dict = todo.model_dump()
    todo_dict['created_at'] = now
    todo_dict['updated_at'] = now
    
    todos.append(todo_dict)
    write_todos(todos)
    
    return todo_dict

@app.put("/todos/{todo_id}", response_model=TodoItem)
def update_todo(todo_id: int, todo_update: TodoUpdate):
    """Update an existing todo"""
    todos = read_todos()
    todo_index = next((i for i, t in enumerate(todos) if t.get('id') == todo_id), None)
    
    if todo_index is None:
        raise HTTPException(status_code=404, detail="Todo not found")
    
    # Update only provided fields
    existing_todo = todos[todo_index]
    # model_dump() is used to convert the Pydantic model to a dictionary
    # exclude_unset=True is used to exclude fields that are not set
    update_data = todo_update.model_dump(exclude_unset=True)
    
    for key, value in update_data.items():
        existing_todo[key] = value
    
    # Update timestamp
    # datetime.now().isoformat() is used to get the current date and time in ISO format
    # ISO format is a standard format for dates and times
    existing_todo['updated_at'] = datetime.now().isoformat()
    
    write_todos(todos)
    return existing_todo

@app.delete("/todos/{todo_id}", status_code=204)
def delete_todo(todo_id: int):
    """Delete a todo"""
    todos = read_todos()
    todo_index = next((i for i, t in enumerate(todos) if t.get('id') == todo_id), None)
    
    if todo_index is None:
        raise HTTPException(status_code=404, detail="Todo not found")
    
    todos.pop(todo_index)
    write_todos(todos)
    return None

@app.delete("/todos", status_code=204)
def delete_all_todos():
    """Delete all todos"""
    write_todos([])
    return None

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)


# Run the server
# uvicorn server_json.main_json:app --reload --port 8000