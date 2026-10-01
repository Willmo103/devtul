"""
Unix-like path matcher engine for DevTul.
Supports directory-level matching, globstar wildcards, Windows separator normalization,
and basename/full-path matching.
"""

import fnmatch
from pathlib import Path, PurePosixPath
from typing import Callable, Optional, Union


def normalize_pattern(pattern: str, root_path: Optional[Path] = None) -> str:
    """
    Normalize a path or pattern string for cross-platform matching.
    Converts backslashes to forward slashes, strips surrounding quotes,
    strips leading './' or '.\\', and resolves absolute paths relative to root_path if applicable.
    """
    pat = pattern.strip().strip("'\"").replace("\\", "/")
    while pat.startswith("./"):
        pat = pat[2:]

    if root_path is not None:
        try:
            p = Path(pattern.strip().strip("'\""))
            if p.is_absolute():
                pat = p.resolve().relative_to(root_path.resolve()).as_posix()
        except Exception:
            pass

    return pat


class UnixPathMatcher:
    """
    Evaluates Unix/Git-style path patterns against relative file paths.
    """

    def __init__(
        self,
        patterns: list[str],
        root_path: Optional[Path] = None,
        debug_callback: Optional[Callable[[str], None]] = None,
    ):
        self.raw_patterns = patterns
        self.root_path = root_path
        self.debug_callback = debug_callback
        self.normalized_patterns = [
            (raw, normalize_pattern(raw, root_path=root_path))
            for raw in patterns
            if raw.strip()
        ]

    def matches(self, file_path: Union[Path, str]) -> tuple[bool, Optional[str], Optional[str]]:
        """
        Check if file_path matches any of the configured patterns.

        Returns:
            (is_match, matching_pattern, reason)
        """
        if isinstance(file_path, Path):
            rel_posix = file_path.as_posix()
        else:
            rel_posix = file_path.replace("\\", "/")

        while rel_posix.startswith("./"):
            rel_posix = rel_posix[2:]

        parts = rel_posix.split("/")
        basename = parts[-1] if parts else ""
        parent_dirs = parts[:-1]

        pure_path = PurePosixPath(rel_posix)

        for raw_pattern, norm_pattern in self.normalized_patterns:
            # 1. Exact match on normalized path
            if rel_posix == norm_pattern:
                reason = f"exact match on '{norm_pattern}'"
                if self.debug_callback:
                    self.debug_callback(f"[DEBUG] Path '{rel_posix}' matched: {reason}")
                return True, raw_pattern, reason

            # 2. Directory pattern with trailing slash: e.g. 'tests/'
            if norm_pattern.endswith("/"):
                clean_dir = norm_pattern.rstrip("/")
                if rel_posix == clean_dir or rel_posix.startswith(norm_pattern) or f"/{clean_dir}/" in f"/{rel_posix}/":
                    reason = f"directory path match '{norm_pattern}'"
                    if self.debug_callback:
                        self.debug_callback(f"[DEBUG] Path '{rel_posix}' matched: {reason}")
                    return True, raw_pattern, reason

            # 3. Bare directory name without slashes: e.g. 'tests' matching 'tests/test_foo.py'
            if "/" not in norm_pattern:
                if any(fnmatch.fnmatch(folder, norm_pattern) for folder in parent_dirs):
                    reason = f"directory component matched '{norm_pattern}'"
                    if self.debug_callback:
                        self.debug_callback(f"[DEBUG] Path '{rel_posix}' matched: {reason}")
                    return True, raw_pattern, reason

                # Filename / basename match: e.g. '*.py' or '*test*'
                if fnmatch.fnmatch(basename, norm_pattern):
                    reason = f"filename matched '{norm_pattern}'"
                    if self.debug_callback:
                        self.debug_callback(f"[DEBUG] Path '{rel_posix}' matched: {reason}")
                    return True, raw_pattern, reason

            # 4. Glob matching with globstar support
            variants = {norm_pattern}
            if "/**/" in norm_pattern:
                variants.add(norm_pattern.replace("/**/", "/"))
            if norm_pattern.startswith("**/"):
                variants.add(norm_pattern[3:])
            if norm_pattern.endswith("/**"):
                variants.add(norm_pattern[:-3])

            for v in variants:
                if fnmatch.fnmatch(rel_posix, v):
                    reason = f"glob matched '{v}'"
                    if self.debug_callback:
                        self.debug_callback(f"[DEBUG] Path '{rel_posix}' matched: {reason}")
                    return True, raw_pattern, reason

                try:
                    if pure_path.match(v) or pure_path.match(f"**/{v}"):
                        reason = f"pure_path matched '{v}'"
                        if self.debug_callback:
                            self.debug_callback(f"[DEBUG] Path '{rel_posix}' matched: {reason}")
                        return True, raw_pattern, reason
                except Exception:
                    pass

        return False, None, None


def matches_unix_pattern(
    file_path: Union[Path, str],
    pattern: str,
    root_path: Optional[Path] = None,
    debug_callback: Optional[Callable[[str], None]] = None,
) -> bool:
    """Convenience helper to test a single pattern against a path."""
    matcher = UnixPathMatcher([pattern], root_path=root_path, debug_callback=debug_callback)
    is_match, _, _ = matcher.matches(file_path)
    return is_match
