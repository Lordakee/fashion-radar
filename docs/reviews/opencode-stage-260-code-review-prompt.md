# opencode Stage 260 Code Review Prompt

You are the fallback read-only code reviewer for Fashion Radar Stage 260 because
the local primary review route did not return a completed review.

Repository: `/home/ubuntu/fashion-radar`
Base commit: `7e56afe9837899cac98be057231872ad246052ac`
Current commit: `7e56afe9837899cac98be057231872ad246052ac`
Head/worktree: uncommitted Stage 260 working-tree diff from the base commit
Stage: `260`
Spec: `docs/superpowers/specs/2026-07-02-row-one-daily-site-design.md`
Plan: `docs/superpowers/plans/2026-07-02-stage-260-row-one-daily-site-plan.md`

Review only the Stage 260 ROW ONE implementation and docs changes. Do not edit
files. Focus on correctness, requirement fit, release readiness, and regressions.

Stage 260 goal:

- Add ROW ONE, a local professional fashion-news static site generator.
- Build from existing Fashion Radar daily report/state data only.
- Provide `row-one build`, `row-one serve`, and `row-one schedule`.
- Generate static HTML/CSS/JS/detail pages/JSON under `reports/row-one/site`.
- Support deterministic bilingual UI/fallback copy without translation services
  or LLM calls.
- Support local `127.0.0.1` serving and explicit `0.0.0.0` IP:port LAN serving
  guidance.
- Support daily 04:00 scheduling snippets where `fashion-radar run` refreshes
  local data first, then `fashion-radar row-one build --latest-only` rebuilds
  the site with the same timestamp and same env.
- Keep cleanup bounded to known generated ROW ONE children.
- Keep non-ASCII and long headlines safe for static detail filenames and served
  detail URLs.
- Do not add new scraping, source acquisition, platform connectors, paid APIs,
  deployment, demand proof, platform coverage verification, or compliance-review
  product features.

Changed/new files to inspect:

- `src/fashion_radar/row_one/__init__.py`
- `src/fashion_radar/row_one/models.py`
- `src/fashion_radar/row_one/edition.py`
- `src/fashion_radar/row_one/templates.py`
- `src/fashion_radar/row_one/render.py`
- `src/fashion_radar/row_one/server.py`
- `src/fashion_radar/workflows.py`
- `src/fashion_radar/cli.py`
- `src/fashion_radar/scheduling.py`
- `tests/test_row_one_edition.py`
- `tests/test_row_one_render.py`
- `tests/test_row_one_cli.py`
- `tests/test_row_one_docs.py`
- `tests/test_scheduling.py`
- `docs/row-one.md`
- `README.md`
- `docs/architecture.md`
- `docs/cli-reference.md`
- `docs/scheduling.md`
- `docs/github-upload-checklist.md`
- `docs/superpowers/specs/2026-07-02-row-one-daily-site-design.md`
- `docs/superpowers/plans/2026-07-02-stage-260-row-one-daily-site-plan.md`
- Stage 260 review artifacts under `docs/reviews/`

Current `git status --porcelain=v1 -uall` snapshot before review:

```text
 M README.md
 M docs/architecture.md
 M docs/cli-reference.md
 M docs/github-upload-checklist.md
 M docs/scheduling.md
 M src/fashion_radar/cli.py
 M src/fashion_radar/scheduling.py
 M src/fashion_radar/workflows.py
 M tests/test_scheduling.py
?? docs/reviews/opencode-stage-260-code-review-prompt.md
?? docs/reviews/opencode-stage-260-plan-review-prompt.md
?? docs/reviews/opencode-stage-260-plan-review.md
?? docs/row-one.md
?? docs/superpowers/plans/2026-07-02-stage-260-row-one-daily-site-plan.md
?? docs/superpowers/specs/2026-07-02-row-one-daily-site-design.md
?? src/fashion_radar/row_one/__init__.py
?? src/fashion_radar/row_one/edition.py
?? src/fashion_radar/row_one/models.py
?? src/fashion_radar/row_one/render.py
?? src/fashion_radar/row_one/server.py
?? src/fashion_radar/row_one/templates.py
?? tests/test_row_one_cli.py
?? tests/test_row_one_docs.py
?? tests/test_row_one_edition.py
?? tests/test_row_one_render.py
```

Fresh verification already run before this review:

```bash
git diff --check
uv --no-config run --frozen pytest -q
uv --no-config run --frozen ruff check .
uv --no-config run --frozen ruff format --check .
UV_NO_CONFIG=1 uv lock --check
uv --no-config run --frozen python scripts/check_release_hygiene.py --repo-root .
```

Observed results:

- `git diff --check`: passed
- `pytest -q`: `1665 passed`
- `ruff check .`: passed
- `ruff format --check .`: `172 files already formatted`
- `UV_NO_CONFIG=1 uv lock --check`: passed
- `scripts/check_release_hygiene.py --repo-root .`: `Release hygiene checks passed.`

Please produce:

1. Verdict: Accept, Accept with fixes, or Reject.
2. Findings grouped as Critical, Important, Minor.
3. For each finding, cite file and line number.
4. Confirm whether the implementation stays inside the Stage 260 boundary.
5. Confirm whether the current verification is sufficient for this node.

Be strict about Critical and Important issues. Avoid broad future-feature
requests; keep findings scoped to this Stage 260 node.
