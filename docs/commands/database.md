# Database Connection Management (`dt db`)

The `dt db` command suite provides persistent connection profile management and session utilities across multiple relational and NoSQL database engines.

Profiles are stored in a dedicated local SQLite database at `~/.devtul/devtul_interface.db` (managed via [sqlite-utils](https://sqlite-utils.datasette.io/)), ensuring your connection credentials remain accessible across projects without storing secrets in repository code.

---

## 🔌 Supported Database Engines

DevTul supports connection profiles for five major database engines:
1. **PostgreSQL** (`pg` extra: `psycopg2-binary`)
2. **MySQL** (`mysql` extra: `mysql`)
3. **Microsoft SQL Server** (`mssql` extra: `pyodbc`)
4. **MongoDB** (`mongo` extra: `pymongo`)
5. **SQLite** (built-in Python standard library)

---

## 📋 Subcommands Reference

### 1. Add a Database Profile (`dt db add`)
Add a new profile using interactive terminal prompts or direct command-line arguments:

```bash
dt db add [OPTIONS]
```

**Options:**
- `--name`: Unique alias for this connection profile (e.g. `prod-analytics`, `local-dev`).
- `--engine`: Database type (`postgres`, `mysql`, `mssql`, `mongo`, `sqlite`).
- `--host`: Hostname or IP address (e.g. `localhost`, `10.0.0.5`).
- `--port`: Port number (default depends on engine).
- `--database`: Database / catalog name.
- `--user`: Username.
- `--password`: Password (prompted securely if omitted).

### 2. List Profiles (`dt db ls`)
View all saved database connection profiles in a formatted Rich table:

```bash
dt db ls
```

### 3. View Databases & Table Schemas (`dt db view`)
Inspect available databases, list tables within a database, or view schema and sample data:

```bash
# View all saved profiles and local SQLite databases in the current directory:
dt db view

# List tables and row counts in a database:
dt db view --db ./my_data.db

# Inspect schema and sample rows for a specific table:
dt db view --db ./my_data.db --table users
```

### 4. Query Databases & Export Results (`dt db query`)
Execute SQL queries against a database and export tabular data in multiple formats or custom Jinja templates:

```bash
# Display Rich terminal table:
dt db query "SELECT id, name FROM users" --db ./my_data.db

# Export to JSON:
dt db query "SELECT id, name FROM users" --db ./my_data.db --fmt json

# Export to CSV / TSV:
dt db query "SELECT id, name FROM users" --db ./my_data.db --fmt csv -o users.csv

# Export to Markdown table:
dt db query "SELECT id, name FROM users" --db ./my_data.db --fmt md

# Render into custom Jinja2 template:
dt db query "SELECT id, name FROM users" --db ./my_data.db --fmt jinja -t "{% for r in rows %}User: {{ r.name }}\n{% endfor %}"
```

### 5. Query Flat Data Files via DuckDB (`dt db query-file`)
Query CSV, Parquet, JSON, and SQLite files directly with DuckDB without loading them into a database server:

```bash
# Inspect first 50 rows of a CSV file:
dt db query-file ./analytics.csv

# Execute analytical SQL queries with DuckDB:
dt db query-file "SELECT department, AVG(salary) as avg_sal FROM 'employees.csv' GROUP BY department" --fmt table

# Query directly to JSON or Markdown:
dt db query-file "SELECT * FROM 'logs.parquet' WHERE status = 'ERROR' LIMIT 10" --fmt md

# Launch interactive DuckDB CLI:
dt db query-file ./analytics.csv --cli
```

---

## 💡 Practical Examples

### Example 1: Add a Local PostgreSQL Connection Interactively
```powershell
dt db create
# Interactively prompts for connection parameters and stores profile in ~/.devtul/devtul_interface.db
```

### Example 2: Inspect a SQLite Table Schema and First 5 Rows
```powershell
dt db view --db ~/.devtul/devtul_interface.db --table file_templates
```

### Example 3: Extract Query Data directly to JSON or CSV File
```powershell
dt db query "SELECT * FROM database_hosts" --db ~/.devtul/devtul_interface.db --fmt json -o hosts.json
```

### Example 4: Analytical Query over a CSV via DuckDB
```powershell
dt db query-file "SELECT count(*), max(amount) FROM 'sales.csv'" --fmt json
```

