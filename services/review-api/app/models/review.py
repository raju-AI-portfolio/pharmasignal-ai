from sqlalchemy import Column, String, DateTime, Integer, JSON, Text
from sqlalchemy.orm import declarative_base
from datetime import datetime

Base = declarative_base()

class ReviewCase(Base):
    """
    Stores agent workflow results waiting for human review.
    Created when orchestrator finishes processing a report.
    """
    __tablename__ = "review_cases"

    id = Column(Integer, primary_key=True, autoincrement=True)
    report_id = Column(String, unique=True, index=True)
    drug_name = Column(String, nullable=True)
    reactions = Column(JSON, nullable=True)

    # Agent outputs
    triage_severity = Column(String, nullable=True)
    triage_reasoning = Column(Text, nullable=True)
    risk_score = Column(Integer, nullable=True)
    routing_decision = Column(String, nullable=True)
    safety_narrative = Column(Text, nullable=True)
    signal_detected = Column(String, nullable=True)
    prr_score = Column(String, nullable=True)
    full_analysis = Column(JSON, nullable=True)

    # Review status
    status = Column(String, default="PENDING")
    # PENDING → APPROVED / REJECTED / ESCALATED

    # Human review fields
    reviewed_by = Column(String, nullable=True)
    review_decision = Column(String, nullable=True)
    review_comments = Column(Text, nullable=True)
    reviewed_at = Column(DateTime, nullable=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class AuditLog(Base):
    """
    Every action taken on a case is logged here.
    This is what regulators inspect during audits.
    """
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    report_id = Column(String, index=True)
    action = Column(String)
    performed_by = Column(String)
    details = Column(JSON, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
