# logger.py

import sqlite3
from datetime import datetime
from classifier import classify_command

DB_NAME = "db.sqlite3"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            session_id TEXT,
            ip_address TEXT,
            command TEXT,
            intent TEXT,
            response TEXT
        )
    """)

    conn.commit()
    conn.close()


def log_event(session_id, ip_address, command, response):
    intent = classify_command(command)
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO events (timestamp, session_id, ip_address, command, intent, response)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (timestamp, session_id, ip_address, command, intent, response))

    conn.commit()
    conn.close()

    return intent


def get_recent_events(limit=20):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT timestamp, session_id, ip_address, command, intent, response
        FROM events
        ORDER BY id DESC
        LIMIT ?
    """, (limit,))

    rows = cursor.fetchall()
    conn.close()
    return rows


def get_intent_counts():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT intent, COUNT(*)
        FROM events
        GROUP BY intent
    """)

    rows = cursor.fetchall()
    conn.close()
    return rows


def get_top_commands(limit=5):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT command, COUNT(*)
        FROM events
        GROUP BY command
        ORDER BY COUNT(*) DESC
        LIMIT ?
    """, (limit,))

    rows = cursor.fetchall()
    conn.close()
    return rows


init_db()