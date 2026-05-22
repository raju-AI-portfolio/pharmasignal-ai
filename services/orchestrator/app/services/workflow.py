import logging
from langgraph.graph import StateGraph, END
from app.models.state import AgentState
from app.agents.triage_agent import triage_agent
from app.agents.medical_agent import medical_agent
from app.agents.signal_agent import signal_agent
from app.agents.narrative_agent import narrative_agent
from app.agents.escalation_agent import escalation_agent

logger = logging.getLogger(__name__)

def should_continue_full_analysis(state: AgentState) -> str:
    if state.get("requires_full_analysis", True):
        return "full_analysis"
    else:
        return "skip_to_escalation"

def build_workflow():
    workflow = StateGraph(AgentState)
    workflow.add_node("triage", triage_agent)
    workflow.add_node("medical", medical_agent)
    workflow.add_node("signal", signal_agent)
    workflow.add_node("narrative", narrative_agent)
    workflow.add_node("escalation", escalation_agent)
    workflow.set_entry_point("triage")
    workflow.add_conditional_edges(
        "triage",
        should_continue_full_analysis,
        {
            "full_analysis": "medical",
            "skip_to_escalation": "escalation"
        }
    )
    workflow.add_edge("medical", "signal")
    workflow.add_edge("signal", "narrative")
    workflow.add_edge("narrative", "escalation")
    workflow.add_edge("escalation", END)
    app = workflow.compile()
    return app

def run_workflow(report: dict) -> dict:
    logger.info(f"Starting workflow for report: {report.get('report_id')}")
    initial_state: AgentState = {
        "report_id": report.get("report_id", "Unknown"),
        "drug_name": report.get("drug_name", "Unknown"),
        "reactions": report.get("reactions", []),
        "serious": report.get("serious", "No"),
        "patient_age": report.get("patient_age"),
        "patient_sex": report.get("patient_sex"),
        "raw_report": report,
        "triage_severity": None,
        "triage_reasoning": None,
        "requires_full_analysis": None,
        "medical_context": None,
        "medical_sources": None,
        "prr_score": None,
        "ror_score": None,
        "signal_detected": None,
        "case_count": None,
        "safety_narrative": None,
        "data_gaps": None,
        "risk_score": None,
        "routing_decision": None,
        "routing_reasoning": None,
        "current_step": "starting",
        "errors": []
    }
    app = build_workflow()
    final_state = app.invoke(initial_state)
    logger.info(f"Workflow complete — routing: {final_state.get('routing_decision')}")
    return final_state
