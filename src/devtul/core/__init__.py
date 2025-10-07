"""
Core utilities for devtul.
"""

from .constants import IGNORE_PARTS, IGNORE_PATTERNS
from .filters import (
    apply_filters,
    get_all_files,
    process_paths_for_subdir,
    should_ignore_path,
)
from .git_utils import (
    format_git_metadata_table,
    get_git_files,
    get_git_metadata,
)
from .output import (
    build_tree_structure,
    search_in_file,
    write_output,
)

__all__ = [
    "IGNORE_PARTS",
    "IGNORE_PATTERNS",
    "apply_filters",
    "build_tree_structure",
    "format_git_metadata_table",
    "get_all_files",
    "get_git_files",
    "get_git_metadata",
    "process_paths_for_subdir",
    "search_in_file",
    "should_ignore_path",
    "write_output",
]
