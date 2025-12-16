from contextlib import contextmanager

from devtul.core.constants import DB_CONN_TYPES
from devtul.core.models import (DatabaseConfig, MongoDBDatabaseConfig,
                                MsSQLDatabaseConfig, MySQLDatabaseConfig,
                                PostgresDatabaseConfig, SQLiteDatabaseConfig)


@contextmanager
def pg_session(database_config: PostgresDatabaseConfig):
    try:
        import psycopg2 as pg  # type: ignore
    except ImportError:
        raise ImportError(
            "psycopg2 is required for PostgreSQL database connections. "
            "Please install it via `uv install devtul['pg']`."
        )
    conn = pg.connect(database_config.conn_info)
    try:
        yield conn
    finally:
        conn.close()


def test_pg_config(database_config: PostgresDatabaseConfig) -> bool:
    """Test PostgreSQL database connection using the provided configuration.
    Args:
        database_config: PostgresDatabaseConfig object containing the connection details
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


@contextmanager
def mysql_session(database_config: MySQLDatabaseConfig):
    conn_info = {
        "host": database_config.host,
        "port": database_config.port,
        "database": database_config.dbname,
        "user": database_config.user,
        "password": database_config.password,
    }
    try:
        import mysql.connector  # type: ignore
    except ImportError:
        raise ImportError(
            "mysql-connector-python is required for MySQL database connections. "
            "Please install it via 'uv install devtul['mysql']'."
        )
    conn = mysql.connector.connect(**conn_info)
    try:
        yield conn
    finally:
        conn.close()


def test_mysql_config(database_config: MySQLDatabaseConfig) -> bool:
    """Test MySQL database connection using the provided configuration.
    Args:
        database_config: MySQLDatabaseConfig object containing the connection details
    Returns:
        True if connection is successful, False otherwise
    """
    try:
        with mysql_session(database_config) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT 1;")
            result = cursor.fetchone()
            return result is not None and result[0] == 1
    except Exception:
        return False


@contextmanager
def mssql_session(database_config: MsSQLDatabaseConfig):
    conn_info = {
        "server": database_config.host,
        "port": database_config.port,
        "database": database_config.dbname,
        "user": database_config.user,
        "password": database_config.password,
    }
    try:
        import pyodbc  # type: ignore
    except ImportError:
        raise ImportError(
            "pyodbc is required for MS SQL Server database connections. "
            "Please install it via 'uv install devtul['mssql']'."
        )
    conn_str = (
        f"DRIVER={{ODBC Driver 17 for SQL Server}};"
        f"SERVER={conn_info['server']},{conn_info['port']};"
        f"DATABASE={conn_info['database']};"
        f"UID={conn_info['user']};"
        f"PWD={conn_info['password']}"
    )
    conn = pyodbc.connect(conn_str)
    try:
        yield conn
    finally:
        conn.close()


def test_mssql_config(database_config: MsSQLDatabaseConfig) -> bool:
    """Test MS SQL Server database connection using the provided configuration.
    Args:
        database_config: MsSQLDatabaseConfig object containing the connection details
    Returns:
        True if connection is successful, False otherwise
    """
    try:
        with mssql_session(database_config) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT 1;")
            result = cursor.fetchone()
            return result is not None and result[0] == 1
    except Exception:
        return False


@contextmanager
def sqlite_session(database_config: SQLiteDatabaseConfig):
    try:
        import sqlite3  # type: ignore
    except ImportError:
        raise ImportError(
            "sqlite3 is required for SQLite database connections. "
            "Please ensure it is included in your Python installation."
        )
    conn = sqlite3.connect(database_config.file_path)
    try:
        yield conn
    finally:
        conn.close()


def test_sqlite_config(database_config: SQLiteDatabaseConfig) -> bool:
    """Test SQLite database connection using the provided configuration.
    Args:
        database_config: SQLiteDatabaseConfig object containing the connection details
    Returns:
        True if connection is successful, False otherwise
    """
    try:
        with sqlite_session(database_config) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT 1;")
            result = cursor.fetchone()
            return result is not None and result[0] == 1
    except Exception:
        return False


@contextmanager
def mongodb_session(database_config: MongoDBDatabaseConfig):
    try:
        from pymongo import MongoClient  # type: ignore
    except ImportError:
        raise ImportError(
            "pymongo is required for MongoDB database connections. "
            "Please install it via 'uv install devtul['mongodb']'."
        )
    client = MongoClient(database_config.uri)
    try:
        yield client
    finally:
        client.close()


def test_mongodb_config(database_config: MongoDBDatabaseConfig) -> bool:
    """Test MongoDB database connection using the provided configuration.
    Args:
        database_config: MongoDBDatabaseConfig object containing the connection details
    Returns:
        True if connection is successful, False otherwise
    """
    try:
        with mongodb_session(database_config) as client:
            # The ismaster command is cheap and does not require auth.
            client.admin.command("ismaster")
            return True
    except Exception:
        return False


# 1. Map Types to Models
MODEL_MAP = {
    DB_CONN_TYPES.POSTGRES: PostgresDatabaseConfig,
    DB_CONN_TYPES.MYSQL: MySQLDatabaseConfig,
    DB_CONN_TYPES.MSSQL: MsSQLDatabaseConfig,
    DB_CONN_TYPES.SQLITE: SQLiteDatabaseConfig,
    DB_CONN_TYPES.MONGODB: MongoDBDatabaseConfig,
}
# 2. Map Types to Session Testers
SESSION_MAP = {
    DB_CONN_TYPES.POSTGRES: pg_session,
    DB_CONN_TYPES.MYSQL: mysql_session,
    DB_CONN_TYPES.MSSQL: mssql_session,
    DB_CONN_TYPES.SQLITE: sqlite_session,
    DB_CONN_TYPES.MONGODB: mongodb_session,
}
USER_DEFAULT_MAP = {
    DB_CONN_TYPES.POSTGRES: "postgres",
    DB_CONN_TYPES.MYSQL: "root",
    DB_CONN_TYPES.MSSQL: "sa",
    DB_CONN_TYPES.MONGODB: "admin",
}
PORT_DEFAULT_MAP = {
    DB_CONN_TYPES.POSTGRES: 5432,
    DB_CONN_TYPES.MYSQL: 3306,
    DB_CONN_TYPES.MSSQL: 1433,
    DB_CONN_TYPES.MONGODB: 27017,
}
SERVICE_DATABASE_MAP = {
    DB_CONN_TYPES.POSTGRES: "postgres",
    DB_CONN_TYPES.MYSQL: "mysql",
    DB_CONN_TYPES.MSSQL: "master",
    DB_CONN_TYPES.MONGODB: "admin",
}


def verify_connection(config: DatabaseConfig, conn_type: str) -> bool:
    """Attempts to establish a connection using the defined session managers."""
    session_manager = SESSION_MAP.get(conn_type)

    if not session_manager:
        typer.secho(
            f"No session manager defined for {conn_type}", fg=typer.colors.YELLOW
        )
        return True  # Assume valid if we can't test it? Or False.

    typer.echo(f"Testing connection to {conn_type}...")
    try:
        # We perform a no-op inside the context manager just to trigger the __enter__ logic
        with session_manager(config):
            pass
        typer.secho("Connection Successful", fg=typer.colors.GREEN)
        return True
    except Exception as e:
        typer.secho(f"Connection Failed, :{e}", fg=typer.colors.RED)
        return False
