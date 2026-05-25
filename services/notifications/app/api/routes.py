from fastapi import APIRouter, HTTPException
from app.services.email_service import notify_escalation, notify_approval, notify_rejection
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/health")
def health_check():
    return {"status": "ok", "service": "notifications"}

@router.post("/notify")
async def send_notification(payload: dict):
    """
    Sends notification based on review decision.
    Called by review-api after a human makes a decision.

    Expected format:
    {
        "decision": "ESCALATED",
        "report_id": "CRM-001",
        "drug_name": "WARFARIN",
        "risk_score": 60,
        "reviewed_by": "dr.smith@pharmasignal.com",
        "comments": "Needs QPPV review",
        "narrative": "Safety narrative text..."
    }
    """
    decision = payload.get("decision", "").upper()
    report_id = payload.get("report_id")
    drug_name = payload.get("drug_name", "Unknown")
    risk_score = payload.get("risk_score", 0)
    reviewed_by = payload.get("reviewed_by", "Unknown")
    comments = payload.get("comments", "")
    narrative = payload.get("narrative", "")

    try:
        if decision == "ESCALATED":
            success = await notify_escalation(
                report_id, drug_name, risk_score, narrative, reviewed_by
            )
        elif decision == "APPROVED":
            success = await notify_approval(
                report_id, drug_name, reviewed_by, comments
            )
        elif decision == "REJECTED":
            success = await notify_rejection(
                report_id, drug_name, reviewed_by, comments
            )
        else:
            raise HTTPException(status_code=400, detail=f"Unknown decision: {decision}")

        return {
            "status": "sent" if success else "failed",
            "decision": decision,
            "report_id": report_id,
            "notified": "qppv@company.com" if decision == "ESCALATED" else "safety@company.com"
        }

    except Exception as e:
        logger.error(f"Notification error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
