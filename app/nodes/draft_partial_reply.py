"""Draft a limited answer for partial policy coverage."""

from app.context import TicketState
from app.nodes.draft_grounded_reply import draft_grounded_reply


def draft_partial_reply(state: TicketState) -> dict[str, object]:
    result = draft_grounded_reply(state)
    result["draft_reply"] = str(result["draft_reply"]) + "\n\nI could not verify the remaining details from the available policies, so a support agent will need to assist further."
    result["requires_human"] = True
    return result
