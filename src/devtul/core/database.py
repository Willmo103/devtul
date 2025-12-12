from typing import Optional
from sqlite_utils import Database
from devtul.core.config import _app_data
from devtul.core.models import DatabaseConfig, DatabaseConfig_DBModel, Server

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


def get_ollama_hosts() -> list[Server]:
    """Retrieve all Ollama server configurations from the database.
    Returns:
        List of Server objects
    """
    ...
