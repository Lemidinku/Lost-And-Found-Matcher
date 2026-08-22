import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { listReports } from "../api";
import type { ReportRead, ReportType } from "../types";

type FilterValue = "all" | ReportType;

const FILTERS: { value: FilterValue; label: string }[] = [
  { value: "all", label: "All" },
  { value: "lost", label: "Lost" },
  { value: "found", label: "Found" },
];

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

function ReportListPage() {
  const [filter, setFilter] = useState<FilterValue>("all");
  const [reports, setReports] = useState<ReportRead[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;

    setIsLoading(true);
    setError(null);

    listReports(filter === "all" ? undefined : { reportType: filter })
      .then((data) => {
        if (!cancelled) {
          setReports(data);
        }
      })
      .catch((err: unknown) => {
        if (!cancelled) {
          setError(err instanceof Error ? err.message : "Failed to load reports.");
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
  }, [filter]);

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
        <h1 style={{ fontSize: "32px", margin: 0 }}>Lost &amp; Found Reports</h1>
        <Link
          to="/new"
          style={{
            display: "inline-block",
            padding: "10px 18px",
            borderRadius: "6px",
            background: "var(--accent)",
            color: "var(--text-h)",
            textDecoration: "none",
            fontWeight: 500,
            whiteSpace: "nowrap",
          }}
        >
          New report
        </Link>
      </div>

      <div
        role="tablist"
        aria-label="Filter reports by type"
        style={{ display: "flex", gap: "8px", marginBottom: "20px" }}
      >
        {FILTERS.map(({ value, label }) => (
          <button
            key={value}
            type="button"
            role="tab"
            aria-selected={filter === value}
            onClick={() => setFilter(value)}
            style={{
              padding: "8px 16px",
              borderRadius: "6px",
              border: "1px solid var(--border)",
              background: filter === value ? "var(--accent-bg)" : "transparent",
              color: filter === value ? "var(--accent)" : "var(--text)",
              fontWeight: filter === value ? 600 : 400,
              cursor: "pointer",
            }}
          >
            {label}
          </button>
        ))}
      </div>

      {isLoading && <p>Loading reports…</p>}

      {!isLoading && error && (
        <p style={{ color: "#d33" }}>Couldn't load reports: {error}</p>
      )}

      {!isLoading && !error && reports.length === 0 && (
        <p>No reports yet.</p>
      )}

      {!isLoading && !error && reports.length > 0 && (
        <table style={{ width: "100%", borderCollapse: "collapse" }}>
          <thead>
            <tr style={{ borderBottom: "2px solid var(--border)", textAlign: "left" }}>
              <th style={{ padding: "10px 8px" }}>Type</th>
              <th style={{ padding: "10px 8px" }}>Category</th>
              <th style={{ padding: "10px 8px" }}>Title</th>
              <th style={{ padding: "10px 8px" }}>Location</th>
              <th style={{ padding: "10px 8px" }}>Occurred</th>
              <th style={{ padding: "10px 8px" }}>Status</th>
            </tr>
          </thead>
          <tbody>
            {reports.map((report) => (
              <tr
                key={report.id}
                style={{ borderBottom: "1px solid var(--border)" }}
              >
                <td style={{ padding: "10px 8px" }}>
                  <Link
                    to={`/reports/${report.id}`}
                    style={{ color: "var(--accent)", textDecoration: "none" }}
                  >
                    {report.report_type === "lost" ? "Lost" : "Found"}
                  </Link>
                </td>
                <td style={{ padding: "10px 8px" }}>{report.category}</td>
                <td style={{ padding: "10px 8px" }}>
                  <Link
                    to={`/reports/${report.id}`}
                    style={{ color: "var(--text-h)", textDecoration: "none" }}
                  >
                    {report.title}
                  </Link>
                </td>
                <td style={{ padding: "10px 8px" }}>{report.location}</td>
                <td style={{ padding: "10px 8px" }}>
                  {formatOccurredAt(report.occurred_at)}
                </td>
                <td style={{ padding: "10px 8px" }}>{report.status}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}

export default ReportListPage;
