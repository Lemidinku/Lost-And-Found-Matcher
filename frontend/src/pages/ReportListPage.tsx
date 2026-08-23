import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { listReports } from "../api";
import { formatOccurredAt } from "../format";
import ReportTypeTag from "../components/ReportTypeTag";
import type { ReportRead, ReportType } from "../types";

type FilterValue = "all" | ReportType;

const FILTERS: { value: FilterValue; label: string }[] = [
  { value: "all", label: "All" },
  { value: "lost", label: "Lost" },
  { value: "found", label: "Found" },
];

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
    <div>
      <div className="mb-6 flex flex-wrap items-center justify-between gap-4">
        <h1 className="font-display text-3xl font-bold text-ink">Browse reports</h1>
        <Link
          to="/new"
          className="rounded-md bg-stamp-green px-4 py-2 font-medium text-paper no-underline transition hover:opacity-90 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-stamp-green"
        >
          + New report
        </Link>
      </div>

      <div
        role="tablist"
        aria-label="Filter reports by type"
        className="mb-6 flex gap-1 border-b border-ink/10"
      >
        {FILTERS.map(({ value, label }) => (
          <button
            key={value}
            type="button"
            role="tab"
            aria-selected={filter === value}
            onClick={() => setFilter(value)}
            className={`border-b-2 px-4 py-2 font-display text-sm uppercase tracking-wide transition focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-stamp-green ${
              filter === value
                ? "border-stamp-green text-ink"
                : "border-transparent text-ink/45 hover:text-ink/70"
            }`}
          >
            {label}
          </button>
        ))}
      </div>

      {isLoading && <p className="text-ink/60">Loading reports…</p>}

      {!isLoading && error && (
        <p className="text-stamp-red">Couldn't load reports: {error}</p>
      )}

      {!isLoading && !error && reports.length === 0 && (
        <div className="rounded-lg border border-dashed border-ink/25 px-6 py-10 text-center text-ink/50">
          No reports yet. The desk is empty.
        </div>
      )}

      {!isLoading && !error && reports.length > 0 && (
        <ul className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {reports.map((report) => (
            <li key={report.id}>
              <Link
                to={`/reports/${report.id}`}
                className="block rounded-lg border border-ink/10 bg-card p-4 no-underline shadow-sm transition hover:-translate-y-0.5 hover:border-stamp-green/40 hover:shadow-md focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-stamp-green"
              >
                <div className="mb-2 flex items-start justify-between gap-2">
                  <ReportTypeTag type={report.report_type} />
                  {report.status === "resolved" && (
                    <span className="font-stamp text-[11px] uppercase tracking-widest text-ink/35">
                      Resolved
                    </span>
                  )}
                </div>
                <h2 className="mb-1 font-display text-lg font-semibold text-ink">
                  {report.title}
                </h2>
                <p className="mb-3 text-sm text-ink/60">
                  {report.category} &middot; {report.location}
                </p>
                <p className="font-stamp text-xs uppercase tracking-wide text-ink/40">
                  {formatOccurredAt(report.occurred_at)}
                </p>
              </Link>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}

export default ReportListPage;
