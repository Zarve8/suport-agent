"""LangGraph state shared by ticket-processing nodes."""

from typing import TypedDict


class TicketState(TypedDict, total=False):
    ticket_id: str
    chat_id: str
    message_id: str
    user_id: str
    customer_message: str
    normalized_question: str
    messages: list[dict[str, str]]
    prompt_messages: list[object]
    output_sections: list[dict[str, str]]
    language: str
    category: str
    urgency: str
    sentiment: str
    safety_flags: list[str]
    requires_human: bool
    routing_reason: str
    retrieved_documents: list[dict[str, str]]
    coverage: str
    draft_reply: str
    citations: list[dict[str, str]]
    validation_errors: list[str]
    final_status: str
