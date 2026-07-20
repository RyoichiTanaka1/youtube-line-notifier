from datetime import datetime, timezone
import logging

import httpx
from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.responses import PlainTextResponse

from .line import push_message

from .youtube import parse_youtube_notification

from .database import init_db

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("youtube-line-notifier")

app = FastAPI(
    title="YouTube LINE Notifier",
    version="0.3.0",
)


@app.get("/")
def root() -> dict[str, str]:
    return {
        "service": "youtube-line-notifier",
        "status": "running",
    }


@app.get("/health")
def health() -> dict[str, str]:
    return {
        "status": "ok",
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


@app.post("/websub")
async def receive_websub(request: Request) -> dict[str, str]:
    body = await request.body()

    logger.info(
        "WebSub notification received: content_type=%s bytes=%d",
        request.headers.get("content-type"),
        len(body),
    )

    try:
        notification = parse_youtube_notification(body)
    except ValueError as exc:
        logger.warning(
            "Invalid YouTube notification: %s",
            exc,
        )
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc

    logger.info(
        "YouTube notification parsed: video_id=%s channel_id=%s title=%s",
        notification.video_id,
        notification.channel_id,
        notification.title,
    )

    message = (
        "YouTube新着動画\n\n"
        f"{notification.title}\n\n"
        f"{notification.video_url}"
    )

    try:
        await push_message(message)
    except httpx.HTTPStatusError as exc:
        logger.error(
            "LINE API error: status=%s response=%s request_id=%s",
            exc.response.status_code,
            exc.response.text,
            exc.response.headers.get("x-line-request-id"),
        )
        raise HTTPException(
            status_code=502,
            detail={
                "message": "LINE API returned an error",
                "line_status": exc.response.status_code,
                "line_response": exc.response.text,
            },
        ) from exc
    except httpx.HTTPError as exc:
        logger.error(
            "LINE connection error: %s",
            exc,
        )
        raise HTTPException(
            status_code=502,
            detail="Failed to connect to LINE API",
        ) from exc

    logger.info(
        "LINE notification sent: video_id=%s",
        notification.video_id,
    )

    return {
        "result": "notified",
        "video_id": notification.video_id,
        "channel_id": notification.channel_id,
        "title": notification.title,
        "video_url": notification.video_url,
    }


@app.get("/websub", response_class=PlainTextResponse)
async def verify_websub(
    hub_mode: str = Query(alias="hub.mode"),
    hub_topic: str = Query(alias="hub.topic"),
    hub_challenge: str = Query(alias="hub.challenge"),
    hub_lease_seconds: int | None = Query(
        default=None,
        alias="hub.lease_seconds",
    ),
) -> str:
    logger.info(
        "WebSub verification received: mode=%s topic=%s lease_seconds=%s",
        hub_mode,
        hub_topic,
        hub_lease_seconds,
    )

    if hub_mode not in {"subscribe", "unsubscribe"}:
        raise HTTPException(
            status_code=400,
            detail="Unsupported hub.mode",
        )

    if not hub_topic.startswith(
        "https://www.youtube.com/feeds/videos.xml?channel_id="
    ):
        raise HTTPException(
            status_code=400,
            detail="Unexpected hub.topic",
        )

    return hub_challenge


@app.post("/websub")
async def receive_websub(request: Request) -> dict[str, str | int]:
    body = await request.body()

    logger.info(
        "WebSub notification received: content_type=%s bytes=%d",
        request.headers.get("content-type"),
        len(body),
    )

    logger.info(
        "WebSub body preview: %s",
        body[:1000].decode("utf-8", errors="replace"),
    )

    return {
        "result": "accepted",
        "bytes": len(body),
    }

@app.on_event("startup")
async def startup():

    init_db()
