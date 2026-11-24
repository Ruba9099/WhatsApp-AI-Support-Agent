"""Small LLM client that works with Anthropic, OpenAI, or a free offline mock.

Why a hand-written client instead of SDKs? It keeps dependencies small and shows
exactly what goes over the wire. Switching provider is one env variable.
"""
import logging

import httpx

from app.config import Settings

logger = logging.getLogger(__name__)

DEFAULT_MODELS = {
    "anthropic": "claude-haiku-5-5",
    "openai": "gpt-4o-mini",
}


class LLMError(Exception):
    pass


def complete(settings: Settings, system: str, messages: list[dict]) -> str:
    """Send a chat to the configured provider and return the reply text.

    `messages` is a list of {"role": "user" | "assistant", "content": str}.
    """
    provider = settings.llm_provider.lower()
    if provider == "mock":
        return _mock(system, messages)
    if not settings.llm_api_key:
        raise LLMError("LLM_API_KEY is not set")

    model = settings.llm_model or DEFAULT_MODELS.get(provider, "")
    try:
        if provider == "anthropic":
            return _anthropic(settings, model, system, messages)
        if provider == "openai":
            return _openai(settings, model, system, messages)
    except httpx.HTTPError as exc:
        raise LLMError(f"{provider} request failed: {exc}") from exc
    raise LLMError(f"Unknown LLM_PROVIDER: {settings.llm_provider}")


def _anthropic(settings: Settings, model: str, system: str, messages: list[dict]) -> str:
    resp = httpx.post(
        "https://api.anthropic.com/v1/messages",
        headers={
            "x-api-key": settings.llm_api_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json",
        },
        json={"model": model, "max_tokens": 500, "system": system, "messages": messages},
        timeout=settings.llm_timeout_seconds,
    )
    resp.raise_for_status()
    blocks = resp.json().get("content", [])
    return "".join(b.get("text", "") for b in blocks if b.get("type") == "text").strip()


def _openai(settings: Settings, model: str, system: str, messages: list[dict]) -> str:
    resp = httpx.post(
        "https://api.openai.com/v1/chat/completions",
        headers={"Authorization": f"Bearer {settings.llm_api_key}"},
        json={
            "model": model,
            "max_tokens": 500,
            "messages": [{"role": "system", "content": system}, *messages],
        },
        timeout=settings.llm_timeout_seconds,
    )
    resp.raise_for_status()
    return resp.json()["choices"][0]["message"]["content"].strip()


def _mock(system: str, messages: list[dict]) -> str:
    """Offline answer: returns the most relevant knowledge snippet from the prompt.

    Lets anyone run and demo the project without an API key.
    """
    marker = "KNOWLEDGE:\n"
    if marker in system:
        knowledge = system.split(marker, 1)[1].split("\n\n---", 1)[0].strip()
        if knowledge and knowledge != "(none)":
            first = knowledge.split("\n\n")[0].strip()
            return f"Thanks for your message! Here's what I found:\n{first}"
    return "Thanks for reaching out! A team member will get back to you shortly."
