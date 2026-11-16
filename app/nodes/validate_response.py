"""Validate output against hard rules and guardrail checks."""

from app.context import TicketState
import re


def validate_response(state: TicketState) -> dict[str, object]:
    errors = list(state.get("validation_errors", []))
    if re.search(r"\b(buy|sell|signal|price target|leverage)\b", state.get("draft_reply", ""), re.I):
        errors.append("Trading advice detected in draft")
    if state.get("coverage") == "unsupported":
        errors.append("No policy coverage")
    if state.get("draft_reply") and state.get("coverage") != "unsupported" and not state.get("citations"):
        errors.append("Missing citations")
    if errors:
        return {"validation_errors": errors, "final_status": "abstained", "requires_human": True, "routing_reason": "Response validation failed"}
    return {"final_status": "ready_for_agent_review"}
