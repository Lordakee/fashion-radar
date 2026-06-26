# Stage 209 Release Review Prompt

Review the current working tree in `/home/ubuntu/fashion-radar` for Stage 209
before commit and GitHub push.

Goal: add local candidate score-component cues to generated Daily Brief
candidate summaries by reusing existing `CandidateReport` component fields,
without changing scoring, ranking, report schemas, source acquisition,
dashboard behavior, dependencies, lockfiles, social connectors, or platform
coverage behavior.

Baseline:

- `HEAD` / `origin/main`: `55cc2c2ee44de2c7a6f7d39ec08cd991e6570b42`
- Stage 209 plan:
  `docs/superpowers/plans/2026-06-26-stage-209-daily-brief-candidate-component-cues-plan.md`
- Stage 209 plan rereview says no Critical or Important planning blockers
  remain.
- Stage 209 code rereview says no Critical, Important, or Minor code findings
  remain.

Files changed in this stage:

- `src/fashion_radar/reports.py`
- `tests/test_reports.py`
- `tests/test_cli_docs.py`
- `README.md`
- `docs/architecture.md`
- `docs/cli-reference.md`
- `CHANGELOG.md`
- Stage 209 plan and OpenCode review artifacts under `docs/reviews/`
- Stage 209 plan artifact under `docs/superpowers/plans/`

Scope assertions to verify:

1. Summary-only Daily Brief change:
   - candidate Daily Brief summaries append:
     `Score components: mentions N.NN; growth N.NN; sources N.NN.`
   - implementation reuses existing
     `CandidateReport.weighted_mention_component`,
     `CandidateReport.growth_component`, and
     `CandidateReport.source_diversity_component`
   - no new `DailyBriefItem`, `DailyBrief`, `CandidateReport`, or
     `CandidateMetric` fields
   - no `daily-brief/v1` contract version change
2. No behavior outside report explanation:
   - no scoring formula, ranking, candidate extraction, thresholds, DB schema,
     migration, dashboard, source acquisition, source config, collector,
     HTTP/proxy, dependency, package, or lockfile changes
   - no social/platform connectors, scraping, browser automation, login/cookie
     behavior, monitoring, scheduling, demand proof, or platform coverage
     verification
3. Tests and docs:
   - JSON Daily Brief candidate summary includes component cue while preserving
     stable shape
   - Markdown assertion is scoped to the Daily Brief candidate subsection, not
     the full untracked-candidate section
   - direct `build_daily_brief(...)` test pins explicit component formatting and
     summary-only behavior
   - docs/changelog describe local candidate score-component cues without
     implying demand proof or platform coverage

Completed review gates:

- Plan review found an Important issue around Markdown false positives; the
  plan was fixed to slice the Daily Brief candidate subsection.
- Plan rereview found an Important docs-guard issue; the plan was fixed to use
  `_normalized_doc_text(path).casefold()` with exact docs phrases.
- Second plan rereview found no Critical or Important blockers.
- Code review found no Critical or Important findings and one Minor test
  over-pinning concern.
- Code rereview verified the Minor was resolved and found no Critical,
  Important, or Minor findings.

Verification evidence already run successfully:

```text
uv --no-config run --frozen pytest \
  tests/test_reports.py::test_daily_report_includes_stable_daily_brief_json_shape \
  tests/test_reports.py::test_markdown_report_renders_daily_brief_before_top_signals \
  tests/test_reports.py::test_daily_brief_candidate_summary_includes_existing_score_components \
  tests/test_cli_docs.py::test_daily_brief_docs_describe_candidate_score_component_cues \
  -q
# RED before production/docs changes: 4 failed
# GREEN after implementation/docs changes: 4 passed

uv --no-config run --frozen pytest tests/test_reports.py tests/test_cli_docs.py tests/test_candidate_discovery_docs.py tests/test_scoring_docs.py tests/test_daily_digest_docs.py -q
# 107 passed

uv --no-config run --frozen ruff check src/fashion_radar/reports.py tests/test_reports.py tests/test_cli_docs.py README.md docs/architecture.md docs/cli-reference.md CHANGELOG.md
# All checks passed

uv --no-config run --frozen ruff format --check src/fashion_radar/reports.py tests/test_reports.py tests/test_cli_docs.py
# 3 files already formatted

uv --no-config run --frozen pytest
# 1517 passed

uv --no-config run --frozen ruff check .
# passed

uv --no-config run --frozen ruff format --check .
# 148 files already formatted

uv --no-config run --frozen python scripts/check_release_hygiene.py --repo-root .
# passed

env -u UV_DEFAULT_INDEX -u UV_INDEX_URL -u UV_EXTRA_INDEX_URL UV_NO_CONFIG=1 uv lock --check
# Resolved 85 packages

UV_NO_CONFIG=1 uv sync --locked --dev --check
# Would make no changes

uv --no-config run --frozen python scripts/check_first_run_smoke.py --repo-root .
# First-run sample smoke passed

git diff --exit-code -- uv.lock pyproject.toml
# clean

git diff --check
# clean
```

Return findings grouped as Critical, Important, and Minor. If there are no
Critical or Important findings, say that clearly. Also call out any release
hygiene risk that should block commit or push.
