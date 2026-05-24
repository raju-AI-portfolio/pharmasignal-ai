import React, { useEffect, useState } from 'react';
import { api } from '../api';

interface Props {
  reportId: string;
  onBack: () => void;
}

const CaseDetail: React.FC<Props> = ({ reportId, onBack }) => {
  const [caseData, setCaseData] = useState<any>(null);
  const [auditTrail, setAuditTrail] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [comments, setComments] = useState('');
  const [reviewerName, setReviewerName] = useState('dr.smith@pharmasignal.com');
  const [message, setMessage] = useState('');

  useEffect(() => {
    loadCase();
  }, [reportId]);

  const loadCase = async () => {
    setLoading(true);
    try {
      const data = await api.getCaseDetail(reportId);
      setCaseData(data);
      const audit = await api.getAuditTrail(reportId);
      setAuditTrail(audit.audit_trail);
    } catch (error) {
      console.error('Error loading case:', error);
    }
    setLoading(false);
  };

  const submitDecision = async (decision: string) => {
    setSubmitting(true);
    try {
      await api.submitReview(reportId, decision, reviewerName, comments);
      setMessage(`Case ${decision} successfully`);
      await loadCase();
    } catch (error: any) {
      setMessage(`Error: ${error.response?.data?.detail || 'Unknown error'}`);
    }
    setSubmitting(false);
  };

  if (loading) return <div className="loading">Loading case details...</div>;
  if (!caseData) return <div className="error">Case not found</div>;

  return (
    <div className="case-detail">
      <button className="back-btn" onClick={onBack}>← Back to Queue</button>

      <div className="case-header">
        <h2>Case Review — {reportId}</h2>
        <span className={`status-badge ${caseData.status.toLowerCase()}`}>
          {caseData.status}
        </span>
      </div>

      <div className="detail-grid">

        {/* Report Summary */}
        <div className="detail-card">
          <h3>Report Summary</h3>
          <div className="detail-row">
            <span className="label">Drug:</span>
            <span>{caseData.drug_name}</span>
          </div>
          <div className="detail-row">
            <span className="label">Reactions:</span>
            <span>{caseData.reactions?.join(', ')}</span>
          </div>
          <div className="detail-row">
            <span className="label">Severity:</span>
            <span className={caseData.triage_severity === 'SERIOUS' ? 'serious' : 'non-serious'}>
              {caseData.triage_severity}
            </span>
          </div>
          <div className="detail-row">
            <span className="label">Triage Reasoning:</span>
            <span>{caseData.triage_reasoning}</span>
          </div>
        </div>

        {/* Signal Analysis */}
        <div className="detail-card">
          <h3>Signal Analysis</h3>
          <div className="detail-row">
            <span className="label">PRR Score:</span>
            <span>{caseData.prr_score}</span>
          </div>
          <div className="detail-row">
            <span className="label">Signal Detected:</span>
            <span>{caseData.signal_detected}</span>
          </div>
          <div className="detail-row">
            <span className="label">Risk Score:</span>
            <span className="risk-number">{caseData.risk_score}/100</span>
          </div>
          <div className="detail-row">
            <span className="label">Routing:</span>
            <span className={`routing ${caseData.routing_decision?.toLowerCase()}`}>
              {caseData.routing_decision}
            </span>
          </div>
        </div>

        {/* Safety Narrative */}
        <div className="detail-card full-width">
          <h3>AI-Generated Safety Narrative</h3>
          <div className="narrative">
            {caseData.safety_narrative}
          </div>
        </div>

        {/* Human Review */}
        {caseData.status === 'PENDING' && (
          <div className="detail-card full-width">
            <h3>Human Review Decision</h3>
            <div className="review-form">
              <div className="form-row">
                <label>Reviewer:</label>
                <input
                  type="text"
                  value={reviewerName}
                  onChange={(e) => setReviewerName(e.target.value)}
                  className="input"
                />
              </div>
              <div className="form-row">
                <label>Comments:</label>
                <textarea
                  value={comments}
                  onChange={(e) => setComments(e.target.value)}
                  className="textarea"
                  placeholder="Add your review comments here..."
                  rows={3}
                />
              </div>
              {message && <div className="message">{message}</div>}
              <div className="decision-buttons">
                <button
                  className="btn approve"
                  onClick={() => submitDecision('APPROVED')}
                  disabled={submitting}
                >
                  ✓ Approve
                </button>
                <button
                  className="btn reject"
                  onClick={() => submitDecision('REJECTED')}
                  disabled={submitting}
                >
                  ✗ Reject
                </button>
                <button
                  className="btn escalate"
                  onClick={() => submitDecision('ESCALATED')}
                  disabled={submitting}
                >
                  ↑ Escalate to QPPV
                </button>
              </div>
            </div>
          </div>
        )}

        {/* Audit Trail */}
        <div className="detail-card full-width">
          <h3>Audit Trail</h3>
          <div className="audit-trail">
            {auditTrail.map((log, index) => (
              <div key={index} className="audit-entry">
                <div className="audit-action">{log.action}</div>
                <div className="audit-by">by {log.performed_by}</div>
                <div className="audit-time">{new Date(log.timestamp).toLocaleString()}</div>
                {log.details?.comments && (
                  <div className="audit-comments">"{log.details.comments}"</div>
                )}
              </div>
            ))}
          </div>
        </div>

      </div>
    </div>
  );
};

export default CaseDetail;
