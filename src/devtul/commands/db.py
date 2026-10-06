import csv
import io
import json
from pathlib import Path
import sys
from typing import Any, Dict, List, Optional

from jinja2 import Template
from rich.console import Console
from rich.table import Table
import typer
from typer import echo
import yaml

from devtul.core.database import (
    add_host,
    execute_duckdb_query,
    execute_sqlite_query,
    get_host_records,
    get_hosts,
    inspect_sqlite_database,
    inspect_sqlite_table_schema,
    resolve_database,
)
from devtul.core.interactive import interactive_create_database_connection
from devtul.core.tools import run_bundled_tool

console = Console()
db_cli = typer.Typer(name="db", help="Database management, inspection, querying, and DuckDB tools")


@db_cli.command(name="create", help="Create a new database connection interactively")
def create_database_connection():
    """
    Wrapper around the interactive database connection creation.
    Returns the created DatabaseConfig and connection type.
    """
    config, conn_type = interactive_create_database_connection()
    add_host(config, conn_type)
    echo(f"Database connection for {conn_type} added successfully.")


@db_cli.command(name="ls", help="List all saved database connections")
def list_database_connections():
    """
    List all saved database connections in the database.
    """
    hosts = get_host_records()
    if not hosts:
        echo("No database connections found.")
        return

    table = Table(title="Saved Database Connections", border_style="cyan")
    table.add_column("#", style="dim")
    table.add_column("Type", style="green")
    table.add_column("Host", style="bold")
    table.add_column("Port")
    table.add_column("Database", style="yellow")
    table.add_column("User")

    for idx, host in enumerate(hosts, start=1):
        table.add_row(
            str(idx),
            host.conn_type,
            host.host,
            str(host.port or ""),
            host.dbname or "",
            host.user,
        )
    console.print(table)


@db_cli.command(name="view", help="View databases, tables, and schemas")
def view_database(
    db: Optional[str] = typer.Option(
        None,
        "--db",
        "-d",
        help="Database name, profile, or SQLite file path",
    ),
    table: Optional[str] = typer.Option(
        None,
        "--table",
        "-t",
        help="Specific table to inspect schema and sample rows",
    ),
):
    """
    View available databases, tables within a database, or schema and sample rows for a table.
    """
    if db is None:
        # Display saved database profiles and local SQLite files
        hosts = get_host_records()
        if hosts:
            prof_table = Table(title="Saved Database Profiles", border_style="cyan")
            prof_table.add_column("#", style="dim")
            prof_table.add_column("Type", style="green")
            prof_table.add_column("Database", style="yellow")
            prof_table.add_column("Host:Port")
            prof_table.add_column("User")
            for idx, h in enumerate(hosts, start=1):
                prof_table.add_row(
                    str(idx),
                    h.conn_type,
                    h.dbname or "",
                    f"{h.host}:{h.port}",
                    h.user,
                )
            console.print(prof_table)

        # Check for local SQLite files
        local_dbs = []
        for ext in [".db", ".sqlite", ".sqlite3"]:
            local_dbs.extend(Path.cwd().glob(f"*{ext}"))

        if local_dbs:
            local_table = Table(title="Local SQLite Databases", border_style="magenta")
            local_table.add_column("#", style="dim")
            local_table.add_column("Filename", style="bold")
            local_table.add_column("Size (bytes)", justify="right")
            for idx, f in enumerate(local_dbs, start=1):
                local_table.add_row(str(idx), f.name, str(f.stat().st_size))
            console.print(local_table)

        if not hosts and not local_dbs:
            console.print("[yellow]No saved database profiles or local SQLite databases found.[/yellow]")
            console.print("Use [cyan]dt db create[/cyan] to add a connection or pass [cyan]--db <file.db>[/cyan].")
        return

    # Resolve database target
    engine_type, target = resolve_database(db)

    if engine_type == "sqlite":
        db_path = Path(target)
        if not db_path.exists():
            console.print(f"[bold red]SQLite database file '{db_path}' does not exist.[/bold red]")
            raise typer.Exit(code=1)

        if table is None:
            # List tables
            tables = inspect_sqlite_database(db_path)
            if not tables:
                console.print(f"[yellow]No tables found in database '{db_path.name}'.[/yellow]")
                return

            tbl = Table(title=f"Tables in {db_path.name}", border_style="cyan")
            tbl.add_column("Table Name", style="bold green")
            tbl.add_column("Type", style="dim")
            tbl.add_column("Columns", justify="right")
            tbl.add_column("Row Count", justify="right")
            for t in tables:
                tbl.add_row(t["name"], t["type"], str(t["columns"]), str(t["rows"]))
            console.print(tbl)
            console.print(f"\n[dim]To view table schema: dt db view --db {db} --table <name>[/dim]")
        else:
            # Inspect table schema and sample rows
            columns_info, sample_rows = inspect_sqlite_table_schema(db_path, table)
            if not columns_info:
                console.print(f"[bold red]Table '{table}' not found in '{db_path.name}'.[/bold red]")
                raise typer.Exit(code=1)

            # Schema Table
            schema_tbl = Table(title=f"Schema: {table} ({db_path.name})", border_style="cyan")
            schema_tbl.add_column("CID", style="dim", justify="right")
            schema_tbl.add_column("Column Name", style="bold")
            schema_tbl.add_column("Type", style="green")
            schema_tbl.add_column("Not Null", justify="center")
            schema_tbl.add_column("Default")
            schema_tbl.add_column("PK", justify="center")

            for col in columns_info:
                schema_tbl.add_row(
                    str(col["cid"]),
                    col["name"],
                    col["type"],
                    "✓" if col["notnull"] else "",
                    str(col["dflt_value"] or ""),
                    "✓" if col["pk"] else "",
                )
            console.print(schema_tbl)

            # Sample Rows Table
            if sample_rows:
                sample_tbl = Table(title=f"Sample Data: {table} (first 5 rows)", border_style="magenta")
                for col in columns_info:
                    sample_tbl.add_column(col["name"])
                for row in sample_rows:
                    sample_tbl.add_row(*[str(row.get(col["name"], "")) for col in columns_info])
                console.print(sample_tbl)
    else:
        console.print(f"[yellow]Remote database inspection for '{db}' requires an active session or direct query.[/yellow]")
        console.print("Use [cyan]dt db query \"SELECT table_name FROM information_schema.tables\" --db {db}[/cyan].")


def format_query_data(
    columns: List[str],
    rows: List[Dict[str, Any]],
    format_type: str = "table",
    template: Optional[str] = None,
) -> Any:
    """Format tabular query results into requested text format or Rich Table."""
    fmt = format_type.lower()
    if fmt == "json":
        return json.dumps(rows, indent=2, default=str)
    if fmt == "yaml":
        return yaml.dump(rows, sort_keys=False, default_flow_style=False)
    if fmt == "csv":
        buf = io.StringIO()
        writer = csv.DictWriter(buf, fieldnames=columns, lineterminator="\n")
        writer.writeheader()
        for r in rows:
            writer.writerow(r)
        return buf.getvalue().strip()
    if fmt == "tsv":
        buf = io.StringIO()
        writer = csv.DictWriter(buf, fieldnames=columns, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        for r in rows:
            writer.writerow(r)
        return buf.getvalue().strip()
    if fmt in ["md", "markdown"]:
        lines = []
        lines.append("| " + " | ".join(str(c) for c in columns) + " |")
        lines.append("| " + " | ".join("---" for _ in columns) + " |")
        for r in rows:
            lines.append("| " + " | ".join(str(r.get(c, "")) for c in columns) + " |")
        return "\n".join(lines)
    if fmt == "jinja":
        if template and Path(template).exists():
            tmpl_str = Path(template).read_text(encoding="utf-8")
        else:
            tmpl_str = template or "{{ rows }}"
        tmpl = Template(tmpl_str)
        return tmpl.render(rows=rows, columns=columns, data=rows)

    # Default Rich Table
    table = Table(border_style="cyan")
    for col in columns:
        table.add_column(col, style="bold")
    for r in rows:
        table.add_row(*[str(r.get(c, "")) for c in columns])
    return table


@db_cli.command(name="query", help="Execute SQL queries and export data in multiple formats")
def query_database(
    sql: Optional[str] = typer.Argument(None, help="SQL query to execute"),
    file: Optional[Path] = typer.Option(None, "--file", "-f", help="Path to SQL file"),
    db: Optional[str] = typer.Option(None, "--db", "-d", help="Database name, profile, or file path"),
    format: str = typer.Option(
        "table",
        "--format",
        "--fmt",
        help="Output format: table (rich), json, yaml, csv, tsv, md (markdown table), jinja",
    ),
    template: Optional[str] = typer.Option(None, "--template", "-t", help="Jinja2 template string or path"),
    outfile: Optional[Path] = typer.Option(None, "--outfile", "-o", help="Output file path"),
):
    """
    Execute SQL against a database and pipe/export data in structured formats or custom Jinja2 templates.
    """
    query_text = sql
    if file is not None and file.exists():
        query_text = file.read_text(encoding="utf-8")
    elif query_text is None:
        if not sys.stdin.isatty():
            query_text = sys.stdin.read().strip()

    if not query_text:
        console.print("[bold red]Error: No SQL query provided.[/bold red]")
        console.print("Provide query as argument, pass [cyan]-f script.sql[/cyan], or pipe via stdin.")
        raise typer.Exit(code=1)

    engine_type, target = resolve_database(db)

    try:
        if engine_type == "sqlite":
            columns, rows = execute_sqlite_query(Path(target), query_text)
        else:
            host_rec, conn_type = target
            from devtul.core.db.session import create_engine_from_config
            # Fallback or sqlalchemy execution
            engine = create_engine_from_config(host_rec, conn_type)
            from sqlalchemy import text
            with engine.connect() as conn:
                res = conn.execute(text(query_text))
                if res.returns_rows:
                    columns = list(res.keys())
                    rows = [dict(zip(columns, r)) for r in res.fetchall()]
                else:
                    conn.commit()
                    columns = ["status"]
                    rows = [{"status": f"Query executed successfully ({res.rowcount} rows affected)"}]

        formatted_output = format_query_data(columns, rows, format_type=format, template=template)

        if outfile:
            out_str = str(formatted_output) if not isinstance(formatted_output, str) else formatted_output
            outfile.write_text(out_str, encoding="utf-8")
            console.print(f"[bold green]Query results written to: {outfile}[/bold green]")
        else:
            if isinstance(formatted_output, Table):
                console.print(formatted_output)
            else:
                print(formatted_output)

    except Exception as e:
        console.print(f"[bold red]Query execution failed: {e}[/bold red]")
        raise typer.Exit(code=1)


@db_cli.command(name="query-file", help="Query data files (CSV, Parquet, JSON, SQLite) using DuckDB")
@db_cli.command(name="duck", hidden=True)
@db_cli.command(name="duckdb", hidden=True)
def query_data_file(
    query_or_file: str = typer.Argument(
        ...,
        help="SQL query or path to data file (csv, parquet, json, jsonl, sqlite)",
    ),
    cli: bool = typer.Option(False, "--cli", help="Launch interactive DuckDB CLI"),
    format: str = typer.Option("table", "--format", "--fmt", help="Output format: table, json, yaml, csv, tsv, md, jinja"),
    template: Optional[str] = typer.Option(None, "--template", "-t", help="Jinja2 template string or path"),
    outfile: Optional[Path] = typer.Option(None, "--outfile", "-o", help="Output file path"),
):
    """
    Query data files like databases using DuckDB, or launch interactive DuckDB CLI.
    """
    if cli:
        # Launch DuckDB CLI
        args = [query_or_file] if Path(query_or_file).exists() else []
        try:
            exit_code = run_bundled_tool("duckdb", args)
            raise typer.Exit(code=exit_code)
        except FileNotFoundError as e:
            console.print(f"[bold red]{e}[/bold red]")
            raise typer.Exit(code=1)

    # Determine SQL
    p = Path(query_or_file)
    if p.exists() and not any(kw in query_or_file.upper() for kw in ["SELECT", "FROM", "PRAGMA", "DESCRIBE"]):
        sql = f"SELECT * FROM '{p.as_posix()}' LIMIT 50"
        console.print(f"[dim]Querying '{p.as_posix()}' (showing first 50 rows)...[/dim]")
    else:
        sql = query_or_file

    try:
        columns, rows = execute_duckdb_query(sql)
        formatted = format_query_data(columns, rows, format_type=format, template=template)

        if outfile:
            out_str = str(formatted) if not isinstance(formatted, str) else formatted
            outfile.write_text(out_str, encoding="utf-8")
            console.print(f"[bold green]DuckDB results written to: {outfile}[/bold green]")
        else:
            if isinstance(formatted, Table):
                console.print(formatted)
            else:
                print(formatted)

    except Exception as e:
        console.print(f"[bold red]DuckDB query failed: {e}[/bold red]")
        raise typer.Exit(code=1)


def entry():
    db_cli()
