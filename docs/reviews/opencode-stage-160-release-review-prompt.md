# Stage 160 Release Review Prompt

Review the Stage 160 release readiness for Fashion Radar.

Return only the completed review body. Do not include process chatter, live tool
status, ANSI output, or command logs. Start the response exactly with:

```text
# Stage 160 Release Review
```

Use repository files and the verification evidence below. Avoid running long
commands; if you run any commands, summarize the result in prose instead of
including logs.

## Scope

Stage 160 makes the package archive checker require expected wheel entry points
under the `[console_scripts]` group in `entry_points.txt`.

Changed files:

- `scripts/check_package_archives.py`
- `tests/test_package_archives.py`
- `docs/superpowers/specs/2026-06-23-stage-160-wheel-entry-points-console-scripts-design.md`
- `docs/superpowers/plans/2026-06-23-stage-160-wheel-entry-points-console-scripts-plan.md`
- `docs/reviews/opencode-stage-160-plan-review-prompt.md`
- `docs/reviews/opencode-stage-160-plan-review.md`
- `docs/reviews/opencode-stage-160-code-review-prompt.md`
- `docs/reviews/opencode-stage-160-code-review.md`
- `docs/reviews/opencode-stage-160-release-review-prompt.md`

Implementation summary:

- Added RED tests for missing console scripts with section-aware wording,
  expected scripts under `[gui_scripts]`, wrong console-script targets, and
  malformed no-header `entry_points.txt`.
- Replaced line-membership validation with section-aware
  `configparser.ConfigParser(interpolation=None)` parsing.
- Set `parser.optionxform = str` before parsing to preserve script-name case.
- Return deterministic checker errors for malformed metadata, missing
  `[console_scripts]` entries, and wrong targets.

Prior local reviews:

- Stage 160 plan review: no critical or important findings.
- Stage 160 code review: no critical or important findings. Minor observations
  were limited to possible future case-mismatch coverage, extra unexpected
  console scripts matching the current design boundary, and possible future
  non-UTF-8 hardening.

## Verification Already Run

Focused RED/GREEN and package archive checks:

```bash
uv --no-config run --frozen pytest tests/test_package_archives.py -q -k "entry_points"
# RED before implementation: 4 failed, 1 passed, 67 deselected.
# GREEN after implementation: 5 passed, 67 deselected.

uv --no-config run --frozen pytest tests/test_package_archives.py -q
# 72 passed.

uv --no-config run --frozen ruff check scripts/check_package_archives.py tests/test_package_archives.py
# All checks passed.

uv --no-config run --frozen ruff format --check scripts/check_package_archives.py tests/test_package_archives.py
# 2 files already formatted.

tmp_build=$(mktemp -d)
uv --no-config build --out-dir "$tmp_build"
uv --no-config run --frozen python scripts/check_package_archives.py "$tmp_build"
rm -rf "$tmp_build"
# Package archives contain required files.
```

Full release gate:

```bash
env -u all_proxy -u ALL_PROXY -u http_proxy -u HTTP_PROXY -u https_proxy -u HTTPS_PROXY -u no_proxy -u NO_PROXY uv --no-config run --frozen pytest -q
# 1320 passed.

uv --no-config run --frozen python scripts/check_first_run_smoke.py --repo-root .
# First-run sample smoke passed.

uv --no-config run --frozen python scripts/check_release_hygiene.py --repo-root .
# Release hygiene checks passed.

uv --no-config run --frozen ruff check .
# All checks passed.

uv --no-config run --frozen ruff format --check .
# 142 files already formatted.

env -u UV_DEFAULT_INDEX -u UV_INDEX_URL -u UV_EXTRA_INDEX_URL UV_NO_CONFIG=1 uv lock --check
# Resolved 84 packages.

git diff --check
# No output.

rg -n 'ghp_[A-Za-z0-9]+' .
# No matches.

git config --get-all http.https://github.com/.extraheader
# No configured persistent extraheader.
```

Package build, archive, and installed-wheel smoke:

```bash
tmp_build=$(mktemp -d)
tmp_env=$(mktemp -d)
uv --no-config build --out-dir "$tmp_build"
uv --no-config run --frozen python scripts/check_package_archives.py "$tmp_build"
uv venv "$tmp_env/venv"
uv pip install --index-url https://pypi.tuna.tsinghua.edu.cn/simple --python "$tmp_env/venv/bin/python" "$tmp_build"/*.whl
"$tmp_env/venv/bin/python" scripts/check_first_run_smoke.py --repo-root . --python "$tmp_env/venv/bin/python" --installed
rm -rf "$tmp_build" "$tmp_env"
# Package archives contain required files.
# First-run sample smoke passed.
```

## Review Questions

1. Is Stage 160 release-ready after the verification above?
2. Do the changed package archive checker and tests satisfy the approved
   section-aware entry-point objective?
3. Are review artifacts clean enough for Stage 159+ release hygiene?
4. Are there any critical or important issues before commit and GitHub push?
5. Does the release preserve scope boundaries: no social connectors, scraping,
   browser automation, platform APIs, login/cookie/session behavior, monitoring,
   scheduling, source acquisition, demand proof, ranking, coverage verification,
   or compliance-review product feature?

Return critical, important, and minor findings. If there are no blocking
findings, say so explicitly.
