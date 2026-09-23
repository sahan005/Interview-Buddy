import type { ParsedDocument, SessionResponse, AnswerResponse, FinalReport } from '../types';

const API_BASE = 'http://localhost:8000';

export const apiClient = {
  async getDemoData(): Promise<{ sample_resume: string; sample_job_description: string; candidate_name: string; target_role: string }> {
    const res = await fetch(`${API_BASE}/api/demo-data`);
    if (!res.ok) throw new Error('Failed to fetch demo data');
    return res.json();
  },

  async uploadResume(file: File): Promise<ParsedDocument> {
    const formData = new FormData();
    formData.append('file', file);
    const res = await fetch(`${API_BASE}/api/upload-resume`, {
      method: 'POST',
      body: formData,
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: 'Failed to upload resume' }));
      throw new Error(err.detail || 'Upload failed');
    }
    return res.json();
  },

  async startInterview(params: {
    resume_text: string;
    job_description: string;
    interview_type: string;
    difficulty: string;
    num_questions: number;
  }): Promise<SessionResponse> {
    const res = await fetch(`${API_BASE}/api/interview/start`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(params),
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: 'Failed to start interview' }));
      throw new Error(err.detail || 'Failed to start interview');
    }
    return res.json();
  },

  async submitAnswer(params: {
    session_id: string;
    question_index: number;
    answer: string;
  }): Promise<AnswerResponse> {
    const res = await fetch(`${API_BASE}/api/interview/answer`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(params),
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: 'Failed to submit answer' }));
      throw new Error(err.detail || 'Submission failed');
    }
    return res.json();
  },

  async endInterviewEarly(session_id: string): Promise<FinalReport> {
    const res = await fetch(`${API_BASE}/api/interview/${session_id}/end`, {
      method: 'POST',
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: 'Failed to complete interview' }));
      throw new Error(err.detail || 'Failed to end interview');
    }
    return res.json();
  }
};
