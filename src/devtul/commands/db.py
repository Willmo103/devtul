import typer
from devtul.core.interactive import interactive_create_database_connection
from devtul.core.database import add_host, get_hosts
from typer import echo

db_cli = typer.Typer(name="db", help="Database related commands")


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

    hosts = get_hosts()
    if not hosts:
        echo("No database connections found.")
        return

    for idx, host in enumerate(hosts, start=1):
        echo(f"{idx}. {host.host}:{host.port} - {host.dbname} (User: {host.user})")
