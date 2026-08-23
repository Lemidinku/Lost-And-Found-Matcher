import type { MatchTier } from "../types";

/**
 * The app's signature element: match tiers rendered as a rotated,
 * worn-edged "ink stamp" rather than a generic pill badge. Strong and
 * Possible get real ink colours; Weak is rendered in faded ink (reduced
 * opacity) so the visual weight of the stamp itself communicates
 * confidence, not just its label -- a literal "running low on ink" read
 * for the tier that carries the least signal.
 */
const STYLES: Record<MatchTier, string> = {
  Strong: "border-stamp-green text-stamp-green",
  Possible: "border-stamp-amber text-stamp-amber",
  Weak: "border-ink/35 text-ink/45",
  // Hidden never reaches the client (the API drops it), kept only so this
  // lookup can't throw if that assumption ever changes.
  Hidden: "border-ink/35 text-ink/45",
};

function TierStamp({ tier }: { tier: MatchTier }) {
  return (
    <span
      className={`inline-flex -rotate-6 items-center rounded-full border-2 border-dashed px-3 py-1 font-stamp text-xs font-bold uppercase tracking-widest ${STYLES[tier]}`}
    >
      {tier}
    </span>
  );
}

export default TierStamp;
