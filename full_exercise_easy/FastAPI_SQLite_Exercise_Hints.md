# FastAPI SQLite Exercise - Quick Reference & Hints

Quick reference guide for common patterns and solutions.

---

## Database Connection Pattern

```python
def get_db_connection():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row  # Important!
    return conn
```

---

## Read All Records Pattern

```python
def read_car_owners() -> list[dict]:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM car_owners")
    rows = cursor.fetchall()
    conn.close()
    return [row_to_dict(row, "car_owners") for row in rows]
```

---

## Get by ID Pattern

```python
def get_car_owner_by_id(owner_id: int) -> dict | None:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM car_owners WHERE id = ?", (owner_id,))
    row = cursor.fetchone()
    conn.close()
    if row:
        return row_to_dict(row, "car_owners")
    return None
```

---

## Create Record Pattern (with RETURNING)

```python
def create_car_owner_in_db(owner: CarOwner) -> dict:
    conn = get_db_connection()
    cursor = conn.cursor()
    now = datetime.now().isoformat()
    
    cursor.execute("""
        INSERT INTO car_owners (name, age, email, created_at)
        VALUES (?, ?, ?, ?)
        RETURNING *
    """, (owner.name, owner.age, owner.email, now))
    
    row = cursor.fetchone()
    conn.commit()
    conn.close()
    
    return row_to_dict(row, "car_owners")
```

---

## Update Record Pattern (Dynamic)

```python
def update_car_owner_in_db(owner_id: int, owner_update: CarOwnerUpdate) -> dict:
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Check if exists
    cursor.execute("SELECT * FROM car_owners WHERE id = ?", (owner_id,))
    if not cursor.fetchone():
        conn.close()
        return None
    
    # Build update dynamically
    update_data = owner_update.model_dump(exclude_unset=True)
    if not update_data:
        conn.close()
        return get_car_owner_by_id(owner_id)
    
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
    
    values.append(owner_id)
    query = f"UPDATE car_owners SET {', '.join(set_clauses)} WHERE id = ?"
    cursor.execute(query, values)
    
    conn.commit()
    conn.close()
    return get_car_owner_by_id(owner_id)
```

---

## Delete Record Pattern

```python
def delete_car_owner_from_db(owner_id: int) -> bool:
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT id FROM car_owners WHERE id = ?", (owner_id,))
    if not cursor.fetchone():
        conn.close()
        return None
    
    cursor.execute("DELETE FROM car_owners WHERE id = ?", (owner_id,))
    conn.commit()
    conn.close()
    return True
```

---

## Filtered Query Pattern

```python
def read_cars(owner_id: int | None = None) -> list[dict]:
    conn = get_db_connection()
    cursor = conn.cursor()
    
    if owner_id is not None:
        cursor.execute("SELECT * FROM cars WHERE owner_id = ?", (owner_id,))
    else:
        cursor.execute("SELECT * FROM cars")
    
    rows = cursor.fetchall()
    conn.close()
    return [row_to_dict(row, "cars") for row in rows]
```

---

## Foreign Key Validation Pattern

```python
def validate_owner_exists(owner_id: int) -> bool:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM car_owners WHERE id = ?", (owner_id,))
    exists = cursor.fetchone() is not None
    conn.close()
    return exists

def create_car_in_db(car: Car) -> dict:
    # Validate owner exists first!
    if not validate_owner_exists(car.owner_id):
        raise HTTPException(status_code=400, detail="Owner not found")
    
    # Then create car (same pattern as create_car_owner_in_db)
    # ...
```

---

## CSV Export Pattern

```python
def export_car_owners_to_csv() -> str:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM car_owners")
    rows = cursor.fetchall()
    conn.close()
    
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
```

---

## CSV Import Pattern

```python
def import_car_owners_from_csv(csv_content: bytes) -> dict:
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        csv_text = csv_content.decode('utf-8')
        csv_reader = csv.DictReader(io.StringIO(csv_text))
        
        imported_count = 0
        now = datetime.now().isoformat()
        
        for row in csv_reader:
            name = row.get('name', '').strip()
            if not name:
                continue
            
            age = int(row.get('age', 0))
            email = row.get('email', '').strip()
            
            cursor.execute("""
                INSERT INTO car_owners (name, age, email, created_at)
                VALUES (?, ?, ?, ?)
            """, (name, age, email, now))
            imported_count += 1
        
        conn.commit()
        return {
            "message": f"Successfully imported {imported_count} car owners",
            "imported_count": imported_count,
            "uploaded_at": now
        }
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=400, detail=f"Error: {str(e)}")
    finally:
        conn.close()
```

---

## CSV Download Endpoint Pattern

```python
@app.get("/car-owners/export-csv")
def export_car_owners_csv():
    csv_content = export_car_owners_to_csv()
    return Response(
        content=csv_content,
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=car_owners.csv"}
    )
```

---

## Common SQL Patterns

### Count Records
```python
cursor.execute("SELECT COUNT(*) FROM car_owners")
count = cursor.fetchone()[0]
```

### Group By
```python
cursor.execute("""
    SELECT brand, COUNT(*) as count 
    FROM cars 
    GROUP BY brand 
    ORDER BY count DESC
""")
```

### Join Query
```python
cursor.execute("""
    SELECT c.*, co.name as owner_name
    FROM cars c
    INNER JOIN car_owners co ON c.owner_id = co.id
    WHERE c.id = ?
""", (car_id,))
```

---

## Error Handling Patterns

### 404 Not Found
```python
owner = get_car_owner_by_id(owner_id)
if owner is None:
    raise HTTPException(status_code=404, detail="Car owner not found")
```

### 400 Bad Request
```python
if not validate_owner_exists(car.owner_id):
    raise HTTPException(status_code=400, detail="Owner not found")
```

### 400 for Invalid File
```python
if not file.filename.endswith('.csv'):
    raise HTTPException(status_code=400, detail="File must be a CSV file")
```

---

## Testing Tips

1. **Use FastAPI docs:** `http://localhost:8003/docs`
2. **Test incrementally:** Build one function at a time
3. **Check database:** Use SQLite CLI to verify data
4. **Test edge cases:** Invalid IDs, empty data, etc.

---

## Quick Debugging

### Check if table exists:
```python
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
print(cursor.fetchall())
```

### Check table structure:
```python
cursor.execute("PRAGMA table_info(car_owners)")
print(cursor.fetchall())
```

### View all data:
```python
cursor.execute("SELECT * FROM car_owners")
for row in cursor.fetchall():
    print(dict(row))
```

