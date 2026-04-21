import { useMemo, useState } from "react";
import { motion } from "framer-motion";

const TYPES = ["technical", "behavioral", "product", "leadership", "hr"];

export default function SetupPage({
  onStart,
  loading,
  error,
  onRegister,
  onLogin,
  authReady,
  history = [],
  onRefreshHistory,
  onRunGapAnalysis,
  gapAnalysis,
  onGetRunDetail,
  historyDetail,
  onRefreshObservability,
  observability,
}) {
  const [jd, setJd] = useState("");
  const [type, setType] = useState("behavioral");
  const [dragActive, setDragActive] = useState(false);
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [resumeFile, setResumeFile] = useState(null);
  const [authMsg, setAuthMsg] = useState("");
  const [showAccountPanel, setShowAccountPanel] = useState(false);
  const jdChars = jd.length;

  const handleFile = async (file) => {
    if (!file) return;
    const text = await file.text();
    setJd(text);
  };

  const whyItems = useMemo(
    () => [
      ["AI-Powered Interviews", "Advanced AI tailors questions to your role and experience."],
      ["Realistic Simulation", "Experience pressure and flow similar to real interviews."],
      ["Instant Feedback", "Get actionable insights and structured guidance."],
      ["Track Progress", "Monitor performance across sessions."],
    ],
    []
  );

  return (
    <div className="container" style={{ paddingTop: 16, paddingBottom: 22 }}>
      <div className="top-nav glass-heavy">
        <div className="brand-mark">
          <span className="mock-icon">◈</span>
          <div>
            <div style={{ fontWeight: 700 }}>QUANTIS</div>
            <small style={{ letterSpacing: 2, opacity: 0.8 }}>INTERVIEW GRID</small>
          </div>
        </div>
        <div style={{ display: "flex", gap: 18, opacity: 0.85, fontSize: 13 }}>
          {["Home", "How it Works", "Pricing", "Contact"].map((item) => (
            <span key={item}>{item}</span>
          ))}
        </div>
        <button type="button" onClick={() => setShowAccountPanel((v) => !v)}>
          {showAccountPanel ? "Close" : "Sign In"}
        </button>
      </div>
      <div style={{ textAlign: "center", marginTop: 20, marginBottom: 12 }}>
        <h1 className="cinzel" style={{ letterSpacing: 4, marginBottom: 0, fontSize: "3rem" }}>QUANTIS</h1>
        <h2 className="cinzel" style={{ letterSpacing: 5, margin: 0, color: "#76a9ff", fontSize: "2rem" }}>INTERVIEW GRID</h2>
        <small style={{ letterSpacing: 7, opacity: 0.75 }}>ENTER THE SIMULATION</small>
      </div>

      <div className="landing-grid">
        <motion.form
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.65, ease: [0.22, 1, 0.36, 1] }}
          className="card glass-heavy"
          onSubmit={(e) => {
            e.preventDefault();
            onStart(jd, type);
          }}
        >
          <label style={{ opacity: 0.8, fontSize: 11, letterSpacing: 1.3 }}>1. SELECT INTERVIEW TYPE</label>
          <div style={{ marginTop: 6, marginBottom: 14 }}>
            <select value={type} onChange={(e) => setType(e.target.value)} style={{ width: "100%" }}>
              {TYPES.map((t) => <option key={t} value={t}>{`${t[0].toUpperCase()}${t.slice(1)} Interview`}</option>)}
            </select>
          </div>
          <label style={{ opacity: 0.8, fontSize: 11, letterSpacing: 1.3 }}>2. UPLOAD JOB DESCRIPTION</label>
          <div
            onDragOver={(e) => {
              e.preventDefault();
              setDragActive(true);
            }}
            onDragLeave={() => setDragActive(false)}
            onDrop={(e) => {
              e.preventDefault();
              setDragActive(false);
              handleFile(e.dataTransfer.files?.[0]);
            }}
            style={{
              marginTop: 6,
              border: `1px dashed ${dragActive ? "#5da6ff" : "rgba(93,166,255,0.35)"}`,
              borderRadius: 10,
              padding: 22,
              textAlign: "center",
            }}
          >
            <div style={{ fontSize: 38, lineHeight: "30px", marginBottom: 8 }}>☁</div>
            Drag & Drop your JD file here
            <div style={{ marginTop: 4 }}>
              or{" "}
              <label style={{ color: "#9dc7ff", cursor: "pointer" }}>
                click to browse
                <input type="file" accept=".txt,.md" style={{ display: "none" }} onChange={(e) => handleFile(e.target.files?.[0])} />
              </label>
            </div>
          </div>
          <small style={{ opacity: 0.6, letterSpacing: 0.6 }}>Supported formats: .txt, .md</small>
          <div style={{ marginTop: 10 }}>
            <label style={{ opacity: 0.8, fontSize: 11, letterSpacing: 1.3 }}>3. PASTE JOB DESCRIPTION (OPTIONAL)</label>
            <textarea
              rows={6}
              value={jd}
              onChange={(e) => setJd(e.target.value)}
              placeholder="Paste the job description here..."
              style={{ width: "100%", marginTop: 8, background: "#0b0f14", color: "#e6edf3" }}
            />
            <div style={{ textAlign: "right", opacity: 0.6, fontSize: 12 }}>{jdChars}/2000</div>
          </div>
          <button type="submit" disabled={loading || jd.trim().length < 30} style={{ marginTop: 8, width: "100%" }}>
            {loading ? "INITIALIZING..." : "ENTER SIMULATION →"}
          </button>
          {error && <p style={{ color: "#ff9b9b" }}>{error}</p>}
        </motion.form>

        <div style={{ display: "grid", gap: 12 }}>
          <div className="card glass-heavy">
            <h3 style={{ marginTop: 0 }}>WHY QUANTIS?</h3>
            {whyItems.map(([title, sub]) => (
              <div key={title} style={{ marginBottom: 12 }}>
                <strong>{title}</strong>
                <div style={{ opacity: 0.75 }}>{sub}</div>
              </div>
            ))}
          </div>
          <div className="card glass-heavy" style={{ minHeight: 180, display: "grid", placeItems: "center", textAlign: "center" }}>
            <div>
              <div style={{ opacity: 0.7, fontSize: 20 }}>“</div>
              <div style={{ fontSize: 22 }}>Preparation Today,</div>
              <div style={{ fontSize: 22 }}>Success Tomorrow.</div>
              <div style={{ opacity: 0.7, fontSize: 20 }}>”</div>
            </div>
          </div>
        </div>
      </div>
      <div className="card glass-heavy" style={{ marginTop: 12 }}>
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
          <h3 style={{ margin: 0 }}>Account & History</h3>
          <button type="button" onClick={() => setShowAccountPanel((v) => !v)}>
            {showAccountPanel ? "Hide" : "Show"}
          </button>
        </div>
        {!showAccountPanel && (
          <p style={{ opacity: 0.8, marginTop: 8 }}>
            Optional: sign in to save history, view run details, observability summary, and resume gap analysis.
          </p>
        )}
        {showAccountPanel && (
          <>
        {!authReady ? (
          <>
            <input placeholder="Email" value={email} onChange={(e) => setEmail(e.target.value)} style={{ width: "100%", marginBottom: 8 }} />
            <input placeholder="Password" type="password" value={password} onChange={(e) => setPassword(e.target.value)} style={{ width: "100%", marginBottom: 8 }} />
            <div style={{ display: "flex", gap: 8 }}>
              <button type="button" onClick={async () => { try { await onRegister(email, password); setAuthMsg("Registered. Please login."); } catch (e) { setAuthMsg(e?.message || "Register failed."); } }}>Register</button>
              <button type="button" onClick={async () => { try { await onLogin(email, password); setAuthMsg("Logged in."); } catch (e) { setAuthMsg(e?.message || "Login failed."); } }}>Login</button>
            </div>
            {authMsg && <p>{authMsg}</p>}
          </>
        ) : (
          <>
            <div style={{ display: "flex", gap: 8, marginBottom: 8 }}>
              <button type="button" onClick={onRefreshHistory}>Refresh History</button>
              <button type="button" onClick={onRefreshObservability}>Refresh Observability</button>
            </div>
            <ul>
              {history.map((h) => (
                <li key={h.id}>
                  {h.role_title} • {h.interview_type} • {h.final_score}
                  <button type="button" style={{ marginLeft: 8 }} onClick={() => onGetRunDetail(h.id)}>Details</button>
                </li>
              ))}
            </ul>
            {historyDetail && (
              <div className="card" style={{ marginTop: 8 }}>
                <strong>Run Detail:</strong> {historyDetail.role_title} ({historyDetail.final_score})
              </div>
            )}
            {observability && (
              <div className="card" style={{ marginTop: 8 }}>
                <strong>API Metrics:</strong> req={observability.requests_total}, err%={observability.error_rate_pct}, p95={observability.latency_ms?.p95}
              </div>
            )}
          </>
        )}
          </>
        )}
      </div>
      {authReady && (
        <div className="card glass-heavy" style={{ marginTop: 12 }}>
          <h3>Resume vs JD Gap Analysis</h3>
          <input type="file" accept=".txt,.md,.pdf" onChange={(e) => setResumeFile(e.target.files?.[0] || null)} />
          <button
            type="button"
            style={{ marginLeft: 8 }}
            disabled={!resumeFile || !jd.trim()}
            onClick={async () => {
              try {
                await onRunGapAnalysis(jd, resumeFile);
              } catch {
                setAuthMsg("Gap analysis failed.");
              }
            }}
          >
            Analyze Gap
          </button>
          {gapAnalysis && (
            <div style={{ marginTop: 8 }}>
              <p><strong>Fit Score:</strong> {gapAnalysis.fit_score}</p>
              <p><strong>Missing Skills:</strong> {(gapAnalysis.missing_skills || []).join(", ") || "None"}</p>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

