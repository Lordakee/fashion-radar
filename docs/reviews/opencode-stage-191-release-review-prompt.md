# Stage 191 Release Review Prompt

Do a release-readiness review for Stage 191. Use only the information in this
prompt; do not run commands or read files.

Stage goal:

- Add a deterministic Daily Brief / Heat Narrative to generated Markdown and
  JSON daily reports.
- Keep it local report-derived from tracked entities, candidate phrases, source
  health, and recent collector runs.
- Preserve boundaries: no new public CLI command or flag, no LLM/external API,
  no source acquisition, no social search, no compliance-review feature, no
  trend/heat/dashboard contract mutation, and no new write behavior outside
  existing report/run report-file writes.

Implementation files changed:

- `src/fashion_radar/models/report.py`
- `src/fashion_radar/reports.py`
- `src/fashion_radar/templates/daily_report.md`
- `tests/test_reports.py`
- `tests/test_cli.py`
- `tests/test_first_run_smoke.py`
- `scripts/check_first_run_smoke.py`
- `README.md`
- `docs/architecture.md`
- `docs/cli-reference.md`
- `docs/trend-deltas.md`
- `docs/daily-digest.md`
- `docs/github-upload-checklist.md`
- `tests/test_cli_docs.py`
- `tests/test_daily_digest_docs.py`
- `tests/test_trend_deltas_docs.py`
- `CHANGELOG.md`

Stage artifacts present:

- `docs/superpowers/specs/2026-06-24-stage-191-daily-brief-heat-narrative-design.md`
- `docs/superpowers/plans/2026-06-24-stage-191-daily-brief-heat-narrative-plan.md`
- `docs/reviews/opencode-stage-191-plan-review-prompt.md`
- `docs/reviews/opencode-stage-191-plan-review.md`
- `docs/reviews/opencode-stage-191-plan-rereview-prompt.md`
- `docs/reviews/opencode-stage-191-plan-rereview.md`
- `docs/reviews/opencode-stage-191-code-review-prompt.md`
- `docs/reviews/opencode-stage-191-code-review.md`

Code review result:

- Stage 191 code review found no Critical or Important issues and approved for
  release.
- It listed only optional Minor polish: unbounded caveat error strings that are
  consistent with existing report sections, possible duplicate source-caveat
  titles, and cosmetic empty-section fallback wording.

Release gate just completed:

```bash
ALL_PROXY=socks5h://127.0.0.1:9 HTTPS_PROXY=socks5h://127.0.0.1:9 HTTP_PROXY=socks5h://127.0.0.1:9 http_proxy=socks5h://127.0.0.1:9 uv --no-config run --frozen pytest -q
# 1435 passed

uv --no-config run --frozen python scripts/check_first_run_smoke.py --repo-root .
# First-run sample smoke passed.

uv --no-config run --frozen python scripts/check_release_hygiene.py --repo-root .
# Release hygiene checks passed.

uv --no-config run --frozen ruff check .
# All checks passed.

uv --no-config run --frozen ruff format --check .
# 146 files already formatted

env -u UV_DEFAULT_INDEX -u UV_INDEX_URL -u UV_EXTRA_INDEX_URL UV_NO_CONFIG=1 uv lock --check
# Resolved 84 packages

git diff --check
# no output

rg -n 'ghp_[A-Za-z0-9]+' .
# no output

git config --get-all http.https://github.com/.extraheader
# no output
```

Current uncommitted status contains exactly Stage 191 modified implementation,
docs, tests, and untracked Stage 191 spec/plan/review artifacts. No unrelated
files are intentionally included.

Questions:

1. Is the stage release-ready to commit and push?
2. Is the commit manifest complete for all Stage 191 files and review artifacts?
3. Are there any Critical or Important blockers before commit?
4. Is it acceptable to leave the code-review Minor items for later polish?

Return one coherent review body starting with:

```text
# Stage 191 Release Review
```

Use these sections exactly:

- Critical
- Important
- Minor
- Verdict
