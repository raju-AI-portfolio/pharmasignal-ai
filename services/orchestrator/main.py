from fastapi import FastAPI
from app.api.routes import router
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

app = FastAPI(
    title="PharmaSignal Agent Orchestrator",
    description="LangGraph multi-agent workflow for adverse event analysis",
    version="1.0.0"
)

app.include_router(router, prefix="/api/v1")

@app.get("/")
def root():
    return {
        "service": "PharmaSignal Agent Orchestrator",
        "status": "running",
        "docs": "/docs",
        "agents": [
            "triage_agent",
            "medical_agent", 
            "signal_agent",
            "narrative_agent",
            "escalation_agent"
        ]
    }