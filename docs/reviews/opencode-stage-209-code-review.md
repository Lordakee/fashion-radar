## Stage 209 Code Review — Findings

I reviewed the working tree against baseline `55cc2c2` and re-ran fresh verification.

### Verification re-run (all green)
- 4 focused tests: 4 passed
- Broader suites (`test_reports`, `test_cli_docs`, `test_candidate_discovery_docs`, `test_scoring_docs`, `test_daily_digest_docs`): 107 passed
- Full suite: **1517 passed**
- `ruff check` (src + docs): All checks passed
- `ruff format --check`: 3 files already formatted
- `check_release_hygiene.py`: passed

### Scope confirmed (review focus 1)
- `src/fashion_radar/reports.py` is the **only** source file changed. `git diff --stat` against baseline is empty for `models/report.py`, `scoring.py`, `discovery/*`, `dashboard/*`, `pyproject.toml`, `uv.lock`, and every other `src/**/*.py`.
- `CandidateReport.weighted_mention_component/growth_component/source_diversity_component` (models/report.py:97-99) are **pre-existing** fields; `_candidate_component_summary` (reports.py:304) only reads them.
- `contract_version` stays `"daily-brief/v1"` (models/report.py:191, untouched). No new `DailyBriefItem` field — the cue is appended to the free-text `summary`, and the new test asserts `not hasattr(candidate_item, "weighted_mention_component")`.

### Semantics confirmed (review focus 2)
- Cue is ordered `mentions → growth → sources`, two decimals (`:.2f`), and only emitted for candidate brief items (`_brief_item_for_candidate` at reports.py:293). `_brief_item_for_entity` (256) and `_source_caveat_items` (313) are untouched, so tracked-entity and source-caveat brief summaries are unchanged.
- Candidate cue contains no `high-weight` term (that remains only in tracked-entity main-body sections, reports.py:641).
- The Markdown negative assertion `high-weight not in candidate_brief` is correctly scoped to the `## Daily Brief` → `### Candidate Signals Needing Review` slice (test_reports.py:449-457), so it is not falsely tripped by the entity `high-weight` line elsewhere.

### Tests confirmed (review focus 3)
- RED-before is inherent: the JSON/Markdown tests assert `"Score components:"` and the docs test asserts `"candidate score-component cues"` — strings that only exist after this stage. GREEN verified post-change.
- Markdown assertion is scoped via `split("## Daily Brief")` / `split("## Top Signals")` / `split("### Candidate Signals Needing Review")` / `split("### Source Caveats")`, not the full `## Untracked Candidate Signals` body.
- The pre-existing main-body assertions at test_reports.py:594 and :976 remain valid (976 now matches in two places, but it's a substring `in markdown` check, so still correct).

### Docs/changelog confirmed (review focus 4)
- README, architecture.md, cli-reference.md all retain "provides no demand proof and no platform coverage verification" and local-observed/needs-review language; the added phrasing is limited to score-component *cues*. CHANGELOG entry is a scope statement, not a demand-proof/coverage claim.

---

**Critical:** None.
**Important:** None.

**Minor:**
1. `test_daily_report_includes_stable_daily_brief_json_shape` (test_reports.py:329-334) now pins exact default-scoring component values (`mentions 2.00; growth 0.00; sources 1.00`) in a test named for *shape stability*. This couples a structural-shape test to specific `ScoringSettings` outputs, so a future default weight/bonus change would fail it even with an unchanged brief shape. Consider hoisting those value assertions into the dedicated `test_daily_brief_candidate_summary_includes_existing_score_components` test and leaving the "stable shape" test asserting only keys/structure. Not a blocker — the values legitimately reflect real discovery scoring.

No Critical or Important findings; Stage 209 is safe to proceed.
