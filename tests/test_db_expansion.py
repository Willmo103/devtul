"""
Unit tests for expanded database commands: view, query, and DuckDB file querying.
"""

from pathlib import Path
import sqlite3
from typer.testing import CliRunner

from devtul.commands.db import db_cli
from devtul.core.database import (
    execute_duckdb_query,
    execute_sqlite_query,
    inspect_sqlite_database,
    inspect_sqlite_table_schema,
    resolve_database,
)
from devtul.core.tools import find_bundled_tool

runner = CliRunner()


def create_sample_sqlite_db(path: Path) -> Path:
    conn = sqlite3.connect(path)
    cur = conn.cursor()
    cur.execute("CREATE TABLE users (id INTEGER PRIMARY KEY, name TEXT NOT NULL, email TEXT);")
    cur.execute("INSERT INTO users (name, email) VALUES ('Alice', 'alice@example.com');")
    cur.execute("INSERT INTO users (name, email) VALUES ('Bob', 'bob@example.com');")
    conn.commit()
    conn.close()
    return path


def test_inspect_sqlite_database(tmp_path):
    db_file = create_sample_sqlite_db(tmp_path / "sample.db")
    tables = inspect_sqlite_database(db_file)
    assert len(tables) == 1
    assert tables[0]["name"] == "users"
    assert tables[0]["columns"] == 3
    assert tables[0]["rows"] == 2


def test_inspect_sqlite_table_schema(tmp_path):
    db_file = create_sample_sqlite_db(tmp_path / "sample.db")
    cols, sample_rows = inspect_sqlite_table_schema(db_file, "users")
    col_names = [c["name"] for c in cols]
    assert "id" in col_names
    assert "name" in col_names
    assert "email" in col_names
    assert len(sample_rows) == 2
    assert sample_rows[0]["name"] == "Alice"


def test_execute_sqlite_query(tmp_path):
    db_file = create_sample_sqlite_db(tmp_path / "sample.db")
    cols, rows = execute_sqlite_query(db_file, "SELECT name, email FROM users WHERE id = 1")
    assert cols == ["name", "email"]
    assert len(rows) == 1
    assert rows[0]["name"] == "Alice"
    assert rows[0]["email"] == "alice@example.com"


def test_execute_duckdb_query_in_memory():
    cols, rows = execute_duckdb_query("SELECT 100 as num, 'DevTul' as project")
    assert cols == ["num", "project"]
    assert rows[0]["num"] == 100
    assert rows[0]["project"] == "DevTul"


def test_execute_duckdb_query_csv_file(tmp_path):
    csv_file = tmp_path / "test.csv"
    csv_file.write_text("id,val\n1,Alpha\n2,Beta\n", encoding="utf-8")
    sql = f"SELECT val FROM '{csv_file.as_posix()}' WHERE id = 2"
    cols, rows = execute_duckdb_query(sql)
    assert cols == ["val"]
    assert len(rows) == 1
    assert rows[0]["val"] == "Beta"


def test_cli_db_view(tmp_path):
    db_file = create_sample_sqlite_db(tmp_path / "sample.db")
    # View tables
    res = runner.invoke(db_cli, ["view", "--db", str(db_file)])
    assert res.exit_code == 0
    assert "users" in res.output

    # View schema
    res_schema = runner.invoke(db_cli, ["view", "--db", str(db_file), "--table", "users"])
    assert res_schema.exit_code == 0
    assert "Alice" in res_schema.output
    assert "email" in res_schema.output


def test_cli_db_query_formats(tmp_path):
    db_file = create_sample_sqlite_db(tmp_path / "sample.db")

    # JSON export
    res_json = runner.invoke(
        db_cli,
        ["query", "SELECT name FROM users WHERE id = 1", "--db", str(db_file), "--fmt", "json"],
    )
    assert res_json.exit_code == 0
    assert '"name": "Alice"' in res_json.output

    # CSV export
    res_csv = runner.invoke(
        db_cli,
        ["query", "SELECT name FROM users", "--db", str(db_file), "--fmt", "csv"],
    )
    assert res_csv.exit_code == 0
    assert "name\nAlice\nBob" in res_csv.output

    # Markdown table export
    res_md = runner.invoke(
        db_cli,
        ["query", "SELECT name FROM users", "--db", str(db_file), "--fmt", "md"],
    )
    assert res_md.exit_code == 0
    assert "| name |" in res_md.output
    assert "| Alice |" in res_md.output

    # Jinja export
    res_jinja = runner.invoke(
        db_cli,
        [
            "query",
            "SELECT name FROM users",
            "--db",
            str(db_file),
            "--fmt",
            "jinja",
            "-t",
            "{% for r in rows %}User: {{ r.name }};{% endfor %}",
        ],
    )
    assert res_jinja.exit_code == 0
    assert "User: Alice;User: Bob;" in res_jinja.output

    # Outfile export
    out_file = tmp_path / "output.csv"
    res_out = runner.invoke(
        db_cli,
        [
            "query",
            "SELECT name FROM users",
            "--db",
            str(db_file),
            "--fmt",
            "csv",
            "-o",
            str(out_file),
        ],
    )
    assert res_out.exit_code == 0
    assert out_file.exists()
    assert "Alice" in out_file.read_text(encoding="utf-8")


def test_cli_db_query_file_duckdb(tmp_path):
    csv_file = tmp_path / "records.csv"
    csv_file.write_text("code,amount\nUSD,150\nEUR,250\n", encoding="utf-8")

    # Query file directly
    res = runner.invoke(
        db_cli,
        ["query-file", str(csv_file), "--fmt", "json"],
    )
    assert res.exit_code == 0
    assert '"code": "USD"' in res.output
    assert '"amount": 150' in res.output


def test_find_bundled_tool():
    # Should locate duckdb installed in venv/scripts or PATH
    duckdb_tool = find_bundled_tool("duckdb")
    assert duckdb_tool is not None
    assert duckdb_tool.exists()

    # Nonexistent tool
    nonexistent = find_bundled_tool("completely_nonexistent_tool_12345")
    assert nonexistent is None
