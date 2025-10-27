from datetime import datetime, timezone
from pydantic import BaseModel, Field
import yaml


class markdownSchema(BaseModel):
    """Schema for markdown metadata."""

    root_path: str = Field(..., description="Root path of the repository")
    total_files: int = Field(..., description="Total number of files")
    included_files: int = Field(
        ..., description="Number of included files after filtering"
    )
    generated_at: str = Field(
        ..., description="Timestamp of when the metadata was generated"
    )
    tree: str = Field(..., description="Tree structure of the files in markdown format")
    git_metadata: dict = Field(
        None, description="Git metadata information", alias="git_metadata"
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
