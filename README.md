---
updated: 2025-12-11 18:01:16
author: Will Morris
version: devtul 0.1.11
---

# Devtul Command Line Tool

This document provides help information for the Devtul command line tool and its subcommands.

 Usage: dt [OPTIONS] COMMAND [ARGS]...

 Generate tree structures and markdown documentation from git repositories

╭─ Options ─────────────────────────────────────────────────────────────────╮
│ --install-completion          Install completion for the current shell.   │
│ --show-completion             Show completion for the current shell, to   │
│                               copy it or customize the installation.      │
│ --help                        Show this message and exit.                 │
╰───────────────────────────────────────────────────────────────────────────╯
╭─ Commands ────────────────────────────────────────────────────────────────╮
│ tree          Generate a tree structure from git tracked files.           │
│ md            Generate a comprehensive markdown documentation from git    │
│               repository.                                                 │
│ ls            List git tracked files with optional filtering.             │
│ meta          Display git repository metadata.                            │
│ find          Search for a term within git tracked files.                 │
│ find-folder   Find directories containing a specific marker file or       │
│               folder.                                                     │
│ version       Show the DevTul version and exit                            │
│ empty         Locate empty files and folders                              │
│ new           Create new files from templates                             │
╰───────────────────────────────────────────────────────────────────────────╯

 Usage: dt tree [OPTIONS] [PATH]

 Generate a tree structure from git tracked files.

 Creates a visual tree representation of all files tracked by git in the
 specified repository. Uses the same tree characters as standard tree
 commands (├── └── │).
 Examples:     tree ./my-repo     tree ./my-repo --match "*.py" --match
 "*.md" --print     tree ./my-repo --sub-dir src -f tree_output.txt

╭─ Arguments ───────────────────────────────────────────────────────────────╮
│   path      [PATH]  Path to the git repository [default: C:\src\devtul]   │
╰───────────────────────────────────────────────────────────────────────────╯
╭─ Options ─────────────────────────────────────────────────────────────────╮
│ --file     -f                PATH  Output file path                       │
│ --match    -m                TEXT  Pattern to match files (can be used    │
│                                    multiple times)                        │
│ --exclude  -e                TEXT  Pattern to exclude files (overrides    │
│                                    match patterns)                        │
│ --empty        --no-empty          Include empty files                    │
│                                    [default: no-empty]                    │
│ --git          --no-git            Look for git tracked files or all      │
│                                    files                                  │
│                                    [default: git]                         │
│ --help                             Show this message and exit.            │
╰───────────────────────────────────────────────────────────────────────────╯

 Usage: dt find [OPTIONS] TERM

 Search for a term within git tracked files.

 Searches for the specified term in all git tracked files and returns
 matching lines with file names and line numbers. Results can be output as a
 table or JSON format.
 Examples:     find ./my-repo "function"     find ./my-repo "TODO" --match
 "*.py" --print     find ./my-repo "import" --sub-dir src -f
 search_results.json --json

╭─ Arguments ───────────────────────────────────────────────────────────────╮
│ *    term      TEXT  Search term to find in files [required]              │
╰───────────────────────────────────────────────────────────────────────────╯
╭─ Options ─────────────────────────────────────────────────────────────────╮
│ --path                     PATH  Path to the git repository               │
│                                  [default: C:\src\devtul]                 │
│ --file     -f              PATH  Output file path                         │
│ --match    -m              TEXT  Pattern to match files (can be used      │
│                                  multiple times)                          │
│ --exclude  -e              TEXT  Pattern to exclude files (overrides      │
│                                  match patterns)                          │
│ --json                           Output as JSON instead of table          │
│ --table                          Output as table format                   │
│ --git          --no-git          look for git files or all files          │
│                                  [default: git]                           │
│ --help                           Show this message and exit.              │
╰───────────────────────────────────────────────────────────────────────────╯

 Usage: dt find-folder [OPTIONS] [ROOT]

 Find directories containing a specific marker file or folder.

╭─ Arguments ───────────────────────────────────────────────────────────────╮
│   root      [ROOT]  Root path to start searching from                     │
│                     [default: C:\src\devtul]                              │
╰───────────────────────────────────────────────────────────────────────────╯
╭─ Options ─────────────────────────────────────────────────────────────────╮
│ --with-dir                    TEXT  Directory name pattern to look for    │
│ --with-file                   TEXT  Filename pattern to look for          │
│              -r  --recurse          Recurse into subdirectories           │
│ --help                              Show this message and exit.           │
╰───────────────────────────────────────────────────────────────────────────╯

 Usage: dt version [OPTIONS]

 Show the DevTul version and exit

╭─ Options ─────────────────────────────────────────────────────────────────╮
│ --help          Show this message and exit.                               │
╰───────────────────────────────────────────────────────────────────────────╯

 Usage: dt empty [OPTIONS] COMMAND [ARGS]...

 Locate empty files and folders

╭─ Options ─────────────────────────────────────────────────────────────────╮
│ --help          Show this message and exit.                               │
╰───────────────────────────────────────────────────────────────────────────╯
╭─ Commands ────────────────────────────────────────────────────────────────╮
│ files   Locate empty files in the specified path.                         │
│ dirs    Locate empty folders in the specified path.                       │
╰───────────────────────────────────────────────────────────────────────────╯

 Usage: dt new [OPTIONS] COMMAND [ARGS]...

 Create new files from templates

╭─ Options ─────────────────────────────────────────────────────────────────╮
│ --help          Show this message and exit.                               │
╰───────────────────────────────────────────────────────────────────────────╯
╭─ Commands ────────────────────────────────────────────────────────────────╮
│ create   Create a new template                                            │
│ ls       List all user-defined templates in the database                  │
│ edit     Edit a user-defined template in the database                     │
│ make     Create a new file from a user-defined template                   │
╰───────────────────────────────────────────────────────────────────────────╯
