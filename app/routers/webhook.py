"""Webhook endpoints that Meta calls."""
import json
import logging

from fastapi import APIRouter, BackgroundTasks, HTTPException, Query, Request
from fastapi.responses import PlainTextResponse

from app.config import get_settings
from app.database import SessionLocal
from app.services import agent, whatsapp

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/webhook", tags=["webhook"])


@router.get("", response_class=PlainTextResponse)
def verify_webhook(
    mode: str = Query("", alias="hub.mode"),
    token: str = Query("", alias="hub.verify_token"),
    challenge: str = Query("", alias="hub.challenge"),
):
    """Meta calls this once when you register the webhook URL.
    We must echo back hub.challenge if the verify token matches."""
    if mode == "subscribe" and token == get_settings().whatsapp_verify_token:
        return challenge
    raise HTTPException(status_code=403, detail="Verification failed")


def _process(payload: dict, kb) -> None:
    """Runs after we have already answered Meta with 200 OK."""
    settings = get_settings()
    with SessionLocal() as db:
        for msg in whatsapp.parse_text_messages(payload):
            try:
                agent.handle_incoming(db, settings, kb, msg)
            except Exception:  # one bad message must not block the others
                logger.exception("Failed to handle message %s", msg.wa_message_id)
                db.rollback()


@router.post("")
async def receive_webhook(request: Request, background: BackgroundTasks):
    """Meta sends every new message here. We reply 200 quickly and do the
    slow work (AI call, CRM, sending) in the background, otherwise Meta retries."""
    settings = get_settings()
    body = await request.body()
    if settings.whatsapp_app_secret and not whatsapp.is_valid_signature(
        settings.whatsapp_app_secret, body, request.headers.get("X-Hub-Signature-256")
    ):
        raise HTTPException(status_code=401, detail="Invalid signature")
    try:
        payload = json.loads(body or b"{}")
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON")

    background.add_task(_process, payload, request.app.state.kb)
    return {"status": "received"}
