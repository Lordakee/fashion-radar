# Claude Code Stage 262 Release Review Prompt

You are the primary release reviewer for Fashion Radar Stage 262.

Repo: `/home/ubuntu/fashion-radar`

This is a read-only final release review. Do not edit files.

Review the current Stage 262 implementation and release artifacts:

- `git status --short --branch`
- current diff and untracked Stage 262 files
- `docs/row-one.md`
- `src/fashion_radar/row_one/templates.py`
- `tests/test_row_one_cli.py`
- `tests/test_row_one_docs.py`
- `tests/test_row_one_render.py`
- `docs/superpowers/specs/2026-07-02-stage-262-row-one-reader-orientation-design.md`
- `docs/superpowers/plans/2026-07-02-stage-262-row-one-reader-orientation-plan.md`
- `docs/reviews/claude-code-stage-262-plan-review.md`
- `docs/reviews/claude-code-stage-262-plan-rereview.md`
- `docs/reviews/claude-code-stage-262-plan-final-review.md`
- `docs/reviews/claude-code-stage-262-code-review-prompt.md`
- `docs/reviews/opencode-stage-262-code-review.md`
- `docs/REVIEW_PROTOCOL.md`
- `AGENTS.md`

## Objective

Stage 262 adds a deterministic reader-orientation layer to ROW ONE:

- homepage edition contents;
- section jump links;
- current story counts;
- story-card orientation metadata;
- detail-page back-to-section links;
- documentation and tests for the presentation-only boundary.

## Full Verification Already Run

The full release gate has passed:

```bash
git status --short --branch
UV_NO_CONFIG=1 uv lock --check
UV_NO_CONFIG=1 uv sync --locked --dev
UV_NO_CONFIG=1 uv sync --locked --dev --check
git diff --check
uv --no-config run --frozen ruff check .
uv --no-config run --frozen ruff format --check .
uv --no-config run --frozen pytest -q
rm -rf dist build
uv --no-config build
uv --no-config run --frozen python scripts/check_package_archives.py dist
uv --no-config run --frozen python scripts/check_first_run_smoke.py
rm -rf dist build
uv --no-config run --frozen python scripts/check_release_hygiene.py --repo-root .
git status --short --branch
```

Results included:

- `1685 passed`
- `All checks passed!`
- `172 files already formatted`
- `Package archives contain required files.`
- `First-run sample smoke passed.`
- `Release hygiene checks passed.`

## Review Focus

Please check:

- release boundaries in `AGENTS.md` and `docs/REVIEW_PROTOCOL.md`;
- no secrets, cookies, tokens, private data, generated reports, SQLite sidecars,
  build artifacts, or CodeGraph DB files are staged or intended for commit;
- review records are coherent enough to commit;
- package/archive/first-run/release hygiene gates are appropriate and complete;
- Stage 262 is ready for commit and push to `origin/main`.

## Output Format

Return one coherent review body only:

- Verdict: accept / accept with fixes / reject
- Critical findings
- Important findings
- Minor findings
- Notes
- State whether Stage 262 is acceptable to push.

Use file and line references where possible. Do not modify files.
