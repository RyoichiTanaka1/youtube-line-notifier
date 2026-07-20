from .database import get_connection


def is_notified(video_id: str):

    conn = get_connection()

    row = conn.execute(
        "SELECT 1 FROM notified_video WHERE video_id=?",
        (video_id,)
    ).fetchone()

    conn.close()

    return row is not None


def save(video_id: str, title: str):

    conn = get_connection()

    conn.execute(
        """
        INSERT INTO notified_video(video_id,title)
        VALUES(?,?)
        """,
        (
            video_id,
            title,
        ),
    )

    conn.commit()
    conn.close()
