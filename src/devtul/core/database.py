from typing import Optional
from sqlite_utils import Database
from devtul.core.config import _app_data
from devtul.core.models import DatabaseConfig, DatabaseConfig_DBModel, NetworkHost

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
