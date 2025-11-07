from datetime import datetime, timezone
from pathlib import Path
from typing import Optional
from pydantic import BaseModel, Field
import yaml


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
