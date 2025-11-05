from sqlite_utils import Database
from devtul.core.config import _app_data

db_path = _app_data / "devtul_interface.db"
database = Database(db_path)
