"""Create one concise grounded response from retrieved policy chunks."""

from __future__ import annotations

from langchain_openai import ChatOpenAI

from app.config import settings
from app.context import TicketState


def summarize_retrieved_data(state: TicketState) -> dict[str, object]:
    """Summarize retrieved evidence into a short customer-facing response."""
    documents = state.get("retrieved_documents", [])
    citations = []
    evidence_parts = []
    question_lower = state["customer_message"].lower()
    if "crypto" in question_lower or "usdt" in question_lower:
        documents = sorted(
            documents,
            key=lambda document: "crypto usdt" in str(document.get("text", "")).lower(),
            reverse=True,
        )
    if "online banking" in question_lower or "malaysia" in question_lower:
        documents = sorted(
            documents,
            key=lambda document: "online banking" in str(document.get("text", "")).lower()
            and ("malaysia" in str(document.get("text", "")).lower() or "myr" in str(document.get("text", "")).lower()),
            reverse=True,
        )
    if "any time" in question_lower or "time of day" in question_lower or "24/7" in question_lower:
        documents = sorted(
            documents,
            key=lambda document: any(
                marker in str(document.get("text", "")).lower()
                for marker in ("24/7", "24 / 7", "availability")
            ),
            reverse=True,
        )
    for document in documents:
        evidence_parts.append(str(document.get("text", ""))[:1400])
        for citation in document.get("citations", []):
            if citation not in citations:
                citations.append(citation)

    evidence = "\n\n".join(evidence_parts[:5])
    citation_text = ", ".join(citations)
    if not settings.openai_configured:
        return {
            "draft_reply": evidence[:500].strip(),
            "citations": [{"citation": citation} for citation in citations],
            "final_status": "ready_for_validation",
        }

    model = ChatOpenAI(model=settings.openai_model, api_key=settings.openai_api_key, temperature=0)
    prompt = f"""You are a support-ticket response writer.

Answer the customer's specific question using only the policy evidence below.

Rules:
1. Ignore retrieved passages that are not directly relevant.
2. Cite only sources that directly support a sentence in the answer.
3. Do not cite every retrieved document automatically.
4. Never invent fees, requirements, timelines, or account decisions.
5. Do not provide trading advice.
6. Do not decide complaints, KYC, or AML outcomes.
7. Use no more than 3 short numbered steps or bullets and no more than 100 words.
8. Do not use Markdown headings.
9. End with a `Sources:` line containing only the exact citation labels used.
10. If policies conflict, explicitly explain the conflict, cite both sources,
    and advise human confirmation. Never silently choose one value.
11. When a policy says a deposit is “instant” and also says the balance is
    visible within 60 minutes, explain that instant refers to processing/initiation
    while the updated balance may take up to 60 minutes to appear.
12. When the question names a specific payment method, such as Crypto USDt,
    prioritize the exact payment-method row for that method (minimum, commission,
    processing time, and availability) over generic account-level deposit FAQs.
13. Do not replace an exact payment-method value with a generic USD 1 or 8 USD
    account minimum. The generic minimum applies only when the customer asks for
    the general account minimum.
14. For a named payment method, use a mandatory completeness checklist before
    writing the answer. Include every field that is present in the relevant
    source, even if the question mentions only one of them:
    - Minimum deposit
    - Commission or fee
    - Processing time
    - Availability (for example, 24/7)
15. For Crypto USDt specifically, if the evidence contains them, the answer
    MUST state all four values: 50 USDT minimum deposit, 1.5 USDT commission,
    10 minutes to 4 hours processing time, and 24/7 availability. Do not stop
    after stating the first three. If a value is not present in the evidence,
    write `Not stated in the cited policy` for that field; never guess it.
16. For named payment-method answers, format the factual content as one short
    line per available checklist field, followed by the required Sources line.
    This is a completeness requirement, not an invitation to add unrelated
    deposit instructions.
17. Match the answer scope to the question. For availability questions, discuss
    only payment-method availability or stated operating hours. Never infer
    availability from words such as "instant" or from processing time. If the
    evidence does not explicitly state availability, say it is not stated in
    the cited policy and do not answer yes. For payment-
    channel questions, list channel names and status only. For a general
    minimum-deposit conflict, report only the conflicting general values and
    map each value to its source; do not add Crypto USDt details.
18. For country- and payment-method-specific questions, use only the exact
    matching row. For Online Banking in Malaysia, prefer the MYR row and do not
    substitute generic USD minimums. If the exact row is absent, say it is not
    stated in the cited policy rather than guessing.
    If another source gives a conflicting generic minimum, report the conflict
    explicitly and map each value to its source; do not present 50 MYR as the
    uncontested answer. Answer only the minimum question, without fees or timing.
19. If the question is a general source-of-funds question, provide a brief,
    neutral explanation from general AML policy with citations. Do not disclose
    or decide the customer's account-specific status.
20. Respond in the detected customer language. For Russian, use Russian; for
    Spanish, use Spanish; and for French, use French when evidence supports an
    answer. If escalation is required, use a short localized equivalent of
    `Waiting for human help` instead of English text.

Customer question:
{state['customer_message']}

Candidate policy evidence:
{evidence}

Available citation labels:
{citation_text}

Detected language: {state.get('language', 'English')}

Return only the final customer-facing answer.
"""
    response = model.invoke(prompt)
    return {
        "draft_reply": str(response.content).strip(),
        "citations": [{"citation": citation} for citation in citations],
        "final_status": "ready_for_validation",
    }
