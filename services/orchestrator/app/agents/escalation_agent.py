import os
import logging
from app.models.state import AgentState
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)

def escalation_agent(state: AgentState) -> AgentState:
    logger.info(f"Escalation Agent processing report: {state['report_id']}")
    score = 0
    reasoning_parts = []

    severity = state.get("triage_severity", "NON-SERIOUS")
    if severity == "SERIOUS":
        score += 40
        reasoning_parts.append("Serious adverse event (+40)")
    else:
        score += 10
        reasoning_parts.append("Non-serious adverse event (+10)")

    signal_detected = state.get("signal_detected", False)
    prr = state.get("prr_score", 0)
    if signal_detected:
        score += 30
        reasoning_parts.append(f"Safety signal detected PRR={prr} (+30)")
    elif prr >= 1.5:
        score += 15
        reasoning_parts.append(f"Elevated PRR={prr} (+15)")
    else:
        reasoning_parts.append(f"No signal PRR={prr} (+0)")

    data_gaps = state.get("data_gaps", [])
    if len(data_gaps) == 0:
        score += 20
        reasoning_parts.append("Complete data (+20)")
    elif len(data_gaps) <= 2:
        score += 10
        reasoning_parts.append(f"{len(data_gaps)} data gaps (+10)")

    case_count = state.get("case_count", 0)
    if case_count >= 5:
        score += 10
        reasoning_parts.append(f"{case_count} cases (+10)")
    elif case_count >= 3:
        score += 5
        reasoning_parts.append(f"{case_count} cases (+5)")

    if score < 40:
        routing = "AUTO-CLOSE"
        routing_reason = f"Risk score {score}/100 — below threshold"
    elif score <= 70:
        routing = "FLAG"
        routing_reason = f"Risk score {score}/100 — flagged for review"
    else:
        routing = "ESCALATE"
        routing_reason = f"Risk score {score}/100 — escalate to QPPV"

    state["risk_score"] = score
    state["routing_decision"] = routing
    state["routing_reasoning"] = routing_reason
    state["current_step"] = "escalation_complete"
    logger.info(f"Escalation complete — Score: {score}, Routing: {routing}")
    return state
