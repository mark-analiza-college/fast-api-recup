# SQLite Tutorial

This tutorial covers the basics of SQLite, including database operations, CSV import, and CLI usage with proper formatting.

## Table of Contents

1. [What is SQLite?](#1-what-is-sqlite)
2. [Installing SQLite](#2-installing-sqlite)
3. [Opening SQLite CLI](#3-opening-sqlite-cli)
4. [Creating Databases and Tables](#4-creating-databases-and-tables)
5. [Basic SQL Operations](#5-basic-sql-operations)
6. [Formatting Output in CLI](#6-formatting-output-in-cli)
7. [Importing CSV Files](#7-importing-csv-files)
8. [Common SQL Queries](#8-common-sql-queries)
9. [Exporting Data](#9-exporting-data)
10. [Best Practices](#10-best-practices)

---

## 1. What is SQLite? ⭐ Required

SQLite is a lightweight, file-based database engine that doesn't require a separate server process. It's perfect for:
- **Small to medium applications**
- **Development and testing**
- **Embedded systems**
- **Mobile applications**
- **Prototyping**

**Key Features:**
- ✅ Zero configuration - no server setup needed
- ✅ Single file database - easy to backup and move
- ✅ ACID compliant - reliable transactions
- ✅ Cross-platform - works on Windows, Mac, Linux
- ✅ Built into Python - no additional installation needed

**Database File:**
- SQLite stores everything in a single file (e.g., `todos_db.sqlite`)
- You can copy, backup, or delete the entire database by managing one file

---

## 2. Installing SQLite ⭐ Required

### macOS
SQLite comes pre-installed. Check version:
```bash
sqlite3 --version
```

If not installed, use Homebrew:
```bash
brew install sqlite3
```

### Linux (Ubuntu/Debian)
```bash
sudo apt-get update
sudo apt-get install sqlite3
```

### Windows
Download from: https://www.sqlite.org/download.html
Or use Windows Subsystem for Linux (WSL)

### Python (Already Available)
SQLite is built into Python's standard library:
```python
import sqlite3  # No pip install needed!
```

---

## 3. Opening SQLite CLI ⭐ Required

### Opening a Database File
```bash
# Open existing database
sqlite3 todos_db.sqlite

# Create new database (if file doesn't exist)
sqlite3 new_database.sqlite
```

### Opening a Database File On windows
```bash
# Open existing database
sqlite3 py -m todos_db.sqlite

# Create new database (if file doesn't exist)
sqlite3 py -m new_database.sqlite
```

### SQLite CLI Prompt
Once opened, you'll see:
```
SQLite version 3.x.x
Enter ".help" for usage hints.
sqlite>
```

### Useful CLI Commands
```sql
-- Show all tables
.tables

-- Show table structure
.schema todos

-- Show all schemas
.schema

-- Exit SQLite
.quit
-- or
.exit

-- Show help
.help

-- Show database file info
.dbinfo
```

---

## 4. Creating Databases and Tables ⭐ Required

### Creating a Table
```sql
CREATE TABLE IF NOT EXISTS todos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    description TEXT,
    completed INTEGER NOT NULL DEFAULT 0,
    created_at TEXT,
    updated_at TEXT
);
```

**Explanation:**
- `INTEGER PRIMARY KEY AUTOINCREMENT` - Auto-incrementing ID (1, 2, 3...)
- `TEXT` - String data type
- `NOT NULL` - Field is required
- `DEFAULT 0` - Default value if not provided
- `IF NOT EXISTS` - Won't error if table already exists

### SQLite Data Types
- `INTEGER` - Whole numbers (1, 2, -5, 100)
- `REAL` - Floating point numbers (3.14, 2.5)
- `TEXT` - Strings ("hello", 'world')
- `BLOB` - Binary data (images, files)
- `NULL` - Missing/unknown value

**Note:** SQLite uses dynamic typing - you can store any type in any column (though not recommended).

### Boolean in SQLite
SQLite doesn't have a native BOOLEAN type. Use:
- `INTEGER` where `0 = False` and `1 = True`
- Convert in your application code: `bool(row['completed'])`

---

## 5. Basic SQL Operations ⭐ Required

### Insert Data
```sql
-- Insert single row
INSERT INTO todos (title, description, completed, created_at, updated_at)
VALUES ('Learn SQLite', 'Complete the tutorial', 0, datetime('now'), datetime('now'));

-- Insert multiple rows
INSERT INTO todos (title, completed, created_at, updated_at) VALUES
    ('Task 1', 0, datetime('now'), datetime('now')),
    ('Task 2', 1, datetime('now'), datetime('now')),
    ('Task 3', 0, datetime('now'), datetime('now'));
```

### Select Data
```sql
-- Select all columns
SELECT * FROM todos;

-- Select specific columns
SELECT id, title, completed FROM todos;

-- Select with condition
SELECT * FROM todos WHERE completed = 1;

-- Select with multiple conditions
SELECT * FROM todos WHERE completed = 0 AND title LIKE '%Learn%';
```

### Update Data
```sql
-- Update single row
UPDATE todos 
SET completed = 1, updated_at = datetime('now')
WHERE id = 1;

-- Update multiple rows
UPDATE todos 
SET completed = 1 
WHERE id IN (1, 2, 3);
```

### Delete Data
```sql
-- Delete specific row
DELETE FROM todos WHERE id = 1;

-- Delete all rows
DELETE FROM todos;

-- Delete with condition
DELETE FROM todos WHERE completed = 1;
```

---

## 6. Formatting Output in CLI ⭐ Required

### Default Output (Hard to Read)
```sql
sqlite> SELECT * FROM todos;
1|Learn SQLite|Complete the tutorial|0|2025-11-25T00:29:04|2025-11-25T00:29:04
2|Task 2||1|2025-11-25T00:29:05|2025-11-25T00:29:05
```

### Enable Headers
```sql
.headers on
SELECT * FROM todos;
```

### Column Mode (Recommended)
```sql
.headers on
.mode column
.width 5 20 30 10 25 25

SELECT * FROM todos;
```

**Output:**
```
id     title          description            completed  created_at              updated_at
-----  -------------  ---------------------  ---------  ----------------------  ----------------------
1      Learn SQLite   Complete the tutorial  0          2025-11-25T00:29:04...  2025-11-25T00:29:04...
2      Task 2                               1          2025-11-25T00:29:05...  2025-11-25T00:29:05...
```

### Box Mode (Nicest)
```sql
.headers on
.mode box
.width 5 20 30 10 25 25

SELECT * FROM todos;
```

**Output:**
```
┌────┬───────────────┬──────────────────────┬───────────┬──────────────────────┬──────────────────────┐
│ id │     title     │     description      │ completed │      created_at       │      updated_at       │
├────┼───────────────┼──────────────────────┼───────────┼──────────────────────┼──────────────────────┤
│ 1  │ Learn SQLite  │ Complete the tutorial│     0     │ 2025-11-25T00:29:04...│ 2025-11-25T00:29:04...│
│ 2  │ Task 2        │                      │     1     │ 2025-11-25T00:29:05...│ 2025-11-25T00:29:05...│
└────┴───────────────┴──────────────────────┴───────────┴──────────────────────┴──────────────────────┘
```

### Table Mode
```sql
.headers on
.mode table

SELECT * FROM todos;
```

### CSV Mode (for export)
```sql
.mode csv
.headers on
SELECT * FROM todos;
```

### Save Settings Permanently
Create `~/.sqliterc` file:
```bash
cat > ~/.sqliterc << 'EOF'
.headers on
.mode box
.width 5 20 30 10 25 25
EOF
```

Now every SQLite session will use these settings automatically!

---

## 7. Importing CSV Files ⭐ Required

### Step 1: Prepare Your CSV File
Create `todos.csv`:
```csv
title,description,completed
Learn SQLite,Complete the tutorial,0
Build API,Create REST endpoints,0
Deploy App,Deploy to production,1
```

**Important:** 
- First row should be column headers
- Match column names to your table (or use column mapping)
- Use commas to separate values
- Enclose text with commas in quotes: `"Learn, SQLite"`

### Step 2: Set Import Mode
```sql
-- Enable CSV mode
.mode csv

-- Show headers (optional, for verification)
.headers on
```

### Step 3: Import CSV
```sql
-- Import into existing table
.import todos.csv todos

-- If table doesn't exist, create it first
CREATE TABLE IF NOT EXISTS todos (
    title TEXT,
    description TEXT,
    completed INTEGER
);
.import todos.csv todos
```

### Step 4: Verify Import
```sql
.headers on
.mode box
SELECT * FROM todos;
```

### Import with Column Mapping
If CSV columns don't match table columns:
```sql
-- Create temporary table
CREATE TEMP TABLE temp_import (
    title TEXT,
    description TEXT,
    completed INTEGER
);

-- Import to temp table
.import todos.csv temp_import

-- Insert into actual table with mapping
INSERT INTO todos (title, description, completed, created_at, updated_at)
SELECT title, description, completed, datetime('now'), datetime('now')
FROM temp_import;

-- Drop temp table
DROP TABLE temp_import;
```

### Common Import Issues

**Issue: "Error: no such table"**
- Solution: Create the table first before importing

**Issue: "Error: expected X columns but found Y"**
- Solution: Check CSV format, ensure consistent column count

**Issue: "Error: datatype mismatch"**
- Solution: Verify data types match table schema

**Issue: Headers imported as data**
- Solution: Use `.import --skip 1 todos.csv todos` (SQLite 3.32.0+)
- Or manually delete the header row after import

---

## 8. Common SQL Queries ⭐ Required

### Sorting
```sql
-- Sort by created date (newest first)
SELECT * FROM todos ORDER BY created_at DESC;

-- Sort by multiple columns
SELECT * FROM todos ORDER BY completed ASC, created_at DESC;
```

### Filtering
```sql
-- WHERE clause
SELECT * FROM todos WHERE completed = 0;

-- LIKE (pattern matching)
SELECT * FROM todos WHERE title LIKE '%Learn%';

-- IN (multiple values)
SELECT * FROM todos WHERE id IN (1, 2, 3);

-- BETWEEN (range)
SELECT * FROM todos WHERE id BETWEEN 1 AND 10;
```

### Aggregation
```sql
-- Count rows
SELECT COUNT(*) FROM todos;

-- Count with condition
SELECT COUNT(*) FROM todos WHERE completed = 1;

-- Group by
SELECT completed, COUNT(*) as count 
FROM todos 
GROUP BY completed;

-- Sum, Average, Min, Max
SELECT 
    COUNT(*) as total,
    SUM(completed) as completed_count,
    AVG(completed) as completion_rate
FROM todos;
```

### Joins (if you have multiple tables)
```sql
-- Inner join
SELECT t.*, u.name as user_name
FROM todos t
INNER JOIN users u ON t.user_id = u.id;

-- Left join
SELECT t.*, u.name as user_name
FROM todos t
LEFT JOIN users u ON t.user_id = u.id;
```

### Limiting Results
```sql
-- Limit number of results
SELECT * FROM todos LIMIT 10;

-- Limit with offset (pagination)
SELECT * FROM todos LIMIT 10 OFFSET 20;  -- Skip first 20, get next 10
```

---

## 9. Exporting Data

### Export to CSV
```sql
.headers on
.mode csv
.output todos_export.csv
SELECT * FROM todos;
.output stdout  -- Reset output to console
```

### Export to SQL (Backup)
```sql
.output todos_backup.sql
.dump todos
.output stdout
```

### Export Specific Query
```sql
.headers on
.mode csv
.output completed_todos.csv
SELECT * FROM todos WHERE completed = 1;
.output stdout
```

### Export Table Structure
```sql
.schema todos > todos_schema.sql
```

---

## 10. Best Practices

### 1. Always Use Transactions
```sql
BEGIN TRANSACTION;
-- Your SQL statements
COMMIT;
-- Or ROLLBACK; if error occurs
```

### 2. Use Parameterized Queries (Prevent SQL Injection)
```python
# Python example
cursor.execute("SELECT * FROM todos WHERE id = ?", (todo_id,))
# NOT: f"SELECT * FROM todos WHERE id = {todo_id}"  # DANGEROUS!
```

### 3. Create Indexes for Frequently Queried Columns
```sql
CREATE INDEX idx_completed ON todos(completed);
CREATE INDEX idx_created_at ON todos(created_at);
```

### 4. Use IF NOT EXISTS
```sql
CREATE TABLE IF NOT EXISTS todos (...);
CREATE INDEX IF NOT EXISTS idx_completed ON todos(completed);
```

### 5. Set Up Display Formatting
Always configure your CLI for readability:
```sql
.headers on
.mode box
```

### 6. Backup Regularly
```bash
# Copy database file
cp todos_db.sqlite todos_db_backup.sqlite

# Or use SQLite backup command
sqlite3 todos_db.sqlite ".backup todos_db_backup.sqlite"
```

### 7. Use Appropriate Data Types
- Use `INTEGER` for IDs and numbers
- Use `TEXT` for strings
- Use `REAL` for decimals
- Use `INTEGER` (0/1) for booleans

### 8. Handle NULL Values
```sql
-- Check for NULL
SELECT * FROM todos WHERE description IS NULL;
SELECT * FROM todos WHERE description IS NOT NULL;

-- Use COALESCE for defaults
SELECT id, title, COALESCE(description, 'No description') as description 
FROM todos;
```

---

## Quick Reference Card

### Essential Commands
```sql
-- Database
.open database.sqlite
.databases

-- Tables
.tables
.schema table_name

-- Display
.headers on
.mode column
.mode box
.mode csv

-- Import/Export
.import file.csv table_name
.output file.csv
.dump table_name

-- Exit
.quit
.exit
```

### Essential SQL
```sql
-- Create
CREATE TABLE name (col1 TYPE, col2 TYPE);
INSERT INTO table VALUES (...);

-- Read
SELECT * FROM table WHERE condition;
SELECT col1, col2 FROM table ORDER BY col1 DESC;

-- Update
UPDATE table SET col1 = value WHERE condition;

-- Delete
DELETE FROM table WHERE condition;
```

---

## Next Steps

1. Practice creating tables and inserting data
2. Import a CSV file with your data
3. Write queries to filter and sort data
4. Export your data to CSV or SQL
5. Integrate SQLite with your Python/FastAPI applications

For more advanced topics, check out:
- SQLite documentation: https://www.sqlite.org/docs.html
- SQLite Python tutorial: https://docs.python.org/3/library/sqlite3.html

