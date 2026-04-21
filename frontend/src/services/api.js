import axios from "axios";

const BASE = process.env.REACT_APP_API_URL || "http://localhost:8000";

export async function setupInterview(jdText, interviewType, sessionId) {
  const { data } = await axios.post(`${BASE}/setup`, {
    jd_text: jdText,
    interview_type: interviewType,
    session_id: sessionId,
  });
  return data;
}

export async function evaluateAnswer(sessionId, questionIndex, answer) {
  const { data } = await axios.post(`${BASE}/evaluate`, {
    session_id: sessionId,
    question_index: questionIndex,
    answer,
  });
  return data;
}

export async function generateReport(sessionId) {
  const { data } = await axios.post(`${BASE}/report`, {
    session_id: sessionId,
  });
  return data;
}

