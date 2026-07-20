from .line import push_message
from .video_repository import (
    acquire_notification_claim,
    complete_notification,
    release_notification_claim,
)
from .youtube import YouTubeNotification


async def notify_video(notification: YouTubeNotification) -> bool:
    """Send one notification. Return False when another request owns it."""
    if not acquire_notification_claim(notification.video_id):
        return False

    message = (
        "YouTube新着動画\n\n"
        f"{notification.title}\n\n"
        f"{notification.video_url}"
    )

    try:
        await push_message(message)
    except Exception:
        release_notification_claim(notification.video_id)
        raise

    complete_notification(notification.video_id, notification.title)
    return True
