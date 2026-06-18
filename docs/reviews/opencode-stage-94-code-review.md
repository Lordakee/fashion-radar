I'll review the Stage 94 implementation. Let me start by reading all the relevant files in parallel.
Now let me read the review artifacts and the dashboard doc to verify the assertions actually match the doc content.
Let me verify the implementation actually passes and check the git scope.
Let me confirm the combined test run and verify scope independence.
All verification passes. Here are my findings.

# Stage 94 Code Review Findings

## Critical
None.

## Important
None.

## Verification Confirmed
- `pytest tests/test_dashboard_docs.py -q` → 3 passed
- `pytest tests/test_dashboard.py tests/test_dashboard_docs.py -q` → 38 passed
- `ruff check` / `ruff format --check` → clean
- `git diff --check` → clean
- Scope (`git status`): only `tests/test_dashboard_docs.py` + Stage 94 spec/plan/review artifacts are untracked. No `docs/dashboard.md`, `src/`, schemas, `uv.lock`, CI, `tests/test_cli_docs.py`, or runtime dashboard test changes.

## Review Question Answers

**1. Does the implementation match the reviewed/re-reviewed plan and scope?**
Yes. `tests/test_dashboard_docs.py` matches the plan Task 2 code exactly, including the post-C1 fix (the invalid `"do not initialize schema, migrate a database, create trend tables"` phrase is gone; only the four valid trend phrases remain at `tests/test_dashboard_docs.py:34-39`). Scope is test-only and clean.

**2. Are the docs assertions present, stable enough, and limited to dashboard boundaries?**
Yes. I traced all 16 assertions through the exact `_normalized` logic (`" ".join(text.split()).casefold()`) against `docs/dashboard.md` — all match:
- Local inspection (`tests/test_dashboard_docs.py:20-27`) → `docs/dashboard.md:3-4, 28, 30-33`
- Trend read-only (`:34-39`) → `docs/dashboard.md:38-39, 42-43`
- Local security (`:46-53`) → `docs/dashboard.md:27, 55-56, 60, 62`

Backtick literals (`` `127.0.0.1:8501` ``, `` `--host 0.0.0.0` ``) survive normalization, and `casefold` correctly maps "APIs" → "apis" (`:51`). Phrases are sentence-specific boundary statements, not overly broad.

**3. Is the new standalone test independent?**
Yes. Imports limited to `from __future__ import annotations` and `from pathlib import Path` (`tests/test_dashboard_docs.py:1, 3`) — no Streamlit, dashboard, app, or SQLite imports, satisfying the design constraint. The function `test_dashboard_docs_current_tab_order_matches_app_labels` in `tests/test_cli_docs.py:614` lives in a different module with a distinct name, so there is no pytest collection collision and no fixture coupling.

**4. Critical/Important blockers before final verification, commit, push?**
None. Implementation may proceed to Task 4 (full verification, commit, push).

## Minor (Non-blocking)
- The doc is read three times (once per test) rather than via a module-scoped fixture. Negligible for a small markdown file and consistent with prior stage docs-guard patterns.
- `UV_NO_CONFIG=1 uv lock --check` and the mirror-leak `rg` guard in Task 4 will validate `uv.lock` integrity, but Stage 94 makes no manifest changes so no risk is introduced.

No Critical or Important blockers. Proceed to full verification and commit.
