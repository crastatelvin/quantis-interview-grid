import { useCallback, useState } from "react";
import {
  analyzeResumeGap,
  evaluateAnswer,
  generateReport,
  getHistory,
  getHistoryRun,
  getObservabilitySummary,
  getToken,
  loginUser,
  registerUser,
  setupInterview,
} from "../services/api";

export default function useInterview() {
  const [phase, setPhase] = useState("setup");
  const [sessionId, setSessionId] = useState(() => `session_${Date.now()}`);
  const [jdAnalysis, setJdAnalysis] = useState(null);
  const [questions, setQuestions] = useState([]);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [evaluations, setEvaluations] = useState([]);
  const [report, setReport] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [history, setHistory] = useState([]);
  const [authReady, setAuthReady] = useState(Boolean(getToken()));
  const [gapAnalysis, setGapAnalysis] = useState(null);
  const [transcript, setTranscript] = useState([]);
  const [historyDetail, setHistoryDetail] = useState(null);
  const [observability, setObservability] = useState(null);

  const startInterview = useCallback(async (jdText, interviewType) => {
    setLoading(true);
    setError("");
    try {
      const data = await setupInterview(jdText, interviewType, sessionId);
      if (!data?.questions?.length) {
        throw new Error("No questions generated");
      }
      setJdAnalysis(data.jd_analysis);
      setQuestions(data.questions || []);
      setCurrentIndex(0);
      setEvaluations([]);
      setReport(null);
      setPhase("interview");
    } catch (e) {
      const detail = e?.response?.data?.detail || e?.response?.data?.error;
      setError(`Setup failed. ${detail || "Check backend/API key and JD content."}`);
    } finally {
      setLoading(false);
    }
  }, [sessionId]);

  const submitAnswer = useCallback(async (answer) => {
    setLoading(true);
    setError("");
    try {
      const evaluation = await evaluateAnswer(sessionId, currentIndex, answer);
      const nextEvaluations = [...evaluations, evaluation];
      setEvaluations(nextEvaluations);
      if (currentIndex + 1 >= questions.length) {
        const rep = await generateReport(sessionId, transcript);
        setReport(rep);
        setPhase("report");
      } else {
        setCurrentIndex((v) => v + 1);
      }
    } catch (e) {
      const detail = e?.response?.data?.detail || e?.response?.data?.error;
      setError(`Evaluation failed. ${detail || "Please retry."}`);
    } finally {
      setLoading(false);
    }
  }, [currentIndex, evaluations, questions.length, sessionId, transcript]);

  const reset = useCallback(() => {
    setPhase("setup");
    setJdAnalysis(null);
    setQuestions([]);
    setCurrentIndex(0);
    setEvaluations([]);
    setReport(null);
    setError("");
    setGapAnalysis(null);
    setTranscript([]);
    setSessionId(`session_${Date.now()}`);
  }, []);

  const register = useCallback(async (email, password) => {
    try {
      await registerUser(email, password);
    } catch (e) {
      throw new Error(e?.response?.data?.detail || "Register failed");
    }
  }, []);

  const login = useCallback(async (email, password) => {
    try {
      await loginUser(email, password);
    } catch (e) {
      throw new Error(e?.response?.data?.detail || "Login failed");
    }
    setAuthReady(true);
    const data = await getHistory();
    setHistory(data.runs || []);
  }, []);

  const refreshHistory = useCallback(async () => {
    if (!getToken()) return;
    const data = await getHistory();
    setHistory(data.runs || []);
  }, []);

  const getRunDetail = useCallback(async (runId) => {
    const data = await getHistoryRun(runId);
    setHistoryDetail(data);
  }, []);

  const refreshObservability = useCallback(async () => {
    const data = await getObservabilitySummary();
    setObservability(data);
  }, []);

  const appendTranscript = useCallback((chunks) => {
    if (!chunks?.length) return;
    setTranscript((prev) => [...prev, ...chunks]);
  }, []);

  const runGapAnalysis = useCallback(async (jdText, file) => {
    const data = await analyzeResumeGap(jdText, file);
    setGapAnalysis(data);
  }, []);

  return {
    phase,
    sessionId,
    jdAnalysis,
    questions,
    currentIndex,
    evaluations,
    report,
    loading,
    error,
    startInterview,
    submitAnswer,
    reset,
    register,
    login,
    history,
    authReady,
    refreshHistory,
    runGapAnalysis,
    gapAnalysis,
    appendTranscript,
    historyDetail,
    getRunDetail,
    observability,
    refreshObservability,
  };
}

