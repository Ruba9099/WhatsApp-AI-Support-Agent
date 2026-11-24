"""Admin endpoints: view conversations and test the agent without WhatsApp.
All routes need the X-API-Key header."""
import secrets
import uuid

from fastapi import APIRouter, Depends, HTTPException, Request, Security
from fastapi.security import APIKeyHeader
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.config import get_settings
from app.database import get_db
from app.models import Customer
from app.schemas import ChatRequest, ChatResponse, ConversationOut, CustomerOut, IncomingText
from app.services import agent


api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


def require_api_key(x_api_key: str | None = Security(api_key_header)) -> None:
    """Gives Swagger UI an 'Authorize' button and rejects wrong keys."""
    if not secrets.compare_digest(x_api_key or "", get_settings().admin_api_key):
        raise HTTPException(status_code=401, detail="Invalid API key")


router = APIRouter(prefix="/admin", tags=["admin"], dependencies=[Depends(require_api_key)])


@router.get("/customers", response_model=list[CustomerOut])
def list_customers(limit: int = 50, offset: int = 0, db: Session = Depends(get_db)):
    limit = max(1, min(limit, 200))
    return db.scalars(
        select(Customer).order_by(Customer.id.desc()).limit(limit).offset(offset)
    ).all()


@router.get("/customers/{customer_id}", response_model=ConversationOut)
def get_conversation(customer_id: int, db: Session = Depends(get_db)):
    customer = db.scalar(
        select(Customer)
        .options(selectinload(Customer.messages))
        .where(Customer.id == customer_id)
    )
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    return customer


@router.post("/test-chat", response_model=ChatResponse)
def test_chat(body: ChatRequest, request: Request, db: Session = Depends(get_db)):
    """Talk to the agent from Swagger UI. Saves the chat but does not send WhatsApp."""
    msg = IncomingText(
        wa_message_id=f"test-{uuid.uuid4()}", phone=body.phone, name=None, text=body.message
    )
    reply = agent.handle_incoming(db, get_settings(), request.app.state.kb, msg, send=False)
    return ChatResponse(reply=reply or "")
