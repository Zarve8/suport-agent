"""Return a safe response when policy coverage is insufficient."""

from app.context import TicketState
from app.mcp.escalation import escalate_to_human


def abstain(state: TicketState) -> dict[str, object]:
    escalate_to_human(state["customer_message"], state["chat_id"])
    language = state.get("language", "English")
    waiting = {
        "Russian": "Ожидайте помощи специалиста.",
        "Spanish": "Espere la ayuda de un especialista.",
        "French": "Veuillez attendre l’aide d’un spécialiste.",
    }.get(language, "Waiting for human help")
    return {"draft_reply": waiting, "requires_human": True, "routing_reason": "Knowledge base does not cover the request", "final_status": "abstained"}
