import axios from "axios";

const BASE = process.env.REACT_APP_API_URL || "http://localhost:8000";
let token = localStorage.getItem("auth_token") || "";

function authHeaders() {
  return token ? { Authorization: `Bearer ${token}` } : {};
}

export function setToken(next) {
  token = next || "";
  if (token) localStorage.setItem("auth_token", token);
  else localStorage.removeItem("auth_token");
}

export function getToken() {
  return token;
}

export async function registerUser(email, password) {
  const { data } = await axios.post(`${BASE}/auth/register`, { email, password });
  return data;
}

export async function loginUser(email, password) {
  const { data } = await axios.post(`${BASE}/auth/login`, { email, password });
  setToken(data.access_token);
  return data;
}

export async function getHistory() {
  const { data } = await axios.get(`${BASE}/history`, { headers: authHeaders() });
  return data;
}

export async function getHistoryRun(runId) {
  const { data } = await axios.get(`${BASE}/history/${runId}`, { headers: authHeaders() });
  return data;
}

export async function getObservabilitySummary() {
  const { data } = await axios.get(`${BASE}/observability/summary`, { headers: authHeaders() });
  return data;
}

export async function analyzeResumeGap(jdText, file) {
  const form = new FormData();
  form.append("jd_text", jdText);
  form.append("resume_file", file);
  const { data } = await axios.post(`${BASE}/resume-gap-analysis`, form, {
    headers: { ...authHeaders(), "Content-Type": "multipart/form-data" },
  });
  return data;
}

export async function setupInterview(jdText, interviewType, sessionId) {
  const { data } = await axios.post(`${BASE}/setup`, {
    jd_text: jdText,
    interview_type: interviewType,
    session_id: sessionId,
  }, { headers: authHeaders() });
  return data;
}

export async function evaluateAnswer(sessionId, questionIndex, answer) {
  const { data } = await axios.post(`${BASE}/evaluate`, {
    session_id: sessionId,
    question_index: questionIndex,
    answer,
  }, { headers: authHeaders() });
  return data;
}

export async function generateReport(sessionId, transcript = []) {
  const { data } = await axios.post(`${BASE}/report`, {
    session_id: sessionId,
    transcript,
  }, { headers: authHeaders() });
  return data;
}

