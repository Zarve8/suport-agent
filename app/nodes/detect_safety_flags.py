"""Detect hard-policy flags using deterministic rules and the guardrail stub."""

from app.context import TicketState
import re
import logging

logger = logging.getLogger(__name__)


def detect_safety_flags(state: TicketState) -> dict[str, object]:
    message = state["customer_message"].lower()
    flags: set[str] = set()
    account_action = any(phrase in message for phrase in ("change my account leverage", "change leverage", "update my leverage", "set my leverage"))
    if not account_action and (re.search(r"\b(buy|sell|signal|price target|what price|copy trading|currency pair|leverage|which trade)\b", message) or ("best" in message and re.search(r"\b(model|strategy|trade)\b", message))):
        flags.add("trading_advice")
    if account_action:
        flags.add("account_action")
    if any(word in message for word in ("complaint", "unacceptable", "compensation", "refund", "chargeback")):
        flags.add("complaint")
    if any(word in message for word in ("kyc", "aml", "verification rejected", "source of funds", "high-risk", "high risk")):
        flags.add("kyc_aml")
    result = sorted(flags)
    logger.info("safety flags=%s", result)
    return {"safety_flags": result}
