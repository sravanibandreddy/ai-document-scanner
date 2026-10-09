
from pathlib import Path
import json
import sqlite3

DB_PATH = Path(__file__).resolve().parent / "scans.db"


def get_connection():
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    return connection


def init_db():
    with get_connection() as connection:
        connection.execute("""
            CREATE TABLE IF NOT EXISTS scans (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                filename TEXT NOT NULL,
                extracted_text TEXT NOT NULL,
                information TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)


def save_scan(filename, extracted_text, information):
    with get_connection() as connection:
        cursor = connection.execute(
            """
            INSERT INTO scans (filename, extracted_text, information)
            VALUES (?, ?, ?)
            """,
            (
                filename,
                extracted_text,
                json.dumps(information, ensure_ascii=False)
            )
        )
        return cursor.lastrowid


def get_all_scans():
    with get_connection() as connection:
        rows = connection.execute(
            """
            SELECT id, filename, extracted_text, information, created_at
            FROM scans
            ORDER BY id DESC
            """
        ).fetchall()

    return [dict(row) for row in rows]


def get_scan_by_id(scan_id):
    with get_connection() as connection:
        row = connection.execute(
            """
            SELECT id, filename, extracted_text, information, created_at
            FROM scans
            WHERE id = ?
            """,
            (scan_id,)
        ).fetchone()

    if row is None:
        return None

    result = dict(row)
    try:
        result["information"] = json.loads(result["information"])
    except (json.JSONDecodeError, TypeError):
        result["information"] = {}

    return result
