# Lost & Found Matcher — Approaches & Assumptions

Research + design options for the Nemma take-home assessment, before any code is written.
Stack decided: **FastAPI backend + separate React frontend**, minimal web UI (forms to submit
reports, a page to view ranked potential matches).

## Design philosophy: matching is advisory, not authoritative

A human ultimately reunites the item with its owner — the app's job is to narrow a big pile of
reports down to a short, ranked shortlist a person can scan in seconds, not to auto-resolve
anything. That framing drives two concrete decisions:

- **Favour recall over precision.** Missing a real match is worse than surfacing a weak one a
  human can dismiss in two seconds. So the app always shows a ranked list of candidates per
  report, not a single "the answer" pick, and the show/hide threshold is set low rather than
  high — better to over-show than to silently drop a real match.
- **Every match must be explainable.** A bare score ("0.82") is worth much less than a sentence
  a human can act on: *"Same category (backpack), colour overlap (black/dark), same location
  (library), 4 hours apart."* Explainability is cheap to build on top of rule-based scoring and
  is what actually lets a human trust — or quickly reject — a suggestion.

This is also the strongest argument for Option D over B/C below: embeddings and LLM scores are
harder to turn into a short, honest "why" sentence, and precision-maximizing behavior (hiding
anything below a high-confidence bar) is the wrong failure mode for a tool whose output a human
double-checks anyway.

## What the brief actually requires (minimum bar)

1. Create/provide lost-item reports.
2. Create/provide found-item reports.
3. See potential matches.
Everything else — fields, comparison logic, match strength, UI, error handling — is our call,
and the brief explicitly rewards *thoughtful, small* over *complicated, unfinished*.

## Common ways this problem gets solved (from research)

| Family | Typical technique | Where it shows up |
|---|---|---|
| Deterministic string/attribute matching | Jaccard index, Levenshtein/edit distance, Jaro-Winkler, BM25, TF-IDF cosine | Classic "fuzzy matching" libraries (e.g. `intuit/fuzzy-matcher`), record-linkage/entity-resolution tooling (dataladder, Informatica, Redis fuzzy search) |
| Semantic text embeddings | Sentence embeddings + cosine similarity (local model or API) | General text-similarity repos, recommendation/item-item-similarity systems |
| LLM-judged comparison | Prompt an LLM with both descriptions, ask for a match score/reasoning | Newer "AI-powered lost & found" campus projects |
| Image similarity | Perceptual hashing / CLIP-style embeddings on photos | Research systems combining text + image (e.g. "LostNet", PLOS ONE 2024) |

For a 3-hour, text-only, no-photo-upload scope, the first two families (and a hybrid of them)
are the realistic candidates. Image similarity is out of scope (see "Deferred" below).

## Matching approach: three options + recommendation

### Option A — Rule-based weighted scoring
Compare structured fields directly, combine into a weighted score:
- **Category** (exact/synonym match against a fixed small taxonomy)
- **Color** (exact/fuzzy string match, maybe a tiny synonym table: "dark" ≈ "black"/"navy")
- **Location** (fuzzy string match, optionally against a fixed list of campus locations)
- **Date proximity** (score decays with days between lost-date and found-date; found should
  generally be on/after lost, but don't hard-reject on this — people misreport)
- **Free-text description** — word-overlap/Jaccard or TF-IDF cosine after stopword removal

**Pros:** deterministic, fast, zero external dependencies, every score is explainable line by
line — you can walk an interviewer through exactly why a match scored 85/100.
**Cons:** brittle to vocabulary mismatch ("AirPods case" vs "earbud case") unless you hand-build
synonym tables; doesn't generalize beyond what you anticipated.

### Option B — Embeddings / semantic similarity
Embed each report's free text (local model like `all-MiniLM-L6-v2`, or an API), compute cosine
similarity between lost/found embeddings, optionally blend with a light structured filter
(category, date window).

**Pros:** catches semantic matches without hand-built synonym dictionaries ("AirPods case" ~
"earbud case" scores high automatically).
**Cons:** adds a real dependency (model download, or an API key + network + cost + latency),
and the score is much harder to *explain* — "cosine similarity 0.83" doesn't tell a user or an
interviewer *why*. Heavier than the brief's "keep it small" asks for.

### Option C — LLM-judged matching
Send each lost/found pair (or top-K prefiltered candidates) to an LLM: "are these plausibly the
same item? score 0–100, one-sentence reasoning."

**Pros:** very fast to build, strong semantic reasoning for free, produces a human-readable
justification per match (nice UX: "Same category, similar color, found near where it was lost").
**Cons:** nondeterministic run-to-run (even at low temperature), needs an API key, cost/latency
scale as O(lost × found) calls, hard to unit test, and — most importantly for an *engineering*
assessment — it outsources the exact design decision ("what makes two reports a possible match?")
that the brief is explicitly asking you to make and defend.

### Recommendation — Option D: Hybrid, rule-based backbone
Structured attribute scoring (category, color, location, date) **plus** a lightweight local
text-similarity signal (TF-IDF cosine or normalized word-overlap — no embedding model, no API
key), combined into one weighted score with a visible breakdown per field. Bucket the total into
tiers (e.g. **Strong / Possible / Weak**) rather than a binary yes/no, which directly answers the
brief's "whether some matches should be considered stronger than others" — and each field
contributing to the score doubles as a plain-English reason, so the explanation is a by-product
of the scoring design rather than a separate thing to build.

Why this wins for *this* task specifically:
- Fully explainable — every score component can be shown in the UI *and* turned directly into a
  human-readable reason string ("same category, colour overlap, same location, 4 hours apart"),
  which is exactly the artifact an advisory (not authoritative) matcher needs to be useful.
- No external dependency/API key — runs offline, deterministic, trivially testable.
- Matches the brief's ambiguous example well: "black backpack" vs "dark-colored backpack near
  library" should score high; "black backpack, football field, two weeks later" should score
  lower on location + date even though color/category still match — and still surface, just
  ranked lower, so a human can glance at it and dismiss it rather than never seeing it at all.
- AI tools can still be used generously to *build* the app (per the brief, this doesn't count
  against us) — we're just choosing not to make AI/embeddings *part of the algorithm itself*, so
  the matching logic stays something we designed and can explain, not something we're borrowing.

## Match presentation
- Ranked list of candidate matches per lost (or found) report — a shortlist for a human to scan,
  not an auto-resolved answer.
- Each candidate shows a total score, a tier badge (Strong/Possible/Weak), and a **generated
  reason string** built from whichever fields actually contributed, e.g.: *"Same category
  (backpack), colour overlap (black/dark), same location (library), 4 hours apart."* Fields that
  scored zero are simply omitted from the sentence rather than listed as a miss.
- Threshold for showing a pair at all is set low (recall-favouring) — a human can dismiss a weak
  suggestion in two seconds, but a real match that never appears can't be dismissed *or* acted on.
  Only pairs scoring at essentially zero relevance (e.g. wrong category *and* no text overlap
  *and* far apart in time) are dropped from the list entirely.

## Assumptions to make (to document in the README)

- **No auth/accounts.** Reports carry a reporter name + contact field but there's no login. Out
  of scope per "keep it small."
- **No photo upload / image matching.** Text-only. Flagged as future work.
- **Single university, single flat list of reports** — no multi-tenant, no departments.
- **Persistence:** SQLite via FastAPI (SQLAlchemy/SQLModel) — enough to persist across restarts,
  no need for a full DB server/Docker for a 3-hour assessment.
- **Fixed small category taxonomy** (e.g. Electronics, Bag, Clothing, Accessory, Documents/Cards,
  Keys, Other) rather than free text — makes structured scoring tractable. Free-text description
  still captures anything the taxonomy misses.
- **Location** is free text, fuzzy-matched (not geocoded/lat-long) — campuses are small enough
  that string similarity on location names is a reasonable proxy.
- **Date proximity, not strict ordering** — a found date before a lost date is treated as a
  weaker signal, not an automatic disqualifier (misremembered dates happen).
- **"Potential match" is a ranked, tiered score, not a boolean** — mirrors the brief's own
  worked example where the football-field backpack "may or may not" be a match.
- **Matching is advisory, not authoritative** — a human makes the final call, so the app is
  tuned to favour recall over precision (show borderline candidates rather than hide them) and
  every match is paired with a plain-English reason, not just a number.
- **No claim/resolution workflow beyond maybe marking a match confirmed** — no notifications,
  no email, no closing the loop with the two students.

## Intentionally deferred (documented, not built)

- Photo upload + image similarity (perceptual hash or CLIP embeddings) for visual matching.
- Proper synonym/ontology handling (WordNet or curated dictionaries) for colors/categories/brands.
- Swappable matching backend — start with Option D, but structure the scorer behind an interface
  so Option B (embeddings) could be dropped in later without touching the rest of the app.
- Admin workflow: confirm/reject a match, notify both parties, auto-close resolved reports.
- Real geolocation (lat/long + radius) instead of fuzzy string matching on location names.
- Authentication, per-user report ownership, rate limiting/abuse handling.
- Pagination and search once report volume grows past a demo-sized list.
- Automated test suite + CI (would add given more time; for 3 hours, a few targeted unit tests
  on the scoring function are the higher-value spend).

## Open questions worth a one-line assumption rather than a blocker

- What counts as "duplicate" reports (same person reporting the same item twice)? → Not
  deduplicated; out of scope.
- Should a resolved/claimed report stop showing up in match lists? → Add a `status` field
  (`open`/`resolved`) and filter resolved items out of match results — cheap to add, meaningfully
  more realistic.

## Next step
Once you've reviewed this, I'll turn Option D into a short concrete design (data model, scoring
formula with weights, API routes, page layout) for your approval before writing any code.
