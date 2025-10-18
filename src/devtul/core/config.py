from pathlib import Path
from dotenv import load_dotenv
from os import environ as env


_env_path = Path.home() / ".env"
_app_data = Path.home() / ".devtul"
_app_data.mkdir(exist_ok=True)
scripts_dir = _app_data / "scripts"
scripts_dir.mkdir(exist_ok=True)


load_dotenv(dotenv_path=_env_path)

INTERFACE_DB_URL = env["DB_CONN_INFO"]
EDITOR = env.get("EDITOR", "nano")
