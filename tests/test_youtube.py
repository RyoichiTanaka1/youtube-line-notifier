import unittest

from app.youtube import parse_youtube_notification


def atom_xml(
    *,
    video_id: str | None = "video-1",
    channel_id: str | None = "channel-1",
    title: str | None = "Test video",
    include_entry: bool = True,
) -> bytes:
    entry = ""
    if include_entry:
        fields = []
        if video_id is not None:
            fields.append(f"<yt:videoId>{video_id}</yt:videoId>")
        if channel_id is not None:
            fields.append(f"<yt:channelId>{channel_id}</yt:channelId>")
        if title is not None:
            fields.append(f"<title>{title}</title>")
        entry = f"<entry>{''.join(fields)}</entry>"

    return (
        '<feed xmlns="http://www.w3.org/2005/Atom" '
        'xmlns:yt="http://www.youtube.com/xml/schemas/2015">'
        f"{entry}</feed>"
    ).encode()


class ParseYouTubeNotificationTest(unittest.TestCase):
    def test_parses_valid_atom_xml(self) -> None:
        notification = parse_youtube_notification(atom_xml())

        self.assertEqual(notification.video_id, "video-1")
        self.assertEqual(notification.channel_id, "channel-1")
        self.assertEqual(notification.title, "Test video")
        self.assertEqual(
            notification.video_url,
            "https://www.youtube.com/watch?v=video-1",
        )

    def test_rejects_malformed_xml(self) -> None:
        with self.assertRaisesRegex(ValueError, "Invalid Atom XML"):
            parse_youtube_notification(b"<feed>")

    def test_rejects_xml_without_entry(self) -> None:
        with self.assertRaisesRegex(ValueError, "Atom entry not found"):
            parse_youtube_notification(atom_xml(include_entry=False))

    def test_rejects_missing_required_fields(self) -> None:
        cases = (
            ({"video_id": None}, "videoId not found"),
            ({"channel_id": None}, "channelId not found"),
            ({"title": None}, "title not found"),
        )
        for arguments, message in cases:
            with self.subTest(arguments=arguments):
                with self.assertRaisesRegex(ValueError, message):
                    parse_youtube_notification(atom_xml(**arguments))
