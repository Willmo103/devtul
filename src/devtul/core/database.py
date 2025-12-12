from typing import Optional
from sqlite_utils import Database
from devtul.core.config import _app_data
from devtul.core.models import DatabaseConfig

db_path = _app_data / "devtul_interface.db"
database = Database(db_path)


def get_hosts() -> Optional[list[DatabaseConfig]]:
    """Retrieve all database host configurations from the database."""
    hosts_table = database["database_hosts"]
    hosts = []
    for record in hosts_table.rows:
        host_config = DatabaseConfig(
            host=record["host"],
            port=record["port"],
            dbname=record["dbname"],
            user=record["user"],
            password=record["password"],
        )
        hosts.append(host_config)
    return hosts if hosts else None
