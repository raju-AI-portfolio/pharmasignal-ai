from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.models.database import get_db
from app.models.report import AdverseEventReport, Base
from app.models.database import engine
from app.services.fda_client import fetch_adverse_events, parse_report
import logging

logger = logging.getLogger(__name__)

# Create all database tables if they don't exist
Base.metadata.create_all(bind=engine)

router = APIRouter()

@router.get("/health")
def health_check():
    """
    Simple health check endpoint.
    Returns ok if the service is running.
    """
    return {"status": "ok", "service": "ingestion"}


@router.post("/ingest")
async def ingest_reports(limit: int = 10, db: Session = Depends(get_db)):
    """
    Fetches adverse event reports from FDA and saves to database.
    
    limit = how many reports to fetch (default 10, max 100)
    """
    if limit > 100:
        raise HTTPException(
            status_code=400,
            detail="limit cannot exceed 100"
        )

    try:
        # Step 1 - fetch from FDA
        logger.info(f"Starting ingestion of {limit} reports")
        raw_data = await fetch_adverse_events(limit=limit)
        reports = raw_data.get("results", [])

        # Step 2 - parse and save each report
        saved = 0
        skipped = 0

        for raw_report in reports:
            parsed = parse_report(raw_report)

            # Check if report already exists in DB
            existing = db.query(AdverseEventReport).filter(
                AdverseEventReport.report_id == parsed["report_id"]
            ).first()

            if existing:
                skipped += 1
                continue

            # Save new report to database
            db_report = AdverseEventReport(**parsed)
            db.add(db_report)
            saved += 1

        db.commit()

        logger.info(f"Ingestion complete - saved: {saved}, skipped: {skipped}")
        return {
            "status": "success",
            "saved": saved,
            "skipped": skipped,
            "total_fetched": len(reports)
        }

    except Exception as e:
        db.rollback()
        logger.error(f"Ingestion failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/reports")
def get_reports(limit: int = 10, db: Session = Depends(get_db)):
    """
    Returns reports stored in the database.
    """
    reports = db.query(AdverseEventReport).limit(limit).all()
    return {
        "total": len(reports),
        "reports": [
            {
                "report_id": r.report_id,
                "drug_name": r.drug_name,
                "reactions": r.reactions,
                "serious": r.serious,
                "patient_age": r.patient_age,
                "patient_sex": r.patient_sex,
                "ingested_at": str(r.ingested_at)
            }
            for r in reports
        ]
    }