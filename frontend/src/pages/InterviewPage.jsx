import AnswerTerminal from "../components/AnswerTerminal";
import HoloAvatar from "../components/HoloAvatar";
import ScoreRings from "../components/ScoreRings";
import { motion } from "framer-motion";
import { useEffect, useState } from "react";

export default function InterviewPage({ jdAnalysis, questions, currentIndex, evaluations, loading, onSubmit, error, onTranscript }) {
  const currentQuestion = questions[currentIndex];
  const last = evaluations[evaluations.length - 1];
  const [micEnabled, setMicEnabled] = useState(false);
  const [speakerEnabled, setSpeakerEnabled] = useState(false);

  useEffect(() => {
    if (!speakerEnabled || !currentQuestion) return;
    window.speechSynthesis.cancel();
    const u = new SpeechSynthesisUtterance(currentQuestion);
    u.rate = 1;
    u.pitch = 1;
    window.speechSynthesis.speak(u);
  }, [currentQuestion, speakerEnabled]);

  const highlights = [
    ["AI Powered", "Get intelligent, real-time interview evaluation."],
    ["Real-time Feedback", "Improve as you go with instant insights."],
    ["Secure & Private", "Your data is encrypted and never shared."],
    ["Track Progress", "Monitor your performance and grow continuously."],
  ];

  return (
    <div className="container" style={{ minHeight: "100vh", paddingTop: 14, paddingBottom: 20 }}>
      <div className="top-nav glass-heavy" style={{ marginBottom: 14 }}>
        <div className="brand-mark">
          <span className="mock-icon">◈</span>
          <div>
            <div style={{ fontWeight: 700 }}>QUANTIS</div>
            <small style={{ letterSpacing: 2, opacity: 0.8 }}>INTERVIEW GRID</small>
          </div>
        </div>
        <div style={{ display: "flex", gap: 10 }}>
          <button type="button" className="pill" onClick={() => setMicEnabled((v) => !v)}>
            {micEnabled ? "Mic ON" : "Mic OFF"}
          </button>
          <button type="button" className="pill" onClick={() => setSpeakerEnabled((v) => !v)}>
            {speakerEnabled ? "Speaker ON" : "Speaker OFF"}
          </button>
        </div>
      </div>
      <div style={{ display: "grid", gridTemplateColumns: "1fr 220px", gap: "1rem", alignContent: "center" }}>
      <div>
        <div className="card glass-heavy" style={{ marginBottom: 12, display: "flex", alignItems: "center", gap: 12 }}>
          <HoloAvatar speaking={loading} size={70} />
          <div>
            <div>{jdAnalysis?.role_title}</div>
            <small>{currentIndex + 1}/{questions.length}</small>
          </div>
          <div style={{ marginLeft: "auto", display: "flex", gap: 8 }}>
            <button type="button" onClick={() => setMicEnabled((v) => !v)}>{micEnabled ? "Mic On" : "Mic Off"}</button>
            <button type="button" onClick={() => setSpeakerEnabled((v) => !v)}>{speakerEnabled ? "Speaker On" : "Speaker Off"}</button>
          </div>
        </div>
        <motion.div
          className="card glass-heavy"
          style={{ marginBottom: 12 }}
          initial={{ opacity: 0, y: 12, scale: 0.98 }}
          animate={{ opacity: 1, y: 0, scale: 1 }}
          transition={{ duration: 0.55, ease: [0.22, 1, 0.36, 1] }}
        >
          <h3 className="cinzel" style={{ marginTop: 2, marginBottom: 0, fontSize: "1.85rem", lineHeight: 1.3 }}>{currentQuestion}</h3>
        </motion.div>
        <AnswerTerminal
          onSubmit={(answer, transcriptChunk) => {
            onTranscript?.(transcriptChunk || []);
            onSubmit(answer);
          }}
          loading={loading}
          disabled={currentIndex >= questions.length}
          micEnabled={micEnabled}
        />
        {error && <p style={{ color: "var(--red)" }}>{error}</p>}
      </div>
      <div>
        <div className="card glass-heavy" style={{ display: "grid", placeItems: "center" }}>
          <div style={{ opacity: 0.8, marginBottom: 8 }}>YOUR SCORE</div>
          <ScoreRings scores={last?.scores} overall={last?.overall || 0} />
          {!last?.scores && <small>Scoring is generated after all questions are answered.</small>}
        </div>
        {last && (
          <div className="card glass-heavy" style={{ marginTop: 12 }}>
            <p>{last.message || last.feedback}</p>
            <ul>
              {(last.strengths || []).map((s, i) => <li key={`s-${i}`}>{s}</li>)}
              {(last.improvements || []).map((s, i) => <li key={`i-${i}`}>{s}</li>)}
            </ul>
          </div>
        )}
      </div>
      </div>
      <div style={{ display: "grid", gridTemplateColumns: "repeat(4, minmax(0, 1fr))", gap: 10, marginTop: 14 }}>
        {highlights.map(([title, sub]) => (
          <div key={title} className="card glass-heavy">
            <strong style={{ fontSize: 15 }}>{title}</strong>
            <div style={{ opacity: 0.75, marginTop: 4 }}>{sub}</div>
          </div>
        ))}
      </div>
      <div style={{ display: "grid", placeItems: "center", marginTop: 14 }}>
        <button type="button" className="pill">End Simulation</button>
      </div>
    </div>
  );
}

