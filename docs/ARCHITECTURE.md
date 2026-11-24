# Architecture

```
Customer's WhatsApp
        │  message
        ▼
Meta WhatsApp Cloud API ──POST /webhook──►  FastAPI app
                                            │ 1. check signature, reply 200 fast
                                            │ 2. background task:
                                            ▼
                                     services/agent.py
              ┌──────────────┬──────────────┼───────────────┬──────────────┐
              ▼              ▼              ▼               ▼              ▼
        MySQL (history)  knowledge.py    llm.py          crm.py       whatsapp.py
        customers,       finds FAQ       Anthropic /     HubSpot      sends reply
        messages         paragraphs      OpenAI / mock   contact      via Graph API
```

## Key design decisions
| Decision | Why |
|---|---|
| Reply 200 first, work in background | Meta retries if the webhook is slow, which causes double replies. |
| Unique `wa_message_id` column | A second layer against retries: the database rejects duplicates. |
| CRM and WhatsApp errors are logged, not raised | A HubSpot outage must never stop a customer getting an answer. |
| Plain `httpx` instead of SDKs | Fewer dependencies; provider switch is one env variable. |
| Mock LLM provider | Anyone can clone, run and test without paying for an API key. |
| Keyword retrieval, not vectors | Small FAQs don't need a vector DB; it's swappable later (Phase 2). |

## Folder map
| Path | Purpose |
|---|---|
| `app/main.py` | App startup, loads knowledge base |
| `app/routers/webhook.py` | Meta's verify + receive endpoints |
| `app/routers/admin.py` | Conversations and test chat (API key) |
| `app/services/agent.py` | The full message flow |
| `app/services/*.py` | One file per external system |
| `knowledge/` | The business's FAQ files |
