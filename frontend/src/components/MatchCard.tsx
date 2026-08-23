import { Link } from "react-router-dom";
import { formatOccurredAt } from "../format";
import TierStamp from "./TierStamp";
import type { MatchResult, MatchTier } from "../types";

const REASON_BORDER: Record<MatchTier, string> = {
  Strong: "border-stamp-green",
  Possible: "border-stamp-amber",
  Weak: "border-ink/30",
  Hidden: "border-ink/30",
};

function MatchCard({ report, score, tier, reason }: MatchResult) {
  return (
    <div className="rounded-lg border border-ink/10 bg-card p-4 shadow-sm">
      <div className="mb-2 flex flex-wrap items-start justify-between gap-3">
        <Link
          to={`/reports/${report.id}`}
          className="font-display text-lg font-semibold text-ink no-underline hover:text-stamp-green"
        >
          {report.title}
        </Link>
        <div className="flex items-center gap-3">
          <span className="font-stamp text-xs text-ink/45">Score {score}</span>
          <TierStamp tier={tier} />
        </div>
      </div>

      <p className="mb-3 text-sm text-ink/60">
        {report.category} &middot; {report.location} &middot; {formatOccurredAt(report.occurred_at)}
      </p>

      {reason && (
        <p className={`border-l-2 pl-3 text-sm italic text-ink/80 ${REASON_BORDER[tier]}`}>
          {reason}
        </p>
      )}
    </div>
  );
}

export default MatchCard;
