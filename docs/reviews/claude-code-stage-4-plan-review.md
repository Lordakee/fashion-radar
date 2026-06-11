# Claude Code Stage 4 Plan Review

Date: 2026-06-11

Reviewer: Claude Code

Scope: Stage 4 plan (heat scoring + Markdown/JSON reports) against the current
Stage 3 implementation, the design spec, and the implementation plan.

## Verdict

**Approved after fixes.** The staging, file layout, TDD approach, and content
boundaries are sound and consistent with the spec. But the plan as written
leaves the scoring math underspecified in ways that will produce arbitrary or
non-reproducible rankings, and it has two concrete correctness/packaging gaps
(weight sourcing, template packaging). Resolve the Critical and Important items
below before implementation.

## Findings

### Critical

**C1. Heat-label thresholds and scoring windows are undefined in config; the
current `ScoringSettings` only holds bonus magnitudes.**

`ScoringSettings` (settings.py:95) defines `weighted_mentions_7d`,
`growth_bonus`, `source_diversity_bonus`, `high_weight_source_bonus`, and
`new_entity_days` — these are coefficients/magnitudes, not decision boundaries.
The plan's heat labels (`new`/`rising`/`hot`/`stable`/`cooling`) and the design
formula (`growth_bonus_7d_vs_30d`, design spec lines 124-138) require values
that do not exist anywhere:

- baseline window length (spec says 7d-vs-30d; plan step 4 says "24h window"
  plus "7-day count" plus "previous comparable window" — three different window
  models that are not reconciled).
- the growth ratio/delta threshold that separates `rising` from `stable`.
- the score and diversity thresholds that define `hot`.
- the below-baseline threshold that defines `cooling`.
- the source-weight value at/above which `high_weight_source_bonus` applies.

Without these in YAML, the implementation will hardcode magic numbers, directly
contradicting plan goal "Heat score constants come from YAML" (plan line 354)
and making "avoid arbitrary or misleading rankings" unverifiable. The design
explicitly requires constants to live in YAML so they can be tuned without code
changes (spec line 140).

Fix before coding: extend `ScoringSettings` (and `configs/scoring.example.yaml`)
with the missing window lengths and thresholds, choose ONE window model, and
write the exact heat-label decision table the tests will assert against. The
five fixture cases in the spec (new/weak, stable/many, rising, high-volume
source that must not dominate; spec lines 142-147) should map 1:1 to named
config thresholds.

**C2. Source weight is not persisted, so weighted scoring is non-deterministic
and diverges from the spec.**

The scoring formula needs per-source weight, but `items` stores only
`source_name`/`source_type` (schema.py:29-42) — not weight. Plan step 4 says
"weighted mention count using source weight from config", i.e. it intends to
read live YAML at scoring time. That breaks reproducibility: renaming, removing,
or reweighting a source retroactively changes historical scores, and an item
whose source is no longer in config has no defined weight. The design called for
a `sources` table holding "weights copied from YAML for run traceability" (spec
lines 109, 50) that was never built — this is a real plan gap, not just a
preference.

Decide and document one of:
- (preferred) add a `sources` table (or a `source_weight` column on `items`)
  capturing weight at collection time, so scoring joins on stored weight; this
  is a schema change and belongs to this stage's scope (see I1), or
- explicitly accept config-time weight lookup AND define the fallback weight for
  unknown sources (e.g. 1.0) plus a test that pins the fallback.

Either way the choice must be explicit and tested; the current plan is silent.

### Important

**I1. No ingestion timestamp — windowing on `published_at` alone is
unreliable.**

`items` has no `collected_at`/`created_at` column (schema.py:29-42);
`published_at` comes from the feed and can be missing, stale, or future-dated.
Bucketing the "current 24h window" by `published_at` means an item collected
today but published last week silently falls outside today's report. Add a
`collected_at` column (reuse the v1->v2 migration pattern at schema.py:118,
bumping to v3), or explicitly document that windows key off `published_at` and
add a test covering a stale-but-freshly-collected item. This needs to be settled
now because it determines the schema and every window query.

**I2. Determinism requires an injected reference time; the plan does not state
it.**

Scoring and report generation must accept an explicit `as_of`/`now` parameter
rather than calling `datetime.now()` (the runner currently calls
`datetime.now(tz=UTC)` directly, runner.py:48,83). `ReportMetadata` already
separates `generated_at` from `report_date` (report.py:13-14), which hints at
this — make it a required function argument so fixture tests are reproducible.
Add this to the plan and to test expectations.

**I3. Mention counting must dedupe aliases per item; "mention" needs a precise
definition.**

`match_entities` emits one `EntityMatchDecision` per matched alias
(entities.py:40-54), and `item_entities` stores one row per alias. An item
matching two aliases of the same entity (e.g. "YSL" and "Saint Laurent") yields
two rows. Counting rows would double-count. Define a mention as a DISTINCT item
per entity (`COUNT(DISTINCT item_id)`), and add a fixture proving multi-alias
single-item counts as one. Also decide explicitly: (a) whether low-`confidence`
matches count toward metrics or are filtered by a threshold, and (b) whether
weighting multiplies by `confidence`. State both in the plan.

**I4. "Source diversity" and "high-weight source" are undefined.**

Plan step 4 lists "source diversity count" and step 5/the formula reference a
high-weight bonus, but neither defines the unit. Specify whether diversity =
distinct `source_name`, distinct `source_type`, or distinct domain (the spec's
"per-domain weighting" language at line 147 implies domain, which is derivable
from `items.url`/`normalized_url`). Pin the diversity threshold for `hot` and the
weight cutoff for the high-weight bonus in config (ties into C1).

### Minor

**M1. Report template must live inside the package, not at repo root.**

Existing config templates are packaged under `src/fashion_radar/templates/configs/`
and loaded via `importlib.resources` (cli.py:3,34); the wheel only includes
`src/fashion_radar` (pyproject.toml:50-51). The proposed
`templates/daily_report.md.j2` at repo root would not ship in the wheel. Place it
at `src/fashion_radar/templates/daily_report.md.j2` and load via
`importlib.resources`.

**M2. Jinja2 is not a declared dependency.**

`jinja2` appears in `uv.lock` only transitively via the `dashboard` extra
(altair/pydeck/streamlit). If `reports.py` imports Jinja2, add `jinja2` to
`[project.dependencies]` (and refresh the lock); otherwise it will fail for users
who install without the dashboard extra. Alternatively render Markdown with plain
Python f-strings/`str.format` and avoid the dependency entirely — viable given
the report's simple structure and arguably better for determinism.

**M3. Rankings need a total, deterministic tie-break order.**

To keep fixture tests stable, define ordering as score desc, then a stable
secondary key (mention count desc, then `entity_name` asc). State this in the
plan so list ordering in both Markdown and JSON is reproducible.

**M4. Guard the growth ratio against divide-by-zero.**

For a `new` entity the previous/baseline window count is 0. Define the
growth metric to use a delta or a guarded ratio (e.g. treat 0-baseline as the
`new` branch before computing a ratio) and add a fixture for it.

**M5. JSON report should serialize only the vetted report model.**

To honor the "no full article text / short summaries only" boundary (plan
steps and spec line 163), build the JSON from the same Pydantic report model as
Markdown and never dump raw `items` rows (which carry `content_hash` and other
internal fields). Add an assertion that `content_hash` and full content never
appear in either output. The 500-char `max_summary_chars` cap (source.py:36) is
appropriately conservative.

## Answers To Review Questions

1. **Safe to execute after Stage 3?** Yes, structurally — Stage 3 is approved and
   the read-only scoring/report layer does not disturb collectors. But not safe
   to start coding until C1/C2 and I1-I4 are resolved, since they determine the
   schema and the scoring contract.
2. **Windows/labels specific enough?** No. C1 and I4 must define windows,
   thresholds, and the label decision table in YAML first.
3. **Schema/repository changes needed?** Yes (I1 collected_at; C2 likely a
   `sources` table/weight column). Read-only repository helpers for windowed
   `COUNT(DISTINCT item_id)` aggregation, source health, and recent failed/skipped
   runs are appropriate and in scope.
4. **Content boundaries conservative enough?** Yes — short stored summaries,
   attribution fields, and the 500-char cap are sufficient; M5 just hardens it.
5. **Tests sufficient?** Almost. Add cases for: multi-alias single-item dedupe
   (I3), confidence handling (I3), stale-but-fresh item windowing (I1), injected
   `as_of` reproducibility (I2), unknown/renamed source weight fallback (C2),
   zero-baseline growth (M4), and an explicit no-full-text/no-content-hash
   assertion (M5). The listed empty-DB case is good and should stay.
6. **Defer to Stage 5?** Keep pandas and Streamlit out of Stage 4 as planned.
   Persisting `entity_daily_metrics`/`reports` rows (spec lines 112-113) is NOT
   required for Stage 4's file artifacts and can be deferred to Stage 5, but the
   `sources`/weight persistence in C2 and `collected_at` in I1 should NOT be
   deferred — they are scoring correctness prerequisites.

## Recommendation

**Approved after fixes** — resolve C1, C2, and I1-I4 (and fold in the Minor
items) in an updated plan before Stage 4 implementation begins.
