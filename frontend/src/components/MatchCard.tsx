import type { CSSProperties } from "react";
import { Link } from "react-router-dom";
import type { MatchResult, MatchTier } from "../types";

const TIER_COLORS: Record<MatchTier, { bg: string; fg: string }> = {
  Strong: { bg: "rgba(34, 197, 94, 0.15)", fg: "#16a34a" },
  Possible: { bg: "rgba(234, 179, 8, 0.15)", fg: "#a16207" },
  Weak: { bg: "rgba(107, 114, 128, 0.15)", fg: "#6b7280" },
  Hidden: { bg: "rgba(107, 114, 128, 0.15)", fg: "#6b7280" },
};

function formatOccurredAt(value: string): string {
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) {
    return value;
  }
  return date.toLocaleString(undefined, {
    year: "numeric",
    month: "short",
    day: "numeric",
    hour: "numeric",
    minute: "2-digit",
  });
}

const cardStyle: CSSProperties = {
  border: "1px solid var(--border)",
  borderRadius: "8px",
  padding: "16px",
  marginBottom: "14px",
};

function MatchCard({ report, score, tier, reason }: MatchResult) {
  const { bg, fg } = TIER_COLORS[tier];

  return (
    <div style={cardStyle}>
      <div
        style={{
          display: "flex",
          justifyContent: "space-between",
          alignItems: "flex-start",
          gap: "12px",
          marginBottom: "8px",
          flexWrap: "wrap",
        }}
      >
        <Link
          to={`/reports/${report.id}`}
          style={{ color: "var(--text-h)", textDecoration: "none", fontWeight: 600, fontSize: "18px" }}
        >
          {report.title}
        </Link>
        <div style={{ display: "flex", alignItems: "center", gap: "10px" }}>
          <span
            style={{
              padding: "4px 10px",
              borderRadius: "999px",
              background: bg,
              color: fg,
              fontWeight: 600,
              fontSize: "13px",
            }}
          >
            {tier}
          </span>
          <span style={{ color: "var(--text)", fontSize: "14px" }}>Score: {score}</span>
        </div>
      </div>

      <p style={{ color: "var(--text)", marginBottom: "6px" }}>
        {report.category} &middot; {report.location} &middot; {formatOccurredAt(report.occurred_at)}
      </p>

      <p style={{ color: "var(--text)", fontStyle: "italic" }}>{reason}</p>
    </div>
  );
}

export default MatchCard;
