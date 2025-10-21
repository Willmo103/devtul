from contextlib import contextmanager
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy import create_engine
from devtul.core.config import INTERFACE_DB_URL
import psycopg2 as pg

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
