"""Ask the customer to provide enough detail to route the ticket."""

from app.context import TicketState


def clarify_request(state: TicketState) -> dict[str, object]:
    """Return a clarification prompt for vague support requests."""
    return {
        "draft_reply": (
            "Of course. Could you tell me more about what you need help with? "
            "For example, is your question about making a deposit, withdrawing "
            "funds, opening an account, or verifying your account?"
        ),
        "requires_human": False,
        "final_status": "clarification_requested",
        "routing_reason": "Customer request is too vague to retrieve safely",
    }
