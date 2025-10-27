# Issues

## Tree command does not render tree on with no-git option

**Discovered:** 10/27/2025
**Description**
When using the `dt tree` command with the `--no-git` option, the output does not render a proper tree structure. Instead, it lists all files and directories without any indentation or hierarchy, making it difficult to visualize the structure of the repository.
**Steps to Reproduce:**

1. Navigate to a Git repository in the terminal.
2. Run the command `uv run dt tree --no-git`.
3. Observe the output.

**Example Output**:

```PowerShell
PS (master.db) - [C:\src\devtul] > uv run dt tree --no-git
C:/src/devtul/
├── .git\COMMIT_EDITMSG
├── .git\FETCH_HEAD
├── .git\HEAD
├── .git\ORIG_HEAD
├── .git\config
├── .git\description
├── .git\index
├── .git\packed-refs
├── commands\__init__.py
├── commands\dirs.py
├── commands\empty_items.py
├── commands\find.py
├── commands\list_files.py
├── commands\markdown.py
├── commands\metadata.py
├── commands\tree.py
├── core\__init__.py
├── core\config.py
├── core\constants.py
├── core\file_utils.py
├── core\filters.py
├── core\git_utils.py
├── core\utils.py
├── db\database.py
├── db\models.py
├── db\schemas.py
├── db\session.py
├── devtul\.flake8
├── devtul\.gitignore
├── devtul\.python-version
├── devtul\__init__.py
├── devtul\devtul.spec
├── devtul\main.py
├── devtul\pyproject.toml
├── devtul\uv.lock
├── heads\dev-master
├── heads\master
├── hooks\applypatch-msg.sample
├── hooks\commit-msg.sample
├── hooks\fsmonitor-watchman.sample
├── hooks\post-update.sample
├── hooks\pre-applypatch.sample
├── hooks\pre-commit.sample
├── hooks\pre-merge-commit.sample
├── hooks\pre-push.sample
├── hooks\pre-rebase.sample
├── hooks\pre-receive.sample
├── hooks\prepare-commit-msg.sample
├── hooks\sendemail-validate.sample
├── hooks\update.sample
├── info\exclude
├── origin\HEAD
├── origin\Willmo103-patch-1
├── origin\master
├── tags\V0.1.1-alpha
├── tags\v0.1.2-alpha
└── tags\v0.1.3
```

In the preceding output, the tree structure is displayed, but there is no indentation or hierarchy shown for the files and directories, even though the tree characters are present.

**Expected Behavior**
When using the `--no-git` option with the `dt tree` command, the output should still render a proper tree structure with correct indentation and hierarchy for files and directories, similar to when Git metadata is available.

**Example of Expected Behavior using default `--git` option**

```PowerShell
PS (master.db) - [C:\src\devtul] > uv run dt tree
C:/src/devtul/
├── src/
│   └── devtul/
│       ├── commands/
│       │   ├── __init__.py
│       │   ├── dirs.py
│       │   ├── empty_items.py
│       │   ├── find.py
│       │   ├── list_files.py
│       │   ├── markdown.py
│       │   ├── metadata.py
│       │   └── tree.py
│       ├── core/
│       │   ├── db/
│       │   │   ├── database.py
│       │   │   ├── models.py
│       │   │   ├── schemas.py
│       │   │   └── session.py
│       │   ├── templates/
│       │   │   └── base.md.jinja
│       │   ├── __init__.py
│       │   ├── config.py
│       │   ├── constants.py
│       │   ├── file_utils.py
│       │   ├── filters.py
│       │   ├── git_utils.py
│       │   └── utils.py
│       ├── __init__.py
│       └── main.py
├── .flake8
├── .gitignore
├── .python-version
└── pyproject.toml
```

---
