"""Request and response shapes for the API."""
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class IncomingText(BaseModel):
    """A single text message pulled out of Meta's webhook payload."""

    wa_message_id: str
    phone: str
    name: str | None = None
    text: str


class ChatRequest(BaseModel):
    """Used by the /admin/test-chat endpoint to try the agent without WhatsApp."""

    phone: str = Field(default="923000000000", max_length=32)
    message: str = Field(min_length=1, max_length=2000)


class ChatResponse(BaseModel):
    reply: str


class MessageOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    direction: str
    body: str
    created_at: datetime


class CustomerOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    phone: str
    name: str | None
    crm_contact_id: str | None
    created_at: datetime


class ConversationOut(CustomerOut):
    messages: list[MessageOut]
