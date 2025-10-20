from contextlib import contextmanager
import psycopg2 as pg
from devtul.core.config import INTERFACE_DB_URL
# from devtul.core.db import database



@contextmanager
def session():
    conn = pg.connect(INTERFACE_DB_URL)
    try:
        yield conn
    finally:
        conn.close()
