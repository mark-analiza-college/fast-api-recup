# SQLite Exercises

Practice SQLite operations with increasing difficulty. Each exercise builds on previous concepts and helps you master SQLite database management.

---

## Exercise 1: Create Database and Table (Easy) ⭐ Required

**Task:** Create a new SQLite database and a `todos` table.

**Requirements:**
- Database file: `exercise1.db`
- Table: `todos` with columns:
  - `id` (INTEGER PRIMARY KEY AUTOINCREMENT)
  - `title` (TEXT NOT NULL)
  - `description` (TEXT)
  - `completed` (INTEGER DEFAULT 0)
  - `created_at` (TEXT)

**Steps:**
```bash
# 1. Open SQLite CLI
sqlite3 exercise1.db

# 2. Create the table
CREATE TABLE IF NOT EXISTS todos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    description TEXT,
    completed INTEGER DEFAULT 0,
    created_at TEXT
);

# 3. Verify table was created
.tables
.schema todos
```

**Expected Result:**
- Table `todos` exists
- Schema shows all 5 columns

---

## Exercise 2: Insert Data (Easy) ⭐ Required

**Task:** Insert at least 5 todos into the `todos` table.

**Requirements:**
- Insert todos with different completion statuses
- Use `datetime('now')` for `created_at`
- Mix completed (1) and incomplete (0) todos

**Steps:**
```sql
-- Insert your todos here
INSERT INTO todos (title, description, completed, created_at) VALUES
    ('Learn SQLite', 'Master SQLite basics', 0, datetime('now')),
    ('Build API', 'Create REST endpoints', 0, datetime('now')),
    ('Write Tests', 'Add unit tests', 1, datetime('now')),
    ('Deploy App', 'Deploy to production', 0, datetime('now')),
    ('Review Code', 'Code review session', 1, datetime('now'));
```

**Verify:**
```sql
.headers on
.mode box
SELECT * FROM todos;
```

**Expected Result:**
- 5 rows in the table
- Mix of completed (1) and incomplete (0) todos

---

## Exercise 3: Query Data (Easy) ⭐ Required

**Task:** Write queries to filter and sort todos.

**Requirements:**
1. Select all incomplete todos
2. Select all completed todos
3. Select todos ordered by creation date (newest first)
4. Select only title and description columns

**Queries:**
```sql
-- 1. All incomplete todos
SELECT * FROM todos WHERE completed = 0;

-- 2. All completed todos
SELECT * FROM todos WHERE completed = 1;

-- 3. Ordered by creation date (newest first)
SELECT * FROM todos ORDER BY created_at DESC;

-- 4. Only title and description
SELECT title, description FROM todos;
```

**Expected Result:**
- Each query returns filtered/sorted results
- Column selection shows only requested fields

---

## Exercise 4: Update and Delete (Easy) ⭐ Required

**Task:** Update and delete todos.

**Requirements:**
1. Mark a specific todo as completed
2. Update a todo's description
3. Delete a completed todo
4. Count remaining todos

**Steps:**
```sql
-- 1. Mark todo with id=1 as completed
UPDATE todos 
SET completed = 1, created_at = datetime('now')
WHERE id = 1;

-- 2. Update description for todo with id=2
UPDATE todos 
SET description = 'Updated description'
WHERE id = 2;

-- 3. Delete a completed todo
DELETE FROM todos WHERE id = 3 AND completed = 1;

-- 4. Count remaining todos
SELECT COUNT(*) as total_todos FROM todos;
```

**Verify:**
```sql
SELECT * FROM todos;
```

**Expected Result:**
- Todo with id=1 is now completed
- Todo with id=2 has updated description
- One todo deleted
- Count shows remaining todos

---

## Exercise 5: Import CSV (Medium) ⭐ Required

**Task:** Import todos from a CSV file.

**Requirements:**
- Use `sample_todos.csv` file
- Import into a new table or existing table
- Verify all rows were imported correctly

**Steps:**
```sql
-- 1. Set CSV mode
.mode csv
.headers on

-- 2. Import CSV (if table exists)
.import sample_todos.csv todos

-- OR create table first, then import
CREATE TABLE IF NOT EXISTS todos (
    title TEXT,
    description TEXT,
    completed INTEGER
);
.import sample_todos.csv todos

-- 3. Verify import
.headers on
.mode box
SELECT COUNT(*) as imported_count FROM todos;
SELECT * FROM todos LIMIT 5;
```

**Expected Result:**
- All rows from CSV imported successfully
- Data matches CSV file

---

## Exercise 6: Aggregation Queries (Medium) ⭐ Required

**Task:** Write aggregation queries to analyze todos.

**Requirements:**
1. Count total todos
2. Count completed vs incomplete todos
3. Calculate completion percentage
4. Group by completion status

**Queries:**
```sql
-- 1. Total count
SELECT COUNT(*) as total FROM todos;

-- 2. Count by status
SELECT 
    completed,
    COUNT(*) as count
FROM todos
GROUP BY completed;

-- 3. Completion percentage
SELECT 
    COUNT(*) as total,
    SUM(completed) as completed_count,
    ROUND(SUM(completed) * 100.0 / COUNT(*), 2) as completion_percentage
FROM todos;

-- 4. Group by status with labels
SELECT 
    CASE 
        WHEN completed = 1 THEN 'Completed'
        ELSE 'Incomplete'
    END as status,
    COUNT(*) as count
FROM todos
GROUP BY completed;
```

**Expected Result:**
- Statistics about todos
- Completion percentage calculated
- Grouped results by status

---

## Exercise 7: Advanced Filtering (Medium)

**Task:** Use advanced WHERE clauses and pattern matching.

**Requirements:**
1. Find todos with "Learn" in title
2. Find todos created in the last 7 days
3. Find todos with specific IDs (1, 3, 5)
4. Find todos with NULL descriptions

**Queries:**
```sql
-- 1. Pattern matching (LIKE)
SELECT * FROM todos WHERE title LIKE '%Learn%';

-- 2. Date range (if you have date column)
SELECT * FROM todos 
WHERE created_at >= datetime('now', '-7 days');

-- 3. Multiple IDs (IN)
SELECT * FROM todos WHERE id IN (1, 3, 5);

-- 4. NULL values
SELECT * FROM todos WHERE description IS NULL;
SELECT * FROM todos WHERE description IS NOT NULL;
```

**Expected Result:**
- Filtered results based on conditions
- Pattern matching finds relevant todos

---

## Exercise 8: Sorting and Limiting (Medium)

**Task:** Sort and limit query results.

**Requirements:**
1. Get 5 most recent todos
2. Get oldest incomplete todo
3. Sort by title alphabetically
4. Get todos 6-10 (pagination)

**Queries:**
```sql
-- 1. 5 most recent
SELECT * FROM todos 
ORDER BY created_at DESC 
LIMIT 5;

-- 2. Oldest incomplete
SELECT * FROM todos 
WHERE completed = 0 
ORDER BY created_at ASC 
LIMIT 1;

-- 3. Alphabetical by title
SELECT * FROM todos 
ORDER BY title ASC;

-- 4. Pagination (rows 6-10)
SELECT * FROM todos 
ORDER BY id ASC 
LIMIT 5 OFFSET 5;
```

**Expected Result:**
- Results sorted correctly
- Limited to requested number
- Pagination works

---

## Exercise 9: Export Data (Medium)

**Task:** Export todos to different formats.

**Requirements:**
1. Export all todos to CSV
2. Export completed todos to CSV
3. Export table schema to SQL file
4. Create a backup of the database

**Steps:**
```sql
-- 1. Export all to CSV
.headers on
.mode csv
.output all_todos.csv
SELECT * FROM todos;
.output stdout

-- 2. Export completed only
.headers on
.mode csv
.output completed_todos.csv
SELECT * FROM todos WHERE completed = 1;
.output stdout

-- 3. Export schema
.output schema.sql
.schema todos
.output stdout

-- 4. Backup database (in terminal, not SQLite CLI)
-- sqlite3 exercise1.db ".backup exercise1_backup.db"
```

**Expected Result:**
- CSV files created with data
- Schema exported to SQL file
- Backup database created

---

## Exercise 10: Create Indexes (Advanced)

**Task:** Create indexes to improve query performance.

**Requirements:**
1. Create index on `completed` column
2. Create index on `created_at` column
3. Verify indexes were created
4. Test query performance

**Steps:**
```sql
-- 1. Index on completed
CREATE INDEX IF NOT EXISTS idx_completed ON todos(completed);

-- 2. Index on created_at
CREATE INDEX IF NOT EXISTS idx_created_at ON todos(created_at);

-- 3. List all indexes
SELECT name, tbl_name FROM sqlite_master WHERE type = 'index';

-- 4. Test query (should use index)
EXPLAIN QUERY PLAN SELECT * FROM todos WHERE completed = 1;
```

**Expected Result:**
- Indexes created successfully
- Query plan shows index usage

---

## Exercise 11: Transactions (Advanced)

**Task:** Use transactions to ensure data consistency.

**Requirements:**
1. Start a transaction
2. Insert multiple todos
3. Commit the transaction
4. Try a transaction with rollback

**Steps:**
```sql
-- 1. Transaction with commit
BEGIN TRANSACTION;

INSERT INTO todos (title, description, completed, created_at) VALUES
    ('Task 1', 'Description 1', 0, datetime('now')),
    ('Task 2', 'Description 2', 0, datetime('now')),
    ('Task 3', 'Description 3', 1, datetime('now'));

COMMIT;

-- 2. Transaction with rollback
BEGIN TRANSACTION;

INSERT INTO todos (title, completed, created_at) VALUES
    ('Should not save', 0, datetime('now'));

ROLLBACK;

-- Verify rollback worked
SELECT * FROM todos WHERE title = 'Should not save';
-- Should return no rows
```

**Expected Result:**
- First transaction commits successfully
- Second transaction rolls back (no data saved)

---

## Exercise 12: Complex Queries (Advanced)

**Task:** Write complex queries combining multiple concepts.

**Requirements:**
1. Find incomplete todos created in last 3 days, sorted by title
2. Count todos by completion status with percentage
3. Find the most recent completed todo
4. Get statistics: total, completed, incomplete, completion rate

**Queries:**
```sql
-- 1. Complex filter and sort
SELECT * FROM todos 
WHERE completed = 0 
  AND created_at >= datetime('now', '-3 days')
ORDER BY title ASC;

-- 2. Count with percentage
SELECT 
    completed,
    COUNT(*) as count,
    ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM todos), 2) as percentage
FROM todos
GROUP BY completed;

-- 3. Most recent completed
SELECT * FROM todos 
WHERE completed = 1 
ORDER BY created_at DESC 
LIMIT 1;

-- 4. Complete statistics
SELECT 
    COUNT(*) as total,
    SUM(completed) as completed_count,
    COUNT(*) - SUM(completed) as incomplete_count,
    ROUND(SUM(completed) * 100.0 / COUNT(*), 2) as completion_rate
FROM todos;
```

**Expected Result:**
- Complex queries return correct results
- Statistics calculated accurately

---

## Bonus Exercise: Python Integration

**Task:** Use SQLite with Python to perform operations.

**Requirements:**
- Connect to database
- Insert a todo
- Query todos
- Update a todo
- Delete a todo

**Python Code:**
```python
import sqlite3
from datetime import datetime

# Connect to database
conn = sqlite3.connect('exercise1.db')
conn.row_factory = sqlite3.Row  # Enable column access by name
cursor = conn.cursor()

# Insert
cursor.execute("""
    INSERT INTO todos (title, description, completed, created_at)
    VALUES (?, ?, ?, ?)
""", ('Python Task', 'Created from Python', 0, datetime.now().isoformat()))
conn.commit()

# Query
cursor.execute("SELECT * FROM todos WHERE completed = 0")
todos = cursor.fetchall()
for todo in todos:
    print(f"{todo['id']}: {todo['title']}")

# Update
cursor.execute("""
    UPDATE todos 
    SET completed = 1 
    WHERE title = ?
""", ('Python Task',))
conn.commit()

# Delete
cursor.execute("DELETE FROM todos WHERE title = ?", ('Python Task',))
conn.commit()

conn.close()
```

**Expected Result:**
- Python successfully interacts with SQLite
- All CRUD operations work

---

## Solutions Checklist

After completing exercises, verify:
- [ ] Can create databases and tables
- [ ] Can insert, update, and delete data
- [ ] Can query with filters and sorting
- [ ] Can import CSV files
- [ ] Can export data to CSV
- [ ] Can use aggregation functions
- [ ] Can create and use indexes
- [ ] Can use transactions
- [ ] Can write complex queries
- [ ] Can integrate with Python

---

## Next Steps

1. Practice with your own data
2. Integrate SQLite into your FastAPI application
3. Learn about database normalization
4. Explore advanced SQL features (JOINs, subqueries)
5. Study database optimization techniques

For more practice, try creating:
- A user management system
- A product catalog
- A blog with posts and comments
- An inventory management system

