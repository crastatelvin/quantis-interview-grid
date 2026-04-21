import { Radar, RadarChart, PolarAngleAxis, PolarGrid, ResponsiveContainer } from "recharts";
import ScoreRings from "../components/ScoreRings";

export default function ReportPage({ report, onReset }) {
  const radarData = Object.entries(report?.avg_scores || {}).map(([k, v]) => ({ dimension: k, score: v }));

  return (
    <div style={{ maxWidth: 980, margin: "2rem auto", padding: "0 1rem" }}>
      <div className="card" style={{ marginBottom: 12, display: "flex", justifyContent: "space-between" }}>
        <h2>FINAL REPORT</h2>
        <button onClick={onReset}>NEW INTERVIEW</button>
      </div>
      <div style={{ display: "grid", gridTemplateColumns: "260px 1fr", gap: 12 }}>
        <div className="card" style={{ display: "grid", placeItems: "center" }}>
          <ScoreRings scores={report.avg_scores} overall={report.final_score} />
          <h3>Grade: {report.grade}</h3>
        </div>
        <div className="card">
          <ResponsiveContainer width="100%" height={250}>
            <RadarChart data={radarData}>
              <PolarGrid stroke="rgba(29,109,245,0.2)" />
              <PolarAngleAxis dataKey="dimension" />
              <Radar dataKey="score" stroke="#1d6df5" fill="#1d6df5" fillOpacity={0.2} />
            </RadarChart>
          </ResponsiveContainer>
        </div>
      </div>
      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 12, marginTop: 12 }}>
        <div className="card">
          <h3>Overall Assessment</h3>
          <p>{report.overall_assessment || "No assessment available."}</p>
        </div>
        <div className="card">
          <h3>Hiring Likelihood</h3>
          <p>{report.hiring_likelihood || "No hiring signal available."}</p>
        </div>
      </div>
      <div className="card" style={{ marginTop: 12 }}>
        <h3>Next Steps</h3>
        <ul>
          {(report.next_steps || []).map((step, i) => (
            <li key={`step-${i}`}>{step}</li>
          ))}
        </ul>
      </div>
      <div className="card" style={{ marginTop: 12 }}>
        <h3>Detailed Metrics</h3>
        <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 8 }}>
          {Object.entries(report.detailed_metrics || {}).map(([k, v]) => (
            <div key={k} className="card" style={{ padding: "0.55rem" }}>
              <div style={{ opacity: 0.7, fontSize: 12 }}>{k.replaceAll("_", " ").toUpperCase()}</div>
              <div style={{ fontSize: 18, fontWeight: 700 }}>{String(v)}</div>
            </div>
          ))}
        </div>
      </div>
      <div className="card" style={{ marginTop: 12 }}>
        <h3>Preparation Resources</h3>
        <ul>
          {(report.preparation_resources || []).map((r, i) => (
            <li key={`res-${i}`}>
              <a href={r.url} target="_blank" rel="noreferrer">{r.title}</a> - {r.why}
            </li>
          ))}
        </ul>
      </div>
    </div>
  );
}

