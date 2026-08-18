import os
import psycopg2
from psycopg2.extras import RealDictCursor
from contextlib import contextmanager
from dotenv import load_dotenv

load_dotenv()

DB_CONFIG = {
    "dbname": os.getenv("POSTGRES_DB"),
    "user": os.getenv("POSTGRES_USER"),
    "password": os.getenv("POSTGRES_PASSWORD"),
    "host": os.getenv("POSTGRES_HOST"),
    "port": os.getenv("POSTGRES_PORT", "5432")
}

@contextmanager
def get_db_cursor():
    conn = psycopg2.connect(**DB_CONFIG)
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    try:
        yield cursor
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        cursor.close()
        conn.close()