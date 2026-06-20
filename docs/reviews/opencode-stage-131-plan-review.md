# Stage 131 Plan Review

The design and plan are well-aligned, correctly scoped to docs/test-only parity, and consistent with the AGENTS.md scope boundaries. Verified against current state of `tests/test_cli_docs.py`, `CONTRIBUTING.md`, and `.github/pull_request_template.md`.

**Review focus responses:**

1. **Drift addressed without behavior changes.** The design correctly identifies that CI and the upload checklist require `check_release_hygiene.py` and `check_first_run_smoke.py`, while the two contributor surfaces omit them. Out-of-scope explicitly rules out CI, package, runtime, dependency, lockfile, README development-block, and all platform-collection behaviors.

2. **Focused docs test is specific.** The new `test_contributing_and_pr_template_include_release_hygiene_and_source_smoke` extracts the `Verification` section via `_markdown_section_exact_heading` from both files (not whole-file substring) and asserts each command is present. This catches a command missing from the Verification section even if it appears elsewhere in the file — a stronger guarantee than the canonical whole-file check. Both helpers (`_read`, `_markdown_section_exact_heading`) and constants (`CONTRIBUTING_DOC`, `PULL_REQUEST_TEMPLATE`) already exist in `tests/test_cli_docs.py:314-450`.

3. **Canonical test extension is surgical.** The plan extends only the two relevant surface tuples — release-hygiene gains `(contributing, pull_request_template)`, first-run-smoke gains `(contributing, pull_request_template)` — and leaves `check_package_archives.py`, `build --out-dir`, ruff/format/pytest, README, and first-run-doc surface tuples intact. The `stale_verification_commands` check (`tests/test_cli_docs.py:840-859`) is unaffected because the new commands use the `uv --no-config run --frozen` form, not the stale `UV_NO_CONFIG=1 uv run` form.

4. **Scope exclusions are complete.** Plan lines 39-43 enumerate every exclusion category called out in review-focus item 4 and match the AGENTS.md boundary list.

5. **Verification commands sufficient.** Both commands match the exact form used by CI and the upload checklist. Plan ordering (release hygiene and first-run smoke after lock/sync, before ruff/pytest) mirrors the existing release-gate ordering.

## Critical findings
None.

## Important findings
None.

## Minor findings
None.

## Blocker statement
There are **no Critical or Important blockers** before implementation. The plan may proceed to Task 1 (RED tests).
