# FastAPI SQLite Exercise - Quick Reference

Minimal reference guide for common patterns. Use `main_sqlite.py` as your primary reference!

---

## Key Patterns to Remember

### Database Connection
- Use `sqlite3.connect(DB_FILE)`
- Set `conn.row_factory = sqlite3.Row` for column access by name
- Always close connections with `conn.close()`

### CRUD Operations
- **Read:** `SELECT * FROM table WHERE condition`
- **Create:** `INSERT INTO table (cols) VALUES (?) RETURNING *`
- **Update:** `UPDATE table SET col = ? WHERE id = ?`
- **Delete:** `DELETE FROM table WHERE id = ?`

### Parameterized Queries
Always use `?` placeholders:
```python
cursor.execute("SELECT * FROM table WHERE id = ?", (id,))
```

### CSV Operations
- **Export:** Use `csv.DictWriter` with `io.StringIO()`
- **Import:** Use `csv.DictReader` with `io.StringIO()`
- Decode bytes: `csv_content.decode('utf-8')`

### Error Handling
- 404: `raise HTTPException(status_code=404, detail="Not found")`
- 400: `raise HTTPException(status_code=400, detail="Bad request")`

### Foreign Key Validation
Always check if related record exists before creating/updating:
```python
# Check owner exists before creating car
if not validate_owner_exists(car.owner_id):
    raise HTTPException(status_code=400, detail="Owner not found")
```

---

## Common Mistakes to Avoid

1. ❌ Forgetting to close database connections
2. ❌ Not using parameterized queries (SQL injection risk)
3. ❌ Not validating foreign keys before inserting
4. ❌ Forgetting to commit transactions
5. ❌ Not handling None/404 cases in endpoints

---

## Quick SQL Reference

```sql
-- Count records
SELECT COUNT(*) FROM table_name

-- Filter by condition
SELECT * FROM table_name WHERE column = ?

-- Group and aggregate
SELECT column, COUNT(*) FROM table_name GROUP BY column

-- Join tables
SELECT * FROM table1 t1 
INNER JOIN table2 t2 ON t1.id = t2.foreign_id
```

---

## Testing Checklist

- [ ] All endpoints return correct status codes
- [ ] Foreign key validation works
- [ ] CSV export downloads correctly
- [ ] CSV import validates data
- [ ] 404 errors handled properly
- [ ] Database connections closed properly

