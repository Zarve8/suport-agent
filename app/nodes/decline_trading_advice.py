"""Decline prohibited trading advice."""

from app.context import TicketState


def decline_trading_advice(state: TicketState) -> dict[str, object]:
    return {
        "draft_reply": "I can’t provide buy or sell recommendations, trading signals, price targets, or leverage advice.",
        "requires_human": False,
        "final_status": "trading_advice_declined",
    }
