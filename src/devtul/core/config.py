from os import environ as env
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv

_env_path = Path.home() / ".env"
_app_data = Path.home() / ".devtul"
_app_data.mkdir(exist_ok=True)
scripts_dir = _app_data / "scripts"
scripts_dir.mkdir(exist_ok=True)
app_root = Path(__file__).parent.parent.resolve()

load_dotenv(dotenv_path=_env_path)

INTERFACE_DB_URL = env["DB_CONN_INFO"]
EDITOR = env["EDITOR"] if "EDITOR" in env else "code -w"
DOT_ENV_PATH = _env_path
SSH_PATH: Optional[Path] = (Path().home() / ".ssh") if Path().home().exists() else None
GIT_CONFIG: Optional[Path] = (
    (Path().home() / ".gitconfig") if Path().home().exists() else None
)
TEMPLATES_DIR = app_root / "templates"
