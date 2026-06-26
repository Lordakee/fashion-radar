# Stage 209 Code Review Prompt

Review the current working tree in `/home/ubuntu/fashion-radar` for Stage 209.

Goal: add local candidate score-component cues to generated Daily Brief
candidate summaries by reusing existing `CandidateReport` component fields,
without changing scoring, ranking, report schemas, source acquisition,
dashboard behavior, dependencies, or lockfiles.

Baseline:

- `HEAD` / `origin/main`: `55cc2c2ee44de2c7a6f7d39ec08cd991e6570b42`
- Stage 209 plan:
  `docs/superpowers/plans/2026-06-26-stage-209-daily-brief-candidate-component-cues-plan.md`
- Stage 209 second plan rereview says I-2 is resolved and no Critical or
  Important planning blockers remain.

Files changed in this stage:

- `src/fashion_radar/reports.py`
- `tests/test_reports.py`
- `tests/test_cli_docs.py`
- `README.md`
- `docs/architecture.md`
- `docs/cli-reference.md`
- `CHANGELOG.md`
- Stage 209 plan and OpenCode review artifacts under `docs/reviews/`

Review focus:

1. Report-summary-only scope:
   - no `DailyBriefItem`, `DailyBrief`, `CandidateReport`, or `CandidateMetric`
     model field changes
   - no `daily-brief/v1` contract version change
   - no scoring formula, ranking, extraction, thresholds, DB schema, dashboard,
     source acquisition, social/platform connector, scraping, dependency, or
     lockfile changes
2. Correct cue semantics:
   - Daily Brief candidate summaries include existing mention/growth/source
     diversity component values
   - formatting is two decimals and ordered `mentions`, `growth`, `sources`
   - candidate cues do not mention tracked-entity `high-weight`
   - tracked entity/source caveat brief summaries stay unchanged
3. Tests:
   - RED observed for JSON summary, Markdown Daily Brief subsection, direct
     `build_daily_brief(...)`, and docs cue guard before production/docs change
   - GREEN observed after implementation
   - Markdown assertion is scoped to `## Daily Brief` and the candidate
     subsection, not the existing full `## Untracked Candidate Signals` section
4. Docs/changelog:
   - language stays local observed / needs review
   - no demand proof, platform coverage, or social trend claims

Focused verification already run successfully:

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

uv --no-config run --frozen python scripts/check_release_hygiene.py --repo-root .
# Release hygiene checks passed
```

Return findings as Critical, Important, and Minor. If there are no Critical or
Important findings, say that clearly.
