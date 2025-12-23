from os import environ as env
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv
from jinja2 import Environment, FileSystemLoader

_env_path = Path.home() / ".env"
_app_data = Path.home() / ".devtul"
_app_data.mkdir(exist_ok=True)
scripts_dir = _app_data / "scripts"
scripts_dir.mkdir(exist_ok=True)
app_root = Path(__file__).parent.parent.resolve()
_templates_dir = Path(__file__).parent / "templates"

load_dotenv(dotenv_path=_env_path)

EDITOR = env["EDITOR"] if "EDITOR" in env else "code -w"
DOT_ENV_PATH = _env_path
SSH_PATH: Optional[Path] = (Path().home() / ".ssh") if Path().home().exists() else None
GIT_CONFIG: Optional[Path] = (
    (Path().home() / ".gitconfig") if Path().home().exists() else None
)
TEMPLATES_DIR = _templates_dir
APP_DATA = _app_data
_loader = FileSystemLoader(str(TEMPLATES_DIR.resolve().as_posix()))
JINJA_ENVIRONMENT = Environment(loader=_loader, autoescape=True)
