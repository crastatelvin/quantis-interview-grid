import AnswerTerminal from "../components/AnswerTerminal";
import HoloAvatar from "../components/HoloAvatar";
import ScoreRings from "../components/ScoreRings";
import { motion } from "framer-motion";
import { useEffect, useState } from "react";

export default function InterviewPage({ jdAnalysis, questions, currentIndex, evaluations, loading, onSubmit, error }) {
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

  return (
    <div style={{ maxWidth: 1200, minHeight: "100vh", margin: "0 auto", padding: "1rem", display: "grid", gridTemplateColumns: "1fr 340px", gap: "1rem", alignContent: "center" }}>
      <div>
        <div className="card" style={{ marginBottom: 12, display: "flex", alignItems: "center", gap: 12 }}>
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
          className="card glass-panel"
          style={{ marginBottom: 12 }}
          initial={{ opacity: 0, y: 12, scale: 0.98 }}
          animate={{ opacity: 1, y: 0, scale: 1 }}
          transition={{ duration: 0.55, ease: [0.22, 1, 0.36, 1] }}
        >
          <h3 className="cinzel">{currentQuestion}</h3>
        </motion.div>
        <AnswerTerminal onSubmit={onSubmit} loading={loading} disabled={currentIndex >= questions.length} micEnabled={micEnabled} />
        {error && <p style={{ color: "var(--red)" }}>{error}</p>}
      </div>
      <div>
        <div className="card" style={{ display: "grid", placeItems: "center" }}>
          <ScoreRings scores={last?.scores} overall={last?.overall || 0} />
          {!last?.scores && <small>Scoring is generated after all questions are answered.</small>}
        </div>
        {last && (
          <div className="card" style={{ marginTop: 12 }}>
            <p>{last.message || last.feedback}</p>
            <ul>
              {(last.strengths || []).map((s, i) => <li key={`s-${i}`}>{s}</li>)}
              {(last.improvements || []).map((s, i) => <li key={`i-${i}`}>{s}</li>)}
            </ul>
          </div>
        )}
      </div>
    </div>
  );
}

