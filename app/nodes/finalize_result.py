"""Log and finalize the agent-facing result."""

from app.context import TicketState


def finalize_result(state: TicketState) -> dict[str, object]:
    status = state.get("final_status", "ready_for_agent_review")
    return {"final_status": status}
