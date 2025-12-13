from devtul.core.models import DatabaseConfig
import pytest
from pathlib import Path
from datetime import datetime, timezone
from devtul.core import models as mod
from devtul.core.constants import FileContentStatus

# --- Fixtures for File Creation ---


@pytest.fixture
def input_dir(tmp_path: Path) -> Path:
    """Fixture for the root input directory."""
    return tmp_path / "input_root"


@pytest.fixture
def non_empty_file(input_dir: Path) -> Path:
    """Fixture for a non-empty test file."""
    # Create the root input directory
    input_dir.mkdir(exist_ok=True)

    file_path = input_dir / "data" / "test_file.txt"
    file_path.parent.mkdir(exist_ok=True)
    file_path.write_text("Test data to make this file non-empty.")
    return file_path


@pytest.fixture
def empty_file(input_dir: Path) -> Path:
    """Fixture for an empty test file."""
    # Create the root input directory
    input_dir.mkdir(exist_ok=True)

    file_path = input_dir / "empty" / "empty_file.log"
    file_path.parent.mkdir(exist_ok=True)
    file_path.touch()  # Creates an empty file
    return file_path


@pytest.fixture
def dummy_datetimes():
    """Fixture for dummy created/modified datetimes."""
    # Use timezone-aware datetimes for best practice
    created = datetime(2025, 1, 1, 10, 0, 0, tzinfo=timezone.utc)
    modified = datetime(2025, 1, 1, 11, 30, 0, tzinfo=timezone.utc)
    return created, modified


# --- Failing Tests (TDD Step) ---


def test_fileresult_init_with_non_empty_file(input_dir: Path, non_empty_file: Path):
    """
    Tests initialization for a non-empty file, relying on file system stats.
    """
    # Act
    result = mod.FileResult(file_path=non_empty_file, input_path=input_dir)

    # Assert
    assert result.full_path == non_empty_file.resolve()
    assert result.relative_path.as_posix() == "data/test_file.txt"
    assert result.size > 0
    assert result.content_status == FileContentStatus.NOT_EMPTY
    # Creation/modification dates will be checked for existence, not specific values
    assert isinstance(result.created_at, datetime)
    assert isinstance(result.modified_at, datetime)


def test_fileresult_init_with_empty_file(input_dir: Path, empty_file: Path):
    """
    Tests initialization for an empty file, checking for FileContentStatus.EMPTY.
    """
    # Act
    result = mod.FileResult(file_path=empty_file, input_path=input_dir)

    # Assert
    assert result.size == 0
    assert result.content_status == FileContentStatus.EMPTY
    assert result.relative_path.as_posix() == "empty/empty_file.log"


def test_fileresult_init_with_explicit_datetimes(
    input_dir: Path, non_empty_file: Path, dummy_datetimes
):
    """
    Tests initialization when created_at and modified_at are passed explicitly.
    The internal file stat logic should be skipped in this case.
    """
    created_at, modified_at = dummy_datetimes

    # Act
    result = mod.FileResult(
        file_path=non_empty_file,
        input_path=input_dir,
        created_at=created_at,
        modified_at=modified_at,
    )

    # Assert
    # Check that explicit values were used
    assert result.created_at == created_at
    assert result.modified_at == modified_at
    # Check that stat logic still ran to populate size and content_status
    assert result.size > 0
    assert result.content_status == FileContentStatus.NOT_EMPTY


def test_fileresult_dict_method(input_dir: Path, non_empty_file: Path):
    """
    Tests the __dict__ method for correct structure and string representation.
    """
    # Arrange
    result = mod.FileResult(file_path=non_empty_file, input_path=input_dir)

    # Act
    output_dict = result.__dict__()

    # Assert
    assert isinstance(output_dict, dict)
    assert output_dict["full_path"] == result.full_path.as_posix()
    assert output_dict["content_state"] == FileContentStatus.NOT_EMPTY.value
    assert "Unknown" not in output_dict["created_at"]
    assert "Unknown" not in output_dict["modified_at"]


def test_fileresult_to_yaml_method(input_dir: Path, empty_file: Path):
    """
    Tests the to_yaml method.
    """
    # Arrange
    result = mod.FileResult(file_path=empty_file, input_path=input_dir)

    # Act
    yaml_output = result.to_yaml()

    # Assert
    assert isinstance(yaml_output, str)
    assert "size: 0" in yaml_output
    assert f"content_state: {FileContentStatus.EMPTY.value}" in yaml_output


def test_fileresult_to_model_method(input_dir: Path, non_empty_file: Path):
    """
    Tests the to_model method returns a Pydantic model with correct fields.
    """
    # Arrange
    result = mod.FileResult(file_path=non_empty_file, input_path=input_dir)

    # Act
    model_instance = result.to_model()

    # Assert
    assert hasattr(model_instance, "full_path")
    assert model_instance.full_path == result.full_path.as_posix()
    assert model_instance.size == result.size
    assert model_instance.content_state == result.content_status.value
    # Assert created_at is an isoformat string or None
    assert isinstance(model_instance.created_at, str)


def test_fileresult_handles_non_existent_file_gracefully(tmp_path: Path):
    """
    Tests graceful error handling (Exception block) when file stat fails.
    """
    # Arrange
    non_existent_path = tmp_path / "does_not_exist.tmp"

    # Act
    result = mod.FileResult(file_path=non_existent_path, input_path=tmp_path)

    # Assert
    assert result.size == -1
    assert result.content_status == FileContentStatus.UNKNOWN
    assert result.created_at is None
    assert result.modified_at is None


def test_database_config_model():
    config = DatabaseConfig(
        host="localhost",
        dbname="test_db",
        user="test_user",
        password="test_pass",
    )
    assert config.host == "localhost"
    assert config.user == "test_user"
    assert config.password == "test_pass"

    assert (
        config.conn_info
        == "host=localhost port=5432 dbname=test_db user=test_user password=test_pass"
    )
