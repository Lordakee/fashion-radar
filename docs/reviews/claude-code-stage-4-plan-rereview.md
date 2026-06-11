# Claude Code Stage 4 Plan Re-Review

Date: 2026-06-11

Reviewer: Claude Code

Scope: Re-review of the updated Stage 4 section of
`docs/superpowers/plans/2026-06-11-fashion-radar-implementation-plan.md`
against the prior review (`claude-code-stage-4-plan-review.md`), the current
code (`settings.py`, `db/schema.py`, `db/repositories.py`,
`collectors/runner.py`, `models/source.py`, `models/report.py`), and the design
spec.

## Verdict

**Approved after fixes.** All nine prior findings (C1, C2, I1-I4, M1-M5) are
resolved in the updated plan. One residual gap remains from the C1 cluster: the
plan now pins every threshold and the label decision table, but never defines
the arithmetic that produces the `heat_score` number those thresholds and the
ranking compare against. Pin that formula before `scoring.py` tests are written;
nothing else blocks the stage.

## Prior-Finding Verification

1. **Windows + heat thresholds in YAML (was C1/I4).** Resolved. The "Scoring
   YAML contract" block adds `current_window_days`, `baseline_window_days`, and
   every label threshold (`rising_growth_ratio`, `cooling_growth_ratio`,
   `hot_score_threshold`, `hot_min_distinct_sources`, `new_entity_days`,
   `min_match_confidence`, etc.). The plan also lists both
   `configs/scoring.example.yaml` and the packaged
   `src/fashion_radar/templates/configs/scoring.example.yaml` for update, which
   matches how config templates ship today.
2. **One window model (was C1).** Resolved. The "Scoring window contract"
   commits to a single model: current = last `current_window_days`, baseline =
   the immediately preceding `baseline_window_days`, growth compared on daily
   rates. The earlier three-window confusion is gone.
3. **Source weight persisted as snapshot (was C2).** Resolved. The schema
   prerequisite adds `items.source_weight` (default `1.0` for old rows) via a
   tested v2->v3 migration, `upsert_item()` takes optional `source_weight`, and
   `collect_sources()` passes `SourceDefinition.weight`. `SourceDefinition`
   already carries `weight` (source.py:68), and `schema.py` is still at
   `SCHEMA_VERSION = 2`, so the v3 bump is real work this stage owns. Acceptance
   criteria explicitly forbid live config lookups.
4. **collected_at persisted + used for windows (was I1).** Resolved. Migration
   adds `items.collected_at`, defaulting old rows to `published_at`; window
   membership keys off `collected_at`, with `published_at` demoted to display.
   A test for a stale-`published_at`/freshly-collected item is listed.
5. **Injected `as_of` (was I2).** Resolved. Every scoring/report function takes
   an explicit UTC `as_of`; an acceptance criterion bans internal
   `datetime.now()`. This mirrors the existing injectable-`now` pattern in
   `collect_sources()` (runner.py:40) and the repositories.
6. **Mention dedupe + confidence (was I3).** Resolved. A mention is one distinct
   `(entity_name, item_id)` pair; only `confidence >= min_match_confidence`
   counts; weighted contribution is `source_weight * max(confidence)` per pair.
   This correctly collapses the multi-alias rows that `replace_item_matches()`
   stores (repositories.py:58). A multi-alias-single-item test is listed.
7. **Diversity + high-weight semantics (was I4).** Resolved. Diversity =
   distinct `source_name` in the current window (domain-level explicitly
   deferred); high-weight bonus triggers when any current-window mention has
   `source_weight >= high_weight_source_threshold`.
8. **Template packaging + Jinja2 (was M1/M2).** Resolved. Template moves to
   `src/fashion_radar/templates/daily_report.md` rendered with plain Python
   formatting, and the plan explicitly declines to add Jinja2. This avoids the
   wheel-packaging gap.
9. **Tie-breakers, zero-baseline, JSON boundary (was M3/M4/M5).** Resolved.
   Total ranking order defined (score desc, current mentions desc, distinct
   sources desc, `entity_name` asc); zero-baseline routed through the `new`
   branch before ratio math; reports built from a vetted Pydantic model with an
   acceptance test that `content_hash`/full text/raw rows never appear.

## Findings

### Critical

None.

### Important

**I-A. The `heat_score` composition formula is still undefined.** The plan pins
all thresholds and the label decision table, but the number they compare against
is never specified. `hot_score_threshold: 5.0` is meaningless and the primary
ranking key (`heat_score` desc) is non-reproducible until the arithmetic is
written down. The design spec gives only a skeleton
(`heat_score = weighted_mentions_7d + growth_bonus_7d_vs_30d +
source_diversity_bonus + high_weight_source_bonus`, spec lines 124-130), and the
YAML names collide with it ambiguously: in the spec `weighted_mentions_7d` is a
*term* (the weighted-mention contribution), but in the YAML
`weighted_mentions_7d: 1.0` reads like a *coefficient*. Before writing
`scoring.py` tests, state explicitly, e.g.:

- `weighted_mention_sum` = sum over distinct `(entity, item)` pairs of
  `source_weight * max(confidence)` (already defined).
- whether `weighted_mentions_7d` multiplies that sum or is added flat,
- whether `growth_bonus` is added flat when the rising condition holds (and
  whether it scales with the growth ratio),
- whether `source_diversity_bonus` is flat or multiplied by distinct-source
  count,
- whether `high_weight_source_bonus` is added flat when the high-weight
  condition holds.

This is the unresolved remainder of the original C1 ("arbitrary or
non-reproducible rankings"); the threshold/label half is fixed, the score half
is not.

### Minor

**M-A. Define `growth_ratio` symbolically.** The window contract gives
`current_rate` and `baseline_rate` and says "growth compares daily rates," and
the decision table uses "growth ratio." Add the one line
`growth_ratio = current_rate / baseline_rate` so no implementer reads it as
`current_mentions / baseline_mentions` (a ~4.3x difference given 7d vs 30d
windows, which would make `rising_growth_ratio: 1.5` and
`cooling_growth_ratio: 0.75` behave very differently than intended).

**M-B. Specify `collected_at` behavior on re-upsert.** `upsert_item()` updates
an existing row when the normalized URL matches (repositories.py:43). The plan
does not say whether `collected_at` is preserved (first-seen) or overwritten on
re-collection. Overwriting would shift an item's window membership and the
entity first-seen time used by the `new` label across runs, undermining
determinism. State that `collected_at` is set once on insert and preserved on
update, and add a test.

**M-C. `stable` fallback for zero-current-mention entities is slightly off.**
Decision rule 6 makes `stable` the fallback for any non-empty entity. An entity
with baseline mentions but zero current-window mentions and baseline `< 2`
(below `cooling_min_baseline_mentions`) would be labeled `stable`, which reads
oddly for something with no recent activity. Harmless, but consider whether such
entities should appear at all or be labeled `cooling`. Confirm intent.

## Recommendation

**Approved after fixes** — resolve I-A (and fold in the three Minor items) in the
plan text before the heat-scoring tasks begin. The schema/migration, persistence,
config, windowing, mention-counting, and report-boundary work can proceed as
written.
