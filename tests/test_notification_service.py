import asyncio
import os
import tempfile
import unittest
from unittest.mock import AsyncMock, patch

os.environ.setdefault("LINE_CHANNEL_ACCESS_TOKEN", "test-token")
os.environ.setdefault("LINE_USER_ID", "test-user")

from app import database  # noqa: E402
from app.notification_service import notify_video  # noqa: E402
from app.video_repository import is_notified  # noqa: E402
from app.youtube import YouTubeNotification  # noqa: E402


def notification(video_id: str = "video-1") -> YouTubeNotification:
    return YouTubeNotification(
        video_id=video_id,
        channel_id="channel-1",
        title="Test video",
        video_url=f"https://www.youtube.com/watch?v={video_id}",
    )


class NotificationServiceTest(unittest.IsolatedAsyncioTestCase):
    def setUp(self) -> None:
        self.temp_directory = tempfile.TemporaryDirectory()
        self.original_db_path = database.DB_PATH
        database.DB_PATH = os.path.join(
            self.temp_directory.name,
            "notifier.db",
        )
        database.init_db()

    def tearDown(self) -> None:
        database.DB_PATH = self.original_db_path
        self.temp_directory.cleanup()

    async def test_concurrent_notifications_send_only_once(self) -> None:
        sender_started = asyncio.Event()
        allow_sender_to_finish = asyncio.Event()

        async def controlled_sender(_message: str) -> None:
            sender_started.set()
            await allow_sender_to_finish.wait()

        with patch(
            "app.notification_service.push_message",
            side_effect=controlled_sender,
        ) as sender:
            first = asyncio.create_task(notify_video(notification()))
            await sender_started.wait()
            second = asyncio.create_task(notify_video(notification()))
            await asyncio.sleep(0)
            allow_sender_to_finish.set()
            results = await asyncio.gather(first, second)

        self.assertEqual(sorted(results), [False, True])
        self.assertEqual(sender.await_count, 1)
        self.assertTrue(is_notified("video-1"))

    async def test_failed_send_is_not_saved_and_can_be_retried(self) -> None:
        failed_sender = AsyncMock(side_effect=RuntimeError("LINE unavailable"))
        with patch(
            "app.notification_service.push_message",
            failed_sender,
        ):
            with self.assertRaisesRegex(RuntimeError, "LINE unavailable"):
                await notify_video(notification())

        self.assertFalse(is_notified("video-1"))

        successful_sender = AsyncMock()
        with patch(
            "app.notification_service.push_message",
            successful_sender,
        ):
            result = await notify_video(notification())

        self.assertTrue(result)
        successful_sender.assert_awaited_once()
        self.assertTrue(is_notified("video-1"))

    async def test_completed_notification_is_skipped(self) -> None:
        sender = AsyncMock()
        with patch("app.notification_service.push_message", sender):
            first = await notify_video(notification())
            second = await notify_video(notification())

        self.assertTrue(first)
        self.assertFalse(second)
        sender.assert_awaited_once()
