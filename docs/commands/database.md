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

Displays:
- Profile Name
- Engine Type
- Host & Port
- Database Name
- Username
- Created & Updated Timestamps

### 3. Test Connections (`dt db test`)
Verify network reachability and database authentication credentials:

```bash
# Test a specific connection profile:
dt db test my-profile

# Test all saved profiles:
dt db test --all
```

### 4. Connect to a Database (`dt db conn`)
Retrieve connection strings or launch an interactive database session:

```bash
# Retrieve connection URI for scripts or environment variables:
dt db conn my-profile --uri

# Launch interactive CLI session:
dt db conn my-profile
```

---

## 💡 Practical Examples

### Example 1: Add a Local PostgreSQL Connection Interactively
```powershell
dt db add
# Prompts for Engine, Name, Host, Port, Database, User, Password
```

### Example 2: Add a SQLite Connection Directly via CLI
```powershell
dt db add --name "app-cache" --engine "sqlite" --database "C:/data/app_cache.db"
```

### Example 3: Test Database Connectivity in CI/CD or Diagnostic Scripts
```powershell
dt db test app-cache
```
