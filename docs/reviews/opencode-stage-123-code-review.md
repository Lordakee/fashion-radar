# Stage 123 Code Review

## Critical findings
None.

## Important findings
None.

## Verification of each review focus

**1. Implementation matches the Stage 123 design and plan — confirmed.**
Every command/surface edit in the design's "Expected Behavior" is present in the diff and pinned by `test_github_verification_surfaces_use_no_config_frozen_uv_run` (tests/test_cli_docs.py:752):
- CI: release hygiene, first-run smoke, ruff check/format, pytest, build, and package archive checker all switched to `uv --no-config run --frozen ...` / `uv --no-config build ...` (.github/workflows/ci.yml:26-41).
- README Development block + smoke/build examples aligned (README.md:325,335,875-877).
- CONTRIBUTING `## Verification` block aligned (CONTRIBUTING.md:58-60).
- PR template checklist aligned, plus the bare `uv build` prose upgraded to `uv --no-config build` (.github/pull_request_template.md:53-56).
- Upload checklist Before-Upload + package smoke blocks aligned (docs/github-upload-checklist.md:20-22,355,363,379-380).
- first-run.md smoke/build aligned (docs/first-run.md:128,146).

**2. Release/agent/CI verification commands use no-config/frozen consistently — confirmed.** All seven no-config command forms are asserted present in their respective surfaces, and the stale `UV_NO_CONFIG=1 uv run ...` / `uv run ruff|pytest` forms are asserted absent across all six scanned surfaces. Release hygiene passes; full suite (1197) passes; ruff check/format clean.

**3. Explicit isolated lock/sync commands preserved — confirmed.** The implementation goes beyond the plan with a useful enhancement: an `isolated_lock_and_sync_commands` assertion block (tests/test_cli_docs.py:783-789) pins `UV_NO_CONFIG=1 uv lock --check`, `UV_NO_CONFIG=1 uv sync --locked --dev`, and `UV_NO_CONFIG=1 uv sync --locked --dev --check` in CONTRIBUTING, the PR template, and the upload checklist. All three are intact and `uv lock --check` still passes with `uv.lock` clean.

**4. Ordinary local workflow examples preserved — confirmed.** `uv run fashion-radar init` and `uv run fashion-radar dashboard` (and dozens of other `uv run fashion-radar ...` usage examples) are untouched in CONTRIBUTING/README. The test explicitly asserts the two CONTRIBUTING examples survive.

**5. Mirror install examples preserved as local install aids only — confirmed.** `UV_DEFAULT_INDEX=https://pypi.tsinghua... uv sync --frozen --dev` in README.md:247 and docs/github-upload-checklist.md:28, plus the "frozen mirror install" framing, are unchanged.

**6. Scope boundaries respected — confirmed.** The diff touches only CI YAML, Markdown docs, one docs-drift test, and stage review artifacts. No `src/`, `pyproject.toml`, `uv.lock`, dependency, runtime, CLI, connector, scraping, browser-automation, platform-API, monitoring, scheduling, source-acquisition, demand-proof, ranking, coverage-verification, or compliance/audit behavior.

## Minor findings (optional polish, non-blocking)

1. **PR template build shorthand is unpinned.** `.github/pull_request_template.md:56` uses `uv --no-config build` (no `--out-dir`), which the new test does not assert for that surface. Consistent with the frozen direction, just not pinned. Optional to leave as prose shorthand.
2. **Historical stage plans/specs still contain old command forms.** ~100 `uv run ruff|pytest` / `UV_NO_CONFIG=1 uv run ...` matches remain under `docs/superpowers/plans/` and `docs/superpowers/specs/`. These are immutable records of past stages and correctly out of scope for this stage (the stale-list scans only the six current GitHub-facing surfaces). No action recommended — rewriting historical records would be inappropriate.
3. **Plan-review record file mode is 0600.** `docs/reviews/opencode-stage-123-plan-review.md` is `-rw-------`. Cosmetic only; content is complete and coherent with no stubs, tool-status lines, or truncation.

## Final statement

There are **no Critical or Important blockers** before release. Stage 123 is ready for commit, push, and CI verification.
