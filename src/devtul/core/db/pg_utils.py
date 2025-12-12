from typing import Optional
from devtul.core.db.session import pg_session
from devtul.core.models import DatabaseConfig


def test_pg_connection(database_config: DatabaseConfig) -> bool:
    """Test PostgreSQL database connection using the provided configuration.
    Args:
        database_config: DatabaseConfig object containing the connection details
    Returns:
        True if connection is successful, False otherwise
    """
    try:
        with pg_session(database_config) as conn:
            with conn.cursor() as cursor:
                cursor.execute("SELECT 1;")
                result = cursor.fetchone()
                return result is not None and result[0] == 1
    except Exception:
        return False


def list_pg_databases(database_config: DatabaseConfig) -> list[str]:
    """List all databases in the PostgreSQL server using the provided configuration.
    Args:
        database_config: DatabaseConfig object containing the connection details
    Returns:
        List of database names
    """
    databases = []
    try:
        with pg_session(database_config) as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    "SELECT datname FROM pg_database WHERE datistemplate = false;"
                )
                rows = cursor.fetchall()
                databases = [row[0] for row in rows]
    except Exception:
        pass
    return databases


def list_pg_tables(database_config: DatabaseConfig) -> list[str]:
    """List all tables in the connected PostgreSQL database using the provided configuration.
    Args:
        database_config: DatabaseConfig object containing the connection details
    Returns:
        List of table names
    """
    tables = []
    try:
        with pg_session(database_config) as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT table_name
                    FROM information_schema.tables
                    WHERE table_schema = 'public' AND table_type = 'BASE TABLE';
                    """
                )
                rows = cursor.fetchall()
                tables = [row[0] for row in rows]
    except Exception:
        pass
    return tables


def get_pg_table_columns(database_config: DatabaseConfig, table_name: str) -> list[str]:
    """Get column names of a specific table in the connected PostgreSQL database.
    Args:
        database_config: DatabaseConfig object containing the connection details
        table_name: Name of the table to retrieve columns for
    Returns:
        List of column names
    """
    columns = []
    try:
        with pg_session(database_config) as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT column_name
                    FROM information_schema.columns
                    WHERE table_name = %s;
                    """,
                    (table_name,),
                )
                rows = cursor.fetchall()
                columns = [row[0] for row in rows]
    except Exception:
        pass
    return columns


def get_pg_primary_key(
    database_config: DatabaseConfig, table_name: str
) -> Optional[str]:
    """Get the primary key column of a specific table in the connected PostgreSQL database.
    Args:
        database_config: DatabaseConfig object containing the connection details
        table_name: Name of the table to retrieve the primary key for
    Returns:
        Primary key column name, or None if not found
    """
    primary_key = None
    try:
        with pg_session(database_config) as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT a.attname
                    FROM pg_index i
                    JOIN pg_attribute a ON a.attrelid = i.indrelid AND a.attnum = ANY(i.indkey)
                    WHERE i.indrelid = %s::regclass AND i.indisprimary;
                    """,
                    (table_name,),
                )
                row = cursor.fetchone()
                if row:
                    primary_key = row[0]
    except Exception:
        pass
    return primary_key


def get_pg_table_info(database_config: DatabaseConfig, table_name: str) -> dict:
    """Get detailed information about a specific table in the connected PostgreSQL database.
    Args:
        database_config: DatabaseConfig object containing the connection details
        table_name: Name of the table to retrieve information for
    Returns:
        Dictionary containing table information:
            - columns: List of column names, types, and nullability
            - primary_key: Primary key column name or None
            - indexes: List of index names
            - row_count: Estimated number of rows in the table
            - size_bytes: Estimated size of the table in bytes
    """
    table_info = {
        "columns": [],
        "primary_key": None,
        "indexes": [],
        "row_count": 0,
        "size_bytes": 0,
    }
    try:
        with pg_session(database_config) as conn:
            with conn.cursor() as cursor:
                # Get columns
                cursor.execute(
                    """
                    SELECT column_name, data_type, is_nullable
                    FROM information_schema.columns
                    WHERE table_name = %s;
                    """,
                    (table_name,),
                )
                table_info["columns"] = [
                    {"name": row[0], "type": row[1], "is_nullable": row[2] == "YES"}
                    for row in cursor.fetchall()
                ]
                # Get primary key
                cursor.execute(
                    """
                    SELECT a.attname
                    FROM pg_index i
                    JOIN pg_attribute a ON a.attrelid = i.indrelid AND a.attnum = ANY(i.indkey)
                    WHERE i.indrelid = %s::regclass AND i.indisprimary;
                    """,
                    (table_name,),
                )
                pk_row = cursor.fetchone()
                if pk_row:
                    table_info["primary_key"] = pk_row[0]
                # Get indexes
                cursor.execute(
                    """
                    SELECT indexname
                    FROM pg_indexes
                    WHERE tablename = %s;
                    """,
                    (table_name,),
                )
                table_info["indexes"] = [row[0] for row in cursor.fetchall()]
                # Get row count
                cursor.execute(
                    f"SELECT reltuples::BIGINT AS estimate FROM pg_class WHERE relname = %s;",
                    (table_name,),
                )
                row_count_row = cursor.fetchone()
                if row_count_row:
                    table_info["row_count"] = int(row_count_row[0])
                # Get size in bytes
                cursor.execute(
                    "SELECT pg_total_relation_size(%s::regclass);",
                    (table_name,),
                )
                size_row = cursor.fetchone()
                if size_row:
                    table_info["size_bytes"] = int(size_row[0])
    except Exception:
        pass
    return table_info


def get_pg_database_info(database_config: DatabaseConfig):
    """Get detailed information about the connected PostgreSQL database.
    Args:
        database_config: DatabaseConfig object containing the connection details
    Returns:
        Dictionary containing database information for each database in a server, and tabl info for each table of each database:
        {
            database_name: {
                tables: {
                    table_name: {
                        columns: [...],
                        primary_key: ...,
                        indexes: [...],
                        row_count: ...,
                        size_bytes: ...,
                    },
                    ...
                }
            },
            ...
        }
    """
    database_info = {}
    try:
        databases = list_pg_databases(database_config)
        for db_name in databases:
            db_config = DatabaseConfig(
                host=database_config.host,
                port=database_config.port,
                dbname=db_name,
                user=database_config.user,
                password=database_config.password,
            )
            tables = list_pg_tables(db_config)
            table_infos = {}
            for table in tables:
                table_infos[table] = get_pg_table_info(db_config, table)
            database_info[db_name] = {"tables": table_infos}
    except Exception:
        pass
    return database_info
