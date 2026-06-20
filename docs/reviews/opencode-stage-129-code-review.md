# Stage 129 Code Review

## Critical findings

None.

## Important findings

None.

## Minor findings

1. **Drift-back guard is phrase-specific.** `test_pull_request_template_package_smoke_uses_temp_build_archive_checker` only negates the exact legacy phrase `` "`uv --no-config build` plus installed-wheel smoke" `` (`tests/test_cli_docs.py:725`). A bare `uv --no-config build` revert without that suffix would not trip this single assertion, but the positive `--out-dir "$tmp_build"` and `check_package_archives.py "$tmp_build"` assertions still fail on such a drift, so net coverage is adequate. Already acknowledged in the plan review; no action required.

2. **Cosmetic parenthesization.** The archive-checker assertion wraps a single string literal in parentheses (`tests/test_cli_docs.py:721-723`) rather than the two-part concatenation shown in the plan. Functionally identical, passes ruff/format. No action required.

## Assessment against review focus

1. **Matches design/plan?** Yes. The PR template packaging checkbox was expanded into the exact four-item nested bullet list specified in the plan (`.github/pull_request_template.md:57-60`), and both test additions match the plan's Task 1.
2. **PR template includes required commands?** Yes — `tmp_build="$(mktemp -d)"`, `uv --no-config build --out-dir "$tmp_build"`, and `uv --no-config run --frozen python scripts/check_package_archives.py "$tmp_build"` are all present.
3. **Canonical surface test updated?** Yes. `test_github_verification_surfaces_use_no_config_frozen_uv_run` adds `pull_request_template` to both the `check_package_archives.py` (`tests/test_cli_docs.py:816`) and `build --out-dir` (`:818`) surface tuples. The stale-variant negation loop still holds because the template carries only `uv --no-config` variants, not the `UV_NO_CONFIG=1 uv ...` stale forms.
4. **Avoids full upload-checklist duplication?** Yes. The focused test asserts only the four specific commands within the `Verification` section; the template keeps a concise nested bullet list without porting the upload checklist.
5. **Scope respected?** Yes. Only `.github/pull_request_template.md` and `tests/test_cli_docs.py` changed; `uv.lock` unchanged; no edits to `src/`, `scripts/`, `.github/workflows/ci.yml`, or `pyproject.toml`. No runtime, package-checker, CI, dependency, lockfile, connector, scraping, browser-automation, platform-API, monitoring, scheduling, source-acquisition, demand-proof, ranking, coverage-verification, or compliance/audit behavior.

Verification run: focused 3 tests pass, full `tests/test_cli_docs.py` (65 tests) passes, ruff check + format pass.

## Final statement

There are **no Critical or Important blockers** before release.
