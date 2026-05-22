import os
import logging
import httpx
from app.models.state import AgentState
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)

RAG_SERVICE_URL = os.getenv("RAG_SERVICE_URL", "http://localhost:8002")

def medical_agent(state: AgentState) -> AgentState:
    logger.info(f"Medical Agent processing report: {state['report_id']}")
    reactions_str = ', '.join(state['reactions'])
    query = f"{state['drug_name']} {reactions_str} adverse event serious"
    try:
        with httpx.Client(timeout=30.0) as client:
            response = client.post(
                f"{RAG_SERVICE_URL}/api/v1/search",
                json={"query": query, "n_results": 3}
            )
            response.raise_for_status()
            results = response.json()
        if results["total_found"] == 0:
            state["medical_context"] = "No relevant regulatory context found"
            state["medical_sources"] = []
            return state
        context_parts = []
        sources = []
        for result in results["results"]:
            context_parts.append(result["content"])
            if result["source"] not in sources:
                sources.append(result["source"])
        state["medical_context"] = "\n\n---\n\n".join(context_parts)
        state["medical_sources"] = sources
        state["current_step"] = "medical_complete"
        return state
    except Exception as e:
        logger.error(f"Medical agent error: {e}")
        state["medical_context"] = f"Error: {e}"
        state["medical_sources"] = []
        state["errors"] = state.get("errors", []) + [str(e)]
        return state
