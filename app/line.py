import httpx

from .config import settings

LINE_PUSH_URL = "https://api.line.me/v2/bot/message/push"


async def push_message(message: str) -> None:
    headers = {
        "Authorization": f"Bearer {settings.line_channel_access_token}",
        "Content-Type": "application/json",
    }

    body = {
        "to": settings.line_user_id,
        "messages": [
            {
                "type": "text",
                "text": message,
            }
        ],
    }

    async with httpx.AsyncClient(timeout=10.0) as client:
        response = await client.post(
            LINE_PUSH_URL,
            headers=headers,
            json=body,
        )
        response.raise_for_status()
