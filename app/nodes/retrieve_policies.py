"""Retrieve policy chunks through the BM25 knowledge-base stub."""

from app.context import TicketState
from app.mcp.knowledge_base import search_knowledge_base


def retrieve_policies(state: TicketState) -> dict[str, object]:
    query = state.get("normalized_question", state["customer_message"])
    lower = query.lower()
    # The policy corpus is English. Add English retrieval terms for supported
    # non-English intents while preserving the original customer question for
    # the response language and audit trail.
    if state.get("language") == "Russian":
        if state.get("category") == "deposit":
            query += " how to deposit funds deposit payment methods balance"
        elif state.get("category") == "withdrawal":
            query += " how to withdraw funds withdrawal payment methods"
        elif state.get("category") == "account_verification":
            query += " how to verify account verification documents"
        elif state.get("category") == "account_opening":
            query += " how to open an account registration"
    elif state.get("language") == "Spanish":
        if state.get("category") == "account_verification":
            query += " how to verify account verification documents"
    elif state.get("language") == "French":
        if state.get("category") == "deposit":
            query += " how to deposit funds deposit payment methods"
        lower = query.lower()
    if "crypto" in lower or "usdt" in lower:
        query += " Crypto USDt minimum deposit commission processing time availability"
    if "online banking" in lower or "malaysia" in lower:
        query += " Online Banking Malaysia MYR minimum deposit commission processing availability"
    if "any time" in lower or "time of day" in lower or "24/7" in lower:
        query += " payment method availability operating hours 24/7"
    documents = search_knowledge_base(query, top_k=5)
    return {"retrieved_documents": [{"text": doc.page_content, **doc.metadata} for doc in documents]}
