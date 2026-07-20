import os
import tempfile
import threading
import unittest
from concurrent.futures import ThreadPoolExecutor

from app import database
from app.video_repository import acquire_notification_claim


class VideoRepositoryConcurrencyTest(unittest.TestCase):
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

    def test_only_one_concurrent_claim_succeeds(self) -> None:
        barrier = threading.Barrier(2)

        def acquire() -> bool:
            barrier.wait()
            return acquire_notification_claim("video-1")

        with ThreadPoolExecutor(max_workers=2) as executor:
            results = list(executor.map(lambda _index: acquire(), range(2)))

        self.assertEqual(sorted(results), [False, True])
