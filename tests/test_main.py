import os
import tempfile
import unittest
from unittest.mock import AsyncMock, patch

os.environ.setdefault("LINE_CHANNEL_ACCESS_TOKEN", "test-token")
os.environ.setdefault("LINE_USER_ID", "test-user")

from fastapi.testclient import TestClient  # noqa: E402

from app import database  # noqa: E402
from app.main import app  # noqa: E402
from tests.test_youtube import atom_xml  # noqa: E402


class WebSubEndpointTest(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_directory = tempfile.TemporaryDirectory()
        self.original_db_path = database.DB_PATH
        database.DB_PATH = os.path.join(
            self.temp_directory.name,
            "notifier.db",
        )
        database.init_db()
        self.client_context = TestClient(app)
        self.client = self.client_context.__enter__()

    def tearDown(self) -> None:
        self.client_context.__exit__(None, None, None)
        database.DB_PATH = self.original_db_path
        self.temp_directory.cleanup()

    def test_health(self) -> None:
        response = self.client.get("/health")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["status"], "ok")

    def test_websub_verification_returns_challenge(self) -> None:
        response = self.client.get(
            "/websub",
            params={
                "hub.mode": "subscribe",
                "hub.topic": (
                    "https://www.youtube.com/feeds/videos.xml?"
                    "channel_id=channel-1"
                ),
                "hub.challenge": "challenge-value",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.text, "challenge-value")

    def test_websub_post_parses_and_deduplicates(self) -> None:
        sender = AsyncMock()
        with patch("app.notification_service.push_message", sender):
            first = self.client.post("/websub", content=atom_xml())
            second = self.client.post("/websub", content=atom_xml())

        self.assertEqual(first.status_code, 200)
        self.assertEqual(first.json()["result"], "notified")
        self.assertEqual(second.status_code, 200)
        self.assertEqual(second.json()["result"], "already_notified")
        sender.assert_awaited_once()

    def test_websub_post_rejects_invalid_xml(self) -> None:
        with patch(
            "app.notification_service.push_message",
            AsyncMock(),
        ) as sender:
            response = self.client.post("/websub", content=b"<feed>")

        self.assertEqual(response.status_code, 400)
        sender.assert_not_awaited()
