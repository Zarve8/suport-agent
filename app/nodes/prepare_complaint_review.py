"""Prepare complaint acknowledgement and human routing."""

from app.context import TicketState
from app.mcp.escalation import escalate_to_human


def prepare_complaint_review(state: TicketState) -> dict[str, object]:
    reason = "Complaint requires human review"
    escalate_to_human(state["customer_message"], state["chat_id"])
    language = state.get("language", "English")
    acknowledgement = {
        "Russian": "Мы получили вашу жалобу. Ожидайте помощи специалиста.",
        "Spanish": "Hemos recibido su queja. Espere la ayuda de un especialista.",
        "French": "Nous avons reçu votre réclamation. Veuillez attendre l’aide d’un spécialiste.",
    }.get(language, "We acknowledge your complaint. Waiting for human help")
    return {"draft_reply": acknowledgement, "requires_human": True, "routing_reason": reason, "final_status": "human_review_required"}
