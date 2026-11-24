import os
import tempfile
from pathlib import Path

# Configure a throwaway database and test settings BEFORE the app is imported.
_tmp = tempfile.mkdtemp()
os.environ["DATABASE_URL"] = f"sqlite:///{Path(_tmp) / 'test.db'}"
os.environ["LLM_PROVIDER"] = "mock"
os.environ["ADMIN_API_KEY"] = "test-admin-key"
os.environ["WHATSAPP_VERIFY_TOKEN"] = "test-verify"
os.environ["WHATSAPP_APP_SECRET"] = ""
os.environ["WHATSAPP_TOKEN"] = ""
os.environ["HUBSPOT_TOKEN"] = ""
os.environ["KNOWLEDGE_DIR"] = str(Path(__file__).resolve().parents[1] / "knowledge")

import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402

from app.config import get_settings  # noqa: E402
from app.main import app  # noqa: E402


@pytest.fixture()
def client():
    get_settings.cache_clear()
    with TestClient(app) as c:
        yield c


@pytest.fixture()
def admin_headers():
    return {"X-API-Key": "test-admin-key"}


def make_payload(msg_id: str, phone: str, text: str, name: str = "Ali Khan") -> dict:
    """A webhook payload shaped exactly like the one Meta sends."""
    return {
        "object": "whatsapp_business_account",
        "entry": [
            {
                "id": "WABA_ID",
                "changes": [
                    {
                        "field": "messages",
                        "value": {
                            "messaging_product": "whatsapp",
                            "contacts": [{"wa_id": phone, "profile": {"name": name}}],
                            "messages": [
                                {
                                    "from": phone,
                                    "id": msg_id,
                                    "timestamp": "1700000000",
                                    "type": "text",
                                    "text": {"body": text},
                                }
                            ],
                        },
                    }
                ],
            }
        ],
    }
