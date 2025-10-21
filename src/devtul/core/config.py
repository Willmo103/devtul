from pathlib import Path
from typing import Optional
from dotenv import load_dotenv
from os import environ as env


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

print(DOT_ENV_PATH.exists())  # Debug line to check if .env is loaded
if SSH_PATH:
    print(SSH_PATH.exists())  # Debug line to check if .ssh path is correct
if GIT_CONFIG:
    print(GIT_CONFIG.exists())  # Debug line to check if .gitconfig path is correct
