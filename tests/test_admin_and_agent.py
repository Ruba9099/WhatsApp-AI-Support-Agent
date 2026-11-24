from app.services.agent import build_system_prompt
from app.services.knowledge import KnowledgeBase
from app.services.whatsapp import parse_text_messages
from tests.conftest import make_payload


def test_admin_requires_api_key(client):
    assert client.get("/admin/customers").status_code == 401
    assert client.get("/admin/customers", headers={"X-API-Key": "wrong"}).status_code == 401


def test_test_chat_endpoint(client, admin_headers):
    r = client.post(
        "/admin/test-chat",
        json={"phone": "923009999999", "message": "Which payment methods do you accept?"},
        headers=admin_headers,
    )
    assert r.status_code == 200
    assert "JazzCash" in r.json()["reply"]


def test_unknown_customer_returns_404(client, admin_headers):
    assert client.get("/admin/customers/999999", headers=admin_headers).status_code == 404


def test_knowledge_search_ranks_relevant_chunk_first():
    kb = KnowledgeBase(
        ["Delivery costs Rs. 200 in Lahore.", "We accept JazzCash.", "Open 10 AM to 9 PM."]
    )
    assert kb.search("how much is delivery in lahore")[0].startswith("Delivery")
    assert kb.search("hello there") == []  # only stopwords -> nothing


def test_system_prompt_handles_empty_knowledge():
    prompt = build_system_prompt("Shop", [])
    assert "(none)" in prompt and "Shop" in prompt


def test_parse_ignores_non_text_messages():
    payload = make_payload("wamid.X", "92300", "hi")
    payload["entry"][0]["changes"][0]["value"]["messages"][0]["type"] = "image"
    assert parse_text_messages(payload) == []
