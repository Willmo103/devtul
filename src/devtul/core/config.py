from pathlib import Path
from sqlite_utils import Database
from dotenv import load_dotenv
from os import environ as env


_env_path = Path.home() / ".env"
_app_data = Path.home() / ".devtul"
_app_data.mkdir(exist_ok=True)

load_dotenv(dotenv_path=_env_path)

INTERFACE_DB_URL = env["DB_CONN_INFO"]

db = Database(_app_data / "devtul.db")
