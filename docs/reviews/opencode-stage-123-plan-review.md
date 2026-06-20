# Stage 123 Plan Review

## Critical findings
None.

## Important findings
None. The plan is internally consistent, complete, and the TDD is valid. Detailed verification below.

**RED validity (confirmed):** Against the current tree, the updated `test_package_archive_smoke_command_is_documented_and_in_ci` and `test_first_run_smoke_command_is_documented_and_in_ci` now assert the `uv --no-config run --frozen …` / `uv --no-config build …` forms, which are absent in ci.yml:26-41, README.md:325/335/875-877, first-run.md:128/146, and github-upload-checklist.md:355/363/379/380 → fail. The new `test_github_verification_surfaces_use_no_config_frozen_uv_run` additionally fails on both the frozen-absent and stale-present (`uv run pytest`, `UV_NO_CONFIG=1 uv build …`) assertions → fail.

**GREEN validity (confirmed cell-by-cell):** Every required command/surface pair in the new test is produced by an explicit plan step (ci.yml 7 lines, README Development + smoke, CONTRIBUTING Verification, PR template checklist, upload Before Upload + Package Smoke, first-run smoke/build). Every stale form is removed from all 6 scanned surfaces. The preservation assertions (`uv run fashion-radar init`/`dashboard` in CONTRIBUTING) already hold and are untouched. No other test asserts these doc command strings (only `tests/test_cli_docs.py`, which Task 1 Step 2 updates); no `scripts/` or other `tests/` reference them.

**Scope (confirmed clean):** Only docs + CI YAML + a docs-drift test. No `src/`, `pyproject.toml`, `uv.lock`, runtime, CLI, dependency, connector, scraping, browser-automation, platform-API, monitoring, scheduling, source-acquisition, demand-proof, ranking, coverage-verification, or compliance/audit behavior.

**Drift addressed without touching local workflow:** `uv run fashion-radar …` examples, mirror installs (`UV_DEFAULT_INDEX=… uv sync --frozen`), `UV_NO_CONFIG=1 uv lock --check` / `uv sync --locked --dev` isolation commands, and the README `uv sync --locked --dev` line are all preserved by design and by the test's targeted stale list.

## Minor findings
1. **PR template retains bare `uv build` in prose** (`.github/present_template.md:56`: "If packaging/templates changed: `uv build` plus installed-wheel smoke…"). Not pinned by the new test and not in the stale list, so harmless, but slightly inconsistent with the frozen `uv --no-config build` used in CI/checklist. Optional to align or leave as shorthand.
2. **Implicit command→surface routing.** The new test uses a substring-keyed `if/elif/else` chain to pick surfaces per command. It is correct for the fixed command set, but an explicit `(command, surfaces)` tuple list (or a per-command comment) would make intent clearer and avoid future mis-routing if commands are added. Stylistic only.
3. **Whole-document stale bans are slightly brittle.** `assert "uv run pytest" not in surface` etc. scan entire files. Safe today (no legitimate prose contains them after GREEN), but any future prose example like `` `uv run pytest -k …` `` in these 6 surfaces would trip it. Acceptable since these surfaces are verification-focused; just noting the coupling.

## Verification command sufficiency
Sufficient. Focused run `-k "no_config or first_run_smoke or package_archive"` selects all 4 affected tests (the new test name contains `no_config`, so it is matched). The release gate adds release-hygiene, full pytest, ruff check/format, `UV_NO_CONFIG=1 uv lock --check`, `git diff --exit-code -- uv.lock`, and `git diff --check` — comprehensive for this docs/CI node.

## Final statement
There are **no Critical or Important blockers** before implementation. The Stage 123 design and plan may proceed; the three minor items are optional polish.
