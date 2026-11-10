import subprocess
import sys


def test_library_import_without_cli_dependencies():
    cmd = [
        sys.executable,
        "-c",
        (
            "import sys; "
            "sys.modules['typer'] = None; "
            "sys.modules['rich'] = None; "
            "import devtul; "
            "assert devtul.app is None; "
            "from devtul.core.file_utils import gather_all_paths; "
            "from devtul.core.models import FileResult; "
            "from devtul.core.path_matcher import UnixPathMatcher; "
            "from devtul.git.utils import get_git_metadata; "
            "print('SUCCESS')"
        ),
    ]
    res = subprocess.run(cmd, capture_output=True, text=True, check=True)
    assert "SUCCESS" in res.stdout


def test_main_cli_error_without_cli_dependencies():
    cmd = [
        sys.executable,
        "-c",
        (
            "import sys; "
            "sys.modules['typer'] = None; "
            "sys.modules['rich'] = None; "
            "from devtul.main import main; "
            "main()"
        ),
    ]
    res = subprocess.run(cmd, capture_output=True, text=True)
    assert res.returncode == 1
    assert "DevTul CLI requires the [cli] extra dependencies" in res.stderr
