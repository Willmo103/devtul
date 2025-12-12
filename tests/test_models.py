from devtul.core.models import DatabaseConfig


def test_database_config_model():
    config = DatabaseConfig(
        host="localhost",
        port=5432,
        dbname="test_db",
        user="test_user",
        password="test_pass",
    )
    assert config.host == "localhost"
    assert config.port == 5432
    assert config.dbname == "test_db"
    assert config.user == "test_user"
    assert config.password == "test_pass"

    assert (
        config.conn_info
        == "host=localhost port=5432 dbname=test_db user=test_user password=test_pass"
    )
