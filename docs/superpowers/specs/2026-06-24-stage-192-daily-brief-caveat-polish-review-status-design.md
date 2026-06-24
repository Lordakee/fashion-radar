# Stage 192 Daily Brief Caveat Polish And Review Status Design

## Objective

Resolve the remaining actionable Stage 191 review polish and update the
full-project review follow-up status so the repository accurately reflects
completed Stages 188-191 before the next product node begins.

## Background

Stage 191 added the deterministic Daily Brief Heat Narrative to generated daily
Markdown and JSON reports. Its opencode code review approved release with no
Critical or Important findings, but identified three optional Minor polish
items:

- source-health and recent-run caveat summaries interpolate raw error-message
  strings without a Daily Brief-specific cap;
- the source-caveats section can include duplicate entries for the same source
  when source health and a failed recent run both report that source;
- per-section empty Markdown fallback reuses the global all-empty message.

Separately, `docs/reviews/opencode-full-project-review.md` is a historical
full-project review whose follow-up section predates Stages 190 and 191. The
review should remain historical, but its follow-up status should not imply that
source-liveness diagnostics are still the next undone product node.

This stage is deliberately small. It fixes already-reviewed report quality
issues and stale planning status only; it does not add source acquisition,
platform/social connectors, scheduling, monitoring, demand proof, coverage
verification, or compliance-review functionality.

## Scope

In scope:

- Cap and normalize Daily Brief source caveat error-message fragments before
  including them in `DailyBriefItem.summary`.
- Reuse the existing report-safe snippet helper instead of adding a second
  truncation policy.
- Avoid duplicate Daily Brief source-caveat items for the same
  `(source_name, source_type)` when a source-health caveat already exists.
- Keep the all-empty Daily Brief Markdown fallback unchanged.
- Use a clearer per-section Markdown fallback when only one section is empty.
- Update `docs/reviews/opencode-full-project-review.md` follow-up status so it
  reflects that:
  - Stage 188 fixed proxy-sensitive tests and roadmap correction;
  - Stage 189 fixed review-capture hygiene;
  - Stage 190 added source-liveness diagnostics;
  - Stage 191 added Daily Brief Heat Narrative;
  - next product work should return to source coverage, matching quality, and
    trend/heat explanation.
- Add focused tests that reproduce the old behavior before production changes.
- Record opencode Stage 192 plan, code, and release review artifacts.

Out of scope:

- No new CLI command or flag.
- No new report JSON top-level field.
- No changes to `DailyBrief`, `DailyBriefSection`, or `DailyBriefItem` model
  shapes.
- No changes to `TrendDelta`, `TrendComparison`, `HeatMover`,
  `HeatMoversReport`, dashboard row projections, scoring formulas, candidate
  scoring formulas, or matching behavior.
- No new source acquisition, scraping, browser automation, platform APIs,
  monitoring, scheduling, connectors, social-platform search, demand proof,
  ranking, coverage verification, or compliance-review product feature.
- No LLM summarization.
- No change to source-health or collector-run persistence behavior.

## Architecture

The implementation stays inside the report renderer/builder layer:

```text
existing DailyReport rows
  -> build_daily_brief(...)
  -> source caveat item selection and summary formatting
  -> render_markdown_report(...)
```

The source-caveat de-duplication happens inside `_source_caveat_items(...)`.
It computes the keys of source-health rows that become Daily Brief caveats and
then only backfills failed recent runs whose `(source_name, source_type)` key is
not already represented.

The error-message cap happens inside the two Daily Brief caveat item helpers:

- `_brief_item_for_source_health(...)`
- `_brief_item_for_recent_run(...)`

Both helpers use `report_safe_snippet(...)` from
`fashion_radar.models.report`, preserving the existing report-wide snippet
policy of whitespace normalization plus `REPORT_SNIPPET_MAX_CHARS` capping.
If the helper returns `None`, the Daily Brief omits the `Last error:` sentence.

The Markdown fallback change is presentation-only. `_render_daily_brief(...)`
continues to return the existing global fallback when no sections contain
items, and uses `- No items in this section.` only for empty sections when at
least one other section has content.

The full-project review update is documentation/status correction only. It must
not rewrite the historical findings or reclassify previously fixed findings as
new work.

## Acceptance Criteria

- A Daily Brief source-health caveat with a long `last_error_message` includes a
  capped, normalized `Last error:` fragment and omits the long tail marker.
- A Daily Brief failed recent-run caveat with a long `error_message` includes a
  capped, normalized `Last error:` fragment and omits the long tail marker.
- If source health and a recent failed collector run refer to the same
  `(source_name, source_type)`, the Daily Brief source-caveats section contains
  one item for that source, while the existing `source_health` and
  `recent_runs` report sections remain unchanged.
- Empty sections inside a non-empty Daily Brief render
  `- No items in this section.`.
- A fully empty Daily Brief still renders `- No daily brief items available.`.
- `docs/reviews/opencode-full-project-review.md` follow-up status reflects
  Stages 188-191 as completed and names the next product priorities without
  claiming demand proof or platform coverage verification.
- Focused tests, lint, format check, release hygiene, and first-run smoke pass
  before commit.
