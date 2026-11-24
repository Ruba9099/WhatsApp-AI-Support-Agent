# WhatsApp AI Support Agent

An AI customer-support assistant that answers a business's WhatsApp messages 24/7,
using only that business's own FAQ. Every new customer is saved as a lead in HubSpot,
and every conversation is stored in MySQL.

![Python](https://img.shields.io/badge/Python-3.12-blue) ![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688) ![MySQL](https://img.shields.io/badge/MySQL-8.4-4479A1) ![Docker](https://img.shields.io/badge/Docker-ready-2496ED)

## Features
- ✅ WhatsApp Business Cloud API webhook (verify, receive, reply) with signature check
- ✅ AI replies from your own documents: Anthropic Claude, OpenAI, or a free offline **mock** mode
- ✅ Replies in English, Urdu or Roman Urdu; remembers recent conversation
- ✅ Duplicate-message protection (Meta retries never cause double replies)
- ✅ HubSpot CRM lead creation on first contact
- ✅ Admin API to browse chats and test the bot from Swagger UI
- ✅ MySQL via Docker Compose, SQLite for quick local runs
- ✅ Tests, GitHub Actions CI, production Dockerfile (multi-stage, non-root)

## How it works
```
Customer → WhatsApp → Meta → POST /webhook → AI agent → reply on WhatsApp
                                          ├─ FAQ search (knowledge/)
                                          ├─ MySQL (history)
                                          └─ HubSpot (new lead)
```
More detail: [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)

## Quick start (local, 2 minutes, no API keys)
```bash
git clone https://github.com/YOUR_USERNAME/whatsapp-ai-support-agent.git
cd whatsapp-ai-support-agent
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements-dev.txt
cp .env.example .env
uvicorn app.main:app --reload
```
Open <http://localhost:8000/docs> → **Authorize** with your `ADMIN_API_KEY` →
`POST /admin/test-chat` with `{"message": "What are your delivery charges?"}`.

## Run with Docker (MySQL included)
```bash
cp .env.example .env      # set passwords and keys
docker compose up -d --build
curl localhost:8000/health
```

## Configuration
All settings live in `.env` (see [.env.example](.env.example)).

| Variable | Purpose |
|---|---|
| `LLM_PROVIDER` | `mock`, `anthropic` or `openai` |
| `LLM_API_KEY` / `LLM_MODEL` | Provider key and optional model name |
| `WHATSAPP_TOKEN`, `WHATSAPP_PHONE_NUMBER_ID` | From Meta's API Setup page |
| `WHATSAPP_VERIFY_TOKEN` | Any string; must match what you type in Meta |
| `WHATSAPP_APP_SECRET` | Enables webhook signature verification |
| `HUBSPOT_TOKEN` | Optional private-app token |
| `ADMIN_API_KEY` | Protects `/admin/*` (send as `X-API-Key`) |
| `BUSINESS_NAME`, `KNOWLEDGE_DIR` | Who the bot speaks for, and where the FAQ lives |

**Customise for a client:** replace `knowledge/business_faq.md` with their info.
One topic per paragraph.

## API
| Method | Path | Description |
|---|---|---|
| GET | `/health` | Health check |
| GET | `/webhook` | Meta verification handshake |
| POST | `/webhook` | Incoming WhatsApp messages |
| GET | `/admin/customers` | List customers |
| GET | `/admin/customers/{id}` | Full conversation |
| POST | `/admin/test-chat` | Talk to the bot without WhatsApp |

## Tests
```bash
pytest -q
```

## Deployment
- [Deploy on AWS EC2 with HTTPS](docs/DEPLOY_AWS.md)
- [Connect a real WhatsApp number](docs/WHATSAPP_SETUP.md)

## Project documents
- [Product brief](docs/PRODUCT_BRIEF.md) · [Roadmap](docs/ROADMAP.md) · [Architecture](docs/ARCHITECTURE.md)

## Project structure
```
app/
  main.py            # FastAPI app
  config.py          # settings from .env
  database.py        # SQLAlchemy engine/session
  models.py          # customers, messages
  routers/           # webhook + admin endpoints
  services/          # agent, llm, knowledge, whatsapp, crm
knowledge/           # business FAQ files
tests/               # pytest suite
docs/                # brief, roadmap, architecture, deployment
```

## Checklist before going live
- [ ] Strong `ADMIN_API_KEY` and MySQL passwords
- [ ] `WHATSAPP_APP_SECRET` set (signature check on)
- [ ] Permanent Meta system-user token
- [ ] HTTPS working
- [ ] FAQ reviewed by the business owner
- [ ] AWS budget alert created

## License
MIT. See [LICENSE](LICENSE).
