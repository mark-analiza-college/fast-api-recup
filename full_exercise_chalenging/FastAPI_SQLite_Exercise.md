# FastAPI SQLite Exercise - Car Owner Management System

Practice building a FastAPI application with SQLite, Pydantic, and CSV handling.

**Exam Topics Covered:**
- ✅ FastAPI endpoints (GET, POST, PUT, DELETE)
- ✅ Pydantic models for data validation
- ✅ SQLite database operations (CRUD)
- ✅ CSV import and export
- ✅ Error handling and HTTP status codes
- ✅ Foreign key relationships

**Estimated Time:** 2-3 hours

---

## Overview

You will build a **Car Owner Management API** that allows you to:
- Manage car owners (people who own cars)
- Manage cars (with relationships to owners)
- Import/export data via CSV files

**Follow the exact structure of `main_sqlite.py`** - use it as a reference!

---

## Part 1: Project Setup and Database Schema ⭐ Required

### Step 1.1: Create Project File

Create a new file: `main_car_owners.py`

### Step 1.2: Import Required Libraries

```python
from fastapi import FastAPI, HTTPException, Request, UploadFile, File, Response
from pydantic import BaseModel, EmailStr
import sqlite3
from datetime import datetime
import uvicorn
import csv
import io
```

### Step 1.3: Initialize FastAPI App

```python
app = FastAPI(title="Car Owner Management API", version="1.0.0")

# Custom middleware
@app.middleware("http")
def print_middleware(request: Request, call_next):
    print(f"Request: {request.method} {request.url.path}")
    response = call_next(request)
    return response
```

### Step 1.4: Define Database Path

```python
DB_FILE = "car_owners_db.sqlite"
```

### Step 1.5: Create Pydantic Models

Create Pydantic models based on the database schema. Use `main_sqlite.py` as reference.

**Requirements:**

1. **CarOwner model** (for full car owner data):
   - Fields: id, name, age, email, created_at
   - Which fields are required? Which are optional?
   - What types should each field be?

2. **CarOwnerUpdate model** (for partial updates):
   - Same fields as CarOwner, but all optional
   - Used when updating only some fields

3. **Car model** (for full car data):
   - Fields: id, brand, model, year, color, owner_id, created_at
   - Which fields are required? Which are optional?

4. **CarUpdate model** (for partial updates):
   - Same fields as Car, but all optional

**Hint:** Look at `TodoItem` and `TodoUpdate` in `main_sqlite.py` to understand the pattern.

### Step 1.6: Database Initialization

Create the `init_db()` function to set up your database tables.

**Requirements:**

1. **car_owners table:**
   - id: INTEGER PRIMARY KEY AUTOINCREMENT
   - name: TEXT NOT NULL
   - age: INTEGER NOT NULL
   - email: TEXT NOT NULL UNIQUE (emails must be unique)
   - created_at: TEXT

2. **cars table:**
   - id: INTEGER PRIMARY KEY AUTOINCREMENT
   - brand: TEXT NOT NULL
   - model: TEXT NOT NULL
   - year: INTEGER NOT NULL
   - color: TEXT NOT NULL
   - owner_id: INTEGER NOT NULL
   - created_at: TEXT
   - FOREIGN KEY (owner_id) REFERENCES car_owners(id)

**Hint:** Look at `init_db()` in `main_sqlite.py` for the pattern. Use `CREATE TABLE IF NOT EXISTS`.

**✅ Checkpoint:** Run your file - it should start without errors. Test: `python main_car_owners.py`

---

## Part 2: Helper Functions for Database Operations ⭐ Required

### Step 2.1: Database Connection Helper

```python
def get_db_connection():
    """Get database connection"""
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row  # Allows column access by name
    return conn
```

### Step 2.2: Row to Dictionary Converter

Create a `row_to_dict()` function that converts SQLite rows to dictionaries.

**Requirements:**
- Takes a row and table_name parameter
- Returns a dictionary with all columns from the row
- Should handle both "car_owners" and "cars" tables

**Hint:** Look at `row_to_dict()` in `main_sqlite.py` for the pattern. Use `row['column_name']` to access columns.

### Step 2.3: Car Owner Database Functions

Implement these functions (follow the pattern from `main_sqlite.py`):

```python
def read_car_owners() -> list[dict]:
    """Read all car owners from database"""
    # TODO: Implement
    # Hint: Similar to read_todos() but no filter needed
    pass

def get_car_owner_by_id(owner_id: int) -> dict | None:
    """Get a single car owner by ID"""
    # TODO: Implement
    # Hint: Similar to get_todo_by_id()
    pass

def create_car_owner_in_db(owner: CarOwner) -> dict:
    """Create a new car owner in database"""
    # TODO: Implement
    # Hint: Use RETURNING clause like in create_todo_in_db()
    # Don't include 'id' in INSERT - let SQLite auto-increment
    pass

def update_car_owner_in_db(owner_id: int, owner_update: CarOwnerUpdate) -> dict:
    """Update an existing car owner in database"""
    # TODO: Implement
    # Hint: Similar to update_todo_in_db()
    # Build SET clause dynamically based on provided fields
    pass

def delete_car_owner_from_db(owner_id: int) -> bool:
    """Delete a car owner from database"""
    # TODO: Implement
    # Hint: Similar to delete_todo_from_db()
    # IMPORTANT: Check if owner has cars first!
    pass
```

**✅ Checkpoint:** Test your helper functions manually before moving to endpoints.

---

## Part 3: Car Owner API Endpoints ⭐ Required

### Step 3.1: Create Endpoints

Implement the following endpoints following the pattern from `main_sqlite.py`:

**GET /car-owners**
- Pseudocode: Retrieve all car owners from database → Return as list

**GET /car-owners/{owner_id}**
- Pseudocode: Retrieve car owner by ID → If not found, return 404 → Return car owner data

**POST /car-owners**
- Pseudocode: Create car owner in database → Return created car owner with generated ID

**PUT /car-owners/{owner_id}**
- Pseudocode: Check if exists → If not found, return 404 → Update only provided fields → Return updated car owner

**DELETE /car-owners/{owner_id}**
- Pseudocode: Check if exists → If not found, return 404 → Delete from database → Return 204 status

**Hint:** Look at the corresponding endpoints in `main_sqlite.py` for the exact pattern.

**✅ Checkpoint:** Test all endpoints using FastAPI docs at `http://localhost:8003/docs`

---

## Part 4: Car Database Functions ⭐ Required

### Step 4.1: Car Database Helper Functions

```python
def read_cars(owner_id: int | None = None) -> list[dict]:
    """Read all cars, optionally filtered by owner_id"""
    # TODO: Implement
    # Hint: If owner_id is provided, add WHERE clause
    pass

def get_car_by_id(car_id: int) -> dict | None:
    """Get a single car by ID"""
    # TODO: Implement
    pass

def create_car_in_db(car: Car) -> dict:
    """Create a new car in database"""
    # TODO: Implement
    # IMPORTANT: Validate owner_id exists first!
    # If owner doesn't exist, raise HTTPException(status_code=400, detail="Owner not found")
    pass

def update_car_in_db(car_id: int, car_update: CarUpdate) -> dict:
    """Update an existing car in database"""
    # TODO: Implement
    # IMPORTANT: If owner_id is being updated, validate it exists
    pass

def delete_car_from_db(car_id: int) -> bool:
    """Delete a car from database"""
    # TODO: Implement
    pass
```

### Step 4.2: Validation Helper

```python
def validate_owner_exists(owner_id: int) -> bool:
    """Check if car owner exists in database"""
    # TODO: Implement
    # Return True if exists, False otherwise
    pass
```

**✅ Checkpoint:** Test validation - try creating a car with invalid owner_id.

---

## Part 5: Car API Endpoints ⭐ Required

### Step 5.1: Create Car Endpoints

Implement the following endpoints:

**GET /cars**
- Pseudocode: If owner_id provided, filter by owner → Otherwise retrieve all → Return list of cars

**GET /cars/{car_id}**
- Pseudocode: Retrieve car by ID → If not found, return 404 → Return car data

**POST /cars**
- Pseudocode: Validate owner_id exists → If not found, return 400 → Create car in database → Return created car

**PUT /cars/{car_id}**
- Pseudocode: Check if car exists → If not found, return 404 → If owner_id updated, validate it exists → Update only provided fields → Return updated car

**DELETE /cars/{car_id}**
- Pseudocode: Check if car exists → If not found, return 404 → Delete from database → Return 204 status

**Hint:** Look at the corresponding endpoints in `main_sqlite.py` for the exact pattern.

**✅ Checkpoint:** Test all car endpoints. Try creating a car with invalid owner_id - should return 400 error.

---

## Part 6: CSV Export Functions ⭐ Required

### Step 6.1: Export Helper Functions

Create functions to export data to CSV format (as strings).

**Requirements:**

1. **export_car_owners_to_csv()** → returns CSV string:
   - Query all car owners from database
   - Use `csv.DictWriter` with `io.StringIO()`
   - Write header row with column names
   - Write data rows
   - Return the CSV string using `output.getvalue()`

2. **export_cars_to_csv(owner_id: int | None = None)** → returns CSV string:
   - Similar to above, but for cars
   - If `owner_id` is provided, filter the query
   - Include all car columns in CSV

**Hint:** Use `csv.DictWriter` and `io.StringIO()` to build CSV in memory.

### Step 6.2: CSV Export Endpoints

Implement the following endpoints:

**GET /car-owners/export-csv**
- Pseudocode: Generate CSV string from all car owners → Return CSV file as response with proper headers (Content-Disposition, media_type)

**GET /cars/export-csv**
- Pseudocode: If owner_id provided, filter cars → Generate CSV string → Return CSV file as response with proper headers

**Hint:** Use `Response` with `media_type="text/csv"` and `Content-Disposition` header for file download.

**✅ Checkpoint:** Test CSV export - download files and open in Excel/text editor.

---

## Part 7: CSV Import Functions ⭐ Required

### Step 7.1: Import Helper Functions

Create functions to import data from CSV.

**Requirements:**

1. **import_car_owners_from_csv(csv_content: bytes)** → returns dict:
   - Decode CSV content from bytes to string
   - Use `csv.DictReader` to parse CSV
   - For each row: extract name, age, email
   - Skip rows with missing required fields
   - Insert each valid row into database
   - Use transactions (try/except/rollback)
   - Return dict with message, imported_count, uploaded_at

2. **import_cars_from_csv(csv_content: bytes)** → returns dict:
   - Similar to above, but for cars
   - **IMPORTANT:** Validate `owner_id` exists before inserting
   - Skip cars with invalid `owner_id`
   - Extract: brand, model, year, color, owner_id

**Hint:** Look at `import_csv_to_db()` in `main_sqlite.py` for the pattern.

### Step 7.2: CSV Import Endpoints

Implement the following endpoints:

**POST /car-owners/upload-csv**
- Pseudocode: Validate file is CSV → Read file contents → Parse CSV and extract data → Insert valid rows into database → Return import result with count

**POST /cars/upload-csv**
- Pseudocode: Validate file is CSV → Read file contents → Parse CSV and extract data → For each car, validate owner_id exists → Insert valid cars → Return import result with count

**Hint:** Use `UploadFile` parameter, validate file extension, and handle errors appropriately.

**✅ Checkpoint:** Test CSV import - use the sample CSV files provided.

---

## Part 8: Relationship Endpoints (Bonus) ⭐ Recommended

### Step 8.1: Get Owner's Cars

**GET /car-owners/{owner_id}/cars**
- Pseudocode: Validate owner exists → If not found, return 404 → Retrieve all cars for owner → Return list of cars

### Step 8.2: Get Car's Owner

**GET /cars/{car_id}/owner**
- Pseudocode: Get car by ID → If car not found, return 404 → Get owner by car.owner_id → If owner not found, return 404 → Return owner data

---

## Part 9: Statistics Endpoint (Bonus) ⭐ Recommended

### Step 9.1: Statistics Function

```python
def get_statistics() -> dict:
    """Calculate and return statistics"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Total car owners
    cursor.execute("SELECT COUNT(*) FROM car_owners")
    total_owners = cursor.fetchone()[0]
    
    # Total cars
    cursor.execute("SELECT COUNT(*) FROM cars")
    total_cars = cursor.fetchone()[0]
    
    # Average cars per owner
    avg_cars = total_cars / total_owners if total_owners > 0 else 0
    
    # Most popular brand
    cursor.execute("""
        SELECT brand, COUNT(*) as count 
        FROM cars 
        GROUP BY brand 
        ORDER BY count DESC 
        LIMIT 1
    """)
    popular_brand_row = cursor.fetchone()
    most_popular_brand = popular_brand_row[0] if popular_brand_row else None
    
    conn.close()
    
    return {
        "total_owners": total_owners,
        "total_cars": total_cars,
        "average_cars_per_owner": round(avg_cars, 2),
        "most_popular_brand": most_popular_brand
    }
```

### Step 9.2: Statistics Endpoint

```python
@app.get("/statistics")
def get_stats():
    """Get statistics about car owners and cars"""
    return get_statistics()
```

---

## Sample CSV Files

### car_owners.csv
```csv
name,age,email
John Doe,35,john@example.com
Jane Smith,28,jane@example.com
Bob Johnson,42,bob@example.com
Alice Brown,31,alice@example.com
```

### cars.csv
```csv
brand,model,year,color,owner_id
Toyota,Corolla,2020,White,1
Honda,Civic,2019,Blue,1
Mazda,3,2021,Red,2
Hyundai,i30,2022,Black,3
Kia,Sportage,2023,Gray,3
Ford,Focus,2020,Silver,4
```

**Note:** Make sure car owners are created first before importing cars!

---

## Testing Checklist

Before submitting, verify:

### Car Owners
- [ ] `GET /car-owners` - Returns all owners
- [ ] `GET /car-owners/{id}` - Returns specific owner
- [ ] `POST /car-owners` - Creates new owner
- [ ] `PUT /car-owners/{id}` - Updates owner
- [ ] `DELETE /car-owners/{id}` - Deletes owner
- [ ] `GET /car-owners/export-csv` - Downloads CSV
- [ ] `POST /car-owners/upload-csv` - Imports from CSV

### Cars
- [ ] `GET /cars` - Returns all cars
- [ ] `GET /cars?owner_id=1` - Filters by owner
- [ ] `GET /cars/{id}` - Returns specific car
- [ ] `POST /cars` - Creates new car (validates owner exists)
- [ ] `POST /cars` with invalid owner_id - Returns 400 error
- [ ] `PUT /cars/{id}` - Updates car
- [ ] `DELETE /cars/{id}` - Deletes car
- [ ] `GET /cars/export-csv` - Downloads CSV
- [ ] `POST /cars/upload-csv` - Imports from CSV

### Relationships
- [ ] `GET /car-owners/{id}/cars` - Returns owner's cars
- [ ] `GET /cars/{id}/owner` - Returns car's owner

### Statistics
- [ ] `GET /statistics` - Returns correct statistics

---

## Common Issues and Solutions

### Issue: "Foreign key constraint failed"
**Solution:** Make sure owner exists before creating a car.

### Issue: "UNIQUE constraint failed" (email)
**Solution:** Email must be unique. Check for duplicates.

### Issue: CSV import not working
**Solution:** Check CSV format matches expected columns exactly.

### Issue: 404 errors
**Solution:** Always check if record exists before returning.

---

## Final Steps

1. **Add main block:**
```python
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8003)
```

2. **Test all endpoints** using FastAPI docs

3. **Create sample data:**
   - Create 3-4 car owners via API
   - Create 5-6 cars via API
   - Test all operations

4. **Test CSV:**
   - Export car owners to CSV
   - Export cars to CSV
   - Import from CSV files
   - Verify data in database

---

## Submission Requirements

Submit:
1. ✅ `main_car_owners.py` - Complete working file
2. ✅ `car_owners.csv` - Sample CSV file
3. ✅ `cars.csv` - Sample CSV file
4. ✅ Screenshot of FastAPI docs (`/docs` page)

---

## Tips for Success

1. **Follow the pattern** - Use `main_sqlite.py` as exact reference
2. **Test incrementally** - Don't build everything at once
3. **Use FastAPI docs** - Test endpoints as you build them
4. **Validate foreign keys** - Always check owner exists before creating car
5. **Handle errors** - Return proper HTTP status codes
6. **Use parameterized queries** - Prevent SQL injection

---

## Exam Preparation

This exercise covers all exam topics:
- ✅ FastAPI route decorators (`@app.get`, `@app.post`, etc.)
- ✅ Pydantic models for validation
- ✅ SQLite CRUD operations
- ✅ CSV handling (import/export)
- ✅ Error handling with HTTPException
- ✅ Foreign key relationships
- ✅ Query parameters
- ✅ Path parameters
- ✅ Request/Response models

**Good luck! 🚗💨**

