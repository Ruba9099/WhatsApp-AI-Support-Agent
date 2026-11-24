# Roadmap

## Phase 1: MVP ✅ (this release)
- [x] WhatsApp webhook verify + receive, signature check
- [x] AI replies from knowledge files (Anthropic, OpenAI or offline mock)
- [x] Conversation memory and MySQL storage
- [x] Duplicate-message protection
- [x] HubSpot lead creation
- [x] Admin API with API key
- [x] Docker, Docker Compose, GitHub Actions CI, tests
- [x] AWS EC2 deployment guide

## Phase 2: Make it sellable
- [ ] React dashboard for owners (chats, leads, edit FAQ in the browser)
- [ ] Human handover: "agent" keyword pauses the bot and alerts the owner
- [ ] Vector search (embeddings) for larger knowledge bases
- [ ] Alembic database migrations
- [ ] Rate limiting per phone number

## Phase 3: SaaS
- [ ] Multi-tenant: many businesses on one deployment
- [ ] Self-service onboarding with Meta Embedded Signup
- [ ] Monthly billing, usage analytics, message templates for follow-ups

## Build order used for Phase 1
1. Config + database models → 2. Webhook verify/parse → 3. Knowledge retrieval →
4. LLM client → 5. Agent orchestration → 6. CRM sync → 7. Admin API → 8. Tests →
9. Docker + CI → 10. Docs + AWS guide
