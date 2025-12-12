from contextlib import contextmanager
from devtul.core.models import (
    PostgresDatabaseConfig,
    MySQLDatabaseConfig,
    MsSQLDatabaseConfig,
    SQLiteDatabaseConfig,
    MongoDBDatabaseConfig,
)


@contextmanager
def pg_session(database_config: PostgresDatabaseConfig):
    try:
        import psycopg2 as pg
    except ImportError:
        raise ImportError(
            "psycopg2 is required for PostgreSQL database connections. "
            "Please install it via 'uv pip install psycopg2-binary'."
        )
    conn = pg.connect(database_config.conn_info)
    try:
        yield conn
    finally:
        conn.close()


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
            "Please install it via 'uv pip install mysql-connector-python'."
        )
    conn = mysql.connector.connect(**conn_info)
    try:
        yield conn
    finally:
        conn.close()


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
            "Please install it via 'uv pip install pyodbc'."
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


@contextmanager
def mongodb_session(database_config: MongoDBDatabaseConfig):
    try:
        from pymongo import MongoClient  # type: ignore
    except ImportError:
        raise ImportError(
            "pymongo is required for MongoDB database connections. "
            "Please install it via 'uv pip install pymongo'."
        )
    client = MongoClient(database_config.uri)
    try:
        yield client
    finally:
        client.close()
