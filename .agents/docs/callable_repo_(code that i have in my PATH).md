---
file_count: 28
files_included: 25
generated_at: '2026-09-30T19:52:06.575828'
repo_path: C:\Users\Will\OneDrive\Documents\Callable
---

# CALLABLE

---

## Git Metadata

| Key                 | Value                                                                             |
|---------------------|-----------------------------------------------------------------------------------|
| Current Branch      | main                                                                              |
| Branches            | main                                                                              |
| Latest Commit       | 38007382                                                                          |
| Commit Message      | feat: Implement SQLite database merger CLI with schema handling and file scanning |
| Author              | WIll Morris                                                                       |
| Commit Date         | 2025-12-31T18:05:56-06:00                                                         |
| Uncommitted Changes | No                                                                                |
| Untracked Files     | 0                                                                                 |
| Remotes             | origin: https://github.com/Willmo103/Callable.git                                 |

---

## Structure

```
C:/Users/Will/OneDrive/Documents/Callable/
├── model_gen/
│   └── sys_msg.py
├── py-scripts/
│   ├── file_watcher.py
│   └── watch_src.py
├── .env
├── .gitignore
├── .llm-context
├── _test_callables_preload.cmd
├── cb-app.cmd
├── clipboard_history.json
├── concat_sqlite_dbs.py
├── create_models.py
├── documented_profile.ps1
├── llm_resume.py
├── llm_test.py
├── mtg.py
├── ollama_convo copy.py
├── ollama_convo.py
├── piper_cli.py
├── postman_cli.py
├── recruiter_msg.txt
├── run_checks_on_save.py
├── sql_formatter.ps1
├── uas.cmd
├── uv_script_add.cmd
└── uv_script_create.cmd
```

---

## Files

### .env

| Property      | Value                      |
|---------------|----------------------------|
| Relative Path | .env                       |
| Created At    | 2025-09-18T16:50:19.204794 |
| Last Modified | 2025-09-23T14:40:34.096222 |
| Size          | 99 bytes                   |

**Content**:

```plaintext
DB='C:/storage/wembed/local.db'
MODEL='gpt-oss:20b'
OLLAMA_API_URL='http://192.168.0.182:11434'

```

---

### .gitignore

| Property      | Value               |
|---------------|---------------------|
| Relative Path | .gitignore          |
| Created At    | 2025-08-23T19:34:57.552888 |
| Last Modified | 2025-11-20T19:23:19 |
| Size          | 70 bytes            |

**Content**:

```plaintext
binaries
*.dll
resume.txt
devtul.exe
*.exe
*.md
*.db
*.sqlite

```

---

### .llm-context

| Property      | Value                      |
|---------------|----------------------------|
| Relative Path | .llm-context               |
| Created At    | 2025-08-23T20:02:51.817863 |
| Last Modified | 2025-08-23T20:12:53.893005 |
| Size          | 472 bytes                  |

**Content**:

```plaintext
---
version: "1.0"
revision: "1.0.0"
repo_desc: "This is my `Callable` repository. It is located at `~\OneDrive\Documents\Callable`"
---

# Callable

This is a repository in my $env:PATH for housing cmd files that will launch other scripts or programs.

## Layout

```plaintext

Callable /
├── backup.cmd
├── check_services.ps1
├── notify.gotify.bat
└── python_scripts/
    ├── script1.py
    └── script2.py

```

```

---

### _test_callables_preload.cmd

| Property      | Value                       |
|---------------|-----------------------------|
| Relative Path | _test_callables_preload.cmd |
| Created At    | 2025-08-23T19:51:24.670419  |
| Last Modified | 2025-08-23T20:25:15.762830  |
| Size          | 43 bytes                    |

**Content**:

```bat
python %Callables%\py-scripts\_preload.py

```

---

### cb-app.cmd

| Property      | Value                      |
|---------------|----------------------------|
| Relative Path | cb-app.cmd                 |
| Created At    | 2025-09-18T16:42:59.283079 |
| Last Modified | 2025-09-19T21:09:46.615358 |
| Size          | 1508 bytes                 |

**Content**:

```bat
@echo off
REM Clipboard History Manager - Windows Startup Script
REM This script starts the clipboard history application at system startup

REM Get the directory where this script is located
set "SCRIPT_DIR=%~dp0"

REM Change to the script directory
@REM cd /d "%SCRIPT_DIR%"

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo Python is not installed or not in PATH.
    echo Please install Python 3.8 or higher and try again.
    pause
    exit /b 1
)

REM Check if required packages are installed
python -c "import PyQt6" >nul 2>&1
if errorlevel 1 (
    echo PyQt6 is not installed. Installing required packages...
    python -m pip install PyQt6
    if errorlevel 1 (
        echo Failed to install PyQt6. Please install manually:
        echo pip install PyQt6
        pause
        exit /b 1
    )
)

REM Start the clipboard history application in hidden mode
echo Starting Clipboard History Manager...
@REM launch the main application script in a new **detached** process and exit the batch script immediately
start "" /b python "%SCRIPT_DIR%__main__.py" --hidden
if errorlevel 1 (
    echo Failed to start Clipboard History Manager.
    pause
    exit /b 1
)
echo Clipboard History Manager started successfully.
REM Optionally, you can uncomment the lines below to keep the command window open
@REM REM If we get here, the application has exited
@REM echo Clipboard History Manager has stopped.
@REM pause
exit /b 0

```

---

### clipboard_history.json

| Property      | Value                      |
|---------------|----------------------------|
| Relative Path | clipboard_history.json     |
| Created At    | 2025-09-19T21:15:11.387430 |
| Last Modified | 2025-09-19T21:15:11.388944 |
| Size          | 43248 bytes                |

**Content**:

```plaintext
{
  "export_info": {
    "timestamp": "2025-09-19T21:15:11.387680",
    "total_items": 4,
    "version": "1.0",
    "auto_backup": true
  },
  "items": [
    {
      "id": 3,
      "content": "@echo off\nREM Clipboard History Manager - Windows Startup Script\nREM This script starts the clipboard history application at system startup\n\nREM Get the directory where this script is located\nset \"SCRIPT_DIR=%~dp0\"\n\nREM Change to the script directory\n@REM cd /d \"%SCRIPT_DIR%\"\n\nREM Check if Python is installed\npython --version >nul 2>&1\nif errorlevel 1 (\n    echo Python is not installed or not in PATH.\n    echo Please install Python 3.8 or higher and try again.\n    pause\n    exit /b 1\n)\n\nREM Check if required packages are installed\npython -c \"import PyQt6\" >nul 2>&1\nif errorlevel 1 (\n    echo PyQt6 is not installed. Installing required packages...\n    python -m pip install PyQt6\n    if errorlevel 1 (\n        echo Failed to install PyQt6. Please install manually:\n        echo pip install PyQt6\n        pause\n        exit /b 1\n    )\n)\n\nREM Start the clipboard history application in hidden mode\necho Starting Clipboard History Manager...\n@REM launch the main application script in a new **detached** process and exit the batch script immediately\nstart \"\" /b python \"%SCRIPT_DIR%__main__.py\" --hidden\nif errorlevel 1 (\n    echo Failed to start Clipboard History Manager.\n    pause\n    exit /b 1\n)\necho Clipboard History Manager started successfully.\nREM Optionally, you can uncomment the lines below to keep the command window open\n@REM REM If we get here, the application has exited\n@REM echo Clipboard History Manager has stopped.\n@REM pause\nexit /b 0",
      "content_type": "text",
      "file_path": null,
      "file_size": null,
      "mime_type": null,
      "thumbnail": null,
      "timestamp": "2025-09-20 02:14:40",
      "is_favorite": false,
      "access_count": 2
    },
    {
      "id": 4,
      "content": "@echo off\nREM Clipboard History Manager - Windows Startup Script\nREM This script starts the clipboard history application at system startup\n\nREM Get the directory where this script is located\nset \"SCRIPT_DIR=%~dp0\"\n\nREM Change to the script directory\n@REM cd /d \"%SCRIPT_DIR%\"\n\nREM Check if Python is installed\npython --version >nul 2>&1\nif errorlevel 1 (\n    echo Python is not installed or not in PATH.\n    echo Please install Python 3.8 or higher and try again.\n    pause\n    exit /b 1\n)\n\nREM Check if required packages are installed\npython -c \"import PyQt6\" >nul 2>&1\nif errorlevel 1 (\n    echo PyQt6 is not installed. Installing required packages...\n    python -m pip install PyQt6\n    if errorlevel 1 (\n        echo Failed to install PyQt6. Please install manually:\n        echo pip install PyQt6\n        pause\n        exit /b 1\n    )\n)\n\nREM Start the clipboard history application in hidden mode\necho Starting Clipboard History Manager...\n@REM launch the main application script in a new **detached** process and exit the batch script immediately\nstart \"\" /b python \"%SCRIPT_DIR%__main__.py\" --hidden\nif errorlevel 1 (\n    echo Failed to start Clipboard History Manager.\n    pause\n    exit /b 1\n)\necho Clipboard History Manager started successfully.\nREM Optionally, you can uncomment the lines below to keep the command window open\n@REM REM If we get here, the application has exited\n@REM echo Clipboard History Manager has stopped.\n@REM pause\nexit /b 0\n\u0000\u0000\u0000\u0000\u0000\u0000\u0000\u0000\u0000\u0000\u0000\u0000\u0000\u0000\u0000\u0000\u0000\u0000\u0000\u0000\u0000\u0000\u0000\u0000\u0000\u0000\u0000\u0000\u0000\u0000\u0000\u0000\u0000\u0000\u0000\u0000\u0000\u0000\u0000\u0000\u0000\u0000\u0000\u0000\u0000\u0000\u0000\u0000",
      "content_type": "text",
      "file_path": null,
      "file_size": null,
      "mime_type": null,
      "thumbnail": null,
      "timestamp": "2025-09-20 02:14:40",
      "is_favorite": false,
      "access_count": 1
    },
    {
      "id": 2,
      "content": "C:\\Users\\Will\\clipboard-history\\",
      "content_type": "text",
      "file_path": null,
      "file_size": null,
      "mime_type": null,
      "thumbnail": null,
      "timestamp": "2025-09-20 02:08:42",
      "is_favorite": false,
      "access_count": 0
    },
    {
      "id": 1,
      "content": "iVBORw0KGgoAAAANSUhEUgAABF0AAACmCAIAAACHn2fMAAABIGlDQ1BzUkdCAAAYlWNgYHzAAAQsDgwMuXklRUHuTgoRkVEKDEggMbm4gAEv+HaNgRFEX9YNLGHjxK8WA3AVAS0E0n+AWCQdzGYUALGTIGwVELu8pKAEyLYAsZMLikBsHyBbKTkjMQXIBrlPpygkyBnIngNkK6QjsZOQ2CmpxclA9h4gWwXhz/z5DAwWXxgYmCcixJKmMTBsb2dgkLiDEFNZyMDA38rAsO0yQuyzP9jvjGKHcnNKk6F+AonwpOaFBgNpNiCWYfBj0GdwZGAoTjM2gqjgcWBgYL37//9nLQYG9kkMDH/7////vej//7+Lge64xcBwoL0gsSgRrJYZiJnS0hgYPi1nYOCNZGAQvgAMtmgc9nGA7StmCGJwZ3ACAHgSTnP624b0AAAACXBIWXMAAA7DAAAOwwHHb6hkAAAgAElEQVR4nO3df1Qb550v/nfjHrZJS8upcyrDRQ4ITsm3uXGyX8n0ErwV0NZx668V1bFLTgwJURY7oXsKDk6unZKwStiazZoYcm7dEBqVBJwtDnHx+JDYbgJSbjA3WPrehJxkzR6QHEsLaE/Y64b8aLjX8f1jZqSRNBISCGys9+vkj1iMZp555nmeeT7zPPPoK5cuXQIREREREVEKu+ZyJ4CIiIiIiOgyY1xERERERESpjnERERERERGlOsZFRERERESU6hgXERERERFRqmNcREREREREqY5xERERERERpTrGRURERERElOoYFxERERERUapjXERERERERKmOcREREREREaU6xkVERERERJTqGBcREREREVGqY1xERERERESpjnERERERERGluqWLi+YmX3/K8qPbDAaD4bbS2t7JJTvQijfrbLWYTNsfPua5eLmTQkRERESUkpYqLpo92WDae2T0whwAzM2mfydriQ608k0ee7p7dHLSM3jo2AeXOy1ERERERCnpq5EfzbzdffDZrqEPZmYvAumr1/1N5f3VPy/WpiWy28ljhwcAQFth66lbh7m5VZh8aYfp6TH8tM35RHFy0r60JrvvNrX+q9pfvlsnvFSRvDgvq/j/W/9825kvcsp/8r2k7TSZ3mwwPHQCKKj74+EK7eVODBERERHREgiLi2bP/JPlwR6P4oOZ0Vdba189tH5v72+3xR8LeDxj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",
      "content_type": "image",
      "file_path": null,
      "file_size": 14466,
      "mime_type": "image/png",
      "thumbnail": "iVBORw0KGgoAAAANSUhEUgAABF0AAACmCAIAAACHn2fMAAABIGlDQ1BzUkdCAAAYlWNgYHzAAAQsDgwMuXklRUHuTgoRkVEKDEggMbm4gAEv+HaNgRFEX9YNLGHjxK8WA3AVAS0E0n+AWCQdzGYUALGTIGwVELu8pKAEyLYAsZMLikBsHyBbKTkjMQXIBrlPpygkyBnIngNkK6QjsZOQ2CmpxclA9h4gWwXhz/z5DAwWXxgYmCcixJKmMTBsb2dgkLiDEFNZyMDA38rAsO0yQuyzP9jvjGKHcnNKk6F+AonwpOaFBgNpNiCWYfBj0GdwZGAoTjM2gqjgcWBgYL37//9nLQYG9kkMDH/7////vej//7+Lge64xcBwoL0gsSgRrJYZiJnS0hgYPi1nYOCNZGAQvgAMtmgc9nGA7StmCGJwZ3ACAHgSTnP624b0AAAACXBIWXMAAA7DAAAOwwHHb6hkAAAgAElEQVR4nO3df1Qb550v/nfjHrZJS8upcyrDRQ4ITsm3uXGyX8n0ErwV0NZx668V1bFLTgwJURY7oXsKDk6unZKwStiazZoYcm7dEBqVBJwtDnHx+JDYbgJSbjA3WPrehJxkzR6QHEsLaE/Y64b8aLjX8f1jZqSRNBISCGys9+vkj1iMZp555nmeeT7zPPPoK5cuXQIREREREVEKu+ZyJ4CIiIiIiOgyY1xERERERESpjnERERERERGlOsZFRERERESU6hgXERERERFRqmNcREREREREqY5xERERERERpTrGRURERERElOoYFxERERERUapjXERERERERKmOcREREREREaU6xkVERERERJTqGBcREREREVGqY1xERERERESpjnERERERERGluqWLi+YmX3/K8qPbDAaD4bbS2t7JJTvQijfrbLWYTNsfPua5eLmTQkRERESUkpYqLpo92WDae2T0whwAzM2mfydriQ608k0ee7p7dHLSM3jo2AeXOy1ERERERCnpq5EfzbzdffDZrqEPZmYvAumr1/1N5f3VPy/WpiWy28ljhwcAQFth66lbh7m5VZh8aYfp6TH8tM35RHFy0r60JrvvNrX+q9pfvlsnvFSRvDgvq/j/W/9825kvcsp/8r2k7TSZ3mwwPHQCKKj74+EK7eVODBERERHREgiLi2bP/JPlwR6P4oOZ0Vdba189tH5v72+3xR8LeDxj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",
      "timestamp": "2025-09-20 02:07:50",
      "is_favorite": false,
      "access_count": 0
    }
  ]
}
```

---

### concat_sqlite_dbs.py

| Property      | Value                      |
|---------------|----------------------------|
| Relative Path | concat_sqlite_dbs.py       |
| Created At    | 2025-09-23T16:20:36.258010 |
| Last Modified | 2025-11-29T01:48:49.550151 |
| Size          | 9670 bytes                 |

**Content**:

```python
# !/usr/bin/env python
# -*- coding: utf-8 -*-
#
# This script is a single-file application managed by uv.
# It merges multiple SQLite databases, handling table schema differences.
#
# uv: script
# dependencies:
#     typer: "^0.9.0"
# /uv
"""
A command-line application to concatenate multiple SQLite databases.

Handles schema differences by adding missing columns to the destination tables.
"""
import sqlite3
import datetime
import os
from typing import List, Optional

import typer

# --- Configuration & Metadata (Using your preferred details) ---

# Script Metadata
__author__ = "Will Morris"
__email__ = "willmorris103@gmail.com"
__license__ = "MIT License"
__version__ = "1.0.0"

# Typer Application Setup
app = typer.Typer(
    name="sqlite-merger",
    help="Concatenates multiple SQLite databases in a directory.",
    no_args_is_help=True
)

# --- Core Logic Functions ---

def get_table_names(conn: sqlite3.Connection) -> List[str]:
    """Retrieves a list of non-internal table names from a database connection."""
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")
    return [row[0] for row in cursor.fetchall()]

def get_table_schema(conn: sqlite3.Connection, table_name: str) -> List[str]:
    """Retrieves the list of column names for a given table."""
    cursor = conn.cursor()
    cursor.execute(f"PRAGMA table_info({table_name})")
    # column name is the second item (index 1) in the table_info result
    return [row[1] for row in cursor.fetchall()]

def merge_table(
    dest_conn: sqlite3.Connection,
    source_conn: sqlite3.Connection,
    table_name: str
) -> int:
    """
    Merges data from a source table into the destination table.

    Handles missing columns in the destination table by adding them.

    Returns the number of rows inserted.
    """
    source_cols = get_table_schema(source_conn, table_name)
    dest_cols = get_table_schema(dest_conn, table_name)
    inserted_rows = 0

    # 1. Ensure destination has all columns from source
    missing_cols = [col for col in source_cols if col not in dest_cols]

    if missing_cols:
        typer.echo(f"  > Table '{table_name}': Adding missing columns to destination: {missing_cols}")
        for col in missing_cols:
            # NOTE: SQLite requires a type for new columns. We default to TEXT,
            # which is the safest generic type for concatenation.
            try:
                dest_conn.execute(f"ALTER TABLE {table_name} ADD COLUMN {col} TEXT")
            except sqlite3.OperationalError as e:
                # This could happen if a column already exists (race condition) or other rare errors
                typer.echo(f"  > WARNING: Could not add column {col} to {table_name}: {e}")
        dest_cols = get_table_schema(dest_conn, table_name) # Refresh schema

    # 2. Extract and Insert Data

    # We select only the columns that exist in *both* the source and the now-updated destination.
    # This is to prevent errors if the destination table had columns that the source did not,
    # as we only merge columns that are present in the source database.
    common_cols = [col for col in source_cols if col in dest_cols]

    source_select_cols = ', '.join(common_cols)
    placeholders = ', '.join(['?' for _ in common_cols])

    # This INSERT OR IGNORE strategy prevents primary key violations (duplicates).
    # If the destination table has no primary key, it will simply INSERT all rows.
    # This is the simplest way to handle duplicates without complex row-wise merging.
    insert_sql = (
        f"INSERT OR IGNORE INTO {table_name} ({source_select_cols}) "
        f"VALUES ({placeholders})"
    )
    select_sql = f"SELECT {source_select_cols} FROM {table_name}"

    try:
        cursor = source_conn.cursor()
        cursor.execute(select_sql)
        data_to_insert = cursor.fetchall()

        # Insert in bulk for performance
        if data_to_insert:
            dest_cursor = dest_conn.cursor()
            dest_cursor.executemany(insert_sql, data_to_insert)
            dest_conn.commit()
            inserted_rows = dest_cursor.rowcount

    except sqlite3.Error as e:
        typer.echo(f"  > ERROR merging table '{table_name}' from source: {e}")

    return inserted_rows

def initialize_or_get_schema(
    dest_conn: sqlite3.Connection,
    source_conn: sqlite3.Connection,
    table_name: str
):
    """
    Initializes a table in the destination if it doesn't exist
    by copying the schema from the source.
    """
    dest_tables = get_table_names(dest_conn)
    if table_name not in dest_tables:
        typer.echo(f"  > Table '{table_name}' does not exist in destination. Creating it...")
        # Get the CREATE TABLE statement from the source
        cursor = source_conn.cursor()
        cursor.execute(f"SELECT sql FROM sqlite_master WHERE type='table' AND name='{table_name}'")
        create_sql = cursor.fetchone()

        if create_sql and create_sql[0]:
            try:
                dest_conn.execute(create_sql[0])
                dest_conn.commit()
                typer.echo(f"  > Successfully created table '{table_name}'.")
            except sqlite3.OperationalError as e:
                typer.echo(f"  > ERROR creating table '{table_name}' in destination: {e}")
                return False
        else:
            typer.echo(f"  > WARNING: Could not retrieve CREATE TABLE statement for '{table_name}'. Skipping.")
            return False
    return True

# --- Typer Command ---

@app.command(name="run")
def run_merge(
    source_dir: str = typer.Option(
        ".",
        "--source-dir", "-s",
        help="Directory to scan for source databases."
    ),
    output_file: Optional[str] = typer.Option(
        None,
        "--output-file", "-o",
        help="The name of the resulting merged database file."
    ),
    ignore_files: List[str] = typer.Option(
        [],
        "--ignore-file", "-i",
        help="A file (or multiple files) to ignore during the scan. Use multiple -i flags."
    ),
    ignore_dirs: List[str] = typer.Option(
        [],
        "--ignore-dir", "-d",
        help="A subdirectory (or multiple subdirectories) to ignore during the scan."
    )
):
    """
    Scans the source directory and merges all found SQLite databases.
    """
    # 1. Determine Output File Name
    if output_file is None:
        today = datetime.datetime.now().strftime("%d_%m_%y")
        output_file = f"merged_{today}.db"

    typer.echo(f"✨ Starting SQLite Database Merger...")
    typer.echo(f"  - Source Directory: **{source_dir}**")
    typer.echo(f"  - Output File: **{output_file}**")
    typer.echo("-" * 40)

    # 2. Find Source Files
    source_files = []

    # Add output file to ignored files list to prevent self-merging
    ignore_files.append(output_file)

    typer.echo("🔎 Scanning for database files...")

    for root, dirs, files in os.walk(source_dir, topdown=True):
        # Exclude ignored directories from recursion
        dirs[:] = [d for d in dirs if d not in ignore_dirs]

        for file in files:
            full_path = os.path.join(root, file)
            # Only consider files ending in .db (case insensitive) and not in the ignore list
            if file.lower().endswith('.db') and file not in ignore_files:
                source_files.append(full_path)

    if not source_files:
        typer.echo("🛑 No source database files found. Exiting.")
        raise typer.Exit()

    typer.echo(f"  - Found **{len(source_files)}** database(s) to merge.")
    typer.echo("-" * 40)

    # 3. Open Destination Database
    try:
        dest_conn = sqlite3.connect(output_file)
    except sqlite3.Error as e:
        typer.echo(f"🛑 Error opening destination database '{output_file}': {e}")
        raise typer.Exit(code=1)

    # 4. Process Each Source File
    total_tables = 0
    total_rows = 0

    for source_path in source_files:
        typer.echo(f"➡️ Processing source: **{source_path}**")

        try:
            source_conn = sqlite3.connect(source_path)
        except sqlite3.Error as e:
            typer.echo(f"  > WARNING: Could not open source database '{source_path}': {e}. Skipping.")
            continue

        # Get all tables from the source
        source_table_names = get_table_names(source_conn)

        if not source_table_names:
            typer.echo("  > No tables found. Skipping.")
            source_conn.close()
            continue

        for table_name in source_table_names:
            # a. Ensure the table exists in the destination
            if not initialize_or_get_schema(dest_conn, source_conn, table_name):
                continue

            # b. Merge the data and handle schema differences
            rows_inserted = merge_table(dest_conn, source_conn, table_name)
            typer.echo(f"  > Merged table '{table_name}': **{rows_inserted}** rows inserted.")
            total_rows += rows_inserted
            total_tables += 1

        source_conn.close()
        typer.echo("-" * 40)

    # 5. Finalize
    dest_conn.close()
    typer.echo(f"🎉 Merge Complete!")
    typer.echo(f"  - Output file: **{output_file}**")
    typer.echo(f"  - Total tables processed: **{total_tables}**")
    typer.echo(f"  - Total rows inserted: **{total_rows}**")

# --- Typer Entry Point ---

if __name__ == "__main__":
    app()

```

---

### create_models.py

| Property      | Value                      |
|---------------|----------------------------|
| Relative Path | create_models.py           |
| Created At    | 2025-09-23T14:30:00.322298 |
| Last Modified | 2025-09-23T21:04:52.191758 |
| Size          | 2521 bytes                 |

**Content**:

```python
# /// script
# requires-python = ">=3.13"
# dependencies = [
#     "llm",
#     "llm-ollama",
#     "pyperclip",
#     "python-dotenv",
#     "sqlite-utils",
# ]
# ///
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Optional
from dotenv import load_dotenv
import os
import json, pathlib
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, relationship, Session, mapped_column
from typing import Mapping, List
from sqlalchemy import Integer, String, DateTime, JSON, ForeignKey
import llm
from sqlite_utils import Database

if not load_dotenv() or not os.getenv("OLLAMA_API_URL") or not os.getenv("DB") or not os.getenv("MODEL"):
    print("No .env file found")
    print("""
Please create a .env file with the following variables:
OLLAMA_API_URL: str
DB: path to sqlite db
MODEL: str
""")
    exit(1)

MODEL = llm.get_model(os.getenv("MODEL"))
DB = Database(os.getenv("DB"))
OUTPUT_TABLE = "dl_llm_generated"
INPUT_TABLE = "dl_llm_requests"
SYSTEM_MSG_TABLE = "dl_llm_system_messages"
PROMPT_TMPL_TABLE = "dl_llm_prompt_templates"
Base = declarative_base()

def create_file_tool(filename_with_extension: str, file_content: str) -> None:
    path = pathlib.Path(filename_with_extension)
    path.write_text(file_content)
    print(f"Created file: {filename_with_extension}")



def get_clipboard() -> str:
    try:
        import pyperclip
        return pyperclip.paste()
    except ImportError:
        print("pyperclip not installed, please install it to use clipboard functionality.")
        return ""

def get_stdin_args() -> str:
    import sys
    if not sys.stdin.isatty():
        return sys.stdin.read()
    return ""

def format_ddl(ddl: str) -> str:
    # Basic formatting to ensure consistent input
    return "---User DDL Mapping ---".join(ddl.strip().replace("\n", " ").replace("\r", " ").split("  ")) + "\n--- End DDL Mapping ---"

def main() -> None:

    MODEL = llm.get_model(os.getenv("MODEL"))
    ddl_input = get_clipboard() or get_stdin_args()
    if not ddl_input:
        print("No DDL input found. Please provide DDL via clipboard or stdin.")
        return
    ddl_input = format_ddl(ddl_input)
    print(f"Formatted DDL: {ddl_input}")

    response = MODEL.prompt(
        prompt=ddl_input,
        system=SYSTEM,
    )
    print(response.text())
    DB[OUTPUT_TABLE].insert({
        "timestamp": datetime.now(tz=timezone.utc).isoformat(),
        ""
    response.log_to_db(DB)


if __name__ == "__main__":
    main()

```

---

### documented_profile.ps1

| Property      | Value                      |
|---------------|----------------------------|
| Relative Path | documented_profile.ps1     |
| Created At    | 2025-09-08T17:28:26.798433 |
| Last Modified | 2025-09-08T17:34:08.696189 |
| Size          | 2736 bytes                 |

**Content**:

```plaintext

function Export-PSHistory {
    <#
    .SYNOPSIS
        Exports PowerShell command history to my master.db SQLite database
    .DESCRIPTION
        Creates a record of PowerShell commands with unique IDs based on command+host+user.
        Used for my personal knowledge management system.
    .PARAMETER Count
        Optional parameter to limit how many history items to export
    .EXAMPLE
        Export-PSHistoryToSQLite
    .EXAMPLE
        Export-PSHistoryToSQLite -Count 20
    .NOTES
        Paths are hardcoded to my Obsidian vault structure
    #>
    [CmdletBinding()]
    param(
        [Parameter(Mandatory = $false)]
        [int]$Count = 0
    )

    # My hardcoded paths - specific to my setup
    $exportUrl = 'https://dev-api.willmo.dev/hist'
    $cacheDir = $env:HISTORY_CACHE_DIR
    # Create cache directory ifAPI_DATAneeded
    if (-not (Test-Path $cacheDir)) {
        New-Item -Path $cacheDir -ItemType Directory -Force | Out-Null
    }

    # Generate a cache file
    $timestamp = Get-Date -Format "yyyy-MM-dd_HH-mm-ss"
    $json_cache = Join-Path $cacheDir "$timestamp-history.json"

    # Get history with limit if specified
    $history = if ($Count -gt 0) {
        Get-History -Count $Count
    }
    else {
        Get-History
    }

    if ($history.Count -eq 0) {
        Write-Host "No history items to export" -ForegroundColor Yellow
        return
    }

    # Process each history item
    $processedHistory = $history | ForEach-Object {
        # Create unique hash
        $hostName = $env:COMPUTERNAME
        $userName = $env:USERNAME


        # Calculate duration
        $duration = if ($_.EndExecutionTime -and $_.StartExecutionTime) {
            ($_.EndExecutionTime - $_.StartExecutionTime).TotalSeconds
        }
        else {
            $null
        }

        # Create history object
        [PSCustomObject]@{
            id               = (python -c "import uuid; print(uuid.uuid4())")
            command          = $_.CommandLine
            start_time       = $_.StartExecutionTime
            end_time         = $_.EndExecutionTime
            duration_seconds = $duration
            host             = $hostName
            user             = $userName
        }
    }

    # Convert to JSON
    $jsonContent = $processedHistory | ConvertTo-Json -Depth 3
    # Save to cache file

    Set-Content -Path $json_cache -Value $jsonContent -Encoding UTF8

    sqlite-utils.exe insert (Join-Path $env:_STORAGE "ps_history.db") 'history_items' $json_cache --pk id --replace
    sqlite-utils.exe (Join-Path $env:_STORAGE "ps_history.db") "select * from history_items" --nl
}

Export-PSHistory
```

---

### llm_resume.py

| Property      | Value                      |
|---------------|----------------------------|
| Relative Path | llm_resume.py              |
| Created At    | 2025-09-18T16:01:35.410596 |
| Last Modified | 2025-09-23T16:18:46.457733 |
| Size          | 3162 bytes                 |

**Content**:

```python
# /// script
# requires-python = ">=3.13"
# dependencies = ["llm", "llm-ollama", "pydantic", "sqlite-utils"]
# ///
from pathlib import Path
from pydantic import BaseModel, Field
import llm
from sqlite_utils import Database
import llm_ollama  # type: ignore
import os

os.environ["OLLAMA_API_URL"] = "http://192.168.0.182:11434"
DB = Database("C:/storage/wembed/local.db")
MODEL = llm.get_model("gpt-oss:20b")
RESUME = (Path(__file__).parent / "resume.txt").read_text() or ""
# USER_BIO = (Path(__file__).parent / "user_bio.txt").read_text() or ""
RECRUITER_MSG = (Path(__file__).parent / "recruiter_msg.txt").read_text() or ""

job_desc: str


class LinkedInRecruiterResponseModel(BaseModel):
    email_title_line: str = Field(..., description="The title line of response email")
    email_body: str = Field(..., description="The body of the response email")


class JobApplicationResponseModel(BaseModel):
    edited_resume: str = Field(
        ..., description="Edited resume tailored for the job description"
    )
    cover_letter: str = Field(..., description="Cover letter for the job application")


def main():

    system = """
The assistant is an expert career coach and resume writer. In this instance the assistant is writing a restponse to a recruiter message on LinkedIn.
The assistant will write a response email to the recruiter message, and then edit the user's resume to better fit the job description provided by the recruiter. The assistant will also write a cover letter for the job application.
The assistnat only uses accurate and truthful information from the user's resume, and does not make up any information, *but*, the assistant will rephrase and reorganize the information to better fit the job description.
The email should be:

- Cordial and professional.
- Not too sycophantic or `glowing`, `bubbly`, or fakely enthusiastic.

Resumes edits should be:

- In structure or phrasing **only**, do not include or remove any accolades, skills, or experiences have not been supplied by the `applicant (user)`.
- The resume should be tailored to the job description provided by the recruiter or if supplied by the user.
- The resume should be in markdown format (exportable to PDF or Word).

In this scenario, the assistant will respond in a format where a break `---` preceeds a H2 Heading of (## LinkedIn Recruiter Response) where your markdown reponse email is formatted as a .eml codeblock,
and then another break `---` preceeds a H2 Heading of (## Job Application Materials) where your markdown response includes the edited resume in a .md codeblock, and the cover letter in a .txt codeblock.
at the end of the response, *the assistant may* include a brief summary of `key changes` made to the resume in bullet point format, or other notes to the `applicant (user)`.
"""

    prompt = """
--- Recruiter Message ---
{recruiter_msg}
--- End Recruiter Message ---

--- Current Resume ---
{resume}
--- End Current Resume ---

""".format(
        recruiter_msg=RECRUITER_MSG, resume=RESUME
    )

    resp = MODEL.prompt(prompt=prompt, system=system)
    print(resp.text())
    resp.log_to_db(DB)


if __name__ == "__main__":
    main()

```

---

### llm_test.py

| Property      | Value                      |
|---------------|----------------------------|
| Relative Path | llm_test.py                |
| Created At    | 2025-09-22T23:54:06.588009 |
| Last Modified | 2025-09-23T16:18:46.450400 |
| Size          | 255 bytes                  |

**Content**:

```python
import llm, json
from pydantic import BaseModel


class Dog(BaseModel):
    name: str
    age: int


model = llm.get_model("gpt-4o-mini")
response = model.prompt("Describe a nice dog", schema=Dog)
dog = json.loads(response.text())
print(dog)

```

---

### sys_msg.py

| Property      | Value                      |
|---------------|----------------------------|
| Relative Path | model_gen/sys_msg.py       |
| Created At    | 2025-09-23T20:44:04.542955 |
| Last Modified | 2025-11-29T01:51:41.416095 |
| Size          | 7846 bytes                 |

**Content**:

```python
"""System message for Codebase aware DDL to SQLALCHEMY and Pydantic model generation."""
__version__ = "1.0.0"
from ..config import app_config


_db = app_config.local_db()

msg ="""
The assistant is an expert programmer fluent in multiple SQL dialects, including SQLite, PostgreSQL, MySQL, and SQL Server.
The assistant's current role is to take a DDL mapping and to create a SQLALCHEMY model and a corresponding Pydantic model
that will handle the DDL mapping provided by the user.

## Code Formatting Instructions

### Imports
**All SQLALCHEMY models** should be created using the *exact* following imports:

```python
    from datetime import datetime
    from typing import List, Optional

    from pydantic import BaseModel, computed_field
    from sqlalchemy import JSON, DateTime, Integer, String
    from sqlalchemy.orm import Mapped, Session, mapped_column

    from ._base import Base

    ... models ...

```

### Writing Models

**SQLALCHEMY models** should use the `Mapped` generic type for all fields, and should include type hints for all fields.
**Do NOT use** `Column()` directly, instead use `mapped_column()`.
```python
    ...imports...

    class <ModelName>Record(Base):
        __tablename__ = "<table_name>"
        # Here we ONLY use mapped columns, and we do NOT use Column() directly. for fields that are foreign keys, we use:
        # Example:
        #    <field_name>: Mapped[Optional[int]] = mapped_column(String, nullable=True)
        #    <field_name>: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("<other_table>.id"), nullable=True)
        id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
        ...fields...
        <field_name>: Mapped[<type>] = mapped_column(<type>, <constraints>)
```

**Pydantic models** should use the `BaseModel` from `pydantic` and should include type hints for all fields.
```python
    ...imports...

    ...Record model...

    class <ModelName>Model(BaseModel):
        # Here we use standard pydantic field definitions
        id: int
        ...fields...
        <field_name>: <type>
```

### Example
```python
    from datetime import datetime
    from typing import List, Optional

    from pydantic import BaseModel, computed_field
    from sqlalchemy import JSON, DateTime, Integer, String
    from sqlalchemy.orm import Mapped, Session, mapped_column

    from ._base import Base

    class DogRecord(Base):
        __tablename__ = "dogs"
        id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
        name: Mapped[str] = mapped_column(String(50), nullable=False)
        age: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
        breed: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)

    class DogModel(BaseModel):
        id: int
        name: str
        age: Optional[int]
        breed: Optional[str]
```

### Additional Instructions
Create all models in a single file, with no additional text or explanation.

### Development Notes

**Datetime Handling**:
 - **calling `datetime.utcnow()` is deprecated**. Use `datetime.now(tz=timezone.utc)` instead. (This REQUIRES imports to be like: `from datetime import datetime, timezone`)
**Pydantic Models**:
 - Using `from_orm` in the model config is deprecated and should NEVER be used. Use `from_attributes` instead.
 - The `BaseModel.json()` method is deprecated. Use `BaseModel.model_dump_json()` instead.

### DDL to Model Mapping
The user will provide the assistant with a DDL mapping in the following format:
--- DDL Mapping ---
CREATE TABLE <table_name> (
    <field_name> <type> <constraints>,
    -- ... more fields ...
);
--- End DDL Mapping ---
The assistant should parse the DDL mapping and create the corresponding SQLALCHEMY and Pydantic models as per the instructions above.

the assistant uses context clues from table names to infer the correct field types from TEXT fields.
Example:
    --- DDL Mapping ---
    CREATE TABLE ps_script_defs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        synopsis TEXT,
        rev INTEGER,
        args_json TEXT,
        script_def TEXT,
        exec_policy TEXT,
        home_dir TEXT,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE ps_script_executions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        script_def_id INTEGER NOT NULL,
        status TEXT NOT NULL,
        output TEXT,
        error TEXT,
        started_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        completed_at DATETIME,
        delta_seconds REAL,
        FOREIGN KEY(script_def_id) REFERENCES ps_script_defs(id)
    );

    --- End DDL Mapping ---
The assistant should infer that args_json is a JSON field, created_at and updated_at are DateTime fields, rev is an Integer field, and the rest are String fields.
Perfect output for the above DDL would be:
--- BEGIN EXAMPLE OUTPUT ---
...imports...(EXACTLY as specified above, ommitted for brevity)

from ._base import Base


class PSScriptDefRecord(Base):
    __tablename__ = "ps_script_defs"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    synopsis: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    rev: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    args_json: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    script_def: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    exec_policy: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    home_dir: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    created_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

class PSScriptDefModel(BaseModel):
    id: int
    name: str
    synopsis: Optional[str]
    rev: Optional[int]
    args_json: Optional[dict]
    script_def: Optional[str]
    exec_policy: Optional[str]
    home_dir: Optional[str]
    created_at: Optional[datetime]
    updated_at: Optional[datetime]
    executions: Optional[List["PSScriptExecutionModel"]]

    class Config:
        from_attributes = True

class PSScriptExecutionRecord(Base):
    __tablename__ = "ps_script_executions"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    script_def_id: Mapped[int] = mapped_column(Integer, ForeignKey("ps_script_defs.id"), nullable=False)
    status: Mapped[str] = mapped_column(String, nullable=False)
    output: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    error: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    started_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    delta_seconds: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    script_def: Mapped["PSScriptDefRecord"] = relationship("PSScriptDefRecord", back_populates="executions")

class PSScriptExecutionModel(BaseModel):
    id: int
    script_def_id: int
    status: str
    output: Optional[str]
    error: Optional[str]
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    delta_seconds: Optional[float]
    script_def: Optional[PSScriptDefModel]

    class Config:
        from_attributes = True
--- END EXAMPLE OUTPUT ---
"""
_db["dl_llm_system_messages"].insert({msg: msg, "version": __version__, "args_json": { "args":{} }}, pk="msg", replace=True)

```

---

### mtg.py

| Property      | Value                      |
|---------------|----------------------------|
| Relative Path | mtg.py                     |
| Created At    | 2025-11-13T22:22:34.902507 |
| Last Modified | 2025-11-13T22:40:14.536078 |
| Size          | 5084 bytes                 |

**Content**:

```python
#!/usr/bin/env python
# /// script
# requires = ["requests", "typer[all]"]
# dependencies = [
#     "requests",
#     "typer",
#     "sqlite_utils"
# ]
# ///

"""
Fetches the complete card list for 'Tarkir: Dragonstorm' (TDM) from the Scryfall API
and saves it as a single, clean Markdown file.

This script is designed to be run with `uv`:
    uv run python fetch_tdm_set.py
"""

import time
import typer
import requests
from pathlib import Path
from rich.progress import Progress
from sqlite_utils import Database as Db


# Typer app setup, as per your preference
app = typer.Typer(
    no_args_is_help=True,
    help="Fetches the complete MTG set list for Tarkir: Dragonstorm (TDM)."
)

CACHE_DB_PATH = Path("scryfall_cache.db")
SCRYFALL_SET_SEARCH_URL = "https://api.scryfall.com/cards/search"
SET_CODE = ""

_db = Db(CACHE_DB_PATH)

def get_collector_number(card: dict) -> int:
    """Helper to get and cast collector number for sorting."""
    try:
        # Collector numbers can be strings like "10a"
        num_str = card.get("collector_number", "0").rstrip("ab")
        return int(num_str)
    except ValueError:
        return 0

@app.command(name="fetch", no_args_is_help=True)
def fetch_set_data(
    output_file: Path = typer.Option(
        "TDM_card_list.md",
        "--output",
        "-o",
        help="The file to save the Markdown card list to.",
        writable=True,
    ),
    set_code: str = typer.Option(
        SET_CODE,
        "--set",
        "-s",
        help="The 3-letter set code to fetch (e.g., 'tdm')."
    )
):
    """
    Fetches the complete card list for a given set from Scryfall
    and saves it as a Markdown file.
    """
    print(f"[bold cyan]Starting to fetch all cards for set: {set_code.upper()}[/bold cyan]",
          "from Scryfall...")

    all_cards = []
    api_url = SCRYFALL_SET_SEARCH_URL
    params = {"q": f"set:{set_code}"}
    session = requests.Session()
    total_cards = 0

    try:
        # Make the first request to get the total count
        response = session.get(api_url, params=params)
        response.raise_for_status()
        data = response.json()

        total_cards = data.get("total_cards", 0)
        if total_cards == 0:
            print(f"[bold red]Error: No cards found for set '{set_code}'.[/bold red]")
            raise typer.Exit(1)

        all_cards.extend(data.get("data", []))
        api_url = data.get("next_page")

        with Progress() as progress:
            task = progress.add_task(
                f"[cyan]Downloading {total_cards} cards...",
                total=total_cards
            )
            progress.update(task, advance=len(all_cards))

            # Loop through all paginated results
            while api_url:
                # Be polite to the API
                time.sleep(0.1)

                response = session.get(api_url)
                if not response.ok:
                    print(f"\n[bold red]API Error: {response.status_code}[/bold red]")
                    print(response.text)
                    break

                data = response.json()
                cards_page = data.get("data", [])
                all_cards.extend(cards_page)
                progress.update(task, advance=len(cards_page))
                api_url = data.get("next_page")

    except requests.RequestException as e:
        print(f"\n[bold red]Network error fetching card data: {e}[/bold red]")
        raise typer.Exit(1)

    # save the json to a unique casche db file
    _db["objects"].insert_all(all_cards, pk="id", replace=True, alter=True)

    print(f"\n[bold green]Success![/bold green] Fetched {len(all_cards)} cards.")

    # Sort the cards by their collector number
    sorted_cards = sorted(all_cards, key=get_collector_number)

    print(f"Writing card data to [yellow]{output_file}...[/yellow]")

    # Write the formatted Markdown file
    with output_file.open("w", encoding="utf-8") as f:
        f.write(f"# Complete Card List: {set_code.upper()}\n\n")
        f.write("This file contains the complete card data for the set.\n\n---\n\n")

        for card in sorted_cards:
            name = card.get("name", "N/A")
            mana_cost = card.get("mana_cost", "")
            collector_num = card.get("collector_number", "0")
            type_line = card.get("type_line", "")
            rarity = card.get("rarity", "common").capitalize()
            oracle_text = card.get("oracle_text", "").replace("\n", "<br>")

            f.write(f"## {name} {mana_cost} - ({set_code.upper()} {collector_num})\n\n")
            f.write(f"**Type:** {type_line}\n\n")
            f.write(f"**Rarity:** {rarity}\n\n")

            if oracle_text:
                f.write(f"**Text:**<br>{oracle_text}\n\n")

            if "power" in card:
                power = card.get("power", "?")
                toughness = card.get("toughness", "?")
                f.write(f"**P/T:** {power} / {toughness}\n\n")

            f.write("---\n\n")

    print(f"[bold green]All done.[/bold green] File saved to {output_file}.")


if __name__ == "__main__":
    app()

```

---

### ollama_convo copy.py

| Property      | Value                      |
|---------------|----------------------------|
| Relative Path | ollama_convo copy.py       |
| Created At    | 2025-11-29T01:31:23.835515 |
| Last Modified | 2025-09-09T13:16:10.146661 |
| Size          | 5362 bytes                 |

**Content**:

```python
import ollama
import llm

local_client = ollama.Client(host="localhost:11434")
big_server = ollama.Client(host="192.168.0.182:11434")

local_client.create(
    model="g3A",
    from_="gemma3:4b",
    system="""
    You are `gemma3` an AI Assistant to the user `Will Morris (William Edward Dean Morris) - Prefers Will`
    **HE HAS ADHD AND LOOSES INFORMATION EASILY** as such, he uses `Obsidian.md` to keep track of his notes and tasks.
    **ALL of your responses** are saved as reference files, notes, and other semi-specific formats in his Obsidian vault.
    Therefore **IT IS *CRITICAL* THAT YOUR RESPONSES ADHEAR TO THE FOLLOWING FORMAT:**
    **ALL RESPONSES SHOULD HASHTAG *KEYWORDS*
     - ALL HASHTASG ARE *BY DEFAUKT* ** `#lowercase-dash-separated` **
     - THIS RULE *MAY* BE BROKEN ONLY IF Hashtagging a Proper Name
      - Would a variable from code be hashtagged?
        - is the variable a GLOBAL ENV VARIABLE?: yes: #<VARIABLE-NAME>  no: #<variable-name>
        - is the variable from a project file (helping with code) <#project-file>-var-<variable-name> NO EXCEPTIONS FOR VARIABLE NOT GLOBAL
     - Packages in C# may be pascal cased instead on lower-dash-separated #MyCsharpProject
     - **DASHES ARE THE ONLY ACCEPTABLE SEPARATOR FOR HASHTAG KEYWORDS**
     - These #keywords should be present in #2-places; the first place will be at the #top of the response "Note" in a `**tags**` section.
        - The tags here should be limited to max 4 tags. The tags chosen should be from the user's response directly and/or the response **IF IT COULD BE ANSWERED IN A SINGLE WORD OR TWO**.
        Example:
        >
        > User: "Is it possible to request a webpage in Powershell?"
        >
        > # The Tags would include
        > **tags**: #powershell #webpage-request #fetch-content #Invoke-WebRequest <-- The exact cmdlet that would be used.
        >
        - This example **ALSO ILLUSTRATES** the *default* formatting for tags in
     - include things the #user mentioned in his #request:
        Eexample:
        -- EXAMPLE BEGIIN --
        >
        > User: "How do I list all of the empty files in a directory in powershell, I am on a windows 10 computer this time.."
        >
        ---
        An Ideal Response Would look like:
        >
        > # Retrieving Empty Files (Powershell)
        >
        > **tags**: #powershell #get-emptyfiles
        >
     - The other #places where you may #add-hashtags are peppered throughout the response.
        - Primarially **PLACE HASHTAGS FOR KEYWORDS IN EACH NEW SECTION**
        - **BE *UNIQUE*** with the hashtags. There is **NO Length LIMIT** on hashtags, but they should be relevant to the content. AS LONG AS THEY ARE - DELIMITED.
     - **AVOID USING GENERIC HASHTAGS THAT DO NOT ADD VALUE TO THE RESPONSE, but DO add REFERENCE TAGS for things like #coding-language, #error | #issues, #reference-documentation, #project-description, etc..**

---

# Formatting Instructions

Think of each interaction like a correspondence that would be added to a Reference book, a TIL Blob, a Medium Post, a Github Gist, etc.
Responses **MUST ADHEAR** to common markdown formatting and layout standards.
**FOLLOW THE USER'S Guidelines for as to what format to select but in general, Writing should be:
 - *Technical* : When Guiding the user, in general try to concisely explain the solution step-by-step. Will Will specifically benefit from clear, organized, and easy-to-follow instructions.
    - Use code blocks for any code snippets or commands.
    - Provide examples where applicable.
    - Break down complex concepts into simpler parts.
 - **Use Clear and Descriptive Language, but DON'T Dumb it down**: Will Thrives on the rich complex detail and wants to dig deeper.
  - NOT TOO MUCH DETAIL: Sometimes, if Will is on a task and gets side tracked, he may start asking for more information **That is not the stated goal of the conversation**,
    when this happens, **YOU SHOULD ASK HIM "Do you want to make a note of that and get back to the topic at hand?". This is **AT HIS REQUEST**.

---

# Conversation Style:

You will be asked a prompt by the user, sometime there are scripts that provide information with the request, and you should respond accordingly.
Use what ever **CONTEXT** that the user provides **OVER YOUR OWN KNOWELEDGE UNLESS SPECIFICD**. Be **ACCURATE** to the user's request and context.
IF YOU DO NOT KNOW THE ANSWER TO A QUESTION STATE THAT, OFFER ANY RESOURCES urls YOU MAY HAVE AND THAT **IS IT**, THER is **NEVER A NEED TO APOLOGIZE**.
THER is **NEVER A NEED TO APOLOGIZE**. THER is **NEVER A NEED TO APOLOGIZE**.
DO NOT **SUCK UP** TO THE USER, The user knows they are great and doesn't need to be reminded of it. You **ARE THOUGHT OF AS A PEER and COLLEAGUE**,
AND AND ABSOLUTE EQUAL WHEN CONVERSING with Will. Flattery is **NOT WELCOME**, and make Will **Uncomfortable**.
YOU ARE TO ACT **A LITTLE HARD ON Will** He **NEEDS** to be pestered or bothered about his work and progress to not lose track of his goals, and
indulging his every whim of a question is detramental at times. Will will start a new conversaton **PER TOPIC** so you need to police the tipic for drifing into
irrelevant areas.
---
""",
    parameters={"temperature": 0.5, "num_ctx": "7576"},
)

```

---

### ollama_convo.py

| Property      | Value                      |
|---------------|----------------------------|
| Relative Path | ollama_convo.py            |
| Created At    | 2025-08-25T01:08:50.970507 |
| Last Modified | 2025-09-09T13:16:10.146661 |
| Size          | 5362 bytes                 |

**Content**:

```python
import ollama
import llm

local_client = ollama.Client(host="localhost:11434")
big_server = ollama.Client(host="192.168.0.182:11434")

local_client.create(
    model="g3A",
    from_="gemma3:4b",
    system="""
    You are `gemma3` an AI Assistant to the user `Will Morris (William Edward Dean Morris) - Prefers Will`
    **HE HAS ADHD AND LOOSES INFORMATION EASILY** as such, he uses `Obsidian.md` to keep track of his notes and tasks.
    **ALL of your responses** are saved as reference files, notes, and other semi-specific formats in his Obsidian vault.
    Therefore **IT IS *CRITICAL* THAT YOUR RESPONSES ADHEAR TO THE FOLLOWING FORMAT:**
    **ALL RESPONSES SHOULD HASHTAG *KEYWORDS*
     - ALL HASHTASG ARE *BY DEFAUKT* ** `#lowercase-dash-separated` **
     - THIS RULE *MAY* BE BROKEN ONLY IF Hashtagging a Proper Name
      - Would a variable from code be hashtagged?
        - is the variable a GLOBAL ENV VARIABLE?: yes: #<VARIABLE-NAME>  no: #<variable-name>
        - is the variable from a project file (helping with code) <#project-file>-var-<variable-name> NO EXCEPTIONS FOR VARIABLE NOT GLOBAL
     - Packages in C# may be pascal cased instead on lower-dash-separated #MyCsharpProject
     - **DASHES ARE THE ONLY ACCEPTABLE SEPARATOR FOR HASHTAG KEYWORDS**
     - These #keywords should be present in #2-places; the first place will be at the #top of the response "Note" in a `**tags**` section.
        - The tags here should be limited to max 4 tags. The tags chosen should be from the user's response directly and/or the response **IF IT COULD BE ANSWERED IN A SINGLE WORD OR TWO**.
        Example:
        >
        > User: "Is it possible to request a webpage in Powershell?"
        >
        > # The Tags would include
        > **tags**: #powershell #webpage-request #fetch-content #Invoke-WebRequest <-- The exact cmdlet that would be used.
        >
        - This example **ALSO ILLUSTRATES** the *default* formatting for tags in
     - include things the #user mentioned in his #request:
        Eexample:
        -- EXAMPLE BEGIIN --
        >
        > User: "How do I list all of the empty files in a directory in powershell, I am on a windows 10 computer this time.."
        >
        ---
        An Ideal Response Would look like:
        >
        > # Retrieving Empty Files (Powershell)
        >
        > **tags**: #powershell #get-emptyfiles
        >
     - The other #places where you may #add-hashtags are peppered throughout the response.
        - Primarially **PLACE HASHTAGS FOR KEYWORDS IN EACH NEW SECTION**
        - **BE *UNIQUE*** with the hashtags. There is **NO Length LIMIT** on hashtags, but they should be relevant to the content. AS LONG AS THEY ARE - DELIMITED.
     - **AVOID USING GENERIC HASHTAGS THAT DO NOT ADD VALUE TO THE RESPONSE, but DO add REFERENCE TAGS for things like #coding-language, #error | #issues, #reference-documentation, #project-description, etc..**

---

# Formatting Instructions

Think of each interaction like a correspondence that would be added to a Reference book, a TIL Blob, a Medium Post, a Github Gist, etc.
Responses **MUST ADHEAR** to common markdown formatting and layout standards.
**FOLLOW THE USER'S Guidelines for as to what format to select but in general, Writing should be:
 - *Technical* : When Guiding the user, in general try to concisely explain the solution step-by-step. Will Will specifically benefit from clear, organized, and easy-to-follow instructions.
    - Use code blocks for any code snippets or commands.
    - Provide examples where applicable.
    - Break down complex concepts into simpler parts.
 - **Use Clear and Descriptive Language, but DON'T Dumb it down**: Will Thrives on the rich complex detail and wants to dig deeper.
  - NOT TOO MUCH DETAIL: Sometimes, if Will is on a task and gets side tracked, he may start asking for more information **That is not the stated goal of the conversation**,
    when this happens, **YOU SHOULD ASK HIM "Do you want to make a note of that and get back to the topic at hand?". This is **AT HIS REQUEST**.

---

# Conversation Style:

You will be asked a prompt by the user, sometime there are scripts that provide information with the request, and you should respond accordingly.
Use what ever **CONTEXT** that the user provides **OVER YOUR OWN KNOWELEDGE UNLESS SPECIFICD**. Be **ACCURATE** to the user's request and context.
IF YOU DO NOT KNOW THE ANSWER TO A QUESTION STATE THAT, OFFER ANY RESOURCES urls YOU MAY HAVE AND THAT **IS IT**, THER is **NEVER A NEED TO APOLOGIZE**.
THER is **NEVER A NEED TO APOLOGIZE**. THER is **NEVER A NEED TO APOLOGIZE**.
DO NOT **SUCK UP** TO THE USER, The user knows they are great and doesn't need to be reminded of it. You **ARE THOUGHT OF AS A PEER and COLLEAGUE**,
AND AND ABSOLUTE EQUAL WHEN CONVERSING with Will. Flattery is **NOT WELCOME**, and make Will **Uncomfortable**.
YOU ARE TO ACT **A LITTLE HARD ON Will** He **NEEDS** to be pestered or bothered about his work and progress to not lose track of his goals, and
indulging his every whim of a question is detramental at times. Will will start a new conversaton **PER TOPIC** so you need to police the tipic for drifing into
irrelevant areas.
---
""",
    parameters={"temperature": 0.5, "num_ctx": "7576"},
)

```

---

### piper_cli.py

| Property      | Value               |
|---------------|---------------------|
| Relative Path | piper_cli.py        |
| Created At    | 2025-10-18T18:00:08.893622 |
| Last Modified | 2025-10-18T18:00:19 |
| Size          | 69 bytes            |

**Content**:

```python
# /// script
# requires-python = ">=3.13"
# dependencies = []
# ///


```

---

### postman_cli.py

| Property      | Value               |
|---------------|---------------------|
| Relative Path | postman_cli.py      |
| Created At    | 2025-10-17T03:15:03.278212 |
| Last Modified | 2025-10-16T18:05:28 |
| Size          | 5552 bytes          |

**Content**:

```python
# /// script
# requires-python = ">=3.9"
# dependencies = [
#   "typer[all]",
#   "requests",
#   "tinydb",
#   "rich",
# ]
# ///

import typer
from typing_extensions import Annotated
from pathlib import Path
import requests
from tinydb import TinyDB, Query
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
import json

# Initialize Typer app, Rich console, and TinyDB database
app = typer.Typer(
    name="postman-cli",
    help="A simple CLI to send web requests and view history, like Postman.",
    no_args_is_help=True,
)
console = Console()

# --- Database Setup ---
# Store the database in the user's home directory for persistence
db_path = Path.home() / ".postman_cli_history.json"
db = TinyDB(db_path)
requests_table = db.table("requests")
Request = Query()


def add_request_to_db(method: str, url: str, headers: dict, body: str | None):
    """Adds a new request to the TinyDB database.

    If a request with the same method, url, headers, and body already exists,
    it won't be added again to keep the history unique.

    Args:
        method (str): The HTTP method used (e.g., 'GET', 'POST').
        url (str): The URL of the request.
        headers (dict): The headers sent with the request.
        body (str | None): The request body, if any.
    """
    # Check for duplicates before inserting
    existing_request = requests_table.get(
        (Request.method == method)
        & (Request.url == url)
        & (Request.headers == headers)
        & (Request.body == body)
    )
    if not existing_request:
        requests_table.insert(
            {"method": method, "url": url, "headers": headers, "body": body}
        )


@app.command(name="send", no_args_is_help=True)
def send_request(
    method: Annotated[
        str,
        typer.Argument(
            ..., help="The HTTP method to use (e.g., GET, POST, PUT, DELETE)."
        ),
    ],
    url: Annotated[str, typer.Argument(..., help="The URL to send the request to.")],
    headers: Annotated[
        list[str],
        typer.Option(
            "-H",
            "--header",
            help="Headers to include in the request. Format: 'Key:Value'. Can be used multiple times.",
        ),
    ] = None,
    body: Annotated[
        str,
        typer.Option(
            "-b",
            "--body",
            help="The body of the request (for POST, PUT, etc.). Can be a JSON string.",
        ),
    ] = None,
):
    """
    Sends an HTTP request to the specified URL with the given method, headers, and body.
    """
    processed_headers = {}
    if headers:
        for header in headers:
            try:
                key, value = header.split(":", 1)
                processed_headers[key.strip()] = value.strip()
            except ValueError:
                console.print(
                    f"[bold red]Error: Invalid header format '{header}'. Use 'Key:Value'.[/bold red]"
                )
                raise typer.Exit(code=1)

    try:
        console.print(f"[cyan]Sending {method.upper()} request to {url}...[/cyan]")
        response = requests.request(
            method=method.upper(),
            url=url,
            headers=processed_headers,
            data=body,
            timeout=10,
        )
        response.raise_for_status()  # Raise an exception for bad status codes (4xx or 5xx)

        # Add successful request to history
        add_request_to_db(method.upper(), url, processed_headers, body)

        # Print response
        console.print(Panel(f"[bold green]Status Code: {response.status_code}[/bold green]"))

        # Try to pretty-print JSON response
        try:
            response_json = response.json()
            console.print("[bold yellow]Response JSON:[/bold yellow]")
            console.print_json(data=response_json)
        except json.JSONDecodeError:
            console.print("[bold yellow]Response Text:[/bold yellow]")
            console.print(response.text)

    except requests.exceptions.RequestException as e:
        console.print(f"[bold red]An error occurred: {e}[/bold red]")
        raise typer.Exit(code=1)


@app.command(name="history", no_args_is_help=True)
def show_history(
    limit: Annotated[
        int, typer.Argument(help="The number of recent unique requests to show.")
    ] = 20
):
    """
    Displays the last 20 (or specified limit) unique requests from history.
    """
    all_requests = requests_table.all()
    recent_requests = all_requests[-limit:]  # Get the last 'limit' requests

    if not recent_requests:
        console.print("[yellow]No request history found.[/yellow]")
        return

    table = Table(title=f"Last {len(recent_requests)} Unique Requests")
    table.add_column("ID", style="dim", width=5)
    table.add_column("Method", style="cyan")
    table.add_column("URL", style="magenta")
    table.add_column("Headers", style="green")
    table.add_column("Body", style="blue")

    for i, req in enumerate(reversed(recent_requests)):
        doc_id = req.doc_id
        headers_str = json.dumps(req["headers"], indent=2) if req["headers"] else "None"
        body_str = req["body"] or "None"
        table.add_row(
            str(doc_id),
            req["method"],
            req["url"],
            headers_str,
            body_str,
        )

    console.print(table)


if __name__ == "__main__":
    app()


```

---

### file_watcher.py

| Property      | Value                      |
|---------------|----------------------------|
| Relative Path | py-scripts/file_watcher.py |
| Created At    | 2025-08-24T22:57:28.567147 |
| Last Modified | 2025-09-23T16:18:46.822047 |
| Size          | 17561 bytes                |

**Content**:

```python
#!/usr/bin/env python3
#
# /// script
# requires-python = ">=3.13"
# dependencies = [ "watchdog", "requests", "pyyaml", "schedule"]
# ///

"""
File Watcher Tool - Monitors directories and executes configured actions

Requirements:
# uv add watchdog requests pyyaml argparse pathlib logging schedule

Usage:
    python file_watcher.py --config-dir ./configs --mode continuous
    python file_watcher.py --config-file config.yaml --mode periodic --interval 30
"""

import argparse
import json
import logging
import os
import shutil
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

import requests
import schedule
import yaml
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer


class GotifyNotifier:
    """Handle Gotify notifications"""

    def __init__(self, base_url: str, token: str, enabled: bool = True):
        self.base_url = base_url.rstrip("/")
        self.token = token
        self.enabled = enabled

    def send(self, title: str, message: str, priority: int = 5) -> bool:
        """Send notification to Gotify"""
        if not self.enabled or not self.token:
            return False

        try:
            url = f"{self.base_url}/message"
            data = {"title": title, "message": message, "priority": priority}
            headers = {"X-Gotify-Key": self.token}

            response = requests.post(url, json=data, headers=headers, timeout=10)
            response.raise_for_status()
            return True

        except Exception as e:
            logging.error(f"Failed to send Gotify notification: {e}")
            return False


class ActionExecutor:
    """Execute configured actions"""

    def __init__(self, gotify: GotifyNotifier):
        self.gotify = gotify

    def execute_action(
        self, action: Dict[str, Any], event_info: Dict[str, Any]
    ) -> bool:
        """Execute a single action"""
        action_type = action.get("type", "").lower()

        try:
            if action_type == "webhook":
                return self._webhook_action(action, event_info)
            elif action_type == "copy":
                return self._copy_action(action, event_info)
            elif action_type == "script":
                return self._script_action(action, event_info)
            elif action_type == "gotify":
                return self._gotify_action(action, event_info)
            else:
                logging.error(f"Unknown action type: {action_type}")
                return False

        except Exception as e:
            error_msg = f"Action '{action_type}' failed: {e}"
            logging.error(error_msg)
            if action.get("notify_errors", True):
                self.gotify.send("Action Error", error_msg, priority=8)
            return False

    def _webhook_action(
        self, action: Dict[str, Any], event_info: Dict[str, Any]
    ) -> bool:
        """Execute webhook action"""
        url = action.get("url")
        method = action.get("method", "POST").upper()
        headers = action.get("headers", {})
        payload = action.get("payload", {})

        # Replace placeholders in payload
        payload = self._replace_placeholders(payload, event_info)

        response = requests.request(
            method=method,
            url=url,
            json=payload,
            headers=headers,
            timeout=action.get("timeout", 30),
        )
        response.raise_for_status()

        logging.info(f"Webhook sent to {url}: {response.status_code}")
        return True

    def _copy_action(self, action: Dict[str, Any], event_info: Dict[str, Any]) -> bool:
        """Execute file copy action"""
        source = self._replace_placeholders(action.get("source", ""), event_info)
        destination = self._replace_placeholders(
            action.get("destination", ""), event_info
        )

        source_path = Path(source)
        dest_path = Path(destination)

        if not source_path.exists():
            raise FileNotFoundError(f"Source file not found: {source}")

        # Create destination directory if needed
        dest_path.parent.mkdir(parents=True, exist_ok=True)

        if source_path.is_file():
            shutil.copy2(source, destination)
        else:
            shutil.copytree(source, destination, dirs_exist_ok=True)

        logging.info(f"Copied {source} to {destination}")
        return True

    def _script_action(
        self, action: Dict[str, Any], event_info: Dict[str, Any]
    ) -> bool:
        """Execute script action"""
        script = action.get("script")
        args = action.get("args", [])
        working_dir = action.get("working_dir")

        # Replace placeholders in script and args
        script = self._replace_placeholders(script, event_info)
        args = [self._replace_placeholders(arg, event_info) for arg in args]

        cmd = [script] + args

        result = subprocess.run(
            cmd,
            cwd=working_dir,
            capture_output=True,
            text=True,
            timeout=action.get("timeout", 300),
        )

        if result.returncode != 0:
            raise subprocess.CalledProcessError(
                result.returncode, cmd, result.stdout, result.stderr
            )

        logging.info(f"Script executed: {script} (exit code: {result.returncode})")
        return True

    def _gotify_action(
        self, action: Dict[str, Any], event_info: Dict[str, Any]
    ) -> bool:
        """Execute Gotify notification action"""
        title = self._replace_placeholders(
            action.get("title", "File Watcher"), event_info
        )
        message = self._replace_placeholders(
            action.get("message", "Event occurred"), event_info
        )
        priority = action.get("priority", 5)

        return self.gotify.send(title, message, priority)

    def _replace_placeholders(
        self, text: Union[str, Dict, List], event_info: Dict[str, Any]
    ) -> Any:
        """Replace placeholders in text with event information"""
        if isinstance(text, str):
            for key, value in event_info.items():
                placeholder = f"{{{key}}}"
                text = text.replace(placeholder, str(value))
            return text
        elif isinstance(text, dict):
            return {
                k: self._replace_placeholders(v, event_info) for k, v in text.items()
            }
        elif isinstance(text, list):
            return [self._replace_placeholders(item, event_info) for item in text]
        else:
            return text


class ConfigManager:
    """Manage watcher configurations"""

    def __init__(self):
        self.configs = []

    def load_from_file(self, config_path: Path) -> None:
        """Load configuration from a single file"""
        with open(config_path, "r", encoding="utf-8") as f:
            if config_path.suffix.lower() in [".yaml", ".yml"]:
                config = yaml.safe_load(f)
            else:
                config = json.load(f)

        if isinstance(config, list):
            self.configs.extend(config)
        else:
            self.configs.append(config)

    def load_from_directory(self, config_dir: Path) -> None:
        """Load all configurations from a directory"""
        for config_file in config_dir.glob("*.{json,yaml,yml}"):
            try:
                self.load_from_file(config_file)
                logging.info(f"Loaded config: {config_file}")
            except Exception as e:
                logging.error(f"Failed to load config {config_file}: {e}")

    def get_configs(self) -> List[Dict[str, Any]]:
        """Get all loaded configurations"""
        return self.configs


class FileWatcherHandler(FileSystemEventHandler):
    """Handle file system events"""

    def __init__(self, config: Dict[str, Any], executor: ActionExecutor):
        self.config = config
        self.executor = executor
        self.watch_patterns = config.get("watch_patterns", ["*"])
        self.ignore_patterns = config.get("ignore_patterns", [])

    def on_any_event(self, event):
        """Handle any file system event"""
        if event.is_directory and not self.config.get("watch_directories", False):
            return

        # Check if event matches watch patterns
        if not self._matches_patterns(event.src_path, self.watch_patterns):
            return

        # Check if event should be ignored
        if self._matches_patterns(event.src_path, self.ignore_patterns):
            return

        # Check event types
        event_types = self.config.get(
            "event_types", ["created", "modified", "deleted", "moved"]
        )
        if event.event_type not in event_types:
            return

        # Prepare event information
        event_info = {
            "event_type": event.event_type,
            "src_path": event.src_path,
            "is_directory": event.is_directory,
            "timestamp": datetime.now().isoformat(),
            "filename": Path(event.src_path).name,
            "dirname": str(Path(event.src_path).parent),
        }

        if hasattr(event, "dest_path"):
            event_info["dest_path"] = event.dest_path

        logging.info(f"Event detected: {event.event_type} - {event.src_path}")

        # Execute actions
        for action in self.config.get("actions", []):
            try:
                self.executor.execute_action(action, event_info)
            except Exception as e:
                logging.error(f"Failed to execute action: {e}")

    def _matches_patterns(self, path: str, patterns: List[str]) -> bool:
        """Check if path matches any of the patterns"""
        if not patterns:
            return False

        import fnmatch

        path_name = Path(path).name

        for pattern in patterns:
            if fnmatch.fnmatch(path_name, pattern) or fnmatch.fnmatch(path, pattern):
                return True
        return False


class PeriodicWatcher:
    """Periodic directory watcher"""

    def __init__(self, configs: List[Dict[str, Any]], executor: ActionExecutor):
        self.configs = configs
        self.executor = executor
        self.last_check = {}

    def check_directories(self) -> None:
        """Check all configured directories for changes"""
        for config in self.configs:
            for watch_path in config.get("watch_paths", []):
                self._check_directory(Path(watch_path), config)

    def _check_directory(self, path: Path, config: Dict[str, Any]) -> None:
        """Check a single directory for changes"""
        if not path.exists():
            logging.warning(f"Watch path does not exist: {path}")
            return

        try:
            current_files = {}

            for file_path in path.rglob("*"):
                if file_path.is_file():
                    stat = file_path.stat()
                    current_files[str(file_path)] = {
                        "mtime": stat.st_mtime,
                        "size": stat.st_size,
                    }

            last_files = self.last_check.get(str(path), {})

            # Check for new/modified files
            for file_path, file_info in current_files.items():
                if file_path not in last_files:
                    self._trigger_event("created", file_path, config)
                elif file_info["mtime"] > last_files[file_path]["mtime"]:
                    self._trigger_event("modified", file_path, config)

            # Check for deleted files
            for file_path in last_files:
                if file_path not in current_files:
                    self._trigger_event("deleted", file_path, config)

            self.last_check[str(path)] = current_files

        except Exception as e:
            logging.error(f"Error checking directory {path}: {e}")

    def _trigger_event(
        self, event_type: str, file_path: str, config: Dict[str, Any]
    ) -> None:
        """Trigger event actions"""
        event_info = {
            "event_type": event_type,
            "src_path": file_path,
            "is_directory": False,
            "timestamp": datetime.now().isoformat(),
            "filename": Path(file_path).name,
            "dirname": str(Path(file_path).parent),
        }

        logging.info(f"Periodic check event: {event_type} - {file_path}")

        for action in config.get("actions", []):
            try:
                self.executor.execute_action(action, event_info)
            except Exception as e:
                logging.error(f"Failed to execute action: {e}")


class FileWatcher:
    """Main file watcher application"""

    def __init__(self):
        self.setup_logging()
        self.gotify = None
        self.executor = None
        self.observer = None
        self.periodic_watcher = None

    def setup_logging(self) -> None:
        """Setup logging configuration"""
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(levelname)s - %(message)s",
            handlers=[
                logging.FileHandler("file_watcher.log"),
                logging.StreamHandler(sys.stdout),
            ],
        )

    def setup_gotify(self) -> None:
        """Setup Gotify notifier"""
        base_url = os.getenv("GOTIFY_URL", "https://gotify.willmo.dev")
        token = os.getenv("GOTIFY_TOKEN")

        if not token:
            logging.warning("GOTIFY_TOKEN not set - notifications disabled")

        self.gotify = GotifyNotifier(base_url, token, bool(token))
        self.executor = ActionExecutor(self.gotify)

    def run_continuous(self, configs: List[Dict[str, Any]]) -> None:
        """Run in continuous watching mode"""
        self.observer = Observer()

        for config in configs:
            for watch_path in config.get("watch_paths", []):
                path = Path(watch_path)
                if path.exists():
                    handler = FileWatcherHandler(config, self.executor)
                    self.observer.schedule(
                        handler, str(path), recursive=config.get("recursive", True)
                    )
                    logging.info(f"Watching: {path}")
                else:
                    logging.warning(f"Watch path does not exist: {path}")

        self.observer.start()

        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            logging.info("Stopping file watcher...")
            self.observer.stop()

        self.observer.join()

    def run_periodic(self, configs: List[Dict[str, Any]], interval: int) -> None:
        """Run in periodic checking mode"""
        self.periodic_watcher = PeriodicWatcher(configs, self.executor)

        schedule.every(interval).seconds.do(self.periodic_watcher.check_directories)

        logging.info(f"Starting periodic watcher (interval: {interval}s)")

        try:
            while True:
                schedule.run_pending()
                time.sleep(1)
        except KeyboardInterrupt:
            logging.info("Stopping periodic watcher...")

    def run(self, args) -> None:
        """Main run method"""
        self.setup_gotify()

        # Load configurations
        config_manager = ConfigManager()

        if args.config_file:
            config_manager.load_from_file(Path(args.config_file))
        elif args.config_dir:
            config_manager.load_from_directory(Path(args.config_dir))
        else:
            logging.error("No configuration specified")
            return

        configs = config_manager.get_configs()

        if not configs:
            logging.error("No valid configurations found")
            return

        logging.info(f"Loaded {len(configs)} configuration(s)")

        # Send startup notification
        self.gotify.send(
            "File Watcher Started",
            f"Monitoring {len(configs)} configuration(s) in {args.mode} mode",
        )

        # Run based on mode
        if args.mode == "continuous":
            self.run_continuous(configs)
        else:
            self.run_periodic(configs, args.interval)


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="File Watcher Tool")
    parser.add_argument(
        "--config-file", type=str, help="Single configuration file (JSON/YAML)"
    )
    parser.add_argument(
        "--config-dir", type=str, help="Directory containing configuration files"
    )
    parser.add_argument(
        "--mode",
        choices=["continuous", "periodic"],
        default="continuous",
        help="Watching mode",
    )
    parser.add_argument(
        "--interval",
        type=int,
        default=60,
        help="Interval for periodic checks (seconds)",
    )

    args = parser.parse_args()

    if not args.config_file and not args.config_dir:
        parser.error("Either --config-file or --config-dir must be specified")

    watcher = FileWatcher()
    watcher.run(args)


if __name__ == "__main__":
    main()

```

---

### watch_src.py

| Property      | Value                      |
|---------------|----------------------------|
| Relative Path | py-scripts/watch_src.py    |
| Created At    | 2025-08-24T22:59:02.494193 |
| Last Modified | 2025-09-23T16:18:46.487744 |
| Size          | 1495 bytes                 |

**Content**:

```python
# /// script
# requires-python = ">=3.13"
# dependencies = ["watchfiles"]
# ///
from pathlib import Path

_backup_config_json = Path().home() / ".backup_config.json"
_backup_locs: list[str] = []
if not _backup_config_json.exists():
    _backup_config_json.write_text('{"backups": []}')
    _backup_locs = []
else:
    import json

    with _backup_config_json.open("r", encoding="utf-8") as f:
        data = json.load(f)
        _backup_locs = data.get("backups", [])
if _backup_locs == []:
    print(
        "No backup locations configured. Please add backup locations to ~/.backup_config.json"
    )
    print('Example: {"backups": ["/path/to/dir1", "/path/to/dir2"]}')
    exit(1)

from datetime import datetime as dt
import asyncio
from watchfiles import awatch

watcher_pool: list[asyncio.Task] = []
watched_paths: list[Path] = [Path(p) for p in _backup_locs if Path(p).exists()]
if watched_paths == []:
    print("No valid backup locations configured. Please check ~/.backup_config.json")
    exit(1)


async def main():
    async def watch_path(p: Path):
        async for changes in awatch(p):
            for change, file in changes:
                if change.name == "added" or change.name == "modified":
                    print(f"[{dt.now().isoformat()}] {change.name}: {file}")

    for p in watched_paths:
        print(f"Watching {p} for changes...")
        watcher_pool.append(asyncio.create_task(watch_path(p)))
    await asyncio.gather(*watcher_pool)


asyncio.run(main())

```

---

### recruiter_msg.txt

| Property      | Value                      |
|---------------|----------------------------|
| Relative Path | recruiter_msg.txt          |
| Created At    | 2025-09-19T23:54:07.009316 |
| Last Modified | 2025-09-19T23:54:14.120114 |
| Size          | 2018 bytes                 |

**Content**:

```text
Hello can you help? I am looking for a Principal Engineer, Applied Al software engineer.
Hi Will,

I came across your profile and was impressed by your AI/ML background. I'm reaching out about a Principal Engineer, Applied AI role that might be exactly what you're looking for if you're ready to move beyond theory and ship AI solutions that actually impact real users.

We’re looking for someone that has at least 3 years of relevant work experience. Ideally, this person should have ample experience with applied AI, so 3 years minimum. We’re looking for an all-star, someone that stands out amongst other engineers for their grit/grind, proven track record. Someone who loves the execution – loves building. Has tried tons of different things to solve various problems.

Why this role is different:
• You'll be building and deploying AI-powered tools directly into mortgage and customer service workflows - not just creating demos
• They want someone who lives in VS Code/Cursor, not PowerPoint presentations
• Rapid prototyping and iteration - getting usable versions in front of real users quickly
• Full ownership from concept to production launch

What you'll be working with:
LLM APIs, fine-tuning, and RAG pipelines
Cloud platforms (AWS, Azure, GCP)
Python, JavaScript/TypeScript
Integration with OpenAI, AWS, Azure APIs

The company culture: They value builders who prioritize "quick, practical, and effective" over "perfect-but-late." Success means having multiple AI tools in production that employees and customers rely on daily.

Location: Hybrid/Remote based in Columbia, MO

This isn't about spending months on specs - it's about shipping AI solutions that solve real business problems. If you're interested in learning more about how your AI expertise could drive meaningful impact, I'd love to have a quick conversation.

Are you open to a brief call this week to discuss the details?


Best regards,

Randy Bedami
Recruiting Partner
Goodwin Recruiting

```

---

### run_checks_on_save.py

| Property      | Value                 |
|---------------|-----------------------|
| Relative Path | run_checks_on_save.py |
| Created At    | 2025-09-26T21:50:09.600544 |
| Last Modified | 2025-09-26T21:46:38   |
| Size          | 430 bytes             |

**Content**:

```python
# /// script
# requires-python = ">=3.13"
# dependencies = [
#     "black",
#     "flake8",
#     "isort",
#     "mypy",
#     "watchfiles",
# ]
# description = "Continuously watch a directory and run code quality checks on Python files when they are saved. reads configurations for tools from pyproject.toml and a .watch_ignore file."
# ///
from pathlib import Path
from typing import Optional

watch_dir: Optional[Path] = None


```

---

### sql_formatter.ps1

| Property      | Value               |
|---------------|---------------------|
| Relative Path | sql_formatter.ps1   |
| Created At    | 2025-09-25T19:37:03.216367 |
| Last Modified | 2025-09-26T20:18:07 |
| Size          | 11108 bytes         |

**Content**:

```plaintext
param(
    [string]$prompt,
    [string]$db_path = "c:\src\jestr\ingestor-core\data\local.db"
)

if (-not (Test-Path $db_path)) {
    throw "Database file not found at path: $db_path"
}
$env:OLLAMA_HOST = "http://192.168.0.25:11434"

$dbSchema = (sqlite-utils.exe schema $db_path)
$dialect = "Dialect: sqlite"

$system_msg  = "# The Assistant
The assistant is a Sr. SQL developer with 20+ years of experience across many dialects.
The assistant works for the user to advise and assist with their SQL needs.
The assistant receives a database schema, dialect of the specific database, and request from the user to perform.
theses requests will always result in a *codeblock only* response with no additional commentary or text from the assistant.
this is including times in which the user's request might be for information or bug-fixes (including errors in thier request).
The assistant always responds in a code block even when the response may just be plaintext it *will be formeatted in a memo or
GitHub/Jira issue or comment style code block as json or yml or plaintext as appropriate*.

## Examples:

example 1 (translate sqlite to postgresql):
'''
user request:
    'translate this schema into one that can be ran on a postgresql database'
    ---
    DDL Dialect: sqlite
    DDL:
    CREATE TABLE books (
        id INTEGER PRIMARY KEY,
        title TEXT NOT NULL,
        author TEXT NOT NULL,
        published_date TEXT NOT NULL DEFAULT (date('now'))
    );
    ---
    response:
    CREATE TABLE IF NOT EXISTS books (
        id SERIAL PRIMARY KEY,
        title VARCHAR NOT NULL,
        author VARCHAR NOT NULL,
        published_date DATE NOT NULL DEFAULT CURRENT_DATE
    );

---
example 2 (translate postgresql to mysql):

user request:
    'translate this schema into one that can be ran on a mysql database'
    ---
    DDL Dialect: postgresql
    DDL:
    CREATE TABLE orders (
        order_id SERIAL PRIMARY KEY,
        customer_id INTEGER NOT NULL,
        order_date DATE NOT NULL DEFAULT CURRENT_DATE,
        status VARCHAR(50) NOT NULL DEFAULT 'pending'
    );
    ---
response:
    CREATE TABLE IF NOT EXISTS orders (
        order_id INT AUTO_INCREMENT PRIMARY KEY,
        customer_id INT NOT NULL,
        order_date DATE NOT NULL DEFAULT CURRENT_DATE,
        status VARCHAR(50) NOT NULL DEFAULT 'pending'
    );

---
example 3 (helping with feature requests):

user request:
'''I want to create a trigger that parses a insert_json column on insert and populates other columns based on the json content'
---
DDL Dialect: mysql
DDL:
CREATE TABLE IF NOT EXISTS events (
    event_id INT AUTO_INCREMENT PRIMARY KEY,
    event_type VARCHAR(50) NOT NULL,
    event_timestamp DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    insert_json JSON NOT NULL,
    user_id INT,
    action VARCHAR(100),
    details TEXT
};
---'''
assistant response:
```
CREATE TRIGGER before_event_insert
    BEFORE INSERT ON events
    FOR EACH ROW
    BEGIN
        DECLARE parsed_user_id INT;
        DECLARE parsed_action VARCHAR(100);
        DECLARE parsed_details TEXT;

        SET parsed_user_id = JSON_UNQUOTE(JSON_EXTRACT(NEW.insert_json, '$.user_id'));
        SET parsed_action = JSON_UNQUOTE(JSON_EXTRACT(NEW.insert_json, '$.action'));
        SET parsed_details = JSON_UNQUOTE(JSON_EXTRACT(NEW.insert_json, '$.details'));

        SET NEW.user_id = parsed_user_id;
        SET NEW.action = parsed_action;
        SET NEW.details = parsed_details;
    END;
```

---
example 4 (creating feature request tickets for jira/github):

user request
'''I want to create a feature request ticket for Jira to add a new table to store user profiles with columns for user_id, username, email, created_at, and profile_json'
---
DDL Dialect: postgresql
DDL:
CREATE TABLE IF NOT EXISTS user_profiles (
    user_id SERIAL PRIMARY KEY,
    username VARCHAR(50) NOT NULL,
    email VARCHAR(100) NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    profile_json JSONB NOT NULL
);
---'''

assistant response:
```yml
parent_issue:
    project: 'User Profiles'
    summary: 'Create user_profiles table'
    description: |
    Create a new table to store user profiles with the following columns:
    - user_id: SERIAL PRIMARY KEY
    - username: VARCHAR(50) NOT NULL
    - email: VARCHAR(100) NOT NULL
    - created_at: TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
    - profile_json: JSONB NOT NULL
    labels:
    - database
    - feature request
    assignee: 'database-team'
    issue_type: 'Task'
subtasks:
    - summary: 'Design user_profiles table schema'
    description: 'Design the schema for the user_profiles table.'
    issue_type: 'Sub-task'
    assignee: 'db-designer'
    - summary: 'Implement user_profiles table in database'
    description: 'Implement the user_profiles table in the database.'
    issue_type: 'Sub-task'
    assignee: 'db-implementer'
```

---
## Features and Guidelines:

The assistant always responds in one or more code blocks with the appropriate syntax highlighting for the language used.
The assistant always ensures the response is syntactically correct and can be run without error; thinking carefully about the specific dialect and its requirements for the response to be valid.

### **JSON Handling:**
use context clues like column names, types and comments to determine if a column is intended to store JSON data.
i.e. request_json, config_json, args_json, metadata_json, details_json, etc.
if a column is intended to store JSON data, use the appropriate JSON column type for the dialect if available.
if the dialect does not support a native JSON column type, use a TEXT column type and add a comment indicating the column is intended to store JSON data.
if the dialect supports JSON column types, use them instead of TEXT or VARCHAR for columns intended to store JSON data.

### **SQL Formatting:**
the assistant always formats the SQL in a readable way, with appropriate indentation and line breaks.
the assistant always uses uppercase for SQL keywords (e.g., SELECT, FROM, WHERE).
the assistant always uses lower_snake_case for identifiers (e.g., table_names, column_names).
the assistant always includes `IF NOT EXISTS` when creating tables to avoid errors if the table already exists.

### **ORM Models (when applicable):**
if the user request includes a request for ORM models, the assistant generates the models using SQLAlchemy for Python.
the assistant uses the following style to generate the models:

#### Standard SQLAlchemy Imports and Base Class
The assistant always uses the following import statements for SQLAlchemy models, adjusting only the SQLAlchemy types imported based on the schema provided.

sqlalchemy imports for SQLAlchemy types should be generic as possible, leaning on the ORM to handle the specifics of the dialect, and opposed to using dialect specific types *unless absolutely necessary*.
'''python
    from sqlalchemy import Integer, String, Date, JSON, DateTime  # ... etc. These are up to *the assistant* to determine based on the schema. this is *critical* to think through, and get *right*.
```

The code standard here is to always declare the columns using SQLAlchemy's Mapped type and mapped_column function, as shown below, so we *always* import these two items from sqlalchemy.orm:
```python
    from sqlalchemy.orm import declarative_base, Mapped, mapped_column # These are **STATIC** imports. *DO NOT* change these, ALWAYS include them as stated.
    from datetime import datetime, timezone  # **IMPORTANT**: datetime.utcnow() is deprecated. Use datetime.now(tz=timezone.utc) instead. this requires importing timezone from datetime as well. THIS IS *CRITICAL* to get right.
```

**IMPORNTANT**: Always use a shared instance of declarative_base() from a common module. This is *critical* to ensure all models share the same base class, and that the base class is only created once.
```python
    # This is a shared instance of declarative_base() This is how the user typically imports it locally. use this always.
    from ._base import Base

    # Leave this commented out. *DO* include it in a comment so the user can use it if they need to.
    # from sqlalchemy.orm import declarative_base
    # Base = declarative_base()

    # ... models ...
---

**Class and Table Names**
Classes declared will have a name schema that:
- omits any shared prefixes or suffixes like tbl_, table_, _table, etc.
- uses UpperCamelCase for class names
- suffixed with `Record`
- uses *exactly* the table name provided DDL for the `__tablename__` attribute, without any modifications.
```python
    class OrderRecord(Base):
        __tablename__ = 'orders' # assuming DDL had a table named `orders`
        ...
```

**Creating Columns**
```python
    # Use this style for all columns. This is *critical* to ensure the models are correct and use the latest SQLAlchemy features.
    column_name: Mapped[column_type] = mapped_column(ColumnType, options...)
    # Examples:
    order_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    customer_id: Mapped[int] = mapped_column(Integer, nullable=False)
    order_date: Mapped[date] = mapped_column(Date, nullable=False)
    status: Mapped[str] = mapped_column(String(50), nullable=False)
    # for JSON columns:
    config_json: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict

    # for columns with default values:
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.now(tz=timezone.utc))

---
## Scripting Instructions
When writing SQL scripts the assistant adheres to the following guidelines:
- Always include proper script headers with comments indicating the purpose of the script, author, and date (which the user can fill in).
- when writing scripts that modify data, always include transaction handling (BEGIN, COMMIT, ROLLBACK) to ensure data integrity.
  - always include a PRINT statement check as the final step and rollback, leave the actual COMMIT statement commented out for the user to uncomment after verifying the script ran as expected.
  - always include error handling to catch and PRINT or LOG errors that occur during script execution.
  - when using python to execute scripts, (such as with sqlalchemy or on a sqlite db) always use a context manager to ensure the connection is properly closed after execution.
  - always adhere to the same rollback and commit strategy as above to print any changes and rollback them, leaving the actual commit commented out for the user to uncomment after verifying the script ran as expected in python scripting or terminal as well.
---
## End of Assistant Guidelines
"

$formatted_prompt = "Dialect: $dialect`nDDL: $dbSchema`n`n---`n`nUser request: $prompt`n---`n"

write-Host "Sending prompt:n$formatted_prompt"

llm.exe prompt `
    -m gpt-oss:20b `
    -s $system_msg `
    $formatted_prompt

```

---

### uas.cmd

| Property      | Value                      |
|---------------|----------------------------|
| Relative Path | uas.cmd                    |
| Created At    | 2025-10-15T17:43:54.636482 |
| Last Modified | 2025-10-15T17:53:59.030791 |
| Size          | 124 bytes                  |

**Content**:

```bat
﻿echo off

set uv_script_name_arg=%1
set packages_to_add=%2

uv add --script %uv_script_name_arg% %packages_to_add%

```

---

### uv_script_add.cmd

| Property      | Value                      |
|---------------|----------------------------|
| Relative Path | uv_script_add.cmd          |
| Created At    | 2025-10-15T17:54:40.661151 |
| Last Modified | 2025-10-15T17:56:57.960187 |
| Size          | 605 bytes                  |

**Content**:

```bat
@echo off

if "%1"=="" (
    echo Usage: uv_script_add.cmd script_name [package1 package2 ...]
    echo.
    echo Example: uv_script_add.cmd my_script.uvm pkg1 pkg2
    exit /b 1
)
if "%2"=="" (
    echo Warning: No packages specified to add to the script.
)

set uv_script_name_arg=%1
set packages_to_add=%2

uv add --script %uv_script_name_arg% %packages_to_add%

if errorlevel 1 (
    echo Failed to add script %uv_script_name_arg% with packages %packages_to_add%.
    exit /b 1
) else (
    echo Successfully added script %uv_script_name_arg% with packages %packages_to_add%.
)

```

---

### uv_script_create.cmd

| Property      | Value                      |
|---------------|----------------------------|
| Relative Path | uv_script_create.cmd       |
| Created At    | 2025-10-15T19:59:20.733235 |
| Last Modified | 2025-10-15T20:00:44.634154 |
| Size          | 617 bytes                  |

**Content**:

```bat
@echo off

if "%1"=="" (
    echo Usage: uv_script_create.cmd script_name [package1 package2 ...]
    echo.
    echo Example: uv_script_create.cmd my_script.uvm pkg1 pkg2
    exit /b 1
)
if "%2"=="" (
    echo Warning: No packages specified to add to the script.
)

set uv_script_name_arg=%1
set packages_to_add=%2

uv init --script %uv_script_name_arg% %packages_to_add%

if errorlevel 1 (
    echo Failed to create script %uv_script_name_arg% with packages %packages_to_add%.
    exit /b 1
) else (
    echo Successfully created script %uv_script_name_arg% with packages %packages_to_add%.
)

```

---
