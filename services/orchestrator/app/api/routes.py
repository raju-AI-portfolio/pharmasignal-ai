from fastapi import APIRouter, HTTPException
from app.services.workflow import run_workflow
import httpx
import os
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

INGESTION_SERVICE_URL = os.getenv("INGESTION_SERVICE_URL", "http://localhost:8001")

@router.get("/health")
def health_check():
    return {"status": "ok", "service": "orchestrator"}

@router.post("/analyse/{report_id}")
async def analyse_report(report_id: str):
    """
    Runs the full 5-agent workflow for a single report.
    Fetches the report from ingestion service then runs all agents.
    """
    try:
        # Fetch report from ingestion service
        with httpx.Client(timeout=30.0) as client:
            response = client.get(
                f"{INGESTION_SERVICE_URL}/api/v1/reports?limit=100"
            )
            response.raise_for_status()
            all_reports = response.json()["reports"]
        
        # Find the specific report
        report = None
        for r in all_reports:
            if r["report_id"] == report_id:
                report = r
                break
        
        if not report:
            raise HTTPException(
                status_code=404,
                detail=f"Report {report_id} not found"
            )
        
        # Run the full agent workflow
        logger.info(f"Running workflow for report: {report_id}")
        result = run_workflow(report)
        
        # Return clean summary
        return {
            "report_id": report_id,
            "drug_name": result.get("drug_name"),
            "reactions": result.get("reactions"),
            "triage": {
                "severity": result.get("triage_severity"),
                "reasoning": result.get("triage_reasoning")
            },
            "signal": {
                "prr_score": result.get("prr_score"),
                "ror_score": result.get("ror_score"),
                "signal_detected": result.get("signal_detected"),
                "case_count": result.get("case_count")
            },
            "narrative": result.get("safety_narrative"),
            "escalation": {
                "risk_score": result.get("risk_score"),
                "routing_decision": result.get("routing_decision"),
                "routing_reasoning": result.get("routing_reasoning")
            },
            "data_gaps": result.get("data_gaps"),
            "errors": result.get("errors")
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Workflow error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/analyse-all")
async def analyse_all_reports():
    """
    Runs the workflow for all reports in the database.
    Returns a summary of all routing decisions.
    """
    try:
        # Fetch all reports
        with httpx.Client(timeout=30.0) as client:
            response = client.get(
                f"{INGESTION_SERVICE_URL}/api/v1/reports?limit=20"
            )
            response.raise_for_status()
            all_reports = response.json()["reports"]
        
        results = []
        for report in all_reports:
            result = run_workflow(report)
            results.append({
                "report_id": result.get("report_id"),
                "drug_name": result.get("drug_name"),
                "severity": result.get("triage_severity"),
                "risk_score": result.get("risk_score"),
                "routing": result.get("routing_decision")
            })
        
        return {
            "total_processed": len(results),
            "results": results
        }
        
    except Exception as e:
        logger.error(f"Batch workflow error: {e}")
        raise HTTPException(status_code=500, detail=str(e))