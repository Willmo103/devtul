from contextlib import contextmanager
import psycopg2 as pg
import devtul.core.config as config  # noqa: F401
from os import environ as env


@contextmanager
def session():
    conn = pg.connect(env["INTERFACE_DB_URL"])
    try:
        yield conn
    finally:
        conn.close()
