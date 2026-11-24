"""FastAPI entry point. Run locally with:  uvicorn app.main:app --reload"""
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.config import get_settings
from app.database import init_db
from app.routers import admin, webhook
from app.services.knowledge import KnowledgeBase

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()
    init_db()
    app.state.kb = KnowledgeBase.from_directory(settings.knowledge_dir)
    logging.getLogger(__name__).info(
        "Loaded %d knowledge chunks; LLM provider=%s", len(app.state.kb.chunks), settings.llm_provider
    )
    yield


app = FastAPI(
    title=get_settings().app_name,
    description="AI customer support on WhatsApp, answering from the business's own documents.",
    version="1.0.0",
    lifespan=lifespan,
)
app.include_router(webhook.router)
app.include_router(admin.router)


@app.get("/health", tags=["system"])
def health():
    return {"status": "ok"}
