from contextlib import closing

from .database import get_connection


def is_notified(video_id: str) -> bool:
    with closing(get_connection()) as conn:
        row = conn.execute(
            "SELECT 1 FROM notified_video WHERE video_id = ?",
            (video_id,),
        ).fetchone()
    return row is not None


def acquire_notification_claim(video_id: str) -> bool:
    """Atomically reserve a video unless it is complete or already reserved."""
    with closing(get_connection()) as conn:
        cursor = conn.execute(
            """
            INSERT OR IGNORE INTO notification_claim(video_id)
            SELECT ?
            WHERE NOT EXISTS (
                SELECT 1 FROM notified_video WHERE video_id = ?
            )
            """,
            (video_id, video_id),
        )
        conn.commit()
        return cursor.rowcount == 1


def complete_notification(video_id: str, title: str) -> None:
    with closing(get_connection()) as conn:
        conn.execute("BEGIN IMMEDIATE")
        conn.execute(
            """
            INSERT INTO notified_video(video_id, title)
            VALUES(?, ?)
            """,
            (video_id, title),
        )
        conn.execute(
            "DELETE FROM notification_claim WHERE video_id = ?",
            (video_id,),
        )
        conn.commit()


def release_notification_claim(video_id: str) -> None:
    with closing(get_connection()) as conn:
        conn.execute(
            "DELETE FROM notification_claim WHERE video_id = ?",
            (video_id,),
        )
        conn.commit()
