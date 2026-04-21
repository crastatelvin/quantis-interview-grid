import { useCallback, useState } from "react";
import { evaluateAnswer, generateReport, setupInterview } from "../services/api";

export default function useInterview() {
  const [phase, setPhase] = useState("setup");
  const [sessionId] = useState(() => `session_${Date.now()}`);
  const [jdAnalysis, setJdAnalysis] = useState(null);
  const [questions, setQuestions] = useState([]);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [evaluations, setEvaluations] = useState([]);
  const [report, setReport] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

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
        const rep = await generateReport(sessionId);
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
  }, [currentIndex, evaluations, questions.length, sessionId]);

  const reset = useCallback(() => {
    setPhase("setup");
    setJdAnalysis(null);
    setQuestions([]);
    setCurrentIndex(0);
    setEvaluations([]);
    setReport(null);
    setError("");
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
  };
}

