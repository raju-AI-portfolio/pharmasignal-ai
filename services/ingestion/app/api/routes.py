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
    Channel 1 — FDA FAERS intake.
    Fetches adverse event reports from FDA public API and saves to database.
    Simulates: scheduled regulatory data pull.
    """
    if limit > 100:
        raise HTTPException(
            status_code=400,
            detail="limit cannot exceed 100"
        )

    try:
        logger.info(f"Starting FDA ingestion of {limit} reports")
        raw_data = await fetch_adverse_events(limit=limit)
        reports = raw_data.get("results", [])

        saved = 0
        skipped = 0

        for raw_report in reports:
            parsed = parse_report(raw_report)

            existing = db.query(AdverseEventReport).filter(
                AdverseEventReport.report_id == parsed["report_id"]
            ).first()

            if existing:
                skipped += 1
                continue

            db_report = AdverseEventReport(**parsed)
            db.add(db_report)
            saved += 1

        db.commit()

        logger.info(f"FDA ingestion complete - saved: {saved}, skipped: {skipped}")
        return {
            "status": "success",
            "source_channel": "fda_faers",
            "saved": saved,
            "skipped": skipped,
            "total_fetched": len(reports)
        }

    except Exception as e:
        db.rollback()
        logger.error(f"Ingestion failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/intake")
async def intake_report(report: dict, db: Session = Depends(get_db)):
    """
    Channel 2 — Generic REST API intake.
    Accepts reports from any channel — call center, CRM, mobile app, chatbot.
    Simulates: Veeva Vault webhook, Salesforce connector, call center submission.

    Expected format:
    {
        "report_id": "CC-001",
        "drug_name": "ASPIRIN",
        "reactions": ["Nausea", "Vomiting"],
        "serious": "Yes",
        "patient_age": "45",
        "patient_sex": "Female",
        "source_channel": "call_center"
    }
    """
    try:
        # Check for duplicate
        existing = db.query(AdverseEventReport).filter(
            AdverseEventReport.report_id == report.get("report_id")
        ).first()

        if existing:
            return {
                "status": "skipped",
                "reason": "duplicate",
                "report_id": report.get("report_id")
            }

        source_channel = report.get("source_channel", "api")

        db_report = AdverseEventReport(
            report_id=report.get("report_id"),
            drug_name=report.get("drug_name"),
            patient_age=str(report.get("patient_age")) if report.get("patient_age") else None,
            patient_sex=report.get("patient_sex"),
            reactions=report.get("reactions", []),
            serious=report.get("serious", "No"),
            outcome=report.get("outcome", "Unknown"),
            raw_data=report.copy()
        )

        db.add(db_report)
        db.commit()

        logger.info(f"Intake saved — ID: {report.get('report_id')} — Channel: {source_channel}")
        return {
            "status": "success",
            "report_id": report.get("report_id"),
            "source_channel": source_channel
        }

    except Exception as e:
        db.rollback()
        logger.error(f"Intake error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/intake/file")
async def intake_from_file(db: Session = Depends(get_db)):
    """
    Channel 3 — File drop intake.
    Reads CSV files from data/incoming/ folder and ingests all rows.
    Simulates: CRM batch export, Veeva overnight file drop, email attachment processing.

    CSV format: report_id, drug_name, reactions, serious, patient_age, patient_sex
    """
    import os
    import csv
    from pathlib import Path

    incoming_dir = Path("./data/incoming")
    incoming_dir.mkdir(parents=True, exist_ok=True)

    csv_files = list(incoming_dir.glob("*.csv"))

    if not csv_files:
        return {
            "status": "no_files",
            "message": "No CSV files found in data/incoming/ folder"
        }

    total_saved = 0
    total_skipped = 0
    processed_files = []

    for csv_file in csv_files:
        try:
            with open(csv_file, "r") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    existing = db.query(AdverseEventReport).filter(
                        AdverseEventReport.report_id == row.get("report_id")
                    ).first()

                    if existing:
                        total_skipped += 1
                        continue

                    reactions = row.get("reactions", "").split("|")

                    db_report = AdverseEventReport(
                        report_id=row.get("report_id"),
                        drug_name=row.get("drug_name"),
                        patient_age=row.get("patient_age"),
                        patient_sex=row.get("patient_sex"),
                        reactions=reactions,
                        serious=row.get("serious", "No"),
                        outcome=row.get("outcome", "Unknown"),
                        raw_data=dict(row)
                    )
                    db.add(db_report)
                    total_saved += 1

            db.commit()
            processed_files.append(csv_file.name)
            logger.info(f"File intake complete: {csv_file.name}")

        except Exception as e:
            logger.error(f"Error processing file {csv_file.name}: {e}")
            db.rollback()

    return {
        "status": "success",
        "source_channel": "file_drop",
        "files_processed": processed_files,
        "saved": total_saved,
        "skipped": total_skipped
    }


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