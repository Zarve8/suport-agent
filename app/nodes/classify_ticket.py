"""Classify a ticket into controlled support dimensions."""

import re
import logging
from difflib import get_close_matches

from app.context import TicketState

logger = logging.getLogger(__name__)


def classify_ticket(state: TicketState) -> dict[str, str]:
    message = state["customer_message"]
    vocabulary = ("withdraw", "deposit", "verify", "verification", "document", "complaint", "refund", "chargeback", "aml", "buy", "sell", "signal", "leverage", "copy", "trading", "model", "strategy")
    normalized_words = []
    for word in message.lower().split():
        stripped = word.strip(".,!?'")
        match = get_close_matches(stripped, vocabulary, n=1, cutoff=0.78)
        normalized_words.append(match[0] if match else word)
    normalized = " ".join(normalized_words)
    lower = normalized
    if re.search(r"(депозит|внести|пополнить|пополнение)", message.lower()) or re.search(r"\b(dépôt|depot|effectuer un dépôt)\b", message.lower()):
        category = "deposit"
    elif re.search(r"\b(verificar|verifique|vérifier)\b", message.lower()):
        category = "account_verification"
    elif any(phrase in lower for phrase in ("balance updated", "after depositing")) or ("funds" in lower and "available" in lower and "trading" in lower):
        category = "deposit"
    elif any(phrase in lower for phrase in ("change my account leverage", "change leverage", "update my leverage", "set my leverage")):
        category = "account_action"
    elif any(word in lower for word in ("withdraw", "cash out")):
        category = "withdrawal"
    elif any(word in lower for word in ("deposit", "fund my account")):
        category = "deposit"
    elif any(word in lower for word in ("verify", "verification", "document", "kyc")):
        category = "account_verification"
    elif any(word in lower for word in ("open account", "register", "sign up")):
        category = "account_opening"
    elif any(word in lower for word in ("complaint", "unacceptable", "compensation", "refund", "chargeback")):
        category = "complaint"
    elif any(word in lower for word in ("aml", "money laundering", "source of funds", "high-risk", "high risk")):
        category = "kyc_aml"
    elif any(word in lower for word in ("buy", "sell", "signal", "leverage", "price target", "what price", "copy trading", "currency pair")) or ("best" in lower and any(word in lower for word in ("model", "strategy", "trade"))):
        category = "trading_advice"
    else:
        category = "other"
    urgency = "high" if re.search(r"\b(urgent|immediately|blocked|today)\b", lower) else "normal"
    sentiment = "negative" if re.search(r"\b(angry|worst|unacceptable|frustrated|complaint)\b", lower) else "neutral"
    if re.search(r"[А-Яа-яЁё]", message):
        language = "Russian"
    elif re.search(r"[¿¡]|\b(cómo|como|verificar|cuenta|depósito|deposito)\b", message.lower()):
        language = "Spanish"
    elif re.search(r"\b(comment|effectuer|dépôt|depot|vérifier|compte)\b", message.lower()):
        language = "French"
    else:
        language = "English"
    logger.info("classified category=%s urgency=%s language=%s sentiment=%s", category, urgency, language, sentiment)
    return {"category": category, "urgency": urgency, "sentiment": sentiment, "language": language, "normalized_question": normalized}
