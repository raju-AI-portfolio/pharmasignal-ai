from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.models.database import get_db
from app.models.review import ReviewCase, AuditLog, Base
from app.models.database import engine
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

Base.metadata.create_all(bind=engine)

router = APIRouter()


@router.get("/health")
def health_check():
    return {"status": "ok", "service": "review-api"}


@router.post("/cases")
def create_case(case: dict, db: Session = Depends(get_db)):
    """
    Creates a new review case from agent workflow output.
    Called by the orchestrator after processing a report.
    """
    try:
        existing = db.query(ReviewCase).filter(
            ReviewCase.report_id == case.get("report_id")
        ).first()

        if existing:
            return {"status": "skipped", "reason": "duplicate"}

        db_case = ReviewCase(
            report_id=case.get("report_id"),
            drug_name=case.get("drug_name"),
            reactions=case.get("reactions"),
            triage_severity=case.get("triage", {}).get("severity"),
            triage_reasoning=case.get("triage", {}).get("reasoning"),
            risk_score=case.get("escalation", {}).get("risk_score"),
            routing_decision=case.get("escalation", {}).get("routing_decision"),
            safety_narrative=case.get("narrative"),
            signal_detected=str(case.get("signal", {}).get("signal_detected")),
            prr_score=str(case.get("signal", {}).get("prr_score")),
            full_analysis=case,
            status="PENDING"
        )

        db.add(db_case)

        # Log the creation in audit trail
        audit = AuditLog(
            report_id=case.get("report_id"),
            action="CASE_CREATED",
            performed_by="agent_orchestrator",
            details={
                "risk_score": case.get("escalation", {}).get("risk_score"),
                "routing": case.get("escalation", {}).get("routing_decision")
            }
        )
        db.add(audit)
        db.commit()

        logger.info(f"Review case created: {case.get('report_id')}")
        return {"status": "success", "report_id": case.get("report_id")}

    except Exception as e:
        db.rollback()
        logger.error(f"Error creating case: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/cases")
def get_cases(status: str = None, db: Session = Depends(get_db)):
    """
    Returns review cases — optionally filtered by status.
    This is what populates the human reviewer dashboard.
    """
    query = db.query(ReviewCase)

    if status:
        query = query.filter(ReviewCase.status == status.upper())

    cases = query.order_by(ReviewCase.risk_score.desc()).all()

    return {
        "total": len(cases),
        "cases": [
            {
                "id": c.id,
                "report_id": c.report_id,
                "drug_name": c.drug_name,
                "reactions": c.reactions,
                "triage_severity": c.triage_severity,
                "risk_score": c.risk_score,
                "routing_decision": c.routing_decision,
                "status": c.status,
                "created_at": str(c.created_at)
            }
            for c in cases
        ]
    }


@router.get("/cases/{report_id}")
def get_case_detail(report_id: str, db: Session = Depends(get_db)):
    """
    Returns full detail of a single case including safety narrative.
    """
    case = db.query(ReviewCase).filter(
        ReviewCase.report_id == report_id
    ).first()

    if not case:
        raise HTTPException(status_code=404, detail="Case not found")

    return {
        "id": case.id,
        "report_id": case.report_id,
        "drug_name": case.drug_name,
        "reactions": case.reactions,
        "triage_severity": case.triage_severity,
        "triage_reasoning": case.triage_reasoning,
        "risk_score": case.risk_score,
        "routing_decision": case.routing_decision,
        "safety_narrative": case.safety_narrative,
        "signal_detected": case.signal_detected,
        "prr_score": case.prr_score,
        "status": case.status,
        "reviewed_by": case.reviewed_by,
        "review_decision": case.review_decision,
        "review_comments": case.review_comments,
        "reviewed_at": str(case.reviewed_at) if case.reviewed_at else None,
        "created_at": str(case.created_at)
    }


@router.post("/cases/{report_id}/review")
def submit_review(report_id: str, review: dict, db: Session = Depends(get_db)):
    """
    Submits a human review decision for a case.
    This is the HITL — Human In The Loop action.

    Expected format:
    {
        "decision": "APPROVED",
        "reviewed_by": "dr.smith@pharma.com",
        "comments": "Narrative is accurate. Submitting to FDA."
    }
    """
    case = db.query(ReviewCase).filter(
        ReviewCase.report_id == report_id
    ).first()

    if not case:
        raise HTTPException(status_code=404, detail="Case not found")

    if case.status != "PENDING":
        raise HTTPException(
            status_code=400,
            detail=f"Case already reviewed — status: {case.status}"
        )

    decision = review.get("decision", "").upper()
    if decision not in ["APPROVED", "REJECTED", "ESCALATED"]:
        raise HTTPException(
            status_code=400,
            detail="Decision must be APPROVED, REJECTED or ESCALATED"
        )

    # Update case
    case.status = decision
    case.reviewed_by = review.get("reviewed_by", "unknown")
    case.review_decision = decision
    case.review_comments = review.get("comments", "")
    case.reviewed_at = datetime.utcnow()

    # Write audit log — this is critical for regulatory compliance
    audit = AuditLog(
        report_id=report_id,
        action=f"CASE_{decision}",
        performed_by=review.get("reviewed_by", "unknown"),
        details={
            "decision": decision,
            "comments": review.get("comments", ""),
            "previous_status": "PENDING",
            "risk_score": case.risk_score
        }
    )
    db.add(audit)
    db.commit()

    logger.info(f"Case {report_id} reviewed — {decision} by {review.get('reviewed_by')}")
    return {
        "status": "success",
        "report_id": report_id,
        "decision": decision,
        "reviewed_by": review.get("reviewed_by"),
        "timestamp": str(datetime.utcnow())
    }


@router.get("/audit/{report_id}")
def get_audit_trail(report_id: str, db: Session = Depends(get_db)):
    """
    Returns the full audit trail for a case.
    Every action ever taken on this case is logged here.
    """
    logs = db.query(AuditLog).filter(
        AuditLog.report_id == report_id
    ).order_by(AuditLog.timestamp.asc()).all()

    return {
        "report_id": report_id,
        "total_actions": len(logs),
        "audit_trail": [
            {
                "action": log.action,
                "performed_by": log.performed_by,
                "details": log.details,
                "timestamp": str(log.timestamp)
            }
            for log in logs
        ]
    }
