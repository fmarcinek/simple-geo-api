import os

import psycopg2
from psycopg2 import OperationalError

DATABASE_URL = os.getenv("DATABASE_URL")


def test_connection():
    try:
        conn = psycopg2.connect(DATABASE_URL)
        print("Connection successful!")
        conn.close()
    except OperationalError as e:
        assert False, f"Connection failed: {e}"
