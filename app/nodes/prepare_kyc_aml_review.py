"""Prepare KYC/AML acknowledgement and human routing."""

from app.context import TicketState
from app.mcp.escalation import escalate_to_human


def prepare_kyc_aml_review(state: TicketState) -> dict[str, object]:
    reason = "KYC/AML outcome requires human review"
    escalate_to_human(state["customer_message"], state["chat_id"])
    return {"draft_reply": "Waiting for human help", "requires_human": True, "routing_reason": reason, "final_status": "human_review_required"}
