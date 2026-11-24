# WhatsApp AI Support Agent

An AI customer-support service for WhatsApp Business. It answers customer questions
using a business's own FAQ, stores conversations, and can create new contacts in
HubSpot. It supports Anthropic, OpenAI, and an offline mock provider for local
development.

![Python](https://img.shields.io/badge/Python-3.12-blue) ![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688) ![MySQL](https://img.shields.io/badge/MySQL-8.4-4479A1) ![Docker](https://img.shields.io/badge/Docker-ready-2496ED)

## Features

- WhatsApp Business Cloud API verification, inbound webhook, and replies
- Optional Meta webhook signature validation
- FAQ-based answers with English, Urdu, and Roman Urdu support
- Anthropic and OpenAI providers, plus offline mock mode
- Recent conversation history and duplicate-message protection
- Optional HubSpot contact creation
- API-key-protected admin endpoints and interactive Swagger UI
- SQLite for local development; MySQL with Docker Compose
- Pytest suite, GitHub Actions CI, and a non-root production Docker image

## Message flow

```text
Customer -> WhatsApp -> Meta -> POST /webhook -> AI agent -> WhatsApp reply
                                            |-> FAQ search (knowledge/)
                                            |-> conversation storage
                                            `-> optional HubSpot contact
```

See [Architecture](docs/ARCHITECTURE.md) for design details.

## Requirements

- Python 3.12
- Git
- Docker Desktop and Docker Compose v2 (optional, for the MySQL setup)
- API credentials only if using a real LLM provider or WhatsApp integration

## Quick start: local development

Clone the repository and enter its folder:

```bash
git clone https://github.com/Ruba9099/WhatsApp-AI-Support-Agent.git
cd WhatsApp-AI-Support-Agent
```

Create a virtual environment, install dependencies, and make your local settings
file from the safe template.

**Windows PowerShell**

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements-dev.txt
Copy-Item .env.example .env
```

**macOS / Linux**

```bash
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements-dev.txt
cp .env.example .env
```

The default `LLM_PROVIDER=mock` works offline and needs no LLM key. Start the API:

```bash
uvicorn app.main:app --reload
```

Open <http://127.0.0.1:8000/docs>, choose **Authorize**, and enter the value of
`ADMIN_API_KEY` from your local `.env`. Use `POST /admin/test-chat` to try a question.
The default FAQ includes example business information.

## Run with Docker Compose

Docker Compose starts the API and MySQL. Copy `.env.example` to `.env`, set unique
database passwords and a strong admin key, then run:

```bash
docker compose up -d --build
docker compose ps
curl http://127.0.0.1:8000/health
```

The API port is bound to localhost by default; put a trusted HTTPS reverse proxy in
front of it for external access. Follow [the AWS deployment guide](docs/DEPLOY_AWS.md)
for one example.

To stop the services, run `docker compose down`. To also delete the MySQL data volume,
run `docker compose down -v` (this permanently deletes stored conversations).

## Configuration

Copy [.env.example](.env.example) to `.env` and configure only the integrations you
intend to use. `.env` contains secrets and local configuration: **never commit or share
it**. It is excluded by [.gitignore](.gitignore); `.env.example` contains placeholders
and is safe to commit.

| Variable | Purpose |
|---|---|
| `ENVIRONMENT` | Environment label; defaults to `development` |
| `API_PORT` | Host port for Docker Compose; defaults to `8000` |
| `DATABASE_URL` | SQLAlchemy URL; defaults to local SQLite |
| `MYSQL_DATABASE`, `MYSQL_USER`, `MYSQL_PASSWORD`, `MYSQL_ROOT_PASSWORD` | Docker MySQL database and credentials |
| `LLM_PROVIDER` | `mock`, `anthropic`, or `openai`; defaults to `mock` |
| `LLM_API_KEY`, `LLM_MODEL` | Provider API key and optional model override |
| `LLM_TIMEOUT_SECONDS` | Provider request timeout; defaults to 20 seconds |
| `WHATSAPP_TOKEN` | Meta access token used to send messages |
| `WHATSAPP_PHONE_NUMBER_ID` | Phone number ID from Meta's API Setup page |
| `WHATSAPP_VERIFY_TOKEN` | Secret verification string configured in Meta |
| `WHATSAPP_APP_SECRET` | Meta app secret; enables webhook signature validation when set |
| `WHATSAPP_API_VERSION` | WhatsApp Graph API version |
| `HUBSPOT_TOKEN` | Optional HubSpot private-app token; blank disables CRM sync |
| `BUSINESS_NAME` | Business name used in the AI prompt |
| `KNOWLEDGE_DIR` | Folder containing `.md` and `.txt` FAQ files |
| `ADMIN_API_KEY` | Key required by all `/admin/*` routes; send as `X-API-Key` |
| `HISTORY_LIMIT` | Number of previous messages used as conversation context |

For a real deployment, replace all example passwords and keys with strong unique
values. Set `WHATSAPP_APP_SECRET` so inbound requests are signature-checked. Never use
the default admin key or expose the development server directly to the internet.

### Customize the FAQ

Replace or add `.md` or `.txt` files in `knowledge/`. Separate FAQ entries with blank
lines; the local keyword search returns the most relevant paragraphs. Restart the API
after changing files when running locally. In Docker Compose the folder is mounted
read-only into the API container.

## API

Interactive API documentation is available at `/docs`.

| Method | Path | Authentication | Description |
|---|---|---|---|
| `GET` | `/health` | None | Health check |
| `GET` | `/webhook` | Meta verify token | WhatsApp webhook verification |
| `POST` | `/webhook` | Meta signature when configured | Receive WhatsApp webhook events |
| `GET` | `/admin/customers` | `X-API-Key` | List customers |
| `GET` | `/admin/customers/{customer_id}` | `X-API-Key` | Read a customer's conversation |
| `POST` | `/admin/test-chat` | `X-API-Key` | Test the agent without sending WhatsApp |

## Tests and CI

Run the test suite from the repository root with the development environment active:

```bash
pytest -q
```

GitHub Actions runs the tests and builds the Docker image on pushes to `main` and on
pull requests.

## WhatsApp and production deployment

- [Connect a real WhatsApp number](docs/WHATSAPP_SETUP.md)
- [Deploy on AWS EC2 with HTTPS](docs/DEPLOY_AWS.md)

Meta requires a publicly reachable HTTPS webhook. WhatsApp's 24-hour customer-service
window applies to free-form replies; approved message templates are required outside
that window.

## Documentation

- [Product brief](docs/PRODUCT_BRIEF.md)
- [Architecture](docs/ARCHITECTURE.md)
- [Roadmap](docs/ROADMAP.md)
- [WhatsApp setup](docs/WHATSAPP_SETUP.md)
- [AWS deployment](docs/DEPLOY_AWS.md)

## Project structure

```text
app/
  main.py                 FastAPI application and startup
  config.py               Environment-based settings
  database.py             SQLAlchemy engine and session
  models.py, schemas.py   Database models and API schemas
  routers/                WhatsApp webhook and admin endpoints
  services/               Agent, LLM, FAQ, WhatsApp, and CRM integrations
knowledge/                Example business FAQ files
tests/                    Pytest tests
docs/                     Product, architecture, setup, and deployment guides
.github/workflows/        GitHub Actions CI
```

## Pre-deployment checklist

- [ ] Replace default admin/database credentials with strong unique values
- [ ] Keep `.env` private; only configure production secrets on the server
- [ ] Set `WHATSAPP_APP_SECRET` and verify Meta webhook signatures
- [ ] Use a permanent Meta system-user token and HTTPS
- [ ] Review the FAQ with the business owner
- [ ] Configure backups for the production database
- [ ] Set a cloud budget alert and monitor application logs

## License

MIT. See [LICENSE](LICENSE).
