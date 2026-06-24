# Stage 191 Plan Review Prompt

Review the Stage 191 design and implementation plan for Fashion Radar.

Files to inspect:

- `docs/superpowers/specs/2026-06-24-stage-191-daily-brief-heat-narrative-design.md`
- `docs/superpowers/plans/2026-06-24-stage-191-daily-brief-heat-narrative-plan.md`
- Existing report pipeline:
  - `src/fashion_radar/models/report.py`
  - `src/fashion_radar/reports.py`
  - `src/fashion_radar/templates/daily_report.md`
  - `tests/test_reports.py`
  - `tests/test_cli.py`
  - `tests/test_first_run_smoke.py`
  - `scripts/check_first_run_smoke.py`
- Docs/test guardrails:
  - `README.md`
  - `docs/architecture.md`
  - `docs/cli-reference.md`
  - `docs/daily-digest.md`
  - `docs/github-upload-checklist.md`
  - `tests/test_cli_docs.py`
  - `tests/test_daily_digest_docs.py`
  - `docs/REVIEW_PROTOCOL.md`

Questions:

1. Is the Stage 191 product direction coherent after the full-project review,
   Stage 188 roadmap correction, Stage 189 review hygiene, and Stage 190
   source-liveness diagnostics?
2. Is adding a report-level `brief` field to `DailyReport` the right bounded
   contract change, or does the plan understate compatibility risks?
3. Are the proposed Pydantic models, key order, default factory, deterministic
   section ordering, reason codes, and Markdown rendering testable and
   technically sound?
4. Does the plan avoid forbidden scope: no new CLI command, no scraping, no
   browser automation, no platform APIs, no social search implementation, no
   compliance-review product feature, no LLM summarization, no trend/heat JSON
   contract mutation, and no dashboard row projection change?
5. Are the TDD steps concrete enough to implement without guessing, and do they
   run RED before production changes?
6. Are docs, docs tests, first-run smoke, release gate, review artifacts, and
   `git add` manifest complete and accurate?
7. Do any planned commands risk the known Markdown formatting pitfall with
   `ruff format --check`?

Return one coherent review body starting with:

```text
# Stage 191 Plan Review
```

Use severity sections:

- Critical
- Important
- Minor

End with a verdict: approved, approved with non-blocking minors, or not approved.
