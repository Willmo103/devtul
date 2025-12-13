from devtul.core.interactive import interactive_create_database_connection
from devtul.core.database import add_host
from typer import echo


def create_database_connection():
    """
    Wrapper around the interactive database connection creation.
    Returns the created DatabaseConfig and connection type.
    """
    config, conn_type = interactive_create_database_connection()
    add_host(config, conn_type)
    echo(f"Database connection for {conn_type} added successfully.")
