import { useEffect, useRef, useState } from "react";

export default function AnswerTerminal({ onSubmit, loading, disabled, micEnabled }) {
  const [answer, setAnswer] = useState("");
  const [listening, setListening] = useState(false);
  const [voiceMode, setVoiceMode] = useState("push");
  const [liveTranscript, setLiveTranscript] = useState("");
  const [finalTranscript, setFinalTranscript] = useState([]);
  const recognitionRef = useRef(null);

  useEffect(() => {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SpeechRecognition || !micEnabled) {
      if (recognitionRef.current) {
        recognitionRef.current.stop();
      }
      setListening(false);
      return;
    }
    const rec = new SpeechRecognition();
    rec.continuous = true;
    rec.interimResults = true;
    rec.lang = "en-US";
    rec.onresult = (event) => {
      let interim = "";
      const finalized = [];
      for (let i = event.resultIndex; i < event.results.length; i += 1) {
        const text = event.results[i][0].transcript.trim();
        if (!text) continue;
        if (event.results[i].isFinal) {
          finalized.push(text);
        } else {
          interim += `${text} `;
        }
      }
      if (finalized.length) {
        setFinalTranscript((prev) => [...prev, ...finalized]);
        setAnswer((prev) => `${prev} ${finalized.join(" ")}`.trim());
      }
      setLiveTranscript(interim.trim());
    };
    rec.onend = () => {
      setListening(false);
      setLiveTranscript("");
    };
    recognitionRef.current = rec;
    return () => rec.stop();
  }, [micEnabled]);

  const startListening = () => {
    if (!recognitionRef.current || listening || !micEnabled) return;
    recognitionRef.current.start();
    setListening(true);
  };

  const stopListening = () => {
    if (!recognitionRef.current || !listening) return;
    recognitionRef.current.stop();
    setListening(false);
  };

  return (
    <div className="card">
      {micEnabled && (
        <div className="glass-panel" style={{ padding: 12, marginBottom: 12 }}>
          <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 8 }}>
            <strong>Voice Interview Mode</strong>
            <select value={voiceMode} onChange={(e) => setVoiceMode(e.target.value)}>
              <option value="push">Push to Talk</option>
              <option value="toggle">Toggle Listening</option>
            </select>
          </div>
          <div style={{ display: "flex", gap: 8, marginBottom: 8 }}>
            {voiceMode === "push" ? (
              <button
                type="button"
                onMouseDown={startListening}
                onMouseUp={stopListening}
                onMouseLeave={stopListening}
                onTouchStart={startListening}
                onTouchEnd={stopListening}
                disabled={loading || disabled}
              >
                Hold to Talk
              </button>
            ) : (
              <button type="button" onClick={() => (listening ? stopListening() : startListening())} disabled={loading || disabled}>
                {listening ? "Stop Listening" : "Start Listening"}
              </button>
            )}
            <span style={{ opacity: 0.8 }}>{listening ? "Listening..." : "Idle"}</span>
          </div>
          <div className="card" style={{ padding: 8, minHeight: 72 }}>
            <div style={{ fontSize: 12, opacity: 0.7, marginBottom: 4 }}>Live Transcript</div>
            <div style={{ fontSize: 13 }}>{liveTranscript || finalTranscript.slice(-3).join(" ") || "Speak to capture transcript..."}</div>
          </div>
        </div>
      )}
      <textarea
        rows={6}
        value={answer}
        onChange={(e) => setAnswer(e.target.value)}
        disabled={loading || disabled}
        placeholder="Type your answer..."
        style={{ width: "100%", background: "#0b0f14", color: "#e6edf3", border: "1px solid rgba(29,109,245,0.25)" }}
      />
      <button
        style={{ marginTop: 10 }}
        onClick={() => {
          if (!answer.trim()) return;
          onSubmit(answer.trim());
          setAnswer("");
          setLiveTranscript("");
          setFinalTranscript([]);
        }}
        disabled={loading || disabled || !answer.trim()}
      >
        {loading ? "EVALUATING..." : "SUBMIT ANSWER"}
      </button>
    </div>
  );
}

