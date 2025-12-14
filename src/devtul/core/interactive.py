import typer
from pydantic import BaseModel
from typing import Type, TypeVar
from rich.prompt import Prompt
from devtul.core.constants import DB_CONN_TYPES
from devtul.core.models import (
    PostgresDatabaseConfig,
    MySQLDatabaseConfig,
    MsSQLDatabaseConfig,
    SQLiteDatabaseConfig,
    MongoDBDatabaseConfig,
    DatabaseConfig,
)
from devtul.core.db.session import (
    pg_session,
    mysql_session,
    mssql_session,
    sqlite_session,
    mongodb_session,
)


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


def interactive_create_database_connection():
    """
    1. Select Type
    2. Prompt for Config (Generic)
    3. Test Connection
    4. Return config if valid or forced
    """
    typer.echo("Creating a new database connection configuration.")

    # Select Type
    conn_type = Prompt.ask(
        "Select database connection type",
        choices=[t.value for t in DB_CONN_TYPES],
        default=DB_CONN_TYPES.POSTGRES.value,
    )

    model_class: DatabaseConfig = MODEL_MAP[conn_type]
    if model_class == SQLiteDatabaseConfig:
        typer.echo("Configuring SQLite connection...")
        db_path = Prompt.ask("Enter SQLite database file path", default=":memory:")
        config = SQLiteDatabaseConfig(db_path=db_path)
        return config, conn_type
    elif model_class in [
        MongoDBDatabaseConfig,
        PostgresDatabaseConfig,
        MySQLDatabaseConfig,
        MsSQLDatabaseConfig,
    ]:

        typer.echo(f"Configuring {conn_type} connection...")
        host = Prompt.ask("Enter database host", default="localhost")
        user = Prompt.ask(
            "Enter database user", default=USER_DEFAULT_MAP.get(conn_type, "admin")
        )
        password = Prompt.ask("Enter database password", password=True, default="")
        port = Prompt.ask(
            "Enter database port",
            default=str(PORT_DEFAULT_MAP.get(conn_type, "")),
            show_default=True,
        )
        dbname = Prompt.ask(
            "Enter database name", default=SERVICE_DATABASE_MAP.get(conn_type, "")
        )
        config = model_class(
            host=host,
            user=user,
            password=password,
            port=int(port),
            dbname=dbname,
        )
        if verify_connection(config, conn_type):
            return config, conn_type
        else:
            # Prompt to alter the config or exit
            retry = Prompt.ask(
                "Connection failed. Do you want to retry? (y/n)",
                choices=["y", "n"],
                default="n",
            )
            if retry == "y":
                while True:
                    host = Prompt.ask("Enter database host", default=config.host)
                    user = Prompt.ask("Enter database user", default=config.user)
                    password = Prompt.ask(
                        "Enter database password",
                        password=True,
                        default=config.password,
                    )
                    port = Prompt.ask(
                        "Enter database port",
                        default=str(config.port),
                        show_default=True,
                    )
                    dbname = Prompt.ask("Enter database name", default=config.dbname)
                    config = model_class(
                        host=host,
                        user=user,
                        password=password,
                        port=int(port),
                        dbname=dbname,
                    )
                    if verify_connection(config, conn_type):
                        return config, conn_type
                    else:
                        # Ask if they want to save anyway or retry
                        save_anyway = Prompt.ask(
                            "Connection failed again. Do you want to save anyway? (y/n)",
                            choices=["y", "n"],
                            default="n",
                        )
                        if save_anyway == "y":
                            return config, conn_type
            typer.secho("Exiting without saving configuration.", fg=typer.colors.RED)
            raise typer.Exit(1)
