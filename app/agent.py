"""Agent initialization and text-only runtime interface."""

from __future__ import annotations

import logging
import json
from collections.abc import Awaitable, Callable

from app.config import Settings
from app.graph import build_graph
from app.mcp.knowledge_base import initialize as initialize_knowledge_base
from app.message import Message, OutputSection

logger = logging.getLogger(__name__)


def initialize_agent(config: Settings) -> Callable[[list[Message]], Awaitable[list[OutputSection]]]:
    """Initialize the graph and return an async structured-sections callable."""
    initialize_knowledge_base()
    graph = build_graph()
    async def run_agent(messages: list[Message]) -> list[OutputSection]:
        if not messages:
            return "Please enter a support question."
        latest = messages[-1]
        if not latest["text"].strip():
            return "Please enter a support question."
        result = graph.invoke({
            "chat_id": latest["chat_id"],
            "user_id": latest["user_id"],
            "message_id": latest["message_id"],
            "ticket_id": latest["message_id"],
            "customer_message": latest["text"],
            "messages": messages,
        })
        logger.debug("agent result status=%s", result.get("final_status"))
        logger.debug(
            "agent result message:\n%s",
            json.dumps(result["output_sections"], ensure_ascii=False, indent=2),
        )
        return result["output_sections"]

    logger.info("agent initialized model=%s openai_configured=%s", config.openai_model, config.openai_configured)
    return run_agent
