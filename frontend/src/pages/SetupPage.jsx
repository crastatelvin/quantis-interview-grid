import { useState } from "react";
import { motion } from "framer-motion";
import HoloAvatar from "../components/HoloAvatar";

const TYPES = ["technical", "behavioral", "product", "leadership", "hr"];

export default function SetupPage({ onStart, loading, error }) {
  const [jd, setJd] = useState("");
  const [type, setType] = useState("behavioral");
  const [dragActive, setDragActive] = useState(false);

  const handleFile = async (file) => {
    if (!file) return;
    const text = await file.text();
    setJd(text);
  };

  return (
    <div style={{ maxWidth: 900, margin: "2rem auto", padding: "0 1rem" }}>
      <div style={{ display: "grid", placeItems: "center" }}>
        <HoloAvatar speaking={false} />
      </div>
      <h1 className="cinzel" style={{ textAlign: "center", letterSpacing: 2, marginBottom: 4 }}>QUANTIS INTERVIEW GRID</h1>
      <p className="calligraphic" style={{ textAlign: "center", fontSize: "1.7rem", marginTop: 0 }}>Enter the simulation</p>
      <motion.form
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.65, ease: [0.22, 1, 0.36, 1] }}
        className="card glass-panel"
        onSubmit={(e) => {
          e.preventDefault();
          onStart(jd, type);
        }}
      >
        <div>
          <label>Interview Type</label>
          <select value={type} onChange={(e) => setType(e.target.value)} style={{ marginLeft: 8 }}>
            {TYPES.map((t) => <option key={t} value={t}>{t.toUpperCase()}</option>)}
          </select>
        </div>
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
            marginTop: 12,
            border: `1px dashed ${dragActive ? "#5da6ff" : "rgba(93,166,255,0.35)"}`,
            borderRadius: 8,
            padding: 10,
            textAlign: "center",
          }}
        >
          Drop JD file (.txt/.md) here or{" "}
          <label style={{ color: "#9dc7ff", cursor: "pointer" }}>
            browse
            <input type="file" accept=".txt,.md" style={{ display: "none" }} onChange={(e) => handleFile(e.target.files?.[0])} />
          </label>
        </div>
        <textarea
          rows={10}
          value={jd}
          onChange={(e) => setJd(e.target.value)}
          placeholder="Paste job description..."
          style={{ width: "100%", marginTop: 12, background: "#0b0f14", color: "#e6edf3" }}
        />
        <button type="submit" disabled={loading || jd.trim().length < 30} style={{ marginTop: 10, width: "100%" }}>
          {loading ? "INITIALIZING..." : "ENTER SIMULATION"}
        </button>
        {error && <p style={{ color: "#ff9b9b" }}>{error}</p>}
      </motion.form>
    </div>
  );
}

