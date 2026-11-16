"""LangGraph workflow construction for the support-ticket co-pilot."""

from langgraph.graph import END, START, StateGraph

from app.context import TicketState
from app.nodes.abstain import abstain
from app.nodes.assess_coverage import assess_coverage
from app.nodes.classify_ticket import classify_ticket
from app.nodes.clarify_request import clarify_request
from app.nodes.decline_trading_advice import decline_trading_advice
from app.nodes.detect_safety_flags import detect_safety_flags
from app.nodes.draft_partial_reply import draft_partial_reply
from app.nodes.finalize_result import finalize_result
from app.nodes.format_output import format_output
from app.nodes.ingest_ticket import ingest_ticket
from app.nodes.prepare_complaint_review import prepare_complaint_review
from app.nodes.prepare_kyc_aml_review import prepare_kyc_aml_review
from app.nodes.prepare_policy_review import prepare_policy_review
from app.nodes.retrieve_policies import retrieve_policies
from app.nodes.route_ticket import route_ticket
from app.nodes.summarize_retrieved_data import summarize_retrieved_data
from app.nodes.validate_response import validate_response


def route_after_coverage(state: TicketState) -> str:
    return state.get("coverage", "unsupported")


def route_after_validation(state: TicketState) -> str:
    return "valid" if state.get("final_status") == "ready_for_agent_review" else "invalid"


def build_graph():
    """Build and compile the full ticket-processing graph."""
    graph = StateGraph(TicketState)
    nodes = {
        "ingest_ticket": ingest_ticket,
        "classify_ticket": classify_ticket,
        "clarify_request": clarify_request,
        "detect_safety_flags": detect_safety_flags,
        "decline_trading_advice": decline_trading_advice,
        "prepare_complaint_review": prepare_complaint_review,
        "prepare_kyc_aml_review": prepare_kyc_aml_review,
        "prepare_policy_review": prepare_policy_review,
        "retrieve_policies": retrieve_policies,
        "assess_coverage": assess_coverage,
        "abstain": abstain,
        "summarize_retrieved_data": summarize_retrieved_data,
        "draft_partial_reply": draft_partial_reply,
        "validate_response": validate_response,
        "finalize_result": finalize_result,
        "format_output": format_output,
    }
    for name, node in nodes.items():
        graph.add_node(name, node)
    graph.add_edge(START, "ingest_ticket")
    graph.add_edge("ingest_ticket", "classify_ticket")
    graph.add_edge("classify_ticket", "detect_safety_flags")
    graph.add_conditional_edges("detect_safety_flags", route_ticket, {
        "trading_advice": "decline_trading_advice",
        "complaint": "prepare_complaint_review",
        "kyc_aml": "prepare_kyc_aml_review",
        "policy_review": "prepare_policy_review",
        "normal_request": "retrieve_policies",
        "clarify_request": "clarify_request",
    })
    for node in ("decline_trading_advice", "prepare_complaint_review", "prepare_kyc_aml_review", "prepare_policy_review", "clarify_request", "abstain"):
        graph.add_edge(node, "finalize_result")
    graph.add_edge("retrieve_policies", "assess_coverage")
    graph.add_conditional_edges("assess_coverage", route_after_coverage, {
        "unsupported": "abstain",
        "partial": "draft_partial_reply",
        "supported": "summarize_retrieved_data",
    })
    graph.add_edge("draft_partial_reply", "validate_response")
    graph.add_edge("summarize_retrieved_data", "validate_response")
    graph.add_conditional_edges("validate_response", route_after_validation, {
        "invalid": "abstain",
        "valid": "finalize_result",
    })
    graph.add_edge("finalize_result", "format_output")
    graph.add_edge("format_output", END)
    return graph.compile()
