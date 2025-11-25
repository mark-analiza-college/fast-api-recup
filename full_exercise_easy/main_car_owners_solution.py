"""
Car Owner Management API - Complete Solution

This is the complete solution for the Car Owner Management API exercise.
All functions and endpoints are fully implemented.
"""

from fastapi import FastAPI, HTTPException, Request, UploadFile, File, Response
from pydantic import BaseModel
import sqlite3
from datetime import datetime
import uvicorn
import csv
import io

app = FastAPI(title="Car Owner Management API", version="1.0.0")

# Custom middleware
@app.middleware("http")
def print_middleware(request: Request, call_next):
    print(f"Request: {request.method} {request.url.path}")
    response = call_next(request)
    return response

# Database file path
DB_FILE = "car_owners_db.sqlite"

# ============================================================================
# Pydantic Models
# ============================================================================

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

# ============================================================================
# Database Initialization
# ============================================================================

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

# ============================================================================
# Helper Functions for Database Operations
# ============================================================================

def get_db_connection():
    """Get database connection"""
    conn = sqlite3.connect(DB_FILE)
    # row_factory = sqlite3.Row converts each row from a tuple to a Row object that allows
    # column access by name (row['id']) instead of by index (row[0]). This makes code more readable.
    conn.row_factory = sqlite3.Row
    return conn

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

# Car Owner Functions
def read_car_owners() -> list[dict]:
    """Read all car owners from database"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM car_owners")
    rows = cursor.fetchall()
    conn.close()
    
    return [row_to_dict(row, "car_owners") for row in rows]

def get_car_owner_by_id(owner_id: int) -> dict | None:
    """Get a single car owner by ID"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM car_owners WHERE id = ?", (owner_id,))
    row = cursor.fetchone()
    conn.close()
    
    if row:
        return row_to_dict(row, "car_owners")
    return None

def create_car_owner_in_db(owner: CarOwner) -> dict:
    """Create a new car owner in database"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Set timestamps
    now = datetime.now().isoformat()
    
    # Always let SQLite auto-increment the ID - we don't include 'id' in the INSERT statement.
    # SQLite will automatically generate the next ID using AUTOINCREMENT.
    # Using RETURNING clause (SQLite 3.35.0+) to get the inserted row atomically.
    cursor.execute("""
        INSERT INTO car_owners (name, age, email, created_at)
        VALUES (?, ?, ?, ?)
        RETURNING *
    """, (owner.name, owner.age, owner.email, now))
    
    # Fetch the row that was just inserted (RETURNING clause returns it directly)
    row = cursor.fetchone()
    
    conn.commit()
    conn.close()
    
    # Convert the returned row to dictionary
    return row_to_dict(row, "car_owners")

def update_car_owner_in_db(owner_id: int, owner_update: CarOwnerUpdate) -> dict:
    """Update an existing car owner in database"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Check if car owner exists
    cursor.execute("SELECT * FROM car_owners WHERE id = ?", (owner_id,))
    row = cursor.fetchone()
    
    if not row:
        conn.close()
        return None
    
    # Build update query dynamically based on provided fields
    update_data = owner_update.model_dump(exclude_unset=True)
    
    if not update_data:
        conn.close()
        return get_car_owner_by_id(owner_id)
    
    # Build SET clause
    set_clauses = []
    values = []
    
    if 'name' in update_data:
        set_clauses.append("name = ?")
        values.append(update_data['name'])
    
    if 'age' in update_data:
        set_clauses.append("age = ?")
        values.append(update_data['age'])
    
    if 'email' in update_data:
        set_clauses.append("email = ?")
        values.append(update_data['email'])
    
    values.append(owner_id)  # For WHERE clause
    
    query = f"UPDATE car_owners SET {', '.join(set_clauses)} WHERE id = ?"
    cursor.execute(query, values)
    
    conn.commit()
    conn.close()
    
    return get_car_owner_by_id(owner_id)

def delete_car_owner_from_db(owner_id: int) -> bool:
    """Delete a car owner from database"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Check if car owner exists
    cursor.execute("SELECT id FROM car_owners WHERE id = ?", (owner_id,))
    if not cursor.fetchone():
        conn.close()
        return None
    
    cursor.execute("DELETE FROM car_owners WHERE id = ?", (owner_id,))
    conn.commit()
    conn.close()
    
    return True

# Car Functions
def read_cars(owner_id: int | None = None) -> list[dict]:
    """Read all cars, optionally filtered by owner_id"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    if owner_id is not None:
        cursor.execute("SELECT * FROM cars WHERE owner_id = ?", (owner_id,))
    else:
        cursor.execute("SELECT * FROM cars")
    
    rows = cursor.fetchall()
    conn.close()
    
    return [row_to_dict(row, "cars") for row in rows]

def get_car_by_id(car_id: int) -> dict | None:
    """Get a single car by ID"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM cars WHERE id = ?", (car_id,))
    row = cursor.fetchone()
    conn.close()
    
    if row:
        return row_to_dict(row, "cars")
    return None

def validate_owner_exists(owner_id: int) -> bool:
    """Check if car owner exists in database"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM car_owners WHERE id = ?", (owner_id,))
    exists = cursor.fetchone() is not None
    conn.close()
    return exists

def create_car_in_db(car: Car) -> dict:
    """Create a new car in database"""
    # Validate owner_id exists first!
    if not validate_owner_exists(car.owner_id):
        raise HTTPException(status_code=400, detail="Owner not found")
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Set timestamps
    now = datetime.now().isoformat()
    
    cursor.execute("""
        INSERT INTO cars (brand, model, year, color, owner_id, created_at)
        VALUES (?, ?, ?, ?, ?, ?)
        RETURNING *
    """, (car.brand, car.model, car.year, car.color, car.owner_id, now))
    
    # Fetch the row that was just inserted
    row = cursor.fetchone()
    
    conn.commit()
    conn.close()
    
    # Convert the returned row to dictionary
    return row_to_dict(row, "cars")

def update_car_in_db(car_id: int, car_update: CarUpdate) -> dict:
    """Update an existing car in database"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Check if car exists
    cursor.execute("SELECT * FROM cars WHERE id = ?", (car_id,))
    row = cursor.fetchone()
    
    if not row:
        conn.close()
        return None
    
    # Build update query dynamically based on provided fields
    update_data = car_update.model_dump(exclude_unset=True)
    
    if not update_data:
        conn.close()
        return get_car_by_id(car_id)
    
    # IMPORTANT: If owner_id is being updated, validate it exists
    if 'owner_id' in update_data:
        if not validate_owner_exists(update_data['owner_id']):
            conn.close()
            raise HTTPException(status_code=400, detail="Owner not found")
    
    # Build SET clause
    set_clauses = []
    values = []
    
    if 'brand' in update_data:
        set_clauses.append("brand = ?")
        values.append(update_data['brand'])
    
    if 'model' in update_data:
        set_clauses.append("model = ?")
        values.append(update_data['model'])
    
    if 'year' in update_data:
        set_clauses.append("year = ?")
        values.append(update_data['year'])
    
    if 'color' in update_data:
        set_clauses.append("color = ?")
        values.append(update_data['color'])
    
    if 'owner_id' in update_data:
        set_clauses.append("owner_id = ?")
        values.append(update_data['owner_id'])
    
    values.append(car_id)  # For WHERE clause
    
    query = f"UPDATE cars SET {', '.join(set_clauses)} WHERE id = ?"
    cursor.execute(query, values)
    
    conn.commit()
    conn.close()
    
    return get_car_by_id(car_id)

def delete_car_from_db(car_id: int) -> bool:
    """Delete a car from database"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Check if car exists
    cursor.execute("SELECT id FROM cars WHERE id = ?", (car_id,))
    if not cursor.fetchone():
        conn.close()
        return None
    
    cursor.execute("DELETE FROM cars WHERE id = ?", (car_id,))
    conn.commit()
    conn.close()
    
    return True

# CSV Functions
def export_car_owners_to_csv() -> str:
    """Export all car owners to CSV format"""
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
    conn = get_db_connection()
    cursor = conn.cursor()
    
    if owner_id is not None:
        cursor.execute("SELECT * FROM cars WHERE owner_id = ?", (owner_id,))
    else:
        cursor.execute("SELECT * FROM cars")
    
    rows = cursor.fetchall()
    conn.close()
    
    # Convert to CSV string
    output = io.StringIO()
    if rows:
        writer = csv.DictWriter(output, fieldnames=['id', 'brand', 'model', 'year', 'color', 'owner_id', 'created_at'])
        writer.writeheader()
        for row in rows:
            writer.writerow({
                'id': row['id'],
                'brand': row['brand'],
                'model': row['model'],
                'year': row['year'],
                'color': row['color'],
                'owner_id': row['owner_id'],
                'created_at': row['created_at']
            })
    
    return output.getvalue()

def import_car_owners_from_csv(csv_content: bytes) -> dict:
    """Import car owners from CSV and append to database"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Read CSV content
        csv_text = csv_content.decode('utf-8')
        csv_reader = csv.DictReader(io.StringIO(csv_text))
        
        imported_count = 0
        now = datetime.now().isoformat()
        
        # Append rows to car_owners table
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
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Read CSV content
        csv_text = csv_content.decode('utf-8')
        csv_reader = csv.DictReader(io.StringIO(csv_text))
        
        imported_count = 0
        now = datetime.now().isoformat()
        
        # Append rows to cars table
        for row in csv_reader:
            brand = row.get('brand', '').strip()
            if not brand:  # Skip rows without brand
                continue
            
            model = row.get('model', '').strip()
            year = int(row.get('year', 0))
            color = row.get('color', '').strip()
            owner_id = int(row.get('owner_id', 0))
            
            # IMPORTANT: Validate owner_id exists for each car!
            if not validate_owner_exists(owner_id):
                continue  # Skip cars with invalid owner_id
            
            cursor.execute("""
                INSERT INTO cars (brand, model, year, color, owner_id, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (brand, model, year, color, owner_id, now))
            imported_count += 1
        
        conn.commit()
        
        return {
            "message": f"Successfully imported {imported_count} cars from CSV",
            "imported_count": imported_count,
            "uploaded_at": now
        }
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=400, detail=f"Error importing CSV: {str(e)}")
    finally:
        conn.close()

# ============================================================================
# API Endpoints
# ============================================================================

@app.get("/")
def read_root():
    """Root endpoint"""
    return {"message": "Welcome to Car Owner Management API", "version": "1.0.0"}

# Car Owner Endpoints
@app.get("/car-owners", response_model=list[CarOwner])
def get_all_car_owners():
    """Get all car owners"""
    owners = read_car_owners()
    return owners

@app.get("/car-owners/{owner_id}", response_model=CarOwner)
def get_car_owner(owner_id: int):
    """Get a specific car owner by ID"""
    owner = get_car_owner_by_id(owner_id)
    if owner is None:
        raise HTTPException(status_code=404, detail="Car owner not found")
    return owner

@app.post("/car-owners", response_model=CarOwner, status_code=201)
def create_car_owner(owner: CarOwner):
    """Create a new car owner"""
    return create_car_owner_in_db(owner)

@app.put("/car-owners/{owner_id}", response_model=CarOwner)
def update_car_owner(owner_id: int, owner_update: CarOwnerUpdate):
    """Update an existing car owner"""
    updated_owner = update_car_owner_in_db(owner_id, owner_update)
    if updated_owner is None:
        raise HTTPException(status_code=404, detail="Car owner not found")
    return updated_owner

@app.delete("/car-owners/{owner_id}", status_code=204)
def delete_car_owner(owner_id: int):
    """Delete a car owner"""
    deleted = delete_car_owner_from_db(owner_id)
    if deleted is None:
        raise HTTPException(status_code=404, detail="Car owner not found")
    return None

# Car Endpoints
@app.get("/cars", response_model=list[Car])
def get_all_cars(owner_id: int | None = None):
    """Get all cars, optionally filtered by owner_id"""
    cars = read_cars(owner_id)
    return cars

@app.get("/cars/{car_id}", response_model=Car)
def get_car(car_id: int):
    """Get a specific car by ID"""
    car = get_car_by_id(car_id)
    if car is None:
        raise HTTPException(status_code=404, detail="Car not found")
    return car

@app.post("/cars", response_model=Car, status_code=201)
def create_car(car: Car):
    """Create a new car"""
    return create_car_in_db(car)

@app.put("/cars/{car_id}", response_model=Car)
def update_car(car_id: int, car_update: CarUpdate):
    """Update an existing car"""
    updated_car = update_car_in_db(car_id, car_update)
    if updated_car is None:
        raise HTTPException(status_code=404, detail="Car not found")
    return updated_car

@app.delete("/cars/{car_id}", status_code=204)
def delete_car(car_id: int):
    """Delete a car"""
    deleted = delete_car_from_db(car_id)
    if deleted is None:
        raise HTTPException(status_code=404, detail="Car not found")
    return None

# CSV Endpoints
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
    csv_content = export_cars_to_csv(owner_id)
    return Response(
        content=csv_content,
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=cars.csv"}
    )

@app.post("/car-owners/upload-csv")
async def upload_car_owners_csv(file: UploadFile = File(...)):
    """Upload a CSV file and import car owners"""
    # Validate file type
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="File must be a CSV file")
    
    # Read file content
    contents = await file.read()
    
    # Import CSV and store in database
    result = import_car_owners_from_csv(contents)
    
    return result

@app.post("/cars/upload-csv")
async def upload_cars_csv(file: UploadFile = File(...)):
    """Upload a CSV file and import cars"""
    # Validate file type
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="File must be a CSV file")
    
    # Read file content
    contents = await file.read()
    
    # Import CSV and store in database
    result = import_cars_from_csv(contents)
    
    return result

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8003)

# Run the server:
# uvicorn full_exercise_easy.main_car_owners_solution:app --reload --port 8003

