# Stage 102 Scoring Docs Limits Design

## Goal

Add a standalone docs drift guard for the `## Limits` section in
`docs/scoring.md` so future edits keep scoring, candidate signals, and trend
deltas framed as local configured-source signals rather than platform-wide,
publication-time, media-analysis, external-engagement, or market-wide claims.

## Scope

Stage 102 is docs-test-only. It creates one focused pytest module that reads the
existing scoring documentation, extracts the `## Limits` section, normalizes
whitespace and case, and asserts scoring boundary phrases.

Allowed changes:

- `tests/test_scoring_docs.py`
- Stage 102 spec, plan, and review artifacts

Out of scope:

- `docs/scoring.md` source text
- scoring algorithms, candidate discovery behavior, trend delta behavior, report
  generation, dashboard behavior, CLI behavior, schemas, configs, dependencies,
  CI, or `uv.lock`
- social platform search, connector behavior, scraping, browser automation,
  scheduling, external services, compliance/audit/legal review features, or
  runtime validation

## Boundary Phrases

The guard should extract only `## Limits` and assert these phrases after
whitespace collapse and case-folding:

- `Scores only reflect configured sources and imported local signals.`
- `Candidate signals only reflect configured sources and imported local signals.`
- `Trend deltas only reflect configured sources and imported local signals.`
- `Candidate deltas are limited by configured candidate discovery thresholds.`
- `Counts use collected time, not necessarily publication time.`
- `Dashboard mention tabs show mention counts, while candidate signal views read the latest report JSON.`
- `There is no image/video or external engagement analysis in v0.1.0.`

These phrases pin scoring docs as local observed-signal documentation without
expanding into scoring implementation, dashboard implementation, source
acquisition, or platform coverage behavior.

## Test Shape

Use the same lightweight pattern as recent docs-boundary stages:

- stdlib-only imports
- repository root derived from `Path(__file__).resolve().parents[1]`
- helper to read `docs/scoring.md`
- helper to normalize whitespace and case
- helper to extract one Markdown `##` section
- one test function with a focused phrase loop

The test must not import application modules, execute scoring, run CLI commands,
read or write data/report files, fetch network resources, or write files.

## Verification

Focused verification should cover the new docs guard, adjacent scoring/trend
tests, ruff, formatting, and whitespace checks. Full verification before commit
should reuse the repository release gate: release hygiene, full pytest with
proxy vars unset, repo-wide ruff check and format check, lockfile check, mirror
URL scan, `uv.lock`/`pyproject.toml` diff guard, staged hygiene, and staged
secret scan.

## Risks

`docs/scoring.md` is referenced by broad CLI docs tests and runtime scoring
tests. This stage intentionally adds a narrower section-scoped docs guard rather
than changing scoring behavior.

The `## Limits` section contains dashboard wording, but Stage 102 should not
assert dashboard behavior outside this scoring limit sentence or modify
dashboard docs/tests.

The section is short, so phrase assertions may need deliberate updates if the
docs are rewritten. That is acceptable because the goal is to catch accidental
drift from local configured-source scoring boundaries.
