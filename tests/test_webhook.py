import hashlib
import hmac
import json

from app.config import get_settings
from tests.conftest import make_payload


def test_health(client):
    assert client.get("/health").json() == {"status": "ok"}


def test_verify_webhook_success(client):
    r = client.get(
        "/webhook",
        params={"hub.mode": "subscribe", "hub.verify_token": "test-verify", "hub.challenge": "12345"},
    )
    assert r.status_code == 200
    assert r.text == "12345"


def test_verify_webhook_wrong_token(client):
    r = client.get(
        "/webhook",
        params={"hub.mode": "subscribe", "hub.verify_token": "wrong", "hub.challenge": "1"},
    )
    assert r.status_code == 403


def test_incoming_message_saves_conversation_and_replies(client, admin_headers):
    payload = make_payload("wamid.A1", "923001111111", "What is your delivery cost?")
    assert client.post("/webhook", json=payload).status_code == 200

    customers = client.get("/admin/customers", headers=admin_headers).json()
    customer = next(c for c in customers if c["phone"] == "923001111111")
    assert customer["name"] == "Ali Khan"

    convo = client.get(f"/admin/customers/{customer['id']}", headers=admin_headers).json()
    directions = [m["direction"] for m in convo["messages"]]
    assert directions == ["inbound", "outbound"]
    assert "Delivery" in convo["messages"][1]["body"]  # answered from the knowledge base


def test_duplicate_webhook_is_processed_once(client, admin_headers):
    payload = make_payload("wamid.DUP", "923002222222", "Opening hours?")
    client.post("/webhook", json=payload)
    client.post("/webhook", json=payload)  # Meta retry

    customers = client.get("/admin/customers", headers=admin_headers).json()
    cid = next(c["id"] for c in customers if c["phone"] == "923002222222")
    convo = client.get(f"/admin/customers/{cid}", headers=admin_headers).json()
    assert len(convo["messages"]) == 2


def test_status_updates_are_ignored(client):
    payload = {"entry": [{"changes": [{"value": {"statuses": [{"status": "read"}]}}]}]}
    assert client.post("/webhook", json=payload).status_code == 200


def test_invalid_json_rejected(client):
    r = client.post("/webhook", content=b"not json", headers={"Content-Type": "application/json"})
    assert r.status_code == 400


def test_signature_required_when_secret_set(client, monkeypatch):
    monkeypatch.setenv("WHATSAPP_APP_SECRET", "s3cret")
    get_settings.cache_clear()
    body = json.dumps(make_payload("wamid.SIG", "923003333333", "hi")).encode()

    bad = client.post("/webhook", content=body, headers={"X-Hub-Signature-256": "sha256=bad"})
    assert bad.status_code == 401

    sig = hmac.new(b"s3cret", body, hashlib.sha256).hexdigest()
    good = client.post("/webhook", content=body, headers={"X-Hub-Signature-256": f"sha256={sig}"})
    assert good.status_code == 200

    monkeypatch.setenv("WHATSAPP_APP_SECRET", "")
    get_settings.cache_clear()
