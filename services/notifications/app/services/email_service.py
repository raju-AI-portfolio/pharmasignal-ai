import os
import logging
import aiosmtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)

SMTP_HOST = os.getenv("SMTP_HOST", "localhost")
SMTP_PORT = int(os.getenv("SMTP_PORT", "1025"))
SMTP_FROM = os.getenv("SMTP_FROM", "pharmasignal@company.com")
QPPV_EMAIL = os.getenv("QPPV_EMAIL", "qppv@company.com")
SAFETY_TEAM_EMAIL = os.getenv("SAFETY_TEAM_EMAIL", "safety@company.com")

async def send_email(to: str, subject: str, body: str):
    """
    Sends an email via SMTP.
    In local dev this goes to MailHog at localhost:1025.
    In production this would go to real SMTP server.
    """
    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = SMTP_FROM
    msg["To"] = to
    msg.attach(MIMEText(body, "html"))

    try:
        await aiosmtplib.send(
            msg,
            hostname=SMTP_HOST,
            port=SMTP_PORT,
            use_tls=False
        )
        logger.info(f"Email sent to {to} — {subject}")
        return True
    except Exception as e:
        logger.error(f"Email failed: {e}")
        return False

async def notify_escalation(report_id: str, drug_name: str, risk_score: int, narrative: str, reviewed_by: str):
    """
    Sends urgent escalation notification to QPPV.
    Triggered when a case is escalated from human review.
    """
    subject = f"URGENT — Case Escalated to QPPV: {report_id} — {drug_name}"
    body = f"""
    <html>
    <body style="font-family: Arial, sans-serif; max-width: 600px;">
        <div style="background: #dc2626; color: white; padding: 16px; border-radius: 8px 8px 0 0;">
            <h2>⚠️ URGENT — QPPV Escalation Required</h2>
        </div>
        <div style="background: #f8fafc; padding: 20px; border: 1px solid #e2e8f0;">
            <p><strong>Report ID:</strong> {report_id}</p>
            <p><strong>Drug:</strong> {drug_name}</p>
            <p><strong>Risk Score:</strong> {risk_score}/100</p>
            <p><strong>Escalated by:</strong> {reviewed_by}</p>
            <p><strong>Action Required:</strong> Please review within 24 hours</p>
            <hr/>
            <h3>Safety Narrative Summary:</h3>
            <p style="background: white; padding: 12px; border-radius: 4px;">{narrative[:500]}...</p>
            <hr/>
            <p style="color: #64748b; font-size: 12px;">
                This is an automated notification from PharmaSignal AI.<br/>
                Please log into the review dashboard to take action.
            </p>
        </div>
    </body>
    </html>
    """
    return await send_email(QPPV_EMAIL, subject, body)

async def notify_approval(report_id: str, drug_name: str, reviewed_by: str, comments: str):
    """
    Sends confirmation notification when a case is approved.
    """
    subject = f"Case Approved — {report_id} — {drug_name}"
    body = f"""
    <html>
    <body style="font-family: Arial, sans-serif; max-width: 600px;">
        <div style="background: #16a34a; color: white; padding: 16px; border-radius: 8px 8px 0 0;">
            <h2>✓ Case Approved for Submission</h2>
        </div>
        <div style="background: #f8fafc; padding: 20px; border: 1px solid #e2e8f0;">
            <p><strong>Report ID:</strong> {report_id}</p>
            <p><strong>Drug:</strong> {drug_name}</p>
            <p><strong>Approved by:</strong> {reviewed_by}</p>
            <p><strong>Comments:</strong> {comments}</p>
            <p><strong>Next step:</strong> Submit to FDA within 15 days per ICH E2B guidelines</p>
        </div>
    </body>
    </html>
    """
    return await send_email(SAFETY_TEAM_EMAIL, subject, body)

async def notify_rejection(report_id: str, drug_name: str, reviewed_by: str, comments: str):
    """
    Sends notification when a case is rejected — requesting more information.
    """
    subject = f"Case Rejected — Additional Information Required: {report_id}"
    body = f"""
    <html>
    <body style="font-family: Arial, sans-serif; max-width: 600px;">
        <div style="background: #d97706; color: white; padding: 16px; border-radius: 8px 8px 0 0;">
            <h2>↩ Case Rejected — More Information Needed</h2>
        </div>
        <div style="background: #f8fafc; padding: 20px; border: 1px solid #e2e8f0;">
            <p><strong>Report ID:</strong> {report_id}</p>
            <p><strong>Drug:</strong> {drug_name}</p>
            <p><strong>Rejected by:</strong> {reviewed_by}</p>
            <p><strong>Reason:</strong> {comments}</p>
            <p><strong>Action required:</strong> Please provide additional information within 30 days.</p>
        </div>
    </body>
    </html>
    """
    return await send_email(SAFETY_TEAM_EMAIL, subject, body)
