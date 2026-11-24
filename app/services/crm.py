"""HubSpot CRM sync: create a contact the first time a customer messages us."""
import logging

import httpx

from app.config import Settings

logger = logging.getLogger(__name__)

HUBSPOT_CONTACTS_URL = "https://api.hubapi.com/crm/v3/objects/contacts"


def create_contact(settings: Settings, phone: str, name: str | None) -> str | None:
    """Create a HubSpot contact and return its id, or None if CRM is off or fails.

    A CRM failure must never stop the customer from getting a reply, so errors
    are logged, not raised.
    """
    if not settings.hubspot_token:
        return None
    first, _, last = (name or "").partition(" ")
    properties = {"phone": phone, "lifecyclestage": "lead", "hs_lead_status": "NEW"}
    if first:
        properties["firstname"] = first
    if last:
        properties["lastname"] = last
    try:
        resp = httpx.post(
            HUBSPOT_CONTACTS_URL,
            headers={"Authorization": f"Bearer {settings.hubspot_token}"},
            json={"properties": properties},
            timeout=15,
        )
        resp.raise_for_status()
        return str(resp.json().get("id"))
    except httpx.HTTPError as exc:
        logger.error("HubSpot contact creation failed for %s: %s", phone, exc)
        return None
