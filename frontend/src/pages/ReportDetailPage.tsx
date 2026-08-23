import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { getMatches, getReport, resolveReport } from "../api";
import { formatOccurredAt } from "../format";
import MatchCard from "../components/MatchCard";
import ReportTypeTag from "../components/ReportTypeTag";
import type { MatchResult, ReportRead } from "../types";

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
    <div>
      <Link
        to="/"
        className="mb-6 inline-block text-sm text-ink/60 no-underline hover:text-stamp-green"
      >
        &larr; Back to reports
      </Link>

      {isLoading && <p className="text-ink/60">Loading report…</p>}

      {!isLoading && error && (
        <p className="text-stamp-red">Couldn't load report: {error}</p>
      )}

      {!isLoading && !error && report && (
        <>
          <div className="relative mb-8 overflow-hidden rounded-lg border border-ink/10 bg-card shadow-sm">
            {report.status === "resolved" && (
              <span className="absolute right-6 top-6 -rotate-12 rounded border-2 border-dashed border-stamp-red px-3 py-1 font-stamp text-sm font-bold uppercase tracking-widest text-stamp-red">
                Resolved
              </span>
            )}

            <div className="p-6">
              <div className="mb-2">
                <ReportTypeTag type={report.report_type} />
              </div>
              <h1 className="mb-2 font-display text-3xl font-bold text-ink">{report.title}</h1>
              <p className="mb-4 text-ink/60">
                {report.category} &middot; {report.color} &middot; {report.location}
              </p>
              <p className="mb-4 max-w-2xl text-ink">{report.description}</p>
              <p className="font-stamp text-xs uppercase tracking-wide text-ink/40">
                Reported {formatOccurredAt(report.occurred_at)} by {report.reporter_name} (
                {report.reporter_contact})
              </p>
            </div>

            <div className="border-t border-dashed border-ink/15 px-6 py-4">
              {report.status === "open" ? (
                <>
                  <button
                    type="button"
                    onClick={handleResolve}
                    disabled={isResolving}
                    className="rounded-md bg-stamp-green px-4 py-2 font-medium text-paper transition hover:opacity-90 disabled:cursor-default disabled:opacity-60 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-stamp-green"
                  >
                    {isResolving ? "Resolving…" : "Mark resolved"}
                  </button>
                  {resolveError && (
                    <p role="alert" className="mt-2 text-sm text-stamp-red">
                      Couldn't mark resolved: {resolveError}
                    </p>
                  )}
                </>
              ) : (
                <p className="font-stamp text-xs uppercase tracking-wide text-ink/40">
                  This item has been claimed.
                </p>
              )}
            </div>
          </div>

          <h2 className="mb-4 font-display text-xl font-bold text-ink">Potential matches</h2>

          {matches.length === 0 && (
            <div className="rounded-lg border border-dashed border-ink/25 px-6 py-10 text-center text-ink/50">
              No potential matches yet.
            </div>
          )}

          {matches.length > 0 && (
            <div className="space-y-3">
              {matches.map((match) => (
                <MatchCard key={match.report.id} {...match} />
              ))}
            </div>
          )}
        </>
      )}
    </div>
  );
}

export default ReportDetailPage;
