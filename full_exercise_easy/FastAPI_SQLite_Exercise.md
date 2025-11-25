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

```python
# Car Owner Models
class CarOwner(BaseModel):
    id: int | None = None
    name: str
    age: int
    email: str
    created_at: str | None = None

class CarOwnerUpdate(BaseModel):
    name: str | None = None
    age: int | None = None
    email: str | None = None

# Car Models
class Car(BaseModel):
    id: int | None = None
    brand: str
    model: str
    year: int
    color: str
    owner_id: int
    created_at: str | None = None

class CarUpdate(BaseModel):
    brand: str | None = None
    model: str | None = None
    year: int | None = None
    color: str | None = None
    owner_id: int | None = None
```

### Step 1.6: Database Initialization

```python
def init_db():
    """Initialize database and create tables if they don't exist"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    # Create car_owners table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS car_owners (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            age INTEGER NOT NULL,
            email TEXT NOT NULL UNIQUE,
            created_at TEXT
        )
    """)
    
    # Create cars table with foreign key
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS cars (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            brand TEXT NOT NULL,
            model TEXT NOT NULL,
            year INTEGER NOT NULL,
            color TEXT NOT NULL,
            owner_id INTEGER NOT NULL,
            created_at TEXT,
            FOREIGN KEY (owner_id) REFERENCES car_owners(id)
        )
    """)
    
    conn.commit()
    conn.close()

# Initialize database on startup
init_db()
```

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

```python
def row_to_dict(row, table_name: str = "car_owners"):
    """Convert SQLite row to dictionary"""
    if table_name == "car_owners":
        return {
            'id': row['id'],
            'name': row['name'],
            'age': row['age'],
            'email': row['email'],
            'created_at': row['created_at']
        }
    else:  # cars
        return {
            'id': row['id'],
            'brand': row['brand'],
            'model': row['model'],
            'year': row['year'],
            'color': row['color'],
            'owner_id': row['owner_id'],
            'created_at': row['created_at']
        }
```

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

```python
@app.get("/")
def read_root():
    """Root endpoint"""
    return {"message": "Welcome to Car Owner Management API", "version": "1.0.0"}

@app.get("/car-owners", response_model=list[CarOwner])
def get_all_car_owners():
    """Get all car owners"""
    # TODO: Call read_car_owners() and return
    pass

@app.get("/car-owners/{owner_id}", response_model=CarOwner)
def get_car_owner(owner_id: int):
    """Get a specific car owner by ID"""
    # TODO: Call get_car_owner_by_id()
    # TODO: Handle 404 if not found
    pass

@app.post("/car-owners", response_model=CarOwner, status_code=201)
def create_car_owner(owner: CarOwner):
    """Create a new car owner"""
    # TODO: Call create_car_owner_in_db()
    pass

@app.put("/car-owners/{owner_id}", response_model=CarOwner)
def update_car_owner(owner_id: int, owner_update: CarOwnerUpdate):
    """Update an existing car owner"""
    # TODO: Call update_car_owner_in_db()
    # TODO: Handle 404 if not found
    pass

@app.delete("/car-owners/{owner_id}", status_code=204)
def delete_car_owner(owner_id: int):
    """Delete a car owner"""
    # TODO: Call delete_car_owner_from_db()
    # TODO: Handle 404 if not found
    pass
```

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

```python
@app.get("/cars", response_model=list[Car])
def get_all_cars(owner_id: int | None = None):
    """Get all cars, optionally filtered by owner_id"""
    # TODO: Call read_cars(owner_id)
    pass

@app.get("/cars/{car_id}", response_model=Car)
def get_car(car_id: int):
    """Get a specific car by ID"""
    # TODO: Call get_car_by_id()
    # TODO: Handle 404
    pass

@app.post("/cars", response_model=Car, status_code=201)
def create_car(car: Car):
    """Create a new car"""
    # TODO: Call create_car_in_db()
    pass

@app.put("/cars/{car_id}", response_model=Car)
def update_car(car_id: int, car_update: CarUpdate):
    """Update an existing car"""
    # TODO: Call update_car_in_db()
    # TODO: Handle 404
    pass

@app.delete("/cars/{car_id}", status_code=204)
def delete_car(car_id: int):
    """Delete a car"""
    # TODO: Call delete_car_from_db()
    # TODO: Handle 404
    pass
```

**✅ Checkpoint:** Test all car endpoints. Try creating a car with invalid owner_id - should return 400 error.

---

## Part 6: CSV Export Functions ⭐ Required

### Step 6.1: Export Helper Functions

```python
def export_car_owners_to_csv() -> str:
    """Export all car owners to CSV format (returns CSV string)"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM car_owners")
    rows = cursor.fetchall()
    conn.close()
    
    # Convert to CSV string
    output = io.StringIO()
    if rows:
        writer = csv.DictWriter(output, fieldnames=['id', 'name', 'age', 'email', 'created_at'])
        writer.writeheader()
        for row in rows:
            writer.writerow({
                'id': row['id'],
                'name': row['name'],
                'age': row['age'],
                'email': row['email'],
                'created_at': row['created_at']
            })
    
    return output.getvalue()

def export_cars_to_csv(owner_id: int | None = None) -> str:
    """Export cars to CSV format, optionally filtered by owner"""
    # TODO: Implement similar to export_car_owners_to_csv()
    # If owner_id is provided, filter the query
    pass
```

### Step 6.2: CSV Export Endpoints

```python
@app.get("/car-owners/export-csv")
def export_car_owners_csv():
    """Export all car owners as CSV file"""
    csv_content = export_car_owners_to_csv()
    return Response(
        content=csv_content,
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=car_owners.csv"}
    )

@app.get("/cars/export-csv")
def export_cars_csv(owner_id: int | None = None):
    """Export cars as CSV file, optionally filtered by owner_id"""
    # TODO: Implement similar to export_car_owners_csv()
    pass
```

**✅ Checkpoint:** Test CSV export - download files and open in Excel/text editor.

---

## Part 7: CSV Import Functions ⭐ Required

### Step 7.1: Import Helper Functions

```python
def import_car_owners_from_csv(csv_content: bytes) -> dict:
    """Import car owners from CSV and append to database"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        csv_text = csv_content.decode('utf-8')
        csv_reader = csv.DictReader(io.StringIO(csv_text))
        
        imported_count = 0
        now = datetime.now().isoformat()
        
        for row in csv_reader:
            name = row.get('name', '').strip()
            if not name:  # Skip rows without name
                continue
            
            age = int(row.get('age', 0))
            email = row.get('email', '').strip()
            
            if not email:
                continue
            
            cursor.execute("""
                INSERT INTO car_owners (name, age, email, created_at)
                VALUES (?, ?, ?, ?)
            """, (name, age, email, now))
            imported_count += 1
        
        conn.commit()
        
        return {
            "message": f"Successfully imported {imported_count} car owners from CSV",
            "imported_count": imported_count,
            "uploaded_at": now
        }
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=400, detail=f"Error importing CSV: {str(e)}")
    finally:
        conn.close()

def import_cars_from_csv(csv_content: bytes) -> dict:
    """Import cars from CSV and append to database"""
    # TODO: Implement similar to import_car_owners_from_csv()
    # IMPORTANT: Validate owner_id exists for each car!
    # Skip cars with invalid owner_id
    pass
```

### Step 7.2: CSV Import Endpoints

```python
@app.post("/car-owners/upload-csv")
async def upload_car_owners_csv(file: UploadFile = File(...)):
    """Upload a CSV file and import car owners"""
    # Validate file type
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="File must be a CSV file")
    
    contents = await file.read()
    result = import_car_owners_from_csv(contents)
    return result

@app.post("/cars/upload-csv")
async def upload_cars_csv(file: UploadFile = File(...)):
    """Upload a CSV file and import cars"""
    # TODO: Implement similar to upload_car_owners_csv()
    pass
```

**✅ Checkpoint:** Test CSV import - use the sample CSV files provided.

---

## Part 8: Relationship Endpoints (Bonus) ⭐ Recommended

### Step 8.1: Get Owner's Cars

```python
@app.get("/car-owners/{owner_id}/cars", response_model=list[Car])
def get_owner_cars(owner_id: int):
    """Get all cars owned by a specific person"""
    # TODO: Validate owner exists first
    # TODO: Call read_cars(owner_id)
    pass
```

### Step 8.2: Get Car's Owner

```python
@app.get("/cars/{car_id}/owner", response_model=CarOwner)
def get_car_owner(car_id: int):
    """Get the owner of a specific car"""
    # TODO: Get car by ID
    # TODO: Get owner by car.owner_id
    # TODO: Handle 404 for both car and owner
    pass
```

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

