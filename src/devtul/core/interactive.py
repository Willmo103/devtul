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


T = TypeVar("T", bound=BaseModel)


def prompt_for_model(model_class: Type[T]) -> T:
    """
    Generic function to interactively populate any Pydantic model.

    - Respects field types (int, str, etc.)
    - Uses field descriptions for prompt text
    - Uses field defaults if available
    - Skips computed or internal fields
    """
    user_data = {}

    for field_name, field_info in model_class.model_fields.items():
        # Skip fields marked as computed or internal logic
        if field_name in ["conn_info", "conn_type"]:
            continue

        # Determine the prompt text
        text = (
            field_info.description if field_info.description else f"Enter {field_name}"
        )

        # Handle Defaults
        # field_info.default is the value, field_info.default is Pydantic's formatting
        default_val = field_info.default

        # If Pydantic says the default is "PydanticUndefined", treat it as required
        if field_info.is_required():
            val = typer.prompt(text, type=field_info.annotation)
        else:
            val = typer.prompt(text, default=default_val, type=field_info.annotation)

        user_data[field_name] = val

    return model_class(**user_data)


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

    while True:
        # Generic Prompt
        model_class = MODEL_MAP[conn_type]
        config = prompt_for_model(model_class)

        # Test Connection
        is_valid = verify_connection(config, conn_type)

        if is_valid:
            return config, conn_type

        # If invalid, ask user what to do
        action = Prompt.ask(
            "Connection failed. What would you like to do?",
            choices=["retry", "save anyway", "abort"],
            default="retry",
        )

        if action == "save anyway":
            return config, conn_type
        elif action == "abort":
            raise typer.Exit()
        # If retry, loop continues and prompts again
