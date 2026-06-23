# Stage 161 Release Review Prompt

Review the Stage 161 release readiness for Fashion Radar.

Return only the completed review body. Do not include process chatter, live tool
status, ANSI output, or command logs. Start the response exactly with:

```text
# Stage 161 Release Review
```

## Scope

Stage 161 adds deterministic source tag counts to the default human table output
from `fashion-radar source-pack-lint`.

Changed files:

- `src/fashion_radar/source_packs.py`
- `tests/test_source_packs.py`
- `tests/test_cli.py`
- `docs/source-pack-quality.md`
- `docs/superpowers/specs/2026-06-23-stage-161-source-pack-lint-tag-counts-design.md`
- `docs/superpowers/plans/2026-06-23-stage-161-source-pack-lint-tag-counts-plan.md`
- `docs/reviews/opencode-stage-161-plan-review-prompt.md`
- `docs/reviews/opencode-stage-161-plan-review.md`
- `docs/reviews/opencode-stage-161-code-review-prompt.md`
- `docs/reviews/opencode-stage-161-code-review.md`
- `docs/reviews/opencode-stage-161-code-rereview-prompt.md`
- `docs/reviews/opencode-stage-161-code-rereview.md`
- `docs/reviews/opencode-stage-161-release-review-prompt.md`

Implementation summary:

- Added `Tags: {_format_counts(result.tag_counts)}` to
  `render_source_pack_lint_table(...)` immediately after `Types:`.
- Added direct renderer tests for deterministic non-empty tag counts and
  documented empty tag counts (`Tags: none`).
- Strengthened the public-pack CLI table smoke to assert `Tags:` is present.
- Updated `docs/source-pack-quality.md` table sample and summary bullets.

Prior local reviews:

- Stage 161 plan review: no critical or important findings.
- Stage 161 code review: no critical or important findings; minor m1 requested
  direct `Tags: none` coverage.
- Stage 161 code rereview: no critical or important findings after adding the
  `Tags: none` test.

## Verification Already Run

Focused RED/GREEN:

```bash
uv --no-config run --frozen pytest tests/test_source_packs.py::test_render_source_pack_lint_table_includes_tag_counts tests/test_cli.py::test_source_pack_lint_prints_table_for_public_pack -q
# RED before implementation: 2 failed.
# GREEN after implementation: 2 passed.

uv --no-config run --frozen pytest tests/test_source_packs.py::test_render_source_pack_lint_table_includes_tag_counts tests/test_source_packs.py::test_render_source_pack_lint_table_shows_none_for_empty_tag_counts tests/test_cli.py::test_source_pack_lint_prints_table_for_public_pack -q
# 3 passed.
```

Stage-focused verification:

```bash
uv --no-config run --frozen pytest tests/test_source_packs.py tests/test_cli.py -k "source_pack_lint" -q
# 9 passed, 301 deselected.

uv --no-config run --frozen pytest tests/test_source_pack_quality_docs.py tests/test_source_packs.py tests/test_cli.py -k "source_pack" -q
# 22 passed, 291 deselected.

uv --no-config run --frozen ruff check src/fashion_radar/source_packs.py tests/test_source_packs.py tests/test_cli.py
# All checks passed.

uv --no-config run --frozen ruff format --check src/fashion_radar/source_packs.py tests/test_source_packs.py tests/test_cli.py
# 3 files already formatted.
```

Full release gate:

```bash
env -u all_proxy -u ALL_PROXY -u http_proxy -u HTTP_PROXY -u https_proxy -u HTTPS_PROXY -u no_proxy -u NO_PROXY uv --no-config run --frozen pytest -q
# 1322 passed.

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

## Review Questions

1. Is Stage 161 release-ready after the verification above?
2. Does the implementation satisfy the tag-count table objective without
   changing JSON shape or lint semantics?
3. Are review artifacts clean enough for Stage 159+ release hygiene?
4. Are there any critical or important issues before commit and GitHub push?
5. Does the release preserve scope boundaries: no social connectors, scraping,
   browser automation, platform APIs, login/cookie/session behavior, monitoring,
   scheduling, source acquisition, demand proof, ranking, coverage verification,
   or compliance-review product feature?

Return critical, important, and minor findings. If there are no blocking
findings, say so explicitly.
