# FastAPI Exercises

Practice creating FastAPI endpoints with increasing difficulty. Each exercise focuses on different aspects of FastAPI including Pydantic models, path parameters, query parameters, and request bodies.

---

## Exercise 1: Simple GET Endpoint (Easy) ⭐ Required

**Task:** Create a simple GET endpoint that returns a welcome message.

**Requirements:**
- Endpoint: `GET /hello`
- Returns: `{"message": "Hello, FastAPI!"}`

**Expected Usage:**
```bash
GET /hello
Response: {"message": "Hello, FastAPI!"}
```

---

## Exercise 2: Path Parameter (Easy) ⭐ Required

**Task:** Create an endpoint that greets a user by name using a path parameter.

**Requirements:**
- Endpoint: `GET /hello/{name}`
- Path parameter: `name` (string)
- Returns: `{"message": "Hello, {name}!"}`

**Expected Usage:**
```bash
GET /hello/Alice
Response: {"message": "Hello, Alice!"}
```

---

## Exercise 3: Query Parameters (Easy) ⭐ Required

**Task:** Create an endpoint that performs basic math operations using query parameters.

**Requirements:**
- Endpoint: `GET /calculate`
- Query parameters: `a` (int), `b` (int), `operation` (str: "add", "subtract", "multiply", "divide")
- Returns: `{"result": <calculated_value>}`
- Handle division by zero with appropriate error

**Expected Usage:**
```bash
GET /calculate?a=10&b=5&operation=add
Response: {"result": 15}

GET /calculate?a=10&b=5&operation=divide
Response: {"result": 2.0}

GET /calculate?a=10&b=0&operation=divide
Response: 400 Bad Request with error message
```

---

## Exercise 4: Simple POST with Pydantic Model (Medium) ⭐ Required

**Task:** Create a user registration endpoint using a Pydantic model.

**Requirements:**
- Endpoint: `POST /users`
- Request body: User model with `name` (str), `email` (str), `age` (int)
- Returns: Created user with status code 201
- Validate that email contains "@"

**Pydantic Model:**
```python
class User(BaseModel):
    name: str
    email: str
    age: int
```

**Expected Usage:**
```bash
POST /users
Content-Type: application/json

{
  "name": "John Doe",
  "email": "john@example.com",
  "age": 30
}

Response: 201 Created
{
  "name": "John Doe",
  "email": "john@example.com",
  "age": 30
}
```

---

## Exercise 5: Path + Query Parameters (Medium) ⭐ Required

**Task:** Create an endpoint to get items with pagination and filtering.

**Requirements:**
- Endpoint: `GET /items/{category}`
- Path parameter: `category` (str)
- Query parameters: `page` (int, default=1), `limit` (int, default=10), `sort` (str | None, optional: "asc" or "desc")
- Returns: List of items with pagination info

**Expected Usage:**
```bash
GET /items/electronics?page=1&limit=5&sort=asc
Response: {
  "category": "electronics",
  "page": 1,
  "limit": 5,
  "sort": "asc",
  "items": [...]
}
```

---

## Exercise 6: PUT with Partial Update (Medium) ⭐ Required

**Task:** Create an endpoint to update a product with optional fields.

**Requirements:**
- Endpoint: `PUT /products/{product_id}`
- Path parameter: `product_id` (int)
- Request body: ProductUpdate model with all optional fields
- Returns: Updated product or 404 if not found

**Pydantic Models:**
```python
class ProductUpdate(BaseModel):
    name: str | None = None
    price: float | None = None
    description: str | None = None
    in_stock: bool | None = None
```

**Expected Usage:**
```bash
PUT /products/1
Content-Type: application/json

{
  "price": 29.99,
  "in_stock": true
}

Response: Updated product object
```

---

## Exercise 7: Complex Query Parameters (Medium) ⭐ Required

**Task:** Create a search endpoint with multiple optional filters.

**Requirements:**
- Endpoint: `GET /search`
- Query parameters:
  - `q` (str, required): search query
  - `min_price` (float | None, optional): minimum price filter
  - `max_price` (float | None, optional): maximum price filter
  - `category` (str | None, optional): filter by category
  - `available_only` (bool, default=False): only show available items
- Returns: Filtered search results

**Expected Usage:**
```bash
GET /search?q=laptop&min_price=500&max_price=2000&category=electronics&available_only=true
Response: {
  "query": "laptop",
  "filters": {
    "min_price": 500,
    "max_price": 2000,
    "category": "electronics",
    "available_only": true
  },
  "results": [...]
}
```

---

## Exercise 8: Nested Pydantic Models (Hard) 🎁 Bonus

**Task:** Create an endpoint to create an order with nested items.

**Requirements:**
- Endpoint: `POST /orders`
- Request body: Order model containing:
  - `customer_name` (str)
  - `customer_email` (str)
  - `items` (list of OrderItem)
  - `shipping_address` (Address model)
- OrderItem model: `product_id` (int), `quantity` (int), `price` (float)
- Address model: `street` (str), `city` (str), `zip_code` (str), `country` (str)
- Calculate total price automatically
- Returns: Created order with calculated total

**Expected Usage:**
```bash
POST /orders
Content-Type: application/json

{
  "customer_name": "Jane Smith",
  "customer_email": "jane@example.com",
  "items": [
    {"product_id": 1, "quantity": 2, "price": 19.99},
    {"product_id": 2, "quantity": 1, "price": 49.99}
  ],
  "shipping_address": {
    "street": "123 Main St",
    "city": "New York",
    "zip_code": "10001",
    "country": "USA"
  }
}

Response: 201 Created with order including calculated total
```

---

## Exercise 9: Multiple Path Parameters + Body (Hard) 🎁 Bonus

**Task:** Create an endpoint to add a comment to a specific post by a specific user.

**Requirements:**
- Endpoint: `POST /users/{user_id}/posts/{post_id}/comments`
- Path parameters: `user_id` (int), `post_id` (int)
- Request body: Comment model with `content` (str), `author_name` (str)
- Validate that `author_name` matches the user_id (or return 403)
- Returns: Created comment with post and user info

**Expected Usage:**
```bash
POST /users/5/posts/12/comments
Content-Type: application/json

{
  "content": "Great post!",
  "author_name": "Alice"
}

Response: 201 Created
{
  "id": 1,
  "content": "Great post!",
  "author_name": "Alice",
  "user_id": 5,
  "post_id": 12,
  "created_at": "2024-01-15T10:30:00"
}
```

---

## Exercise 10: Advanced Validation with Pydantic (Hard) 🎁 Bonus

**Task:** Create a complex registration endpoint with multiple validations.

**Requirements:**
- Endpoint: `POST /register`
- Request body: Registration model with:
  - `username` (str): 3-20 characters, alphanumeric only
  - `email` (str): must be valid email format
  - `password` (str): minimum 8 characters, must contain uppercase, lowercase, and digit
  - `confirm_password` (str): must match password
  - `age` (int): must be 18 or older
  - `phone` (str | None, optional): if provided, must match format XXX-XXX-XXXX
- Validate all constraints using Pydantic validators
- Returns: Success message with user info (without password)

**Expected Usage:**
```bash
POST /register
Content-Type: application/json

{
  "username": "johndoe123",
  "email": "john@example.com",
  "password": "SecurePass123",
  "confirm_password": "SecurePass123",
  "age": 25,
  "phone": "555-123-4567"
}

Response: 201 Created
{
  "message": "Registration successful",
  "username": "johndoe123",
  "email": "john@example.com",
  "age": 25
}
```

**Hints:**
- Use Pydantic's `@field_validator` or `@model_validator` decorators
- Use regex patterns for validation
- Create custom validation functions

---

## Bonus Exercise: File Upload with Metadata (Hard) 🎁 Bonus

**Task:** Create an endpoint that accepts file uploads with additional metadata.

**Requirements:**
- Endpoint: `POST /upload`
- Form data:
  - `file` (UploadFile, required)
  - `title` (str, required)
  - `description` (str | None, optional)
  - `tags` (list[str], optional)
- Validate file size (max 10MB) and type (only images: jpg, png, gif)
- Returns: Upload info with file metadata

**Expected Usage:**
```bash
POST /upload
Content-Type: multipart/form-data

file: [binary data]
title: "My Image"
description: "A beautiful sunset"
tags: ["nature", "sunset"]

Response: 201 Created
{
  "filename": "image.jpg",
  "title": "My Image",
  "description": "A beautiful sunset",
  "tags": ["nature", "sunset"],
  "size": 245678,
  "content_type": "image/jpeg"
}
```

---

## Solutions Template

Create a new file `solutions.py` and implement all exercises there. Here's a starter template:

```python
from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from pydantic import BaseModel, field_validator, model_validator, EmailStr
from typing import List
import re

app = FastAPI()

# Exercise 1: Simple GET Endpoint
# TODO: Implement here

# Exercise 2: Path Parameter
# TODO: Implement here

# Exercise 3: Query Parameters
# TODO: Implement here

# Exercise 4: Simple POST with Pydantic Model
# TODO: Implement here

# Exercise 5: Path + Query Parameters
# TODO: Implement here

# Exercise 6: PUT with Partial Update
# TODO: Implement here

# Exercise 7: Complex Query Parameters
# TODO: Implement here

# Exercise 8: Nested Pydantic Models
# TODO: Implement here

# Exercise 9: Multiple Path Parameters + Body
# TODO: Implement here

# Exercise 10: Advanced Validation with Pydantic
# TODO: Implement here

# Bonus: File Upload with Metadata
# TODO: Implement here
```

---

## Tips for Success

1. **Start Simple**: Begin with exercises 1-3 to get comfortable with basic concepts
2. **Test Your Endpoints**: Use FastAPI's automatic docs at `/docs` or tools like Postman/curl
3. **Read Error Messages**: FastAPI provides helpful validation error messages
4. **Use Type Hints**: Always use proper type hints for better IDE support and validation
5. **Validate Early**: Use Pydantic validators to catch errors before processing
6. **Handle Edge Cases**: Think about what happens with invalid input, missing data, etc.
7. **Follow REST Conventions**: Use appropriate HTTP methods and status codes

---

## Learning Path

- **Exercises 1-3**: Master basic parameter types
- **Exercises 4-5**: Combine parameters and use Pydantic models
- **Exercises 6-7**: Handle complex queries and partial updates
- **Exercises 8-10**: Work with nested models and advanced validation
- **Bonus**: Explore file uploads and form data

Good luck and happy coding! 🚀

