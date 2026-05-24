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

def triage_agent(state: AgentState) -> AgentState:
    """
    Triage Agent — classifies adverse event severity.
    
    Reads:  report data from state
    Writes: triage_severity, triage_reasoning, requires_full_analysis
    """
    logger.info(f"Triage Agent processing report: {state['report_id']}")
    
    client = get_llm_client()
    
    # Build the prompt
    prompt = f"""You are a pharmacovigilance triage specialist.

Classify this adverse event report severity based on ICH E2B criteria.

Report Details:
- Report ID: {state['report_id']}
- Drug: {state['drug_name']}
- Reactions: {', '.join(state['reactions'])}
- Already marked serious: {state['serious']}
- Patient age: {state.get('patient_age', 'Unknown')}
- Patient sex: {state.get('patient_sex', 'Unknown')}

ICH E2B Serious Criteria — classify as SERIOUS if ANY of these apply:
- Results in death
- Is life-threatening  
- Requires hospitalisation
- Results in disability
- Is a congenital anomaly
- Is medically significant

Respond in exactly this format:
SEVERITY: [SERIOUS or NON-SERIOUS]
REASONING: [One sentence explanation]
REQUIRES_FULL_ANALYSIS: [YES or NO]"""

    try:
        response = client.chat.completions.create(
            model=os.getenv("AZURE_OPENAI_CHAT_DEPLOYMENT"),
            messages=[
                {"role": "system", "content": "You are a pharmacovigilance expert. Be concise and precise."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=150,
            temperature=0
        )
        
        result = response.choices[0].message.content
        logger.info(f"Triage result: {result}")
        
        # Parse the response
        lines = result.strip().split('\n')
        severity = "SERIOUS"
        reasoning = "Unable to parse"
        requires_full = True
        
        for line in lines:
            if line.startswith("SEVERITY:"):
                severity = line.replace("SEVERITY:", "").strip()
            elif line.startswith("REASONING:"):
                reasoning = line.replace("REASONING:", "").strip()
            elif line.startswith("REQUIRES_FULL_ANALYSIS:"):
                val = line.replace("REQUIRES_FULL_ANALYSIS:", "").strip()
                requires_full = val == "YES"
        
        # Update state
        state["triage_severity"] = severity
        state["triage_reasoning"] = reasoning
        state["requires_full_analysis"] = requires_full
        state["current_step"] = "triage_complete"
        
        logger.info(f"Triage complete — {severity} — Full analysis: {requires_full}")
        return state
        
    except Exception as e:
        logger.error(f"Triage agent error: {e}")
        state["triage_severity"] = "SERIOUS"
        state["triage_reasoning"] = f"Error in triage — defaulting to SERIOUS: {e}"
        state["requires_full_analysis"] = True
        state["errors"] = state.get("errors", []) + [str(e)]
        return state