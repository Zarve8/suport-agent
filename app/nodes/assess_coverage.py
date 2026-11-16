"""Assess whether BM25 results contain enough evidence."""

from app.context import TicketState

STOPWORDS = {"about", "after", "can", "could", "does", "from", "have", "help", "how", "into", "need", "the", "this", "what", "when", "where", "with", "would", "you"}

CATEGORY_TERMS = {
    "deposit": ("deposit", "funds", "payment"),
    "withdrawal": ("withdraw", "withdrawal"),
    "account_verification": ("verify", "verification", "document"),
    "account_opening": ("open", "account", "register"),
    "kyc_aml": ("aml", "kyc", "funds"),
}


def assess_coverage(state: TicketState) -> dict[str, str]:
    documents = state.get("retrieved_documents", [])
    if not documents:
        return {"coverage": "unsupported"}
    if state.get("category") == "other":
        return {"coverage": "unsupported"}
    query_words = {
        word.strip(".,?!'")
        for word in state["customer_message"].lower().split()
        if len(word) > 3 and word.strip(".,?!'") not in STOPWORDS
    }
    evidence = " ".join(str(doc.get("text", "")) for doc in documents).lower()
    matched = sum(word in evidence for word in query_words)
    if query_words and matched >= 1:
        return {"coverage": "supported"}

    # For translated/non-English questions, lexical overlap with English
    # evidence is not expected. Retrieval has already been expanded using the
    # classified intent, so require intent evidence instead of rejecting it.
    category_terms = CATEGORY_TERMS.get(state.get("category", ""), ())
    category_match = sum(term in evidence for term in category_terms)
    if state.get("language") != "English" and category_terms and category_match >= 1:
        return {"coverage": "supported"}
    if state.get("category") == "kyc_aml" and state.get("language") == "English" and documents:
        # General AML questions may be answered from policy evidence. The
        # account-specific cases are routed to human review before retrieval.
        if "source of funds" in state.get("customer_message", "").lower():
            return {"coverage": "supported"}
    return {"coverage": "unsupported"}
