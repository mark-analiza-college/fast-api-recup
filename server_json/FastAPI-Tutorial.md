# FastAPI Parameter Passing Tutorial

This tutorial explains all the ways to pass parameters implicitly in FastAPI. FastAPI automatically detects parameter types based on their declaration in the function signature.

## Table of Contents

1. [Path Parameters](#1-path-parameters)
2. [Query Parameters](#2-query-parameters)
3. [Request Body](#3-request-body)
4. [Combining Path and Query Parameters](#4-combining-path-and-query-parameters)
5. [Headers](#5-headers)
6. [Cookies](#6-cookies)
7. [Form Data](#7-form-data)
8. [File Uploads](#8-file-uploads)

---

## 1. Path Parameters ⭐ Required

Path parameters are extracted from the URL path itself. They are declared in the route path using `{variable_name}` and as function parameters.

### Example from main.py:

```python
from fastapi import HTTPException

@app.get("/todos/{todo_id}", response_model=TodoItem)
def get_todo(todo_id: int):
    """Get a specific todo by ID"""
    todos = read_todos()
    todo = next((t for t in todos if t.get('id') == todo_id), None)
    if todo is None:
        raise HTTPException(status_code=404, detail="Todo not found")
    return todo
```

**Explanation:** The `todo_id` parameter is automatically extracted from the URL path. When you call `GET /todos/5`, FastAPI automatically converts the string "5" to an integer and passes it to the `todo_id` parameter.

**Note on `next()` function:** The code uses `next()` with a generator expression to efficiently find the first matching todo. This is more efficient than a list comprehension because:
- **Generator expression** `(t for t in todos if t.get('id') == todo_id)` - lazy evaluation, stops after finding first match
  - Used as one liner: `todo = next((t for t in todos if t.get('id') == todo_id), None)`
- **List comprehension** `[t for t in todos if t.get('id') == todo_id]` - eager evaluation, checks ALL items even after finding a match
  - Requires additional line: `todo = matching_todos[0] if matching_todos else None`

The `next()` function takes the generator and returns the first matching item. If no match is found, it returns the default value (the second argument). In this case, we use `None` as the default, but you can use any value:
- `next(generator, None)` - returns `None` if no match
- `next(generator, {})` - returns empty dict if no match
- `next(generator, -1)` - returns `-1` if no match
- `next(generator)` - raises `StopIteration` exception if no match (no default provided)

This is optimal for finding a single item in a list.

**Usage:** `GET /todos/123` → `todo_id = 123`

---

## 2. Query Parameters ⭐ Required

Query parameters are passed in the URL after the `?` symbol. Any function parameter that is not a path parameter and not a Pydantic model is treated as a query parameter.

### Example from main.py:

```python
@app.get("/todos", response_model=list[TodoItem])
def get_all_todos(completed: bool | None = None):
    """Get all todos, optionally filtered by completed status"""
    todos = read_todos()
    if completed is not None:
        todos = [todo for todo in todos if todo.get('completed') == completed]
    return todos
```

**Explanation:** The `completed` parameter is automatically treated as a query parameter because it's not in the path and it's a simple (primitive) type (not a Pydantic model, dict, or other complex type). The `bool | None = None` makes it optional. FastAPI automatically parses the query string and converts the value to the specified type.

**Usage:** 
- `GET /todos` → `completed = None` (returns all todos)
- `GET /todos?completed=true` → `completed = True` (returns only completed todos)
- `GET /todos?completed=false` → `completed = False` (returns only incomplete todos)

### Additional Query Parameter Examples:

```python
# Multiple query parameters
@app.get("/todos/search", response_model=list[TodoItem])
def search_todos(q: str):
    """Search todos by title or description"""
    todos = read_todos()
    
    # Filter todos that match the search query in title or description
    filtered_todos = [
        todo for todo in todos
        if q.lower() in todo.get('title', '').lower() 
        or q.lower() in todo.get('description', '').lower()
    ]
    
    return filtered_todos
```

**Explanation:** This endpoint searches todos by matching the query string against title or description fields. The search is case-insensitive and returns all matching todos.

**Usage:** 
- `GET /todos/search?q=learn` - Search for todos containing "learn"
- `GET /todos/search?q=python` - Search for todos containing "python"

---

## 3. Request Body ⭐ Required

Request body parameters are used for POST, PUT, and PATCH requests. They are declared as Pydantic models or complex types (dict, list, or other complex objects).

*Note: simple/primitive types (str, int, bool) are treated as query parameters, not request bodies.*

### Example from main.py:

```python
from fastapi import BaseModel, HTTPException

# Pydantic models
class TodoItem(BaseModel):
    id: int | None = None
    title: str
    description: str | None = None
    completed: bool = False
    created_at: str | None = None
    updated_at: str | None = None
    
@app.post("/todos", response_model=TodoItem, status_code=201)
def create_todo(todo: TodoItem):
    """Create a new todo"""
    todos = read_todos()
    
    # Generate ID if not provided
    if todo.id is None:
        todo.id = get_next_id(todos)
    
    # Set timestamps
    now = datetime.now().isoformat()
    todo_dict = todo.model_dump()
    todo_dict['created_at'] = now
    todo_dict['updated_at'] = now
    
    todos.append(todo_dict)
    write_todos(todos)
    
    return todo_dict
```

**Explanation:** The `todo: TodoItem` parameter is automatically treated as a request body. FastAPI expects a JSON payload that matches the `TodoItem` Pydantic model structure. FastAPI automatically validates the incoming JSON against the model schema.

**Usage:** 
```bash
POST /todos
Content-Type: application/json

{
  "title": "Learn FastAPI",
  "description": "Complete the tutorial",
  "completed": false
}
```

### Partial Update Example from main.py:

```python
from fastapi import BaseModel, HTTPException

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

@app.put("/todos/{todo_id}", response_model=TodoItem)
def update_todo(todo_id: int, todo_update: TodoUpdate):
    """Update an existing todo"""
    todos = read_todos()
    todo_index = next((i for i, t in enumerate(todos) if t.get('id') == todo_id), None)
    
    if todo_index is None:
        raise HTTPException(status_code=404, detail="Todo not found")
    
    existing_todo = todos[todo_index]
    update_data = todo_update.model_dump(exclude_unset=True)
    
    for key, value in update_data.items():
        existing_todo[key] = value
    
    existing_todo['updated_at'] = datetime.now().isoformat()
    write_todos(todos)
    return existing_todo
```

**Explanation:** This endpoint combines a path parameter (`todo_id`) with a request body (`todo_update`). The `TodoUpdate` model has all optional fields, allowing partial updates. The `exclude_unset=True` ensures only provided fields are updated.

**Usage:**
```bash
PUT /todos/1
Content-Type: application/json

{
  "completed": true
}
```

---

## 4. Combining Path and Query Parameters ⭐ Required

You can combine path parameters with query parameters in the same endpoint.

### Example from main.py with a small change:

```python
@app.get("/todos/{todo_id}", response_model=TodoItem)
def get_todo(todo_id: int, minimal: bool = False):
    """Get a specific todo by ID, optionally return minimal info"""
    todos = read_todos()
    todo = next((t for t in todos if t.get('id') == todo_id), None)
    
    if todo is None:
        raise HTTPException(status_code=404, detail="Todo not found")
    
    # If minimal=True, return only id, title, and completed status
    if minimal:
        return {
            "id": todo.get('id'),
            "title": todo.get('title'),
            "completed": todo.get('completed')
        }
    
    return todo
```

**Explanation:** `todo_id` comes from the path parameter, while `minimal` comes from the query string. FastAPI automatically distinguishes between them. This endpoint allows you to get a full todo or just minimal information based on the query parameter.

**Usage:** 
- `GET /todos/5` → Returns full todo with all fields including created_at and updated_at
- `GET /todos/5?minimal=true` → Returns only id, title, and completed status

---

## 5. Headers 🎁 Bonus

Headers are accessed using the `Header` function from FastAPI. They are useful for authentication tokens, content types, etc.

### Example:

```python
from fastapi import Header

@app.get("/protected")
def protected_route(authorization: str = Header(...)):
    """Access protected resource with authorization header"""
    return {"message": "Access granted", "token": authorization}
```

**Explanation:** The `Header(...)` function tells FastAPI to extract the value from the request headers. The `...` means it's required. FastAPI automatically converts header names from snake_case to kebab-case (e.g., `authorization` → `Authorization`).

**Usage:**
```bash
GET /protected
Authorization: Bearer token123
```

### Optional Header Example:

```python
@app.get("/items")
def get_items(user_agent: str | None = Header(None)):
    """Get items with optional user agent"""
    return {"user_agent": user_agent}
```

---

## 6. Cookies 🎁 Bonus

Cookies are accessed using the `Cookie` function from FastAPI.

### Example:

```python
from fastapi import Cookie

@app.get("/profile")
def get_profile(session_id: str = Cookie(...)):
    """Get user profile using session cookie"""
    return {"session_id": session_id, "message": "Profile loaded"}
```

**Explanation:** The `Cookie(...)` function tells FastAPI to extract the value from cookies. FastAPI automatically reads cookies from the request.

**Usage:**
```bash
GET /profile
Cookie: session_id=abc123xyz
```

### Optional Cookie Example:

```python
@app.get("/preferences")
def get_preferences(theme: str | None = Cookie(None)):
    """Get user preferences with optional theme cookie"""
    return {"theme": theme or "default"}
```

---

## 7. Form Data 🎁 Bonus

Form data is used for HTML form submissions. Use `Form` from FastAPI for individual fields.

### Example:

```python
from fastapi import Form

@app.post("/login")
def login(username: str = Form(...), password: str = Form(...)):
    """Login with form data"""
    return {"username": username, "message": "Login successful"}
```

**Explanation:** The `Form(...)` function tells FastAPI to extract values from form-encoded data (application/x-www-form-urlencoded). This is different from JSON request bodies.

**Usage:**
```bash
POST /login
Content-Type: application/x-www-form-urlencoded

username=john&password=secret123
```

### Combining Form with Pydantic Model:

```python
from fastapi import Form
from pydantic import BaseModel

class LoginData(BaseModel):
    username: str
    password: str

@app.post("/login-v2")
def login_v2(
    username: str = Form(...),
    password: str = Form(...),
    remember_me: bool = Form(False)
):
    """Login with multiple form fields"""
    return LoginData(username=username, password=password)
```

---

## 8. File Uploads 🎁 Bonus

File uploads use the `File` and `UploadFile` classes from FastAPI.

### Single File Upload Example:

```python
from fastapi import File, UploadFile

@app.post("/upload")
def upload_file(file: UploadFile = File(...)):
    """Upload a single file"""
    return {
        "filename": file.filename,
        "content_type": file.content_type,
        "size": file.size
    }
```

**Explanation:** `UploadFile` is a special class that handles file uploads. FastAPI automatically reads the file from the multipart/form-data request.

**Usage:**
```bash
POST /upload
Content-Type: multipart/form-data

[file binary data]
```

### Multiple Files Upload Example:

```python
@app.post("/upload-multiple")
def upload_files(files: list[UploadFile] = File(...)):
    """Upload multiple files"""
    return {
        "count": len(files),
        "filenames": [f.filename for f in files]
    }
```

### Combining File with Form Data:

```python
@app.post("/upload-with-data")
def upload_with_metadata(
    file: UploadFile = File(...),
    description: str = Form(...)
):
    """Upload file with additional form data"""
    return {
        "filename": file.filename,
        "description": description
    }
```

---

## Parameter Priority Rules

FastAPI determines parameter types in this order:

1. **Path parameters** - If the parameter name is in the path (e.g., `/items/{item_id}`)
2. **Request body** - If the parameter is a Pydantic model or complex type
3. **Query parameters** - If it's a simple type (str, int, bool, etc.) and not in the path
4. **Explicit types** - If you use `Query()`, `Header()`, `Cookie()`, `Form()`, or `File()`

---

## Best Practices

1. **Use Pydantic models for request bodies** - Provides automatic validation and documentation
2. **Make optional parameters explicit** - Use `Type | None = None` for query parameters
3. **Use type hints** - FastAPI uses them for validation and OpenAPI documentation
4. **Combine parameter types wisely** - Path + Query + Body is common and well-supported
5. **Use `exclude_unset=True`** - For partial updates with Pydantic models

---

## Summary

FastAPI's automatic parameter detection makes it easy to work with different types of data:

- **Path parameters**: Declare in URL path `{variable}`
- **Query parameters**: Simple types not in path
- **Request body**: Pydantic models
- **Headers**: Use `Header()`
- **Cookies**: Use `Cookie()`
- **Form data**: Use `Form()`
- **Files**: Use `File()` and `UploadFile`

All parameter types are automatically validated, documented, and available in the interactive API docs at `/docs`.

