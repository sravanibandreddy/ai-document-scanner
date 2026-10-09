
import sqlite3
import json
from pathlib import Path


# Store the database in the project folder
BASE_DIR = Path(__file__).resolve().parent
DATABASE_FILE = BASE_DIR / "document_scanner.db"


def get_connection():
    """Create a connection to the SQLite database."""
    connection = sqlite3.connect(DATABASE_FILE)
    connection.row_factory = sqlite3.Row
    return connection


def init_db():
    """Create the scans table if it does not exist."""
    connection = get_connection()

    try:
        connection.execute("""
            CREATE TABLE IF NOT EXISTS scans (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                filename TEXT NOT NULL,
                extracted_text TEXT NOT NULL,
                emails TEXT,
                phone_numbers TEXT,
                dates TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)

        connection.commit()

    finally:
        connection.close()


def save_scan(filename, extracted_text, information):
    """Save a completed scan and its extracted information."""
    emails = information.get("emails", [])
    phone_numbers = information.get("phone_numbers", [])
    dates = information.get("dates", [])

    connection = get_connection()

    try:
        cursor = connection.execute("""
            INSERT INTO scans (
                filename,
                extracted_text,
                emails,
                phone_numbers,
                dates
            )
            VALUES (?, ?, ?, ?, ?)
        """, (
            filename,
            extracted_text,
            json.dumps(emails),
            json.dumps(phone_numbers),
            json.dumps(dates)
        ))

        connection.commit()
        return cursor.lastrowid

    finally:
        connection.close()


def get_all_scans():
    """Return scan history, newest first."""
    connection = get_connection()

    try:
        rows = connection.execute("""
            SELECT id, filename, created_at
            FROM scans
            ORDER BY id DESC
        """).fetchall()

        return [dict(row) for row in rows]

    finally:
        connection.close()


def get_scan_by_id(scan_id):
    """Return one saved scan, or None if it does not exist."""
    connection = get_connection()

    try:
        row = connection.execute("""
            SELECT *
            FROM scans
            WHERE id = ?
        """, (scan_id,)).fetchone()

        if row is None:
            return None

        result = dict(row)

        # Convert the saved JSON strings back to Python lists
        for field in ("emails", "phone_numbers", "dates"):
            try:
                result[field] = json.loads(result[field] or "[]")
            except (json.JSONDecodeError, TypeError):
                result[field] = []

        return result

    finally:
        connection.close()
