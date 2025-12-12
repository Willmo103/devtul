import typer
from rich.prompt import Prompt
from devtul.core.models import (
    DatabaseConfig,
    PostgresDatabaseConfig,
    MySQLDatabaseConfig,
    MsSQLDatabaseConfig,
    SQLiteDatabaseConfig,
    MongoDBDatabaseConfig,
)

# Map string choices to their specific Pydantic models
CONN_TYPE_MAP = {
    "postgres": PostgresDatabaseConfig,
    "mysql": MySQLDatabaseConfig,
    "mssql": MsSQLDatabaseConfig,
    "sqlite": SQLiteDatabaseConfig,
    "mongodb": MongoDBDatabaseConfig,
}


def prompt_for_model(model_class: type[DatabaseConfig]) -> DatabaseConfig:
    """
    Dynamically prompts user for fields defined in a Pydantic model.
    """
    user_data = {}

    # Iterate over model fields to generate prompts automatically
    for field_name, field_info in model_class.model_fields.items():
        # Skip internal or computed fields if necessary
        if field_name == "conn_info":
            continue

        default_val = field_info.default
        is_required = field_info.is_required()

        # Determine prompt text
        prompt_text = f"Enter {field_name}"
        if field_info.description:
            prompt_text = f"{field_info.description}"

        # If strict required (no default), use typer.prompt without default
        if is_required and (default_val is None or default_val == str):
            val = typer.prompt(prompt_text, type=field_info.annotation)
        else:
            # Use default from model
            val = typer.prompt(
                prompt_text, default=default_val, type=field_info.annotation
            )

        user_data[field_name] = val

    return model_class(**user_data)


def interactive_create_database_connection() -> tuple[DatabaseConfig, str]:
    """
    Collect database connection details interactively.
    """
    typer.echo("Creating a new database connection configuration.")

    # Use Rich Prompt for choices (Typer.prompt doesn't support 'choices' list natively)
    choices = list(CONN_TYPE_MAP.keys())
    conn_type = Prompt.ask(
        "Select database connection type", choices=choices
    )

    # Get the specific model class based on choice
    model_class = CONN_TYPE_MAP[conn_type]

    # Dynamically prompt for that model's data
    config = prompt_for_model(model_class)

    return config, conn_type
