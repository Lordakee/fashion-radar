# Stage 205 Release Review Prompt

Review Stage 205 final release readiness.

Goal: release a read-only dashboard/report transparency stage that carries
candidate score components from latest report JSON into the dashboard Candidate
Signals table with legacy-report defaults.

Changed files expected in this stage:

- `src/fashion_radar/dashboard/queries.py`
- `tests/test_dashboard.py`
- `docs/dashboard.md`
- `tests/test_dashboard_docs.py`
- `CHANGELOG.md`
- `docs/superpowers/plans/2026-06-25-stage-205-dashboard-candidate-score-parity-plan.md`
- `docs/reviews/opencode-stage-205-plan-review-prompt.md`
- `docs/reviews/opencode-stage-205-plan-review.md`
- `docs/reviews/opencode-stage-205-code-review-prompt.md`
- `docs/reviews/opencode-stage-205-code-review.md`
- `docs/reviews/opencode-stage-205-release-review-prompt.md`

Verification to consider for this release review:

```bash
uv --no-config run --frozen pytest tests/test_dashboard.py tests/test_dashboard_docs.py -q
uv --no-config run --frozen ruff check src/fashion_radar/dashboard/queries.py tests/test_dashboard.py docs/dashboard.md tests/test_dashboard_docs.py CHANGELOG.md docs/superpowers/plans/2026-06-25-stage-205-dashboard-candidate-score-parity-plan.md docs/reviews/opencode-stage-205-plan-review.md docs/reviews/opencode-stage-205-plan-review-prompt.md docs/reviews/opencode-stage-205-code-review.md docs/reviews/opencode-stage-205-code-review-prompt.md
uv --no-config run --frozen ruff format --check src/fashion_radar/dashboard/queries.py tests/test_dashboard.py tests/test_dashboard_docs.py
uv --no-config run --frozen python scripts/check_release_hygiene.py --repo-root .
env -u UV_DEFAULT_INDEX -u UV_INDEX_URL -u UV_EXTRA_INDEX_URL UV_NO_CONFIG=1 uv lock --check
git diff --check
uv --no-config run --frozen pytest
uv --no-config run --frozen ruff check .
uv --no-config run --frozen ruff format --check .
UV_NO_CONFIG=1 uv sync --locked --dev --check
uv --no-config run --frozen python scripts/check_first_run_smoke.py --repo-root .
git diff --exit-code -- uv.lock pyproject.toml
```

Important expected results:

- Focused dashboard tests pass.
- Full pytest passes.
- Full ruff check and format check pass.
- Release hygiene passes with clean OpenCode review artifacts.
- Config-isolated `uv lock --check` and `uv sync --locked --dev --check` pass.
- `uv.lock` and `pyproject.toml` have no diff.

Please review:

1. Are the implementation, tests, docs, changelog, and review artifacts ready
   to commit and push?
2. Does release hygiene pass on the current working tree, including all Stage
   205 review artifacts?
3. Is the verification set sufficient for a dashboard/report transparency
   parity stage?
4. Does the stage avoid report generation, scoring, database schema, dashboard
   writes, source acquisition, connectors, scraping, demand proof, platform
   coverage verification, dependency changes, and compliance-review behavior?
5. Is the current git status limited to expected Stage 205 files?

Return findings as Critical, Important, and Minor. If there are no Critical or
Important findings, say that clearly.
