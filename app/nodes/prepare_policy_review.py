"""Escalate requests whose required policy source is unavailable."""

from app.context import TicketState
from app.mcp.escalation import escalate_to_human


def prepare_policy_review(state: TicketState) -> dict[str, object]:
    """Escalate withdrawal/account-policy questions without guessing."""
    reason = "Required approved policy source is unavailable"
    escalate_to_human(state["customer_message"], state["chat_id"])
    language = state.get("language", "English")
    waiting = {
        "Russian": "Ожидайте помощи специалиста.",
        "Spanish": "Espere la ayuda de un especialista.",
        "French": "Veuillez attendre l’aide d’un spécialiste.",
    }.get(language, "Waiting for human help")
    acknowledgement = ""
    if state.get("category") == "withdrawal" and "pending" not in state.get("customer_message", "").lower():
        acknowledgement = {
            "Russian": "Ваш вопрос о выводе средств передан специалисту. ",
            "Spanish": "Su pregunta sobre el retiro de fondos se ha enviado a un especialista. ",
            "French": "Votre question concernant le retrait a été transmise à un spécialiste. ",
        }.get(language, "Your withdrawal question has been sent to a support specialist. ")
    return {
        "draft_reply": acknowledgement + waiting,
        "requires_human": True,
        "routing_reason": reason,
        "final_status": "human_review_required",
    }
