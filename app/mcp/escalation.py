"""Logging-only human-escalation MCP stub."""

import logging


def escalate_to_human(question: str, chat_id: str) -> dict[str, object]:
    """Escalate a customer question to a human support agent.

    Called by sensitive or unsupported graph branches. In production this
    attaches to the broker's support/case-management system and must create a
    review task containing the chat ID, original question, priority, queue, and
    trace metadata. The current implementation only logs the request and
    returns a deterministic success response.
    """
    logging.getLogger("mcp.escalation").info(
        "stub escalation chat_id=%s question=%s", chat_id, question
    )
    return {"escalated": True, "chat_id": chat_id}
