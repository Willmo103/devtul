from pathlib import Path
from typing import Any, Optional

from sqlite_utils import Database

from devtul.core.config import _app_data
from devtul.core.models import (DatabaseConfig, DatabaseConfig_DBModel,
                                NetworkHost)

db_path = _app_data / "devtul_interface.db"
database = Database(db_path)


def get_hosts(conn_type: Optional[str] = None) -> list[DatabaseConfig]:
    """Retrieve all database host configurations from the database.
    Args:
        conn_type: Optional; Filter by connection type (e.g., "postgres", "mysql")
    Returns:
        List of DatabaseConfig objects
    """
    if "database_hosts" not in database.table_names():
        return []
    hosts_table = database["database_hosts"]
    hosts = []
    for record in hosts_table.rows:
        if conn_type and record["conn_type"] != conn_type:
            continue
        host_config = DatabaseConfig(
            host=record["host"],
            port=record["port"],
            dbname=record["dbname"],
            user=record["user"],
            password=record["password"],
        )
        hosts.append(host_config)
    return hosts


def add_host(database_config: DatabaseConfig, conn_type: str) -> None:
    """Add a new database host configuration to the database.
    Args:
        database_config: DatabaseConfig object containing the host details
        conn_type: Type of the database connection (e.g., "postgres", "mysql")
    """
    hosts_table = database["database_hosts"]
    host_record = DatabaseConfig_DBModel(
        host=database_config.host,
        port=database_config.port,
        dbname=database_config.dbname,
        user=database_config.user,
        password=database_config.password,
        conn_type=conn_type,
    )
    hosts_table.insert(host_record.model_dump(), pk=None)


def update_host(
    original_config: DatabaseConfig,
    updated_config: DatabaseConfig,
    conn_type: str,
) -> None:
    """Update an existing database host configuration in the database.
    Args:
        original_config: Original DatabaseConfig object to identify the record
        updated_config: Updated DatabaseConfig object with new details
        conn_type: Type of the database connection (e.g., "postgres", "mysql")
    """
    hosts_table = database["database_hosts"]
    original_record = {
        "host": original_config.host,
        "port": original_config.port,
        "dbname": original_config.dbname,
        "user": original_config.user,
        "password": original_config.password,
        "conn_type": conn_type,
    }
    updated_record = {
        "host": updated_config.host,
        "port": updated_config.port,
        "dbname": updated_config.dbname,
        "user": updated_config.user,
        "password": updated_config.password,
        "conn_type": conn_type,
    }
    hosts_table.update(original_record, updated_record)


def delete_host(database_config: DatabaseConfig, conn_type: str) -> None:
    """Delete a database host configuration from the database.
    Args:
        database_config: DatabaseConfig object containing the host details
        conn_type: Type of the database connection (e.g., "postgres", "mysql")
    """
    hosts_table = database["database_hosts"]
    record_to_delete = {
        "host": database_config.host,
        "port": database_config.port,
        "dbname": database_config.dbname,
        "user": database_config.user,
        "password": database_config.password,
        "conn_type": conn_type,
    }
    hosts_table.delete(record_to_delete)


def add_network_host(host: NetworkHost) -> None:
    """Add a new host configuration to the database.
    Args:
        host: host object containing the host details
    """
    database["hosts"].insert(host.model_dump(), pk="ip_address")


def get_network_hosts() -> list[NetworkHost]:
    """Retrieve all network host configurations from the database.
    Returns:
        List of NetworkHost objects
    """
    if "hosts" not in database.table_names():
        return []
    hosts_table = database["hosts"]
    hosts = []
    for record in hosts_table.rows:
        host_config = NetworkHost(
            hostname=record["hostname"],
            ip_address=record["ip_address"],
            mac_address=record.get("mac_address"),
            description=record.get("description"),
        )
        hosts.append(host_config)
    return hosts


def get_network_host_range(min_ip: str, max_ip: str) -> list[NetworkHost]:
    """Retrieve network hosts within a specified IP range from the database.
    Args:
        min_ip: Minimum IP address in the range
        max_ip: Maximum IP address in the range
    Returns:
        List of NetworkHost objects within the specified IP range
    """
    if "hosts" not in database.table_names():
        return []
    hosts_table = database["hosts"]
    query = f"ip_address >= '{min_ip}' AND ip_address <= '{max_ip}'"
    hosts = []
    for record in hosts_table.rows_where(query):
        host_config = NetworkHost(
            hostname=record["hostname"],
            ip_address=record["ip_address"],
            mac_address=record.get("mac_address"),
            description=record.get("description"),
        )
        hosts.append(host_config)
    return hosts


def get_network_host_by_ip(ip_address: str) -> Optional[NetworkHost]:
    """Retrieve a network host by its IP address from the database.
    Args:
        ip_address: IP address of the host to retrieve
    Returns:
        NetworkHost object if found, else None
    """
    if "hosts" not in database.table_names():
        return None
    hosts_table = database["hosts"]
    record = hosts_table.get(ip_address, default=None)
    if record:
        return NetworkHost(
            hostname=record["hostname"],
            ip_address=record["ip_address"],
            mac_address=record.get("mac_address"),
            description=record.get("description"),
        )
    return None


def get_host_records(conn_type: Optional[str] = None) -> list[DatabaseConfig_DBModel]:
    """Retrieve all database host records with conn_type from the database."""
    if "database_hosts" not in database.table_names():
        return []
    hosts_table = database["database_hosts"]
    hosts = []
    for record in hosts_table.rows:
        if conn_type and record.get("conn_type") != conn_type:
            continue
        hosts.append(
            DatabaseConfig_DBModel(
                host=record["host"],
                port=record["port"],
                dbname=record["dbname"],
                user=record["user"],
                password=record["password"],
                conn_type=record.get("conn_type", "unknown"),
            )
        )
    return hosts


def resolve_database(db_target: Optional[str] = None) -> tuple[str, Any]:
    """
    Resolve a database target into (engine_type, target_object).
    engine_type can be 'sqlite' (target_object is Path) or 'remote' (target_object is (DatabaseConfig, conn_type)).
    """
    if db_target:
        # Check if it's an existing file or explicit sqlite extension
        p = Path(db_target)
        if p.exists() or p.suffix.lower() in [".db", ".sqlite", ".sqlite3"]:
            return "sqlite", p.resolve()

        # Check saved database host profiles
        records = get_host_records()
        for rec in records:
            if db_target in [rec.dbname, rec.host, f"{rec.host}:{rec.port}"]:
                return "remote", (rec, rec.conn_type)

        # Default fallback to sqlite path
        return "sqlite", p.resolve()

    # If no db_target provided, check current directory for sqlite files
    for ext in [".db", ".sqlite", ".sqlite3"]:
        local_files = list(Path.cwd().glob(f"*{ext}"))
        if local_files:
            return "sqlite", local_files[0].resolve()

    # Fallback to devtul default database
    return "sqlite", db_path.resolve()


def inspect_sqlite_database(path: Path) -> list[dict]:
    """List tables and metadata in a SQLite database."""
    import sqlite3
    if not path.exists():
        return []
    conn = sqlite3.connect(str(path))
    cur = conn.cursor()
    cur.execute(
        "SELECT name, type FROM sqlite_master WHERE type IN ('table', 'view') AND name NOT LIKE 'sqlite_%' ORDER BY name;"
    )
    tables = []
    for name, item_type in cur.fetchall():
        try:
            cur.execute(f'SELECT COUNT(*) FROM "{name}"')
            count = cur.fetchone()[0]
        except Exception:
            count = "N/A"
        try:
            cur.execute(f'PRAGMA table_info("{name}")')
            col_count = len(cur.fetchall())
        except Exception:
            col_count = "N/A"
        tables.append({
            "name": name,
            "type": item_type,
            "columns": col_count,
            "rows": count,
        })
    conn.close()
    return tables


def inspect_sqlite_table_schema(path: Path, table_name: str) -> tuple[list[dict], list[dict]]:
    """Inspect schema and sample rows for a SQLite table."""
    import sqlite3
    if not path.exists():
        return [], []
    conn = sqlite3.connect(str(path))
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute(f'PRAGMA table_info("{table_name}")')
    columns_info = []
    for col in cur.fetchall():
        columns_info.append({
            "cid": col["cid"],
            "name": col["name"],
            "type": col["type"],
            "notnull": bool(col["notnull"]),
            "dflt_value": col["dflt_value"],
            "pk": bool(col["pk"]),
        })

    cur.execute(f'SELECT * FROM "{table_name}" LIMIT 5')
    sample_rows = [dict(row) for row in cur.fetchall()]
    conn.close()
    return columns_info, sample_rows


def execute_sqlite_query(path: Path, sql: str) -> tuple[list[str], list[dict]]:
    """Execute a SQL query against a SQLite database."""
    import sqlite3
    conn = sqlite3.connect(str(path))
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute(sql)
    if cur.description:
        columns = [d[0] for d in cur.description]
        rows = [dict(r) for r in cur.fetchall()]
    else:
        conn.commit()
        columns = ["status"]
        rows = [{"status": f"Query executed successfully, {cur.rowcount} rows affected."}]
    conn.close()
    return columns, rows


def execute_duckdb_query(sql: str) -> tuple[list[str], list[dict]]:
    """Execute a query against DuckDB (supports direct CSV/Parquet/JSON/SQLite file scanning)."""
    import duckdb
    conn = duckdb.connect(":memory:")
    rel = conn.execute(sql)
    if rel.description:
        columns = [desc[0] for desc in rel.description]
        fetched = rel.fetchall()
        rows = [dict(zip(columns, row)) for row in fetched]
    else:
        columns = ["status"]
        rows = [{"status": "Query executed successfully."}]
    return columns, rows
