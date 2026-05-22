from typing import TypedDict, Optional, List

class AgentState(TypedDict):
    """
    This is the shared state that flows between all agents.
    Every agent reads from this and writes back to it.
    Think of it as a shared whiteboard all agents can see.
    """
    # The original adverse event report
    report_id: str
    drug_name: str
    reactions: List[str]
    serious: str
    patient_age: Optional[str]
    patient_sex: Optional[str]
    raw_report: dict

    # Triage agent output
    triage_severity: Optional[str]       # SERIOUS or NON-SERIOUS
    triage_reasoning: Optional[str]      # Why it classified this way
    requires_full_analysis: Optional[bool]

    # Medical agent output
    medical_context: Optional[str]       # What literature says
    medical_sources: Optional[List[str]] # Which documents were found

    # Signal agent output
    prr_score: Optional[float]           # Proportional Reporting Ratio
    ror_score: Optional[float]           # Reporting Odds Ratio
    signal_detected: Optional[bool]      # True if signal threshold met
    case_count: Optional[int]            # How many similar cases exist

    # Narrative agent output
    safety_narrative: Optional[str]      # Full ICH E2B narrative
    data_gaps: Optional[List[str]]       # Missing information

    # Escalation agent output
    risk_score: Optional[int]            # 0-100
    routing_decision: Optional[str]      # AUTO-CLOSE, FLAG, ESCALATE
    routing_reasoning: Optional[str]     # Why this routing was chosen

    # Workflow metadata
    current_step: Optional[str]
    errors: Optional[List[str]]