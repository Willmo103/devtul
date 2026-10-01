"""
Command abstractions for DevTul.
Provides BaseCommand with standardized usage/examples documentation synthesis,
and FileCommand with centralized, Unix-like path gathering, filtering, and debugging.
"""

from abc import ABC, abstractmethod
from datetime import datetime, timezone
from pathlib import Path
import sys
import time
from typing import Any, Callable, List, Optional, Tuple

import typer

from devtul.core.constants import FileContentStatus
from devtul.core.file_utils import (
    filter_gathered_paths_by_default_ignores,
    gather_all_paths,
    is_git_repo,
    try_gather_all_git_tracked_paths,
)
from devtul.core.models import (
    CommandResult,
    FileFilterOptions,
    FilePath,
    FileResult,
    FilterMetrics,
)
from devtul.core.path_matcher import UnixPathMatcher


class BaseCommand(ABC):
    """
    Abstract base class for all DevTul CLI commands.
    Enforces standardized metadata, usage strings, examples, and help generation.
    """

    name: str = ""
    help: str = ""

    @property
    @abstractmethod
    def usage(self) -> str:
        """Command usage line (e.g. 'dt tree [PATH] [OPTIONS]')."""
        pass

    @property
    @abstractmethod
    def examples(self) -> list[str]:
        """Concrete usage examples for the command."""
        pass

    def get_formatted_help(self) -> str:
        """
        Synthesize help text, usage instructions, and examples into a structured docstring.
        """
        doc = self.help.strip()
        if self.usage:
            doc += f"\n\nUsage:\n  {self.usage.strip()}"
        if self.examples:
            doc += "\n\nExamples:\n" + "\n".join(f"  {ex.strip()}" for ex in self.examples)
        return doc

    def register(self, app: typer.Typer) -> None:
        """
        Register this command onto a Typer application instance.
        Subclasses should implement registration or bind their execution method.
        """
        pass


class FileCommand(BaseCommand):
    """
    Abstract base class for commands that operate on files in a repository or directory.
    Provides standardized input filtering, Unix-like path matching, and debug logging.
    """

    def debug_log(self, message: str) -> None:
        """Output debug message to stderr."""
        sys.stderr.write(f"{message}\n")
        sys.stderr.flush()

    def gather_and_filter_files(
        self, options: FileFilterOptions
    ) -> Tuple[List[FileResult], FilterMetrics]:
        """
        Execute the centralized file discovery, filtering, and metric collection pipeline.
        """
        start_time = time.perf_counter()
        target_path = options.path.resolve()
        has_git = is_git_repo(target_path)
        git_mode = options.git and has_git

        if options.debug:
            self.debug_log(f"[DEBUG] Target path: {target_path} (git_mode={git_mode}, has_git={has_git})")

        # 1. Path Gathering
        if git_mode:
            paths = try_gather_all_git_tracked_paths(target_path)
        else:
            paths = gather_all_paths(target_path)

        total_scanned = len(paths)

        # 2. Default ignore filtering for non-git runs
        if not git_mode and not options.no_ignore:
            paths = filter_gathered_paths_by_default_ignores(paths, root_path=target_path)

        # 3. Domain Model Wrapping
        file_results: List[FileResult] = []
        for p in paths:
            if p.is_file():
                file_results.append(FileResult(p, target_path))

        # 4. Pattern Matcher setup
        debug_cb = self.debug_log if options.debug else None
        match_matcher = (
            UnixPathMatcher(options.match, root_path=target_path, debug_callback=debug_cb)
            if options.match
            else None
        )
        exclude_matcher = (
            UnixPathMatcher(options.exclude, root_path=target_path, debug_callback=debug_cb)
            if options.exclude
            else None
        )

        filtered: List[FileResult] = []
        matched_count = 0
        excluded_count = 0
        empty_count = 0

        for res in file_results:
            rel_posix = res.relative_path.as_posix()

            # Check match patterns
            if match_matcher:
                is_match, pat, reason = match_matcher.matches(res.relative_path)
                if not is_match:
                    if options.debug:
                        self.debug_log(f"[DEBUG] File '{rel_posix}' omitted (did not match any match pattern)")
                    continue
                matched_count += 1
            else:
                matched_count += 1

            # Check exclude patterns
            if exclude_matcher:
                is_excl, pat, reason = exclude_matcher.matches(res.relative_path)
                if is_excl:
                    excluded_count += 1
                    if options.debug:
                        self.debug_log(f"[DEBUG] File '{rel_posix}' excluded by pattern '{pat}' ({reason})")
                    continue

            # Check empty status
            if not options.include_empty and res.content_status == FileContentStatus.EMPTY:
                empty_count += 1
                if options.debug:
                    self.debug_log(f"[DEBUG] File '{rel_posix}' omitted (empty file)")
                continue

            filtered.append(res)

        elapsed = time.perf_counter() - start_time
        metrics = FilterMetrics(
            total_scanned=total_scanned,
            matched_count=matched_count,
            excluded_count=excluded_count,
            empty_count=empty_count,
            duration_seconds=round(elapsed, 4),
        )

        if options.debug:
            self.debug_log(
                f"[DEBUG] File pipeline finished in {metrics.duration_seconds}s: "
                f"{len(filtered)} selected, {excluded_count} excluded, {empty_count} empty."
            )

        return filtered, metrics
