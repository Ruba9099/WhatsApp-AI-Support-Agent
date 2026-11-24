"""The support agent: the one place that ties WhatsApp, AI, CRM and database together.

Flow for each incoming message:
  1. Skip it if we already processed this WhatsApp message id (Meta retries webhooks).
  2. Find or create the customer (and their HubSpot contact on first contact).
  3. Save the inbound message.
  4. Look up relevant knowledge and recent history, ask the LLM for a reply.
  5. Save and send the reply.
"""
import logging

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.config import Settings
from app.models import Customer, Message
from app.schemas import IncomingText
from app.services import crm, llm, whatsapp
from app.services.knowledge import KnowledgeBase

logger = logging.getLogger(__name__)

FALLBACK_REPLY = (
    "Sorry, I'm having trouble answering right now. A team member will reply soon."
)

SYSTEM_PROMPT = """You are the friendly WhatsApp support assistant for {business}.
Answer in the same language the customer uses (English, Urdu or Roman Urdu).
Keep replies short: 1-4 sentences, plain text, no markdown.
Use ONLY the knowledge below. If the answer isn't there, say a team member
will follow up, and never invent prices, policies or dates.

KNOWLEDGE:
{knowledge}

---"""


def build_system_prompt(business: str, knowledge_chunks: list[str]) -> str:
    knowledge = "\n\n".join(knowledge_chunks) if knowledge_chunks else "(none)"
    return SYSTEM_PROMPT.format(business=business, knowledge=knowledge)


def _get_or_create_customer(db: Session, settings: Settings, msg: IncomingText) -> Customer:
    customer = db.scalar(select(Customer).where(Customer.phone == msg.phone))
    if customer:
        if msg.name and not customer.name:
            customer.name = msg.name
        return customer
    customer = Customer(phone=msg.phone, name=msg.name)
    customer.crm_contact_id = crm.create_contact(settings, msg.phone, msg.name)
    db.add(customer)
    db.flush()
    return customer


def generate_reply(
    db: Session, settings: Settings, kb: KnowledgeBase, customer: Customer, text: str
) -> str:
    history = db.scalars(
        select(Message)
        .where(Message.customer_id == customer.id)
        .order_by(Message.id.desc())
        .limit(settings.history_limit)
    ).all()
    chat = [
        {"role": "user" if m.direction == "inbound" else "assistant", "content": m.body}
        for m in reversed(history)
    ]
    # The newest inbound message is already saved, so it is the last item in chat.
    if not chat or chat[-1]["content"] != text:
        chat.append({"role": "user", "content": text})
    # Anthropic requires the conversation to start with a user turn.
    while chat and chat[0]["role"] != "user":
        chat.pop(0)

    system = build_system_prompt(settings.business_name, kb.search(text))
    try:
        reply = llm.complete(settings, system, chat)
        return reply or FALLBACK_REPLY
    except llm.LLMError as exc:
        logger.error("LLM failed: %s", exc)
        return FALLBACK_REPLY


def handle_incoming(
    db: Session, settings: Settings, kb: KnowledgeBase, msg: IncomingText, send: bool = True
) -> str | None:
    """Process one incoming message. Returns the reply, or None if it was a duplicate."""
    if msg.wa_message_id and db.scalar(
        select(Message.id).where(Message.wa_message_id == msg.wa_message_id)
    ):
        logger.info("Duplicate message %s ignored", msg.wa_message_id)
        return None

    customer = _get_or_create_customer(db, settings, msg)
    db.add(
        Message(
            customer_id=customer.id,
            direction="inbound",
            body=msg.text,
            wa_message_id=msg.wa_message_id or None,
        )
    )
    try:
        db.commit()
    except IntegrityError:  # the same message arrived twice at the same moment
        db.rollback()
        return None

    reply = generate_reply(db, settings, kb, customer, msg.text)
    db.add(Message(customer_id=customer.id, direction="outbound", body=reply))
    db.commit()

    if send:
        whatsapp.send_text(settings, msg.phone, reply)
    return reply
