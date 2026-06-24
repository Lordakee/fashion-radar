# Stage 191 Code Review Prompt

Do a narrow code review of the attached Stage 191 files. Do not run commands,
do not read additional files, and do not perform a full project review.

Stage goal:

- Add a deterministic Daily Brief / Heat Narrative to generated Markdown and
  JSON daily reports.
- Derive it from already-built local report-safe rows: tracked entity reports,
  candidate reports, source health, and recent collector runs.
- Preserve boundaries: no new public CLI command or flag, no LLM/external API,
  no source acquisition, no social search, no compliance-review feature, no
  trend/heat/dashboard contract mutation, and no new write behavior outside
  existing report/run report-file writes.

Files attached for review:

- report models, builder, renderer, and template;
- report/CLI/first-run smoke tests and validator;
- docs/docs-test files that guard the Daily Brief wording and no-new-command
  boundary.

Verification already run locally:

```bash
uv --no-config run --frozen pytest tests/test_reports.py -q
uv --no-config run --frozen pytest tests/test_cli.py -q
uv --no-config run --frozen pytest tests/test_cli_docs.py tests/test_daily_digest_docs.py tests/test_trend_deltas_docs.py tests/test_reports.py tests/test_first_run_smoke.py -q
uv --no-config run --frozen pytest tests/test_dashboard.py -q
uv --no-config run --frozen python scripts/check_first_run_smoke.py --repo-root .
uv --no-config run --frozen ruff check src/fashion_radar/models/report.py src/fashion_radar/reports.py tests/test_reports.py tests/test_cli.py tests/test_first_run_smoke.py scripts/check_first_run_smoke.py tests/test_cli_docs.py tests/test_daily_digest_docs.py tests/test_trend_deltas_docs.py
uv --no-config run --frozen ruff format --check src/fashion_radar/models/report.py src/fashion_radar/reports.py tests/test_reports.py tests/test_cli.py tests/test_first_run_smoke.py scripts/check_first_run_smoke.py tests/test_cli_docs.py tests/test_daily_digest_docs.py tests/test_trend_deltas_docs.py
git diff --check
```

Review questions:

1. Does the implementation satisfy the Stage 191 goal and boundaries?
2. Is the Daily Brief JSON/Markdown contract deterministic and report-safe?
3. Does it avoid leaking raw matcher/storage internals, full article content, or
   unbounded source snippets?
4. Are tests/docs aligned with the implemented behavior and no-new-command
   boundary?
5. Are there any Critical or Important issues that should block release?

Return one coherent review body starting with:

```text
# Stage 191 Code Review
```

Use these sections exactly:

- Critical
- Important
- Minor
- Verdict
