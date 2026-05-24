import React, { useEffect, useState } from 'react';
import { api } from '../api';

interface Case {
  id: number;
  report_id: string;
  drug_name: string;
  reactions: string[];
  triage_severity: string;
  risk_score: number;
  routing_decision: string;
  status: string;
  created_at: string;
}

interface Props {
  onSelectCase: (reportId: string) => void;
  activeTab: 'pending' | 'all';
  setActiveTab: (tab: 'pending' | 'all') => void;
}

const CaseQueue: React.FC<Props> = ({ onSelectCase, activeTab, setActiveTab }) => {
  const [cases, setCases] = useState<Case[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadCases();
  }, [activeTab]);

  const loadCases = async () => {
    setLoading(true);
    try {
      const status = activeTab === 'pending' ? 'PENDING' : undefined;
      const data = await api.getCases(status);
      setCases(data.cases);
    } catch (error) {
      console.error('Error loading cases:', error);
    }
    setLoading(false);
  };

  const getRoutingColor = (routing: string) => {
    if (routing === 'ESCALATE') return '#dc2626';
    if (routing === 'FLAG') return '#d97706';
    return '#16a34a';
  };

  const getSeverityColor = (severity: string) => {
    return severity === 'SERIOUS' ? '#dc2626' : '#16a34a';
  };

  return (
    <div className="case-queue">
      <div className="queue-header">
        <h2>Signal Review Queue</h2>
        <div className="tabs">
          <button
            className={activeTab === 'pending' ? 'tab active' : 'tab'}
            onClick={() => setActiveTab('pending')}
          >
            Pending Review
          </button>
          <button
            className={activeTab === 'all' ? 'tab active' : 'tab'}
            onClick={() => setActiveTab('all')}
          >
            All Cases
          </button>
        </div>
        <button className="refresh-btn" onClick={loadCases}>Refresh</button>
      </div>

      {loading ? (
        <div className="loading">Loading cases...</div>
      ) : cases.length === 0 ? (
        <div className="empty">No cases found. Run the agent workflow to generate cases.</div>
      ) : (
        <table className="case-table">
          <thead>
            <tr>
              <th>Report ID</th>
              <th>Drug</th>
              <th>Reactions</th>
              <th>Severity</th>
              <th>Risk Score</th>
              <th>Routing</th>
              <th>Status</th>
              <th>Action</th>
            </tr>
          </thead>
          <tbody>
            {cases.map((c) => (
              <tr key={c.report_id}>
                <td><code>{c.report_id}</code></td>
                <td>{c.drug_name}</td>
                <td>{c.reactions?.join(', ')}</td>
                <td>
                  <span style={{ color: getSeverityColor(c.triage_severity), fontWeight: 'bold' }}>
                    {c.triage_severity}
                  </span>
                </td>
                <td>
                  <div className="risk-score">
                    <div
                      className="risk-bar"
                      style={{
                        width: `${c.risk_score}%`,
                        backgroundColor: getRoutingColor(c.routing_decision)
                      }}
                    />
                    <span>{c.risk_score}/100</span>
                  </div>
                </td>
                <td>
                  <span
                    className="routing-badge"
                    style={{ backgroundColor: getRoutingColor(c.routing_decision) }}
                  >
                    {c.routing_decision}
                  </span>
                </td>
                <td>{c.status}</td>
                <td>
                  <button
                    className="review-btn"
                    onClick={() => onSelectCase(c.report_id)}
                  >
                    Review
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
};

export default CaseQueue;
