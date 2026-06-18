# Stage 105 Trend Deltas What Is Compared Docs Design

## Goal

Add a standalone docs drift guard for the `## What Is Compared` section in
`docs/trend-deltas.md` so future edits keep the trend-delta comparison boundary
explicit: entity deltas reuse local heat scoring, candidate deltas reuse
candidate discovery snapshots and configured thresholds, mention fields compare
current-window counts across snapshots, internal baseline-window counts stay
separate, and trend statuses are local observed review signals rather than
market-wide rankings.

## Scope

Stage 105 is docs-test-only. It creates one focused pytest module that reads the
existing trend-deltas documentation, extracts the `## What Is Compared` section,
normalizes whitespace and case, and asserts comparison-boundary phrases.

Allowed changes:

- `tests/test_trend_deltas_docs.py`
- Stage 105 spec, plan, and review artifacts

Out of scope:

- `docs/trend-deltas.md` source text
- `src/`, `scripts/`, `examples/`, configs, schemas, dependencies, CI,
  `uv.lock`, package metadata, release hygiene, dashboard behavior, report
  generation, CLI behavior, database schema, scoring logic, candidate discovery
  logic, local heat mover behavior, source acquisition, connector behavior,
  social/platform scraping, browser automation, account/session/cookie/proxy
  handling, scheduling, monitoring, coverage verification, or ranking behavior
- compliance/audit/legal review product features

## Boundary Phrases

The guard should extract only `## What Is Compared` and assert these phrases
after whitespace collapse and case-folding:

- `Entity deltas reuse the same local heat scoring used by reports.`
- `Candidate deltas reuse candidate discovery snapshots.`
- `configured `candidate_discovery` settings`
- `not a complete raw phrase inventory.`
- `` `current_mentions` is the current comparison snapshot's current-window mention count. ``
- `` `baseline_mentions` is the baseline comparison snapshot's current-window mention count. ``
- `` Scoring's internal baseline-window counts are exposed only as `current_internal_baseline_mentions` and `baseline_internal_baseline_mentions`. ``
- `` Existing signals are labeled `rising` or `cooling` only when score and mention movement agree. ``
- `` Mixed-direction movement is `stable`. ``
- `These statuses are local observed signals for review, not market-wide rankings.`

These phrases pin the public explanation of what trend deltas compare without
expanding into runtime scoring, source collection, platform monitoring, or
market-ranking features.

## Test Shape

Use the same lightweight pattern as recent docs-boundary stages:

- stdlib-only imports
- repository root derived from `Path(__file__).resolve().parents[1]`
- helper to read `docs/trend-deltas.md`
- helper to normalize whitespace and case
- helper to extract one Markdown `##` section
- one test function with a focused phrase loop

The test must not import application modules, execute CLI commands, open
SQLite, read or write data/report files, fetch network resources, run matching
or scoring, or write files.

## Verification

Focused verification should cover the new docs guard and the existing CLI docs
test module that references `docs/trend-deltas.md`, then ruff, formatting, and
whitespace checks. Full verification before commit should reuse the repository
release gate: release hygiene, full pytest with proxy vars unset, repo-wide ruff
check and format check, lockfile check, mirror URL scan, `uv.lock`/
`pyproject.toml` diff guard, staged hygiene, and staged secret scan.

## Risks

`docs/trend-deltas.md` also documents CLI usage, manual signals, and dashboard
behavior. Stage 105 deliberately scopes to `## What Is Compared` only so the
guard does not duplicate command examples, dashboard read-only constraints,
or broader source-boundary docs.

Phrase assertions may need deliberate updates if the comparison wording is
rewritten. That is acceptable because the goal is to catch accidental drift from
the local-observed comparison boundary.
