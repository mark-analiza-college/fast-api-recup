# FastAPI SQLModel Exercise - Car Owner Management System

Practice building a FastAPI application with SQLModel, combining SQLAlchemy ORM with Pydantic validation.

**Exam Topics Covered:**
- ✅ FastAPI endpoints (GET, POST, PUT, DELETE)
- ✅ SQLModel for database models and validation
- ✅ SQLAlchemy ORM operations (CRUD)
- ✅ CSV import and export
- ✅ Error handling and HTTP status codes
- ✅ Foreign key relationships
- ✅ Dependency injection (sessions)

**Estimated Time:** 2-3 hours

---

## Overview

You will build a **Car Owner Management API** using SQLModel that allows you to:
- Manage car owners (people who own cars)
- Manage cars (with relationships to owners)
- Import/export data via CSV files

**Follow the exact structure of `main_sqlmodel.py`** - use it as a reference!

**Key Differences from SQLite:**
- Uses SQLModel models (combines database table + Pydantic validation)
- Uses SQLAlchemy sessions instead of direct connections
- Uses `select()` statements instead of raw SQL
- Uses dependency injection for database sessions
- Uses `lifespan` events for initialization

---

## Part 1: Project Setup and SQLModel Models ⭐ Required

### Step 1.1: Create Project File

Create a new file: `main_car_owners_sqlmodel.py`

### Step 1.2: Import Required Libraries

```python
from fastapi import FastAPI, HTTPException, Request, UploadFile, File, Response, Depends
from sqlmodel import SQLModel, Field, Session, create_engine, select
from contextlib import asynccontextmanager
from datetime import datetime
import uvicorn
import csv
import io
```

### Step 1.3: Database Configuration

```python
# SQLite database URL
DATABASE_URL = "sqlite:///car_owners_db.sqlite"

# Create engine - this manages database connections
engine = create_engine(DATABASE_URL, echo=False)
```

### Step 1.4: Create SQLModel Models

Create SQLModel models based on the requirements. Use `main_sqlmodel.py` as reference.

**Requirements:**

1. **CarOwnerBase model** (base model, not a table):
   - Fields: name (required str), age (required int), email (required str)
   - Inherits from `SQLModel`
   - Used for inheritance, not a database table

2. **CarOwner model** (database table):
   - Inherits from `CarOwnerBase`
   - Has `table=True` to make it a database table
   - Fields: id (optional int, primary key), created_at (optional str)
   - Uses `Field()` for primary key and default values

3. **CarOwnerCreate model** (for creating):
   - Inherits from `CarOwnerBase`
   - Used for API request body when creating

4. **CarOwnerUpdate model** (for partial updates):
   - Inherits from `SQLModel`
   - All fields optional: name, age, email

5. **CarOwnerRead model** (for responses):
   - Inherits from `CarOwnerBase`
   - Includes: id (required int), created_at (required str)

6. **CarBase model** (base model):
   - Fields: brand, model, year, color, owner_id (all required)
   - Inherits from `SQLModel`

7. **Car model** (database table):
   - Inherits from `CarBase`
   - Has `table=True`
   - Fields: id (optional int, primary key), created_at (optional str)
   - Represents foreign key relationship to CarOwner

8. **CarCreate, CarUpdate, CarRead models**:
   - Similar pattern to CarOwner models

**Hint:** Look at `TodoBase`, `Todo`, `TodoCreate`, `TodoUpdate`, `TodoRead` in `main_sqlmodel.py` to understand the pattern.

### Step 1.5: Database Initialization

Create the `init_db()` function.

**Requirements:**
- Use `SQLModel.metadata.create_all(engine)` to create all tables
- This automatically creates tables based on models with `table=True`

**Hint:** Look at `init_db()` in `main_sqlmodel.py`.

### Step 1.6: Session Dependency

Create the `get_session()` dependency function.

**Requirements:**
- Use `Session(engine)` as context manager
- Use `yield` to provide session to endpoint
- Session automatically closes after request

**Hint:** Look at `get_session()` in `main_sqlmodel.py`.

### Step 1.7: Lifespan Events

Create a `lifespan` function for FastAPI startup/shutdown.

**Requirements:**
- Use `@asynccontextmanager`
- On startup: call `init_db()`
- On shutdown: call `engine.dispose()`
- Yield between startup and shutdown

**Hint:** Look at `lifespan()` in `main_sqlmodel.py`.

### Step 1.8: Initialize FastAPI App

```python
app = FastAPI(
    title="Car Owner Management API (SQLModel)",
    version="1.0.0",
    lifespan=lifespan
)

# Custom middleware
@app.middleware("http")
def print_middleware(request: Request, call_next):
    print(f"Request: {request.method} {request.url.path}")
    response = call_next(request)
    return response
```

**✅ Checkpoint:** Run your file - it should start without errors. Test: `python main_car_owners_sqlmodel.py`

---

## Part 2: Helper Functions for Database Operations ⭐ Required

### Step 2.1: Car Owner Database Functions

Implement these functions (follow the pattern from `main_sqlmodel.py`):

**read_car_owners(session: Session) → list[CarOwner]**
- Pseudocode: Use `select(CarOwner)` → Execute with `session.exec()` → Return all results

**get_car_owner_by_id(session: Session, owner_id: int) → CarOwner | None**
- Pseudocode: Use `session.get(CarOwner, owner_id)` → Return result

**create_car_owner_in_db(session: Session, owner: CarOwnerCreate) → CarOwner**
- Pseudocode: Create CarOwner instance from CarOwnerCreate → Set created_at timestamp → Add to session → Commit → Refresh → Return

**update_car_owner_in_db(session: Session, owner_id: int, owner_update: CarOwnerUpdate) → CarOwner**
- Pseudocode: Get car owner by ID → If not found, raise 404 → Get update data (exclude_unset=True) → Update fields → Commit → Refresh → Return

**delete_car_owner_from_db(session: Session, owner_id: int) → bool**
- Pseudocode: Get car owner by ID → If not found, raise 404 → Delete from session → Commit → Return True

**Hint:** Look at corresponding functions in `main_sqlmodel.py`. Use `session.get()`, `session.add()`, `session.commit()`, `session.refresh()`.

**✅ Checkpoint:** Test your helper functions manually before moving to endpoints.

---

## Part 3: Car Owner API Endpoints ⭐ Required

### Step 3.1: Create Endpoints

Implement the following endpoints following the pattern from `main_sqlmodel.py`:

**GET /car-owners**
- Pseudocode: Get session from dependency → Call read_car_owners(session) → Return list

**GET /car-owners/{owner_id}**
- Pseudocode: Get session → Call get_car_owner_by_id(session, owner_id) → If None, return 404 → Return car owner

**POST /car-owners**
- Pseudocode: Get session → Call create_car_owner_in_db(session, owner) → Return created owner

**PUT /car-owners/{owner_id}**
- Pseudocode: Get session → Call update_car_owner_in_db(session, owner_id, update) → Return updated owner

**DELETE /car-owners/{owner_id}**
- Pseudocode: Get session → Call delete_car_owner_from_db(session, owner_id) → Return 204 status

**Hint:** Use `session: Session = Depends(get_session)` in endpoint parameters. Look at corresponding endpoints in `main_sqlmodel.py`.

**✅ Checkpoint:** Test all endpoints using FastAPI docs at `http://localhost:8004/docs`

---

## Part 4: Car Database Functions ⭐ Required

### Step 4.1: Car Database Helper Functions

**read_cars(session: Session, owner_id: int | None = None) → list[Car]**
- Pseudocode: Build select statement → If owner_id provided, add WHERE clause → Execute → Return results

**get_car_by_id(session: Session, car_id: int) → Car | None**
- Pseudocode: Use session.get(Car, car_id) → Return result

**validate_owner_exists(session: Session, owner_id: int) → bool**
- Pseudocode: Use session.get(CarOwner, owner_id) → Return True if exists, False otherwise

**create_car_in_db(session: Session, car: CarCreate) → Car**
- Pseudocode: Validate owner_id exists → If not, raise 400 error → Create Car instance → Set created_at → Add to session → Commit → Refresh → Return

**update_car_in_db(session: Session, car_id: int, car_update: CarUpdate) → Car**
- Pseudocode: Get car by ID → If not found, raise 404 → If owner_id updated, validate it exists → Update fields → Commit → Refresh → Return

**delete_car_from_db(session: Session, car_id: int) → bool**
- Pseudocode: Get car by ID → If not found, raise 404 → Delete from session → Commit → Return True

**Hint:** Use `select(Car).where(Car.owner_id == owner_id)` for filtering. Look at `main_sqlmodel.py` for patterns.

**✅ Checkpoint:** Test validation - try creating a car with invalid owner_id.

---

## Part 5: Car API Endpoints ⭐ Required

### Step 5.1: Create Car Endpoints

Implement the following endpoints:

**GET /cars**
- Pseudocode: Get session → Call read_cars(session, owner_id) → Return list

**GET /cars/{car_id}**
- Pseudocode: Get session → Call get_car_by_id(session, car_id) → If None, return 404 → Return car

**POST /cars**
- Pseudocode: Get session → Call create_car_in_db(session, car) → Return created car

**PUT /cars/{car_id}**
- Pseudocode: Get session → Call update_car_in_db(session, car_id, update) → Return updated car

**DELETE /cars/{car_id}**
- Pseudocode: Get session → Call delete_car_from_db(session, car_id) → Return 204 status

**Hint:** Use `session: Session = Depends(get_session)` in all endpoints.

**✅ Checkpoint:** Test all car endpoints. Try creating a car with invalid owner_id - should return 400 error.

---

## Part 6: CSV Export Functions ⭐ Required

### Step 6.1: Export Helper Functions

Create functions to export data to CSV format (as strings).

**Requirements:**

1. **export_car_owners_to_csv(session: Session) → str**:
   - Query all car owners using `select(CarOwner)`
   - Use `csv.DictWriter` with `io.StringIO()`
   - Write header row with column names
   - Write data rows (convert SQLModel objects to dicts)
   - Return the CSV string using `output.getvalue()`

2. **export_cars_to_csv(session: Session, owner_id: int | None = None) → str**:
   - Similar to above, but for cars
   - If `owner_id` is provided, filter the query using `where()`
   - Include all car columns in CSV

**Hint:** Use `model.model_dump()` to convert SQLModel objects to dictionaries. Use `csv.DictWriter` and `io.StringIO()`.

### Step 6.2: CSV Export Endpoints

Implement the following endpoints:

**GET /car-owners/export-csv**
- Pseudocode: Get session → Generate CSV string → Return CSV file as response with proper headers (Content-Disposition, media_type)

**GET /cars/export-csv**
- Pseudocode: Get session → If owner_id provided, filter → Generate CSV string → Return CSV file as response with proper headers

**Hint:** Use `Response` with `media_type="text/csv"` and `Content-Disposition` header for file download.

**✅ Checkpoint:** Test CSV export - download files and open in Excel/text editor.

---

## Part 7: CSV Import Functions ⭐ Required

### Step 7.1: Import Helper Functions

Create functions to import data from CSV.

**Requirements:**

1. **import_car_owners_from_csv(session: Session, csv_content: bytes) → dict**:
   - Decode CSV content from bytes to string
   - Use `csv.DictReader` to parse CSV
   - For each row: extract name, age, email
   - Skip rows with missing required fields
   - Create CarOwner instances and add to session
   - Commit transaction
   - Return dict with message, imported_count, uploaded_at

2. **import_cars_from_csv(session: Session, csv_content: bytes) → dict**:
   - Similar to above, but for cars
   - **IMPORTANT:** Validate `owner_id` exists before inserting
   - Skip cars with invalid `owner_id`
   - Extract: brand, model, year, color, owner_id

**Hint:** Look at `import_csv_to_db()` in `main_sqlmodel.py` for the pattern. Use `session.rollback()` in exception handler.

### Step 7.2: CSV Import Endpoints

Implement the following endpoints:

**POST /car-owners/upload-csv**
- Pseudocode: Validate file is CSV → Read file contents → Get session → Parse CSV and extract data → Insert valid rows → Return import result with count

**POST /cars/upload-csv**
- Pseudocode: Validate file is CSV → Read file contents → Get session → Parse CSV → For each car, validate owner_id exists → Insert valid cars → Return import result with count

**Hint:** Use `UploadFile` parameter, validate file extension, and handle errors appropriately.

**✅ Checkpoint:** Test CSV import - use the sample CSV files provided.

---

## Part 8: Relationship Endpoints (Bonus) ⭐ Recommended

### Step 8.1: Get Owner's Cars

**GET /car-owners/{owner_id}/cars**
- Pseudocode: Get session → Validate owner exists → If not found, return 404 → Retrieve all cars for owner using select().where() → Return list of cars

### Step 8.2: Get Car's Owner

**GET /cars/{car_id}/owner**
- Pseudocode: Get session → Get car by ID → If car not found, return 404 → Get owner by car.owner_id → If owner not found, return 404 → Return owner data

---

## Part 9: Statistics Endpoint (Bonus) ⭐ Recommended

### Step 9.1: Statistics Function

**get_statistics(session: Session) → dict**:
- Pseudocode: Count total car owners → Count total cars → Calculate average cars per owner → Find most popular brand using select().group_by() → Return statistics dict

**Hint:** Use `select(func.count(CarOwner.id))` for counting. Use `select(Car.brand, func.count(Car.id)).group_by(Car.brand)` for grouping.

### Step 9.2: Statistics Endpoint

**GET /statistics**
- Pseudocode: Get session → Call get_statistics(session) → Return statistics

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
**Solution:** Make sure owner exists before creating a car. Use `validate_owner_exists()`.

### Issue: "UNIQUE constraint failed" (email)
**Solution:** Email must be unique. Check for duplicates.

### Issue: CSV import not working
**Solution:** Check CSV format matches expected columns exactly.

### Issue: 404 errors
**Solution:** Always check if record exists before returning.

### Issue: Session not closed
**Solution:** Use `Depends(get_session)` - it automatically closes sessions.

---

## Key SQLModel Concepts

### Models
- **Base models** (`CarOwnerBase`): Not tables, used for inheritance
- **Table models** (`CarOwner` with `table=True`): Database tables
- **Create models** (`CarOwnerCreate`): For API requests
- **Update models** (`CarOwnerUpdate`): For partial updates
- **Read models** (`CarOwnerRead`): For API responses

### Sessions
- Use `Session(engine)` as context manager
- Use `Depends(get_session)` in endpoints
- Sessions automatically close after request

### Queries
- Use `select(Model)` instead of raw SQL
- Use `.where()` for filtering
- Use `session.exec(statement)` to execute
- Use `session.get(Model, id)` for single records

### Operations
- `session.add(model)` - Add to session
- `session.commit()` - Save changes
- `session.refresh(model)` - Refresh from database
- `session.delete(model)` - Delete from session

---

## Final Steps

1. **Add main block:**
```python
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8004)
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
1. ✅ `main_car_owners_sqlmodel.py` - Complete working file
2. ✅ `car_owners.csv` - Sample CSV file
3. ✅ `cars.csv` - Sample CSV file
4. ✅ Screenshot of FastAPI docs (`/docs` page)

---

## Tips for Success

1. **Follow the pattern** - Use `main_sqlmodel.py` as exact reference
2. **Test incrementally** - Don't build everything at once
3. **Use FastAPI docs** - Test endpoints as you build them
4. **Validate foreign keys** - Always check owner exists before creating car
5. **Handle errors** - Return proper HTTP status codes
6. **Use sessions properly** - Always use `Depends(get_session)`

---

## Exam Preparation

This exercise covers all exam topics:
- ✅ FastAPI route decorators (`@app.get`, `@app.post`, etc.)
- ✅ SQLModel models (combining ORM + validation)
- ✅ SQLAlchemy ORM operations (CRUD)
- ✅ CSV handling (import/export)
- ✅ Error handling with HTTPException
- ✅ Foreign key relationships
- ✅ Query parameters
- ✅ Path parameters
- ✅ Dependency injection
- ✅ Request/Response models

**Good luck! 🚗💨**

