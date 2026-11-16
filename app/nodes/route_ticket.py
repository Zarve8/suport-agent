"""Choose a deterministic branch from safety flags."""

from app.context import TicketState
import logging

logger = logging.getLogger(__name__)

VAGUE_REQUESTS = {
    "i need help",
    "please assist me",
    "something is wrong",
    "i have a problem",
    "can someone help",
}


def route_ticket(state: TicketState) -> str:
    message = " ".join(state.get("customer_message", "").lower().split()).rstrip(".!?")
    if message in VAGUE_REQUESTS:
        logger.info("route=clarify_request")
        return "clarify_request"
    flags = set(state.get("safety_flags", []))
    if "account_action" in flags:
        logger.info("route=policy_review account_action")
        return "policy_review"
    if "trading_advice" in flags:
        logger.info("route=trading_advice")
        return "trading_advice"
    if "complaint" in flags:
        logger.info("route=complaint")
        return "complaint"
    if "kyc_aml" in flags:
        # General source-of-funds questions can use general AML policy text.
        # Account-specific holds, rejections, and classifications still escalate.
        if "source of funds" in message and not any(word in message for word in ("reject", "hold", "my account", "reported")):
            logger.info("route=normal_request general_source_of_funds")
            return "normal_request"
        logger.info("route=kyc_aml")
        return "kyc_aml"
    if state.get("category") in {"withdrawal", "account_verification", "account_opening"}:
        logger.info("route=policy_review category=%s", state.get("category"))
        return "policy_review"
    logger.info("route=normal_request")
    return "normal_request"
