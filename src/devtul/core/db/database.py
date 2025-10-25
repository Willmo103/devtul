from contextlib import contextmanager

import psycopg2 as pg
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from devtul.core.config import INTERFACE_DB_URL

Base = declarative_base()
engine = create_engine(INTERFACE_DB_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@contextmanager
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@contextmanager
def get_postgres_session():
    conn = pg.connect(INTERFACE_DB_URL)
    try:
        yield conn
    finally:
        conn.close()
