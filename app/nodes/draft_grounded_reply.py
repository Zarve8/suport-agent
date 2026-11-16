"""Draft a response from retrieved policy evidence."""

from app.context import TicketState


def draft_grounded_reply(state: TicketState) -> dict[str, object]:
    documents = state.get("retrieved_documents", [])
    evidence = documents[0].get("text", "") if documents else ""
    citations = []
    for document in documents:
        for citation in document.get("citations", []):
            if citation not in [item["citation"] for item in citations]:
                citations.append({"citation": citation, "source_file": document.get("source_files", [])})
    reply = f"Based on the available policy information:\n\n{evidence[:900]}"
    return {"draft_reply": reply, "citations": citations, "final_status": "ready_for_validation"}
