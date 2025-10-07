"""
Constants used throughout the devtul package.
"""

# Patterns for file parts to ignore (matched anywhere in path)
IGNORE_PARTS = [
    "uv.lock",
    ".idea",
    ".vscode",
    ".DS_Store",
    "__pycache__",
    "coverage.xml",
    ".python-version",
    "node_modules",
    ".git",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
    ".tox",
    ".eggs",
    "*.egg-info",
    "dist",
    "build",
    ".venv",
    "venv",
]

# Glob patterns to ignore when scanning filesystem
IGNORE_PATTERNS = [
    "*cache*",
    "*.pyc",
    "*.pyo",
    "*.pyd",
    ".DS_Store",
    "*.so",
    "*.dylib",
    "*.dll",
    "Thumbs.db",
    "*.swp",
    "*.swo",
    "*~",
    ".*.swp",
]
