from sqlalchemy import Column, String, DateTime, Text, JSON
from sqlalchemy.orm import declarative_base
from datetime import datetime

Base = declarative_base()

class AdverseEventReport(Base):
    __tablename__ = "adverse_event_reports"

    # Unique report ID from FDA
    report_id = Column(String, primary_key=True, index=True)

    # Drug information
    drug_name = Column(String, nullable=True)

    # Patient information
    patient_age = Column(String, nullable=True)
    patient_sex = Column(String, nullable=True)

    # Reaction information
    reactions = Column(JSON, nullable=True)

    # Outcome
    serious = Column(String, nullable=True)
    outcome = Column(String, nullable=True)

    # Raw report stored as JSON for reference
    raw_data = Column(JSON, nullable=True)

    # When we ingested this report
    ingested_at = Column(DateTime, default=datetime.utcnow)