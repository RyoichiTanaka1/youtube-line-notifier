from dataclasses import dataclass
from xml.etree import ElementTree


ATOM_NS = "http://www.w3.org/2005/Atom"
YT_NS = "http://www.youtube.com/xml/schemas/2015"


@dataclass
class YouTubeNotification:
    video_id: str
    channel_id: str
    title: str
    video_url: str


def parse_youtube_notification(xml_body: bytes) -> YouTubeNotification:
    root = ElementTree.fromstring(xml_body)

    entry = root.find(f"{{{ATOM_NS}}}entry")
    if entry is None:
        raise ValueError("Atom entry not found")

    video_id = entry.findtext(f"{{{YT_NS}}}videoId")
    channel_id = entry.findtext(f"{{{YT_NS}}}channelId")
    title = entry.findtext(f"{{{ATOM_NS}}}title")

    if not video_id:
        raise ValueError("videoId not found")

    if not channel_id:
        raise ValueError("channelId not found")

    if not title:
        raise ValueError("title not found")

    return YouTubeNotification(
        video_id=video_id,
        channel_id=channel_id,
        title=title,
        video_url=f"https://www.youtube.com/watch?v={video_id}",
    )
