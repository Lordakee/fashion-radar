# Stage 129 Plan Review

## Critical findings

None.

## Important findings

None.

## Minor findings

1. **Task 1 Step 3 is slightly underspecified.** The plan instructs "add `pull_request_template` to the surfaces used for `check_package_archives.py` and `build --out-dir`" but does not show the exact diff. The intent is unambiguous (append `pull_request_template` to the two existing tuples at `tests/test_cli_docs.py:803` and `:805`), and a competent worker will infer it, but spelling out the two modified `elif` branches would remove ambiguity. Not a blocker.

2. **Drift-back guard is phrase-specific.** The assertion `` "`uv --no-config build` plus installed-wheel smoke" not in verification `` only catches regression to the *exact* legacy phrase. A partial revert (e.g. bare `uv --no-config build` without the suffix) would not trip this assertion, but the positive `--out-dir "$tmp_build"` and `check_package_archives.py "$tmp_build"` assertions would still fail, so net coverage is adequate. No action required.

3. **Plan-review artifact creation is implicit.** The Files section lists `opencode-stage-129-plan-review-prompt.md` / `opencode-stage-129-plan-review.md`, but no task creates them — they are produced by this review step, matching the established workflow and the commit list in Task 4 Step 2. Consistent, just worth noting so the worker does not re-create them.

## Assessment against review focus

1. **Addresses drift without behavior change?** Yes. The change is confined to `.github/pull_request_template.md` (contributor-facing guidance) plus docs tests. No edits to `.github/workflows/ci.yml`, `scripts/check_package_archives.py`, `scripts/check_release_hygiene.py`, `src/`, `pyproject.toml`, or `uv.lock`.
2. **Focused docs test specific enough?** Yes. `test_pull_request_template_package_smoke_uses_temp_build_archive_checker` asserts the exact `mktemp`, `--out-dir "$tmp_build"`, archive-checker, and `"$tmp_build"/*.whl` strings inside the `Verification` section, and will be RED before Task 2.
3. **Canonical surface test updated?** Yes. Task 1 Step 3 adds `pull_request_template` to both the `check_package_archives.py "$tmp_build"` and `build --out-dir "$tmp_build"` surface tuples, and the existing `stale_verification_commands` negation loop still holds because the template will carry only the `uv --no-config` variants.
4. **Avoids duplicating the upload checklist?** Yes. A four-item nested bullet list under the existing packaging checkbox; no porting of the full upload checklist.
5. **Scope boundaries respected?** Yes. No runtime, package-checker, CI, dependency, lockfile, connector, scraping, browser-automation, platform-API, monitoring, scheduling, source-acquisition, demand-proof, ranking, coverage-verification, or compliance/audit behavior. Confirmed via grep that only `test_github_verification_surfaces_use_no_config_frozen_uv_run` references the PR template.
6. **Verification commands sufficient?** Yes. Focused RED→GREEN tests, ruff check/format on the test file, plus the full release gate (release hygiene, full pytest, ruff, format, lock check, lockfile diff, whitespace, token/auth-header absence) in Task 4.

## Final statement

There are **no Critical or Important blockers** before implementation. The Stage 129 design and plan are approved to proceed.
