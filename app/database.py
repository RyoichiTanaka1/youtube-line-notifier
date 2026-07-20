import sqlite3
from contextlib import closing

DB_PATH = "/data/notifier.db"


def get_connection() -> sqlite3.Connection:
    return sqlite3.connect(DB_PATH, timeout=30.0)


def init_db() -> None:
    with closing(get_connection()) as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS notified_video (
                video_id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                notified_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS notification_claim (
                video_id TEXT PRIMARY KEY,
                claimed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        conn.commit()
