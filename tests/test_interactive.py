from unittest.mock import patch
from devtul.core.interactive import interactive_create_database_connection
from devtul.core.models import PostgresDatabaseConfig


def test_interactive_create_postgres_connection():
    # Arrange
    # Inputs: "postgres" (choice), "localhost" (host), "5432" (port), "mydb" (dbname), "admin" (user), "secret" (pass)
    user_inputs = ["localhost", "admin", "secret", "postgres", "mydb", "5432"]

    # We patch the prompt functions to return our list items one by one
    with (
        patch("rich.prompt.Prompt.ask", side_effect=[user_inputs[0]]),
        patch("typer.prompt", side_effect=user_inputs[1:]),
    ):

        # Act
        config, conn_type = interactive_create_database_connection()

    # Assert
    assert conn_type == "postgres"
    assert isinstance(config, PostgresDatabaseConfig)
    assert config.host == "localhost"
    assert config.dbname == "mydb"
    assert config.port == 5432
    assert config.user == "admin"
    assert config.password == "secret"
