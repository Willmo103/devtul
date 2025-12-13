from datetime import datetime, timezone
from pathlib import Path
from git import Optional
from pydantic import BaseModel, Field, computed_field
from devtul.core.constants import FileContentStatus
import yaml


class FileResult:
    full_path: Path
    relative_path: Path
    size: int
    empty_state: FileContentStatus
    created_at: Optional[datetime]
    modified_at: Optional[datetime]

    def __init__(
        self,
        file_path: Path,
        input_path: Path,
    ):
        self.full_path = file_path.resolve()
        self.relative_path = file_path.resolve().relative_to(input_path.resolve())
        try:
            stat = file_path.stat(
                follow_symlinks=False
            )  # not using os.stat to avoid symlink issues
            self.size = stat.st_size
            self.empty_state = (
                FileContentStatus.EMPTY
                if self.size == 0
                else FileContentStatus.NON_EMPTY
            )
            self.created_at = datetime.fromtimestamp(
                stat.st_birthtime
            ) or datetime.fromtimestamp(stat.st_ctime_ns / 1e9)
            self.modified_at = datetime.fromtimestamp(
                stat.st_mtime
            ) or datetime.fromtimestamp(stat.st_mtime_ns / 1e9)
        except Exception:
            self.size = -1
            self.empty_state = FileContentStatus.UNKNOWN
            self.created_at = None
            self.modified_at = None


class MarkedDirectoryResult(BaseModel):
    """
    Schema for results from marked directory file retrieval.

    Attributes:
        directory: The path of the marked directory
        files: List of file paths within the marked directory
    """

    directory: str = Field(..., description="Path of the marked directory")
    marker_match: str = Field(
        ..., description="The marker pattern used to identify the directory"
    )
    files: list[str] = Field(
        ..., description="List of file paths within the marked directory"
    )


class GitCommit(BaseModel):
    """Schema for git commit information."""

    hash: str = Field(..., description="Commit hash")
    message: str = Field(..., description="Commit message")
    author: str = Field(..., description="Author of the commit")
    date: str = Field(..., description="Date of the commit")

    def to_yaml(self):
        return yaml.dump(self.model_dump())


class GitMetadata(BaseModel):
    """Schema for git repository metadata."""

    remotes: dict = Field(..., description="Git remotes")
    current_branch: str = Field(..., description="Current branch name")
    branches: list = Field(..., description="List of all branches")
    latest_commit: GitCommit = Field(..., description="Latest commit information")
    uncommitted_changes: bool = Field(
        ..., description="Whether there are uncommitted changes"
    )
    untracked_files: int = Field(..., description="Number of untracked files")

    def to_yaml(self):
        return yaml.dump(self.model_dump())


class RepoMarkdownHeader(BaseModel):
    """
    Schema for repository markdown header metadata.

    Attributes:
        generated_at: str
        repo_path: str
        file_count: int
        files_included: int
    """

    generated_at: str = Field(
        default_factory=lambda: datetime.now(tz=timezone.utc).isoformat(),
        description="Timestamp of when the markdown was generated",
    )
    repo_path: str = Field(..., description="Path of the repository")
    file_count: int = Field(..., description="Total number of files in the repository")
    files_included: int = Field(
        ..., description="Number of files included after filtering"
    )

    def to_yaml(self):
        return yaml.dump(self.model_dump())

    def frontmatter(self) -> str:
        """Render the header as a YAML frontmatter string."""
        yaml_content = self.to_yaml()
        return f"---\n{yaml_content}---\n"


class markdownSchema(BaseModel):
    """Schema for markdown metadata."""

    root_path: Optional[str] = Field(None, description="Root path of the repository")
    total_files: Optional[int] = Field(0, description="Total number of files")
    included_files: Optional[int] = Field(
        None, description="Number of included files after filtering"
    )
    generated_at: Optional[datetime] = Field(
        default_factory=lambda: datetime.now(tz=timezone.utc).isoformat(),
        description="Timestamp of when the metadata was generated",
    )
    tree: str = Field(..., description="Tree structure of the files in markdown format")
    git_metadata: dict = Field(
        None, description="Git metadata information", alias="git_metadata"
    )
    markdown_content: str = Field(..., description="Full markdown content")


class FileSearchMatch(BaseModel):
    """Schema for a search match within a file."""

    file_path: Optional[str] = Field(
        None, description="Path of the file containing the match"
    )
    relative_path: Optional[str] = Field(
        None, description="Relative path of the file from the search root"
    )
    line_number: Optional[int] = Field(None, description="Line number of the match")
    content: Optional[str] = Field(None, description="Content of the matching line")
    error: Optional[str] = Field(None, description="Error message if any occurred")

    def is_error(self) -> bool:
        """Check if this match represents an error."""
        return self.error is not None

    def as_line(self) -> Optional[str]:
        """Format the match as a single line string."""
        if self.is_error():
            return None
        if self.file_path is None and self.relative_path is not None:
            self.file_path = Path(self.relative_path).resolve().as_posix()
        return f"{Path(self.file_path).resolve().as_posix()}:{self.line_number}"


class FileMatchResults(BaseModel):
    """Schema for file match results."""

    search_term: str = Field(..., description="The term that was searched for")
    total_matches: int = Field(..., description="Total number of matches found")
    matches: list[FileSearchMatch] = Field(
        ..., description="List of file search matches"
    )

    def to_yaml(self) -> str:
        """Convert the results to a YAML string."""
        return yaml.dump(self.model_dump())


class UserTemplate(BaseModel):
    """Schema for user-defined templates stored in the database."""

    name: str
    content: str


class DatabaseConfig(BaseModel):
    """Base Configuration"""

    host: str = Field("localhost", description="Database host")
    user: str = Field("admin", description="Database user")
    password: str = Field(..., description="Database password")  # No default, required


class DatabaseConfig_DBModel(DatabaseConfig):
    """Pydantic model for the sqlite-utils database representation of DatabaseConfig.
    The only vairance is the type of the `conn_type` feild which is hidden and set from
    the DB_CONN_TYPES enum.
    """

    conn_type: str = Field(..., description="Type of the database connection")


class PostgresDatabaseConfig(DatabaseConfig):
    port: int = Field(5432, description="Port")
    dbname: str = Field("postgres", description="Database Name")

    @computed_field
    def conn_info(self) -> str:
        return f"dbname='{self.dbname}' user='{self.user}' host='{self.host}' password='{self.password}' port='{self.port}'"


class MySQLDatabaseConfig(DatabaseConfig):
    port: int = Field(3306, description="Port")
    dbname: str = Field(..., description="Database Name")


class MsSQLDatabaseConfig(DatabaseConfig):
    port: int = Field(1433, description="Port")
    dbname: str = Field("master", description="Database Name")


class SQLiteDatabaseConfig(BaseModel):
    file_path: str = Field(
        "data.db", description="Path to SQLite file relative to execution"
    )


class MongoDBDatabaseConfig(BaseModel):
    uri: str = Field("mongodb://localhost:27017", description="MongoDB Connection URI")


class HostService(BaseModel):
    id: Optional[int] = Field(None, description="Database ID")
    name: str = Field(..., description="Service name")
    port: Optional[int] = Field(None, description="Service port")
    status: str = Field(
        "undefined", description="Service status (e.g., running, stopped)"
    )
    dsescription: Optional[str] = Field(None, description="Service description")
    host_ip: Optional[str] = Field(None, description="IP address of the host")


class NetworkHost(BaseModel):
    id: Optional[int] = Field(None, description="Database ID")
    hostname: str = Field(..., description="Server hostname")
    ip_address: str = Field(..., description="Server IP address")
    mac_address: Optional[str] = Field(None, description="Server MAC address")
    description: Optional[str] = Field(None, description="Server description")


class ScanningRoot(BaseModel):
    id: Optional[int] = Field(None, description="Database ID")
    path: str = Field(..., description="Path to the scanning root")
    description: Optional[str] = Field(
        None, description="Description of the scanning root"
    )
