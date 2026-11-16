"""Validate and normalize incoming ticket data."""

import logging

from app.context import TicketState
from app.message import Message, to_langchain_messages

logger = logging.getLogger(__name__)


def ingest_ticket(state: TicketState) -> dict[str, object]:
    message = " ".join(state.get("customer_message", "").split())
    if not message:
        raise ValueError("customer_message is required")
    ticket_id = state.get("message_id") or "message-unknown"
    logger.info("ingested chat_id=%s message_id=%s", state.get("chat_id"), ticket_id)
    messages = [Message(**item) for item in state.get("messages", [])]
    return {
        "ticket_id": ticket_id,
        "customer_message": message,
        "prompt_messages": to_langchain_messages(messages),
    }
