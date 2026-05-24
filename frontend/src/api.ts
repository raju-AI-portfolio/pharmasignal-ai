import axios from 'axios';

const REVIEW_API = 'http://localhost:8004/api/v1';
const ORCHESTRATOR_API = 'http://localhost:8003/api/v1';
const INGESTION_API = 'http://localhost:8001/api/v1';

export const api = {
  // Get all cases
  getCases: async (status?: string) => {
    const url = status ? `${REVIEW_API}/cases?status=${status}` : `${REVIEW_API}/cases`;
    const response = await axios.get(url);
    return response.data;
  },

  // Get case detail
  getCaseDetail: async (reportId: string) => {
    const response = await axios.get(`${REVIEW_API}/cases/${reportId}`);
    return response.data;
  },

  // Submit review decision
  submitReview: async (reportId: string, decision: string, reviewedBy: string, comments: string) => {
    const response = await axios.post(`${REVIEW_API}/cases/${reportId}/review`, {
      decision,
      reviewed_by: reviewedBy,
      comments
    });
    return response.data;
  },

  // Get audit trail
  getAuditTrail: async (reportId: string) => {
    const response = await axios.get(`${REVIEW_API}/audit/${reportId}`);
    return response.data;
  },

  // Analyse a report
  analyseReport: async (reportId: string) => {
    const response = await axios.post(`${ORCHESTRATOR_API}/analyse/${reportId}`);
    return response.data;
  },

  // Get all reports
  getReports: async () => {
    const response = await axios.get(`${INGESTION_API}/reports?limit=20`);
    return response.data;
  }
};
