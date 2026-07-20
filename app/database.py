import sqlite3

DB_PATH = "/data/notifier.db"


def get_connection():
    return sqlite3.connect(DB_PATH)


def init_db():

    conn = get_connection()

    conn.execute("""
    CREATE TABLE IF NOT EXISTS notified_video (

        video_id TEXT PRIMARY KEY,
        title TEXT NOT NULL,
        notified_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP

    )
    """)

    conn.commit()
    conn.close()
