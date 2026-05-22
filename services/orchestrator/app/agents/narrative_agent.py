import os
import logging
from openai import AzureOpenAI
from app.models.state import AgentState
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)

def get_llm_client():
    return AzureOpenAI(
        azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
        api_key=os.getenv("AZURE_OPENAI_KEY"),
        api_version=os.getenv("AZURE_OPENAI_API_VERSION")
    )

def narrative_agent(state: AgentState) -> AgentState:
    logger.info(f"Narrative Agent processing report: {state['report_id']}")
    client = get_llm_client()
    prompt = f"""You are a pharmacovigilance medical writer.
Write an ICH E2B compliant safety narrative for this adverse event report.

REPORT DATA:
- Report ID: {state['report_id']}
- Drug: {state['drug_name']}
- Reactions: {', '.join(state['reactions'])}
- Patient Age: {state.get('patient_age', 'Unknown')}
- Patient Sex: {state.get('patient_sex', 'Unknown')}
- Serious: {state['serious']}

TRIAGE: {state.get('triage_severity')} — {state.get('triage_reasoning')}
SIGNAL: PRR={state.get('prr_score')} ROR={state.get('ror_score')} Detected={state.get('signal_detected')}

REGULATORY CONTEXT:
{str(state.get('medical_context', 'None'))[:500]}

Write narrative with these sections:
1. PATIENT BACKGROUND
2. DRUG EXPOSURE
3. ADVERSE EVENT
4. OUTCOME
5. SIGNAL CONTEXT
6. REGULATORY ASSESSMENT
7. DATA GAPS

Maximum 300 words. Be factual."""
    try:
        response = client.chat.completions.create(
            model=os.getenv("AZURE_OPENAI_CHAT_DEPLOYMENT"),
            messages=[
                {"role": "system", "content": "You are a pharmacovigilance medical writer."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=500,
            temperature=0
        )
        narrative = response.choices[0].message.content
        data_gaps = []
        if "DATA GAPS:" in narrative:
            gaps_section = narrative.split("DATA GAPS:")[-1].strip()
            data_gaps = [g.strip() for g in gaps_section.split('\n') if g.strip()]
        state["safety_narrative"] = narrative
        state["data_gaps"] = data_gaps
        state["current_step"] = "narrative_complete"
        return state
    except Exception as e:
        logger.error(f"Narrative agent error: {e}")
        state["safety_narrative"] = f"Error: {e}"
        state["data_gaps"] = ["Narrative generation failed"]
        state["errors"] = state.get("errors", []) + [str(e)]
        return state
