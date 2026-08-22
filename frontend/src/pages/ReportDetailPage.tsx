import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { getMatches, getReport, resolveReport } from "../api";
import MatchCard from "../components/MatchCard";
import type { MatchResult, ReportRead } from "../types";

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

function ReportDetailPage() {
  const { id } = useParams<{ id: string }>();
  const reportId = Number(id);

  const [report, setReport] = useState<ReportRead | null>(null);
  const [matches, setMatches] = useState<MatchResult[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [isResolving, setIsResolving] = useState(false);
  const [resolveError, setResolveError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;

    setIsLoading(true);
    setError(null);

    Promise.all([getReport(reportId), getMatches(reportId)])
      .then(([reportData, matchData]) => {
        if (!cancelled) {
          setReport(reportData);
          setMatches(matchData);
        }
      })
      .catch((err: unknown) => {
        if (!cancelled) {
          setError(err instanceof Error ? err.message : "Failed to load report.");
        }
      })
      .finally(() => {
        if (!cancelled) {
          setIsLoading(false);
        }
      });

    return () => {
      cancelled = true;
    };
  }, [reportId]);

  async function handleResolve() {
    setResolveError(null);
    setIsResolving(true);
    try {
      const updated = await resolveReport(reportId);
      setReport(updated);
    } catch (err) {
      setResolveError(err instanceof Error ? err.message : "Failed to resolve report.");
    } finally {
      setIsResolving(false);
    }
  }

  return (
    <div style={{ padding: "24px", textAlign: "left" }}>
      <div
        style={{
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
          marginBottom: "20px",
          gap: "16px",
          flexWrap: "wrap",
        }}
      >
        <h1 style={{ fontSize: "32px", margin: 0 }}>Report detail</h1>
        <Link
          to="/"
          style={{ color: "var(--accent)", textDecoration: "none", whiteSpace: "nowrap" }}
        >
          Back to reports
        </Link>
      </div>

      {isLoading && <p>Loading report…</p>}

      {!isLoading && error && (
        <p style={{ color: "#d33" }}>Couldn't load report: {error}</p>
      )}

      {!isLoading && !error && report && (
        <>
          <div
            style={{
              border: "1px solid var(--border)",
              borderRadius: "8px",
              padding: "20px",
              marginBottom: "24px",
            }}
          >
            <div
              style={{
                display: "flex",
                justifyContent: "space-between",
                alignItems: "flex-start",
                gap: "16px",
                flexWrap: "wrap",
                marginBottom: "12px",
              }}
            >
              <h2 style={{ margin: 0 }}>{report.title}</h2>
              <div style={{ display: "flex", alignItems: "center", gap: "10px" }}>
                <span
                  style={{
                    padding: "4px 10px",
                    borderRadius: "999px",
                    background: "var(--accent-bg)",
                    color: "var(--accent)",
                    fontWeight: 600,
                    fontSize: "13px",
                    textTransform: "capitalize",
                  }}
                >
                  {report.report_type}
                </span>
                <span
                  style={{
                    padding: "4px 10px",
                    borderRadius: "999px",
                    background: "var(--code-bg)",
                    color: "var(--text-h)",
                    fontWeight: 600,
                    fontSize: "13px",
                    textTransform: "capitalize",
                  }}
                >
                  {report.status}
                </span>
              </div>
            </div>

            <p style={{ color: "var(--text)", marginBottom: "10px" }}>
              {report.category} &middot; {report.color} &middot; {report.location} &middot;{" "}
              {formatOccurredAt(report.occurred_at)}
            </p>

            <p style={{ color: "var(--text-h)", marginBottom: "14px" }}>{report.description}</p>

            <p style={{ color: "var(--text)", fontSize: "15px", marginBottom: "0" }}>
              Reported by {report.reporter_name} ({report.reporter_contact})
            </p>

            {report.status === "open" && (
              <div style={{ marginTop: "18px" }}>
                <button
                  type="button"
                  onClick={handleResolve}
                  disabled={isResolving}
                  style={{
                    padding: "10px 20px",
                    borderRadius: "6px",
                    border: "none",
                    background: "var(--accent)",
                    color: "var(--text-h)",
                    fontWeight: 500,
                    cursor: isResolving ? "default" : "pointer",
                    opacity: isResolving ? 0.7 : 1,
                  }}
                >
                  {isResolving ? "Resolving…" : "Mark resolved"}
                </button>
                {resolveError && (
                  <p role="alert" style={{ color: "#d33", marginTop: "10px" }}>
                    {resolveError}
                  </p>
                )}
              </div>
            )}
          </div>

          <h2 style={{ fontSize: "22px", marginBottom: "14px" }}>Potential matches</h2>

          {matches.length === 0 && <p>No potential matches yet.</p>}

          {matches.map((match) => (
            <MatchCard key={match.report.id} {...match} />
          ))}
        </>
      )}
    </div>
  );
}

export default ReportDetailPage;
