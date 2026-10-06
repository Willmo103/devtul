from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

import yaml
from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    computed_field,
    field_serializer,
    model_serializer,
)

from devtul.core.constants import FileContentStatus


class FilePath(BaseModel):
    """
    Decomposed path model representing pathlib.Path attributes.
    Cherrypicked from controller-api for rich cross-platform path inspection.
    """

    name: str
    suffix: str = ""
    suffixes: list[str] = Field(default_factory=list)
    stem: str = ""
    parent: str = ""
    parents: list[str] = Field(default_factory=list)
    anchor: str = ""
    drive: str = ""
    root: str = ""
    parts: list[str] = Field(default_factory=list)
    is_absolute: bool = False

    @property
    def Path(self) -> Path:
        """Reconstruct the original Path object."""
        return Path(*self.parts) if self.parts else Path(self.name)

    @classmethod
    def from_path(cls, path: Path) -> "FilePath":
        resolved = path.resolve()
        return cls(
            name=resolved.name,
            suffix=resolved.suffix,
            suffixes=list(resolved.suffixes),
            stem=resolved.stem,
            parent=str(resolved.parent),
            parents=[str(p) for p in resolved.parents],
            anchor=resolved.anchor,
            drive=resolved.drive,
            root=resolved.root,
            parts=list(resolved.parts),
            is_absolute=resolved.is_absolute(),
        )


class BaseFileStat(BaseModel):
    """
    Pydantic model representing decomposed file statistics across operating systems.
    Cherrypicked from controller-api.
    """

    st_mode: Optional[int] = None
    st_ino: Optional[int] = None
    st_dev: Optional[int] = None
    st_nlink: Optional[int] = None
    st_uid: Optional[int] = None
    st_gid: Optional[int] = None
    st_size: Optional[int] = None
    st_atime: Optional[float] = None
    st_mtime: Optional[float] = None
    st_ctime: Optional[float] = None
    st_atime_ns: Optional[int] = None
    st_mtime_ns: Optional[int] = None
    st_ctime_ns: Optional[int] = None
    st_file_attributes: Optional[int] = None

    @classmethod
    def from_stat(cls, stat_obj: Any) -> "BaseFileStat":
        data = {}
        for attr in [
            "st_mode", "st_ino", "st_dev", "st_nlink", "st_uid", "st_gid",
            "st_size", "st_atime", "st_mtime", "st_ctime",
            "st_atime_ns", "st_mtime_ns", "st_ctime_ns", "st_file_attributes",
        ]:
            if hasattr(stat_obj, attr):
                data[attr] = getattr(stat_obj, attr)
        return cls(**data)

    @classmethod
    def from_path(cls, path: Union[Path, str]) -> "BaseFileStat":
        """Construct BaseFileStat directly from a filesystem path."""
        p = Path(path).resolve()
        return cls.from_stat(p.stat())

    def to_iso_dict(self) -> dict:
        d = self.model_dump()
        for k in ["st_atime", "st_mtime", "st_ctime"]:
            val = d.get(k)
            if val is not None:
                try:
                    d[k] = datetime.fromtimestamp(val, tz=timezone.utc).isoformat()
                except Exception:
                    pass
        return d


class TextFileLine(BaseModel):
    """
    Represents an indexed line in a text file.
    Cherrypicked from controller-api for structured line indexing and search.
    """

    file_id: Optional[str] = None
    line_number: int
    content: str
    content_hash: Optional[str] = None

    @property
    def is_empty(self) -> bool:
        """Check if line consists only of whitespace."""
        return self.content.strip() == ""

    @property
    def line_length(self) -> int:
        """Return length of line content."""
        return len(self.content)


class BaseTextFile(BaseModel):
    """
    Structured text file model with content and enumerated lines.
    Cherrypicked from controller-api.
    """

    path: FilePath
    stat: BaseFileStat
    sha256: Optional[str] = None
    content: Optional[str] = None
    lines: list[TextFileLine] = Field(default_factory=list)

    @classmethod
    def from_file(cls, file_path: Path, read_content: bool = True) -> "BaseTextFile":
        resolved = file_path.resolve()
        st = resolved.stat()
        fp = FilePath.from_path(resolved)
        bs = BaseFileStat.from_stat(st)
        content = None
        lines = []
        if read_content and resolved.is_file():
            try:
                with resolved.open("r", encoding="utf-8", errors="replace") as f:
                    content = f.read()
                    lines = [
                        TextFileLine(
                            file_id=fp.name,
                            line_number=idx + 1,
                            content=line.rstrip("\r\n"),
                        )
                        for idx, line in enumerate(content.splitlines())
                    ]
            except Exception:
                pass
        return cls(path=fp, stat=bs, content=content, lines=lines)

    @classmethod
    def from_path(cls, file_path: Union[Path, str], read_content: bool = True) -> "BaseTextFile":
        """Alias for from_file accepting Path or str."""
        return cls.from_file(Path(file_path), read_content=read_content)


class Paths(BaseModel):
    matched: list[Path] = Field([], description="List of paths that matched the filter")

    @computed_field
    def total_paths(self) -> int:
        return len(self.matched) + len(self.ignored)

    @computed_field
    def matched_count(self) -> int:
        return len(self.matched)


class FilteredPaths(BaseModel):
    matched: list[Path] = Field([], description="List of paths that matched the filter")
    ignored: list[Path] = Field(
        [], description="List of paths that were ignored by the filter"
    )

    @computed_field
    def ignored_count(self) -> int:
        return len(self.ignored)


class FileResult(BaseModel):
    full_path: Path
    relative_path: Path
    size: int = 0
    content_status: FileContentStatus = FileContentStatus.UNKNOWN
    created_at: Optional[datetime] = None
    modified_at: Optional[datetime] = None
    content: Optional[str] = None
    events: list[dict] = Field(default_factory=list)

    model_config = ConfigDict(arbitrary_types_allowed=True)

    def __init__(
        self,
        file_path: Optional[Union[Path, str]] = None,
        input_path: Optional[Union[Path, str]] = None,
        full_path: Optional[Union[Path, str]] = None,
        relative_path: Optional[Union[Path, str]] = None,
        size: Optional[int] = None,
        content_status: Optional[FileContentStatus] = None,
        created_at: Optional[datetime] = None,
        modified_at: Optional[datetime] = None,
        content: Optional[str] = None,
        events: Optional[list[dict]] = None,
        fetch_stat: bool = True,
        **kwargs: Any,
    ):
        if file_path is not None and input_path is not None:
            f_p = Path(file_path).resolve()
            r_p = f_p.relative_to(Path(input_path).resolve())
        elif full_path is not None and relative_path is not None:
            f_p = Path(full_path).resolve() if not isinstance(full_path, Path) else full_path
            r_p = Path(relative_path) if not isinstance(relative_path, Path) else relative_path
        elif file_path is not None:
            f_p = Path(file_path).resolve()
            r_p = f_p
        else:
            f_p = Path(full_path).resolve() if full_path else Path()
            r_p = Path(relative_path) if relative_path else Path()

        calc_size = size if size is not None else 0
        calc_status = (
            content_status if content_status is not None else FileContentStatus.UNKNOWN
        )
        calc_created = created_at
        calc_modified = modified_at

        if fetch_stat and (size is None or created_at is None or modified_at is None):
            try:
                st = f_p.stat(follow_symlinks=False)
                calc_size = st.st_size
                calc_status = (
                    FileContentStatus.EMPTY
                    if calc_size == 0
                    else FileContentStatus.NOT_EMPTY
                )
                if hasattr(st, "st_birthtime"):
                    calc_created = datetime.fromtimestamp(st.st_birthtime)
                elif hasattr(st, "st_ctime_ns"):
                    calc_created = datetime.fromtimestamp(st.st_ctime_ns / 1e9)
                else:
                    calc_created = datetime.fromtimestamp(st.st_ctime)

                calc_modified = datetime.fromtimestamp(st.st_mtime)
            except Exception:
                calc_size = -1
                calc_status = FileContentStatus.UNKNOWN

        super().__init__(
            full_path=f_p,
            relative_path=r_p,
            size=calc_size,
            content_status=calc_status,
            created_at=calc_created,
            modified_at=calc_modified,
            content=content,
            events=events if events is not None else [],
            **kwargs,
        )

    def to_yaml(self) -> str:
        return yaml.dump(self.to_dict())

    def to_dict(self) -> dict:
        return {
            "full_path": self.full_path.as_posix(),
            "relative_path": self.relative_path.as_posix(),
            "size": self.size,
            "content_state": self.content_status.value,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "modified_at": (
                self.modified_at.isoformat() if self.modified_at else None
            ),
            "events": [event for event in self.events],
        }

    def add_event(self, event: dict) -> None:
        self.events.append(event)

    @property
    def file_path_model(self) -> FilePath:
        """Decomposed FilePath model for this file."""
        return FilePath.from_path(self.full_path)

    @property
    def file_stat_model(self) -> BaseFileStat:
        """Decomposed BaseFileStat model for this file."""
        try:
            return BaseFileStat.from_stat(self.full_path.stat(follow_symlinks=False))
        except Exception:
            return BaseFileStat()


class FileResultModel(BaseModel):
    id: Optional[int] = Field(None, description="Database ID")
    scan_date: Optional[str] = Field(
        None, description="Timestamp of when the file was scanned"
    )
    full_path: str = Field(..., description="Full path of the file")
    relative_path: str = Field(..., description="Relative path of the file")
    size: int = Field(..., description="Size of the file in bytes")
    content_state: str = Field(..., description="Empty state of the file")
    created_at: Optional[str] = Field(
        None, description="Creation timestamp of the file"
    )
    modified_at: Optional[str] = Field(
        None, description="Last modified timestamp of the file"
    )

    model_config = ConfigDict(arbitrary_types_allowed=True)


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


class UserTemplate(BaseModel):
    """Schema for user-defined templates stored in the database."""

    name: str
    content: str


class DatabaseConfig(BaseModel):
    """Base Configuration"""

    host: str = Field("localhost", description="Database host")
    user: str = Field("admin", description="Database user")
    password: str = Field(..., description="Database password")  # No default, required
    dbname: Optional[str] = Field(None, description="Database name")
    port: Optional[int] = Field(None, description="Database port")

    @computed_field
    def conn_info(self) -> str:
        return f"host={self.host} port={self.port} dbname={self.dbname} user={self.user} password={self.password}"


class DatabaseConfig_DBModel(DatabaseConfig):
    """Pydantic model for the sqlite-utils database representation of DatabaseConfig.
    The only vairance is the type of the `conn_type` feild which is hidden and set from
    the DB_CONN_TYPES enum.
    """

    conn_type: str = Field(..., description="Type of the database connection")


class PostgresDatabaseConfig(DatabaseConfig):

    def __init__(self, **data):
        super().__init__(**data)
        if self.port is None:
            self.port = 5432
        if self.dbname is None:
            self.dbname = "postgres"


class MySQLDatabaseConfig(DatabaseConfig):

    def __init__(self, **data):
        super().__init__(**data)
        if self.port is None:
            self.port = 3306
        if self.dbname is None:
            self.dbname = "mysql"


class MsSQLDatabaseConfig(DatabaseConfig):

    def __init__(self, **data):
        super().__init__(**data)
        if self.port is None:
            self.port = 1433
        if self.dbname is None:
            self.dbname = "master"


class SQLiteDatabaseConfig(BaseModel):
    file_path: str = Field(
        "data.db", description="Path to SQLite file relative to execution"
    )


class MongoDBDatabaseConfig(DatabaseConfig):
    def __init__(self, **data):
        super().__init__(**data)
        if self.port is None:
            self.port = 27017
        if self.dbname is None:
            self.dbname = "admin"

    @computed_field
    def uri(self) -> str:
        return f"mongodb://{self.user}:{self.password}@{self.host}:{self.port}/{self.dbname}"


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


class FileResultsModel(BaseModel):
    root_path: str = Field(..., description="Root path for the scan")
    total_files: int = Field(..., description="Total number of files scanned")
    scanned_at: str = Field(..., description="Timestamp of when the scan was performed")


class FilterMetrics(BaseModel):
    """Execution metrics for file scanning and filtering operations."""

    total_scanned: int = 0
    matched_count: int = 0
    excluded_count: int = 0
    empty_count: int = 0
    duration_seconds: float = 0.0


class FileFilterOptions(BaseModel):
    """Standardized input options for file gathering and filtering."""

    path: Path = Field(default_factory=Path.cwd)
    match: list[str] = Field(default_factory=list)
    exclude: list[str] = Field(default_factory=list)
    git: bool = True
    include_empty: bool = False
    no_ignore: bool = False
    debug: bool = False

    model_config = ConfigDict(arbitrary_types_allowed=True)


class CommandResult(BaseModel):
    """Base model for structured command execution outputs."""

    command_name: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    success: bool = True
    metadata: dict[str, Any] = Field(default_factory=dict)

    model_config = ConfigDict(arbitrary_types_allowed=True)

    def render(self, format: str = "text") -> str:
        """Render the command result in the specified format."""
        if format == "json":
            return self.model_dump_json(indent=2)
        return str(self)

    def to_speech_summary(self) -> str:
        """Produce a natural language summary suitable for TTS synthesis."""
        status = "successfully" if self.success else "with errors"
        return f"Command {self.command_name} finished {status}."


class FileCommandResult(CommandResult):
    """Structured output for repository and directory file commands."""

    root_path: FilePath
    files: list[Any] = Field(default_factory=list)
    metrics: FilterMetrics = Field(default_factory=FilterMetrics)

    @field_serializer("files", mode="plain", check_fields=False)
    def serialize_files(self, files: list[Any]) -> list[Any]:
        serialized = []
        for f in files:
            if hasattr(f, "relative_path"):
                serialized.append(
                    {
                        "full_path": str(getattr(f, "full_path", "")),
                        "relative_path": getattr(f, "relative_path", Path()).as_posix(),
                        "size": getattr(f, "size", 0),
                        "content_status": (
                            getattr(f, "content_status", "").value
                            if hasattr(getattr(f, "content_status", ""), "value")
                            else str(getattr(f, "content_status", ""))
                        ),
                    }
                )
            elif hasattr(f, "model_dump"):
                serialized.append(f.model_dump())
            else:
                serialized.append(str(f))
        return serialized

    def to_speech_summary(self) -> str:
        count = len(self.files)
        file_word = "file" if count == 1 else "files"
        return f"DevTul {self.command_name} processed {count} {file_word} in {self.root_path.name}."

    def render(self, format: str = "text") -> str:
        if format == "json":
            return self.model_dump_json(indent=2)
        if format == "yaml":
            return yaml.dump(self.model_dump(mode="json"), sort_keys=False)
        return "\n".join(
            getattr(f, "relative_path", Path(str(f))).as_posix()
            if hasattr(f, "relative_path")
            else str(f)
            for f in self.files
        )


class TreeResult(FileCommandResult):
    """Output model for the dt tree command."""

    tree_text: str = ""

    def to_speech_summary(self) -> str:
        count = len(self.files)
        file_word = "file" if count == 1 else "files"
        return f"DevTul tree rendered {count} {file_word} in {self.root_path.name}."

    def render(self, format: str = "text") -> str:
        if format in ["tree", "text"]:
            return self.tree_text
        return super().render(format=format)


class MarkdownResult(FileCommandResult):
    """Output model for the dt md command."""

    header: Optional[RepoMarkdownHeader] = None
    markdown_text: str = ""

    def to_speech_summary(self) -> str:
        count = len(self.files)
        file_word = "file" if count == 1 else "files"
        return f"DevTul markdown generated repository documentation for {count} {file_word}."

    def render(self, format: str = "text") -> str:
        if format in ["md", "markdown", "text"]:
            return self.markdown_text
        return super().render(format=format)


class ListingResult(FileCommandResult):
    """Output model for the dt ls command."""

    relative_paths: list[str] = Field(default_factory=list)

    def to_speech_summary(self) -> str:
        count = len(self.relative_paths)
        file_word = "file" if count == 1 else "files"
        return f"DevTul list found {count} {file_word}."

    def render(self, format: str = "text") -> str:
        if format == "csv":
            import csv
            import io

            output = io.StringIO()
            writer = csv.writer(output, lineterminator="\n")
            writer.writerow(["path"])
            for p in self.relative_paths:
                writer.writerow([p])
            return output.getvalue().strip()
        if format == "json":
            import json

            return json.dumps(self.relative_paths, indent=2)
        if format == "yaml":
            return yaml.dump(self.relative_paths, sort_keys=False)
        return "\n".join(self.relative_paths)


class FindResult(FileCommandResult):
    """Output model for the dt find command."""

    term: str = ""
    matches: list[Any] = Field(default_factory=list)

    def to_speech_summary(self) -> str:
        count = len(self.matches)
        occ_word = "match" if count == 1 else "matches"
        return f"DevTul find located {count} {occ_word} for '{self.term}'."

    def render(self, format: str = "text") -> str:
        if format == "json":
            return self.model_dump_json(indent=2)
        lines = []
        for m in self.matches:
            rel = getattr(m, "relative_path", "")
            ln = getattr(m, "line_number", "")
            cnt = getattr(m, "content", "")
            lines.append(f"{rel}:{ln}: {cnt}")
        return "\n".join(lines)


class StringFilterOptions(BaseModel):
    """Configuration options for StringCommand line and stream filtering."""

    head: Optional[int] = None
    tail: Optional[int] = None
    grep: Optional[str] = None
    sed: Optional[str] = None
    numbered: bool = False
    lines_with: Optional[str] = None


class StringCommandResult(CommandResult):
    """Output model for string-based commands."""

    command_name: str = "string"
    lines: list[str] = Field(default_factory=list)
    total_lines: int = 0

    def to_speech_summary(self) -> str:
        count = len(self.lines)
        line_word = "line" if count == 1 else "lines"
        return f"DevTul processed {count} {line_word}."

    def render(self, format: str = "text") -> str:
        if format == "json":
            return self.model_dump_json(indent=2)
        return "\n".join(self.lines)


class ReprResult(FileCommandResult):
    """Output model for the dt rpr command."""

    command_name: str = "rpr"
    format: str = "md"
    content: Union[str, bytes] = ""
    output_file: Optional[Path] = None

    def to_speech_summary(self) -> str:
        count = len(self.files)
        file_word = "file" if count == 1 else "files"
        return f"DevTul generated {self.format.upper()} representation for {count} {file_word}."

    def render(self, format: str = "text") -> str:
        if isinstance(self.content, str):
            return self.content
        return f"<Binary {self.format.upper()} content: {len(self.content)} bytes>"
