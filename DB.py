import os
import psycopg
from psycopg.rows import dict_row


def connect():
    return psycopg.connect(os.environ.get('DATABASE_URL', 'postgresql://localhost/ruins_events'), row_factory=dict_row)


def fetch_all(query, params=()):
    with connect() as conn:
        return conn.execute(query, params).fetchall()


def fetch_one(query, params=()):
    with connect() as conn:
        return conn.execute(query, params).fetchone()


def execute(query, params=()):
    with connect() as conn:
        return conn.execute(query, params).rowcount
