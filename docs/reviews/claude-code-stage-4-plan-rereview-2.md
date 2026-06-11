# Claude Code Stage 4 Plan Re-Review 2

Date: 2026-06-11

Reviewer: Claude Code

Scope: Second re-review of the Stage 4 section of
`docs/superpowers/plans/2026-06-11-fashion-radar-implementation-plan.md` after
the scoring-formula fixes, against the prior reviews
(`claude-code-stage-4-plan-review.md`, `claude-code-stage-4-plan-rereview.md`)
and the current code (`db/schema.py`, `db/repositories.py`,
`collectors/runner.py`, `models/source.py`, `settings.py`).

## Verdict

**Approved for Stage 4 implementation.** All five remaining findings from the
first re-review (I-A, M-A, M-B, M-C) are resolved in the updated plan. The
scoring contract is now fully reproducible: the formula, the growth-ratio
definition, the collected-at lifecycle, and the zero-current-entity handling are
each pinned, and tests are listed for the heat-score components and collected-at
preservation. Nothing blocks the stage.

## Prior-Finding Verification

1. **`heat_score` formula explicit and reproducible (was I-A).** Resolved. The
   "Heat score formula" block (plan lines 401-425) defines four named components
   and their sum:
   - `weighted_mention_component = weighted_mention_sum * weighted_mentions_7d`
     (so `weighted_mentions_7d` is correctly stated as a coefficient, not a flat
     term — the ambiguity flagged in I-A is gone).
   - `growth_component = max(0, growth_ratio - 1) * growth_bonus` when
     `baseline_mentions > 0`, else `0` (scales with the ratio, guarded against
     the zero-baseline case).
   - `source_diversity_component = max(0, distinct_sources - 1) * source_diversity_bonus`.
   - `high_weight_component = high_weight_source_bonus` when any current-window
     mention has `source_weight >= high_weight_source_threshold`, else `0`.
   `weighted_mention_sum` is defined upstream (lines 392-393) as the sum of
   `source_weight * max(confidence)` over distinct `(entity, item)` pairs. The
   `hot_score_threshold: 5.0` now compares against a defined quantity. Fully
   reproducible.
2. **`growth_ratio = current_rate / baseline_rate` defined (was M-A).** Resolved.
   Plan line 360 states it symbolically, with `current_rate = current_mentions /
   current_window_days` and `baseline_rate = baseline_mentions /
   baseline_window_days` defined at lines 357-359. No implementer can misread it
   as a raw mention ratio.
3. **`items.collected_at` first-seen + preserved on re-upsert (was M-B).**
   Resolved. Lines 344-345: "`collected_at` is a first-seen timestamp: it is set
   on insert and preserved on re-upsert/update for an existing normalized URL."
   This is consistent with the existing URL-match update path in
   `upsert_item()` (repositories.py:43) and with the v2->v3 migration that
   defaults old rows to `published_at`. A preservation test is listed (lines
   477-481).
4. **Zero-current-mention entities not mislabeled `stable` (was M-C).** Resolved.
   Lines 427-429 omit entities with `current_mentions == 0` from the main ranked
   sections entirely; line 442 makes rule 6 (`stable`) a fallback "only for
   entities with `current_mentions > 0`." The off case from M-C (baseline
   mentions, zero current, baseline below the cooling minimum) is no longer
   labeled `stable` — it is excluded from ranked output.
5. **Tests planned for heat-score components and collected-at preservation.**
   Resolved. The TDD task at lines 499-502 writes failing tests for "the exact
   heat score formula components: weighted mention coefficient, scaled growth
   bonus, source-diversity bonus, and flat high-weight-source bonus." The task at
   lines 477-481 writes failing tests that `upsert_item()` "stores source weight
   and first-seen collected time, preserves collected time on re-upsert." The
   fixture-comparison task (lines 497-498) and the `as_of`/collected-at windowing
   task (lines 492-494) round out coverage.

## Findings

### Critical

None.

### Important

None.

### Minor

**M-1. `stable` rules 5 and 6 are redundant.** Decision-table rule 5 (`stable`
when `current_mentions >= stable_min_mentions`, default `1`) and rule 6
(`stable` fallback for `current_mentions > 0`) collapse to the same outcome once
zero-current entities are omitted from ranking. Harmless — both yield `stable` —
but the table would read more cleanly as a single fallback rule. Cosmetic; no
action required before implementation.

**M-2. Current-window boundary wording.** Line 354 describes the current window
as "inclusive of items with `collected_at > as_of - current_window_days`," which
uses a strict `>`. The operator is precise and the baseline window ("ending at
the start of the current window") does not overlap it, so behavior is
well-defined; only the word "inclusive" is slightly loose. Pick the exact
comparison in the windowing test (lines 492-494) so the boundary item lands
deterministically on one side.

## Recommendation

**Approved for Stage 4 implementation.** The two Minor items are cosmetic and can
be folded in during implementation or left as-is. The schema/migration,
persistence, config, windowing, mention-counting, scoring-formula, ranking, and
report-boundary work can all proceed as written.
