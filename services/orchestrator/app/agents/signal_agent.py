import os
import logging
import httpx
from app.models.state import AgentState
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)

INGESTION_SERVICE_URL = os.getenv("INGESTION_SERVICE_URL", "http://localhost:8001")

def calculate_prr(a, b, c, d):
    if b == 0 or c == 0 or d == 0:
        return 0.0
    numerator = a / (a + b)
    denominator = c / (c + d)
    if denominator == 0:
        return 0.0
    return round(numerator / denominator, 2)

def calculate_ror(a, b, c, d):
    if b == 0 or c == 0 or d == 0:
        return 0.0
    return round((a * d) / (b * c), 2)

def calculate_chi_square(a, b, c, d):
    n = a + b + c + d
    if n == 0:
        return 0.0
    expected = ((a + b) * (a + c)) / n
    if expected == 0:
        return 0.0
    return round(((a - expected) ** 2) / expected, 2)

def signal_agent(state: AgentState) -> AgentState:
    logger.info(f"Signal Agent processing report: {state['report_id']}")
    try:
        with httpx.Client(timeout=30.0) as client:
            response = client.get(f"{INGESTION_SERVICE_URL}/api/v1/reports?limit=100")
            response.raise_for_status()
            all_reports = response.json()["reports"]
        total_reports = len(all_reports)
        if total_reports < 3:
            state["prr_score"] = 0.0
            state["ror_score"] = 0.0
            state["signal_detected"] = False
            state["case_count"] = total_reports
            state["current_step"] = "signal_complete"
            return state
        drug_name = state["drug_name"].upper()
        target_reactions = [r.upper() for r in state["reactions"]]
        a = b = c = d = 0
        for report in all_reports:
            is_this_drug = report["drug_name"].upper() == drug_name
            report_reactions = [r.upper() for r in (report["reactions"] or [])]
            has_this_reaction = any(r in report_reactions for r in target_reactions)
            if is_this_drug and has_this_reaction:
                a += 1
            elif is_this_drug and not has_this_reaction:
                b += 1
            elif not is_this_drug and has_this_reaction:
                c += 1
            else:
                d += 1
        prr = calculate_prr(a, b, c, d)
        ror = calculate_ror(a, b, c, d)
        chi_sq = calculate_chi_square(a, b, c, d)
        signal_detected = prr >= 2.0 and chi_sq >= 4.0 and a >= 3
        state["prr_score"] = prr
        state["ror_score"] = ror
        state["signal_detected"] = signal_detected
        state["case_count"] = a
        state["current_step"] = "signal_complete"
        return state
    except Exception as e:
        logger.error(f"Signal agent error: {e}")
        state["prr_score"] = 0.0
        state["ror_score"] = 0.0
        state["signal_detected"] = False
        state["case_count"] = 0
        state["errors"] = state.get("errors", []) + [str(e)]
        return state
