"""WhatsApp Business Cloud API helpers: verify, parse and reply."""
import hashlib
import hmac
import logging

import httpx

from app.config import Settings
from app.schemas import IncomingText

logger = logging.getLogger(__name__)


def is_valid_signature(app_secret: str, body: bytes, signature_header: str | None) -> bool:
    """Check Meta's X-Hub-Signature-256 header so only Meta can call our webhook."""
    if not signature_header or not signature_header.startswith("sha256="):
        return False
    expected = hmac.new(app_secret.encode(), body, hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected, signature_header.removeprefix("sha256="))


def parse_text_messages(payload: dict) -> list[IncomingText]:
    """Pull every incoming text message out of a webhook payload.

    Meta nests messages as entry[] -> changes[] -> value -> messages[].
    Status updates (delivered, read) and non-text messages are ignored.
    """
    found: list[IncomingText] = []
    for entry in payload.get("entry", []):
        for change in entry.get("changes", []):
            value = change.get("value", {})
            names = {
                c.get("wa_id"): c.get("profile", {}).get("name")
                for c in value.get("contacts", [])
            }
            for msg in value.get("messages", []):
                if msg.get("type") != "text":
                    continue
                phone = msg.get("from", "")
                found.append(
                    IncomingText(
                        wa_message_id=msg.get("id", ""),
                        phone=phone,
                        name=names.get(phone),
                        text=msg.get("text", {}).get("body", ""),
                    )
                )
    return found


def send_text(settings: Settings, to_phone: str, text: str) -> bool:
    """Send a text reply. Returns False (and logs) instead of crashing on failure."""
    if not settings.whatsapp_token or not settings.whatsapp_phone_number_id:
        logger.info("WhatsApp not configured; would send to %s: %s", to_phone, text)
        return False
    url = (
        f"https://graph.facebook.com/{settings.whatsapp_api_version}/"
        f"{settings.whatsapp_phone_number_id}/messages"
    )
    try:
        resp = httpx.post(
            url,
            headers={"Authorization": f"Bearer {settings.whatsapp_token}"},
            json={
                "messaging_product": "whatsapp",
                "to": to_phone,
                "type": "text",
                "text": {"body": text[:4096]},
            },
            timeout=15,
        )
        resp.raise_for_status()
        return True
    except httpx.HTTPError as exc:
        logger.error("WhatsApp send failed for %s: %s", to_phone, exc)
        return False
