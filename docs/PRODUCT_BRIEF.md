# Product Brief: WhatsApp AI Support Agent

## Problem
Small businesses in Pakistan (shops, clinics, schools, real estate agents) get dozens of
repeated WhatsApp questions every day: timings, prices, delivery, payment. Owners answer
by hand, reply late at night or miss messages, and lose customers.

## Target users
- **Business owner:** wants customers answered 24/7 without hiring staff.
- **Customer:** wants a quick, correct answer in English, Urdu or Roman Urdu.

## Goals
1. Answer common questions instantly, using only the business's own information.
2. Capture every new customer as a lead in the CRM automatically.
3. Keep a full conversation history the owner can review.

## Success metrics
| Metric | Target |
|---|---|
| Reply time | Under 10 seconds |
| Questions answered without a human | 60%+ |
| New WhatsApp contacts saved as CRM leads | 100% |
| Wrong or invented answers in review | 0 |

## Scope
**MVP (built):** webhook verification and signature check, AI replies from a knowledge folder,
multi-language prompt, conversation memory, duplicate-message protection, MySQL storage,
HubSpot lead creation, admin API, offline mock AI mode, Docker, CI, tests.

**Nice to have:** web dashboard, human handover button, vector search, media messages.

**Out of scope:** payments in chat, voice notes, multi-tenant SaaS billing.

## User stories (MVP)
| # | Story | Acceptance criteria |
|---|---|---|
| 1 | As a customer, I ask "delivery charges?" and get an answer. | Reply comes from the FAQ text; nothing invented. |
| 2 | As an owner, I connect my number once. | `GET /webhook` returns the challenge only with the right verify token. |
| 3 | As an owner, every new customer appears in HubSpot. | First message creates one contact with phone and name. |
| 4 | As an owner, I read past chats. | `/admin/customers/{id}` returns ordered messages, behind an API key. |
| 5 | As an owner, Meta retries don't cause double replies. | Same message id is processed once. |

## Risks, assumptions, open questions
- **Risk:** the AI answers outside the FAQ. *Mitigation:* strict prompt, knowledge-only rule, review chats.
- **Risk:** Meta's 24-hour rule. Free-form replies only work within 24h of the customer's last message.
- **Assumption:** each business has one WhatsApp number and a short FAQ (under ~50 paragraphs).
- **Open:** which CRM do local clients actually use? (HubSpot free tier chosen as default.)

See the [roadmap](ROADMAP.md).
