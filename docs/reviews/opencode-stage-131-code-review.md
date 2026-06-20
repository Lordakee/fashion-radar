# Stage 131 Code Review

## Implementation vs. design/plan

The implementation matches the Stage 131 design and plan exactly:

- **New focused test** `test_contributing_and_pr_template_include_release_hygiene_and_source_smoke` at `tests/test_cli_docs.py:728` extracts the `Verification` section via `_markdown_section_exact_heading` from both `CONTRIBUTING.md` and `.github/pull_request_template.md` (stronger than whole-file substring, since it would catch a command present elsewhere but missing from the Verification section) and asserts both `check_release_hygiene.py --repo-root .` and `check_first_run_smoke.py --repo-root .` are present.
- **Canonical test** `test_github_verification_surfaces_use_no_config_frozen_uv_run` at `tests/test_cli_docs.py:809` was extended surgically:
  - `check_release_hygiene.py` surfaces: `(ci_workflow, checklist)` → `(ci_workflow, contributing, pull_request_template, checklist)`.
  - `check_first_run_smoke.py` surfaces: `(ci_workflow, checklist, readme, first_run_doc)` → `(ci_workflow, contributing, pull_request_template, checklist, readme, first_run_doc)`.
  - All other surface tuples (package archives, `build --out-dir`, generic ruff/format/pytest, isolated lock/sync, stale-command block) are unchanged.
- **CONTRIBUTING.md** `Verification` block (lines 58–59) adds both commands after the lock/sync checks and before ruff/pytest, matching the existing release-gate ordering.
- **`.github/pull_request_template.md`** `Verification` checklist (lines 53–54) adds both commands before the conditional packaging/dashboard bullets, matching the plan.

## Contributor-facing surfaces

Both `CONTRIBUTING.md` and `.github/pull_request_template.md` now include:
- `uv --no-config run --frozen python scripts/check_release_hygiene.py --repo-root .`
- `uv --no-config run --frozen python scripts/check_first_run_smoke.py --repo-root .`

inside their `## Verification` sections, matching the exact form used in CI (`.github/workflows/ci.yml:26,28`) and the upload checklist (`docs/github-upload-checklist.md:355,363`).

## Scope boundary

Tracked-file diff is limited to the three planned files: `tests/test_cli_docs.py`, `CONTRIBUTING.md`, `.github/pull_request_template.md` (+30/-2 lines). No changes to `README.md`, `pyproject.toml`, `uv.lock`, `.github/workflows/ci.yml`, runtime/product code, or any connector/scrape/platform surface. README development block was not expanded; it retains only first-run-smoke, as before.

## Verification performed

- Focused tests pass: `test_contributing_and_pr_template_include_release_hygiene_and_source_smoke` and `test_github_verification_surfaces_use_no_config_frozen_uv_run` (2 passed).
- Full module: `pytest tests/test_cli_docs.py -q` → 66 passed.
- `ruff check` and `ruff format --check` on the modified test file: clean.
- `git diff --check`: clean.

## Critical findings
None.

## Important findings
None.

## Minor findings
None.

## Blocker statement
There are **no Critical or Important blockers** before release. The stage is docs/test-only, the two contributor-facing verification surfaces are now aligned with CI and the upload checklist, the canonical test was extended correctly while preserving existing expectations, and all scope exclusions called out in the design are respected.
