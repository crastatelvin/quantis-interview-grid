import { motion } from "framer-motion";

const DIMENSIONS = [
  { key: "relevance", color: "#1d6df5", radius: 70 },
  { key: "clarity", color: "#39d0f5", radius: 58 },
  { key: "depth", color: "#3dd68c", radius: 46 },
  { key: "structure", color: "#f0a429", radius: 34 },
  { key: "confidence", color: "#9c6cf5", radius: 22 },
];

export default function ScoreRings({ scores = {}, overall = 0 }) {
  const size = 160;
  const c = size / 2;
  return (
    <div style={{ position: "relative", width: size, height: size }}>
      <svg width={size} height={size}>
        {DIMENSIONS.map(({ key, color, radius }) => {
          const val = scores[key] || 0;
          const circ = 2 * Math.PI * radius;
          return (
            <g key={key}>
              <circle cx={c} cy={c} r={radius} fill="none" stroke="rgba(255,255,255,0.06)" strokeWidth="4" />
              <motion.circle
                cx={c}
                cy={c}
                r={radius}
                fill="none"
                stroke={color}
                strokeWidth="4"
                strokeLinecap="round"
                strokeDasharray={circ}
                initial={{ strokeDashoffset: circ }}
                animate={{ strokeDashoffset: circ - (val / 100) * circ }}
                style={{ transform: "rotate(-90deg)", transformOrigin: `${c}px ${c}px` }}
              />
            </g>
          );
        })}
      </svg>
      <div style={{ position: "absolute", inset: 0, display: "grid", placeItems: "center", fontSize: "2rem", fontWeight: 700 }}>
        {overall}
      </div>
    </div>
  );
}

