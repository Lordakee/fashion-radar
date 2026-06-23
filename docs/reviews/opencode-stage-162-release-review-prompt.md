# Stage 162 Release Review Prompt

You are reviewing Stage 162 for release readiness in `/home/ubuntu/fashion-radar`.

Use model context only from the repository files and this prompt. Do not edit files.

## Objective

Stage 162 is a source-pack-only grammar polish for the human table output of
`source-pack-lint`: exactly one finding should render with singular labels
(`1 error`, `1 warning`, `1 info`), while zero and non-one counts should keep
the existing plural/non-count wording (`0 errors`, `2 warnings`, `0 info`).

## Changed Files

- `src/fashion_radar/source_packs.py`
  - Adds private helper `_format_finding_count(...)`.
  - Updates only `render_source_pack_lint_table(...)` `Findings:` line.
- `tests/test_source_packs.py`
  - Updates the single-warning source-pack expectation to `1 warning`.
  - Adds direct renderer coverage for singular one-of-each counts.
  - Adds direct renderer coverage for plural two-of-each counts.
- `docs/superpowers/specs/2026-06-23-stage-162-source-pack-lint-finding-count-grammar-design.md`
- `docs/superpowers/plans/2026-06-23-stage-162-source-pack-lint-finding-count-grammar-plan.md`
- `docs/reviews/opencode-stage-162-plan-review-prompt.md`
- `docs/reviews/opencode-stage-162-plan-review.md`
- `docs/reviews/opencode-stage-162-code-review-prompt.md`
- `docs/reviews/opencode-stage-162-code-review.md`

## Scope Boundaries

Review the implementation against these boundaries:

- Source-pack lint renderer only.
- No changes to source-pack lint semantics, JSON output, strict-mode behavior,
  CLI command flow, source pack loading, or source pack validation rules.
- Entity-pack, community-signal, and directory lint renderer grammar are
  intentionally deferred.
- No social connectors, scraping, browser automation, platform APIs, login,
  cookies, monitoring, scheduling, source acquisition, demand proof, ranking,
  coverage verification, or compliance-review product features.

## Verification Evidence

RED verification before implementation:

- `uv --no-config run --frozen pytest tests/test_source_packs.py::test_render_source_pack_lint_table_shows_none_for_empty_tag_counts tests/test_source_packs.py::test_render_source_pack_lint_table_singularizes_one_finding_count tests/test_source_packs.py::test_render_source_pack_lint_table_keeps_plural_finding_counts -q`
- Result before implementation: 2 failed, 1 passed, as expected.

Focused GREEN verification after implementation:

- `uv --no-config run --frozen pytest tests/test_source_packs.py::test_render_source_pack_lint_table_includes_tag_counts tests/test_source_packs.py::test_render_source_pack_lint_table_shows_none_for_empty_tag_counts tests/test_source_packs.py::test_render_source_pack_lint_table_singularizes_one_finding_count tests/test_source_packs.py::test_render_source_pack_lint_table_keeps_plural_finding_counts tests/test_cli.py::test_source_pack_lint_prints_table_for_public_pack -q`
- Result: 5 passed.
- `uv --no-config run --frozen pytest tests/test_source_packs.py tests/test_source_pack_quality_docs.py -q`
- Result: 17 passed.
- `uv --no-config run --frozen pytest tests/test_cli.py -q -k "source_pack_lint"`
- Result: 7 passed, 291 deselected.
- `uv --no-config run --frozen ruff check src/fashion_radar/source_packs.py tests/test_source_packs.py tests/test_source_pack_quality_docs.py tests/test_cli.py`
- Result: clean.
- `uv --no-config run --frozen ruff format --check src/fashion_radar/source_packs.py tests/test_source_packs.py tests/test_source_pack_quality_docs.py tests/test_cli.py`
- Result: 4 files already formatted.

Full release gate after code review and review artifact cleanup:

- `env -u all_proxy -u ALL_PROXY -u http_proxy -u HTTP_PROXY -u https_proxy -u HTTPS_PROXY -u no_proxy -u NO_PROXY uv --no-config run --frozen pytest -q`
- Result: 1324 passed.
- `uv --no-config run --frozen python scripts/check_first_run_smoke.py --repo-root .`
- Result: First-run sample smoke passed.
- `uv --no-config run --frozen python scripts/check_release_hygiene.py --repo-root .`
- Initial result: failed on non-ASCII arrows in `docs/reviews/opencode-stage-162-code-review.md`.
- Fix applied: replaced the arrows with ASCII text and removed a trailing fence.
- Re-run result: Release hygiene checks passed.
- `uv --no-config run --frozen ruff check .`
- Result: All checks passed.
- `uv --no-config run --frozen ruff format --check .`
- Result: 142 files already formatted.
- `env -u UV_DEFAULT_INDEX -u UV_INDEX_URL -u UV_EXTRA_INDEX_URL UV_NO_CONFIG=1 uv lock --check`
- Result: Resolved 84 packages in 24ms.
- `git diff --check`
- Result: clean.
- `rg -n 'ghp_[A-Za-z0-9]+' .`
- Result: no matches.
- `git config --get-all http.https://github.com/.extraheader`
- Result: no configured extraheader.

## Prior Reviews

- Plan review: `docs/reviews/opencode-stage-162-plan-review.md`
  - No critical or important findings.
  - Minor issues were addressed in the plan/spec artifacts.
- Code review: `docs/reviews/opencode-stage-162-code-review.md`
  - No critical or important findings.
  - Minor non-blocking notes:
    - New tests use `in lines` instead of exact header slice assertions.
    - Negative count helper behavior is unreachable with current derived counts.
    - Entity/community lint grammar remains intentionally deferred.

## Review Questions

Please answer:

1. Does the final diff meet the Stage 162 source-pack-only objective?
2. Are the tests sufficient for the grammar change without expanding scope?
3. Did any out-of-scope behavior change?
4. Are the release artifacts clean enough to commit?
5. Are there any critical or important findings that must be fixed before commit and push?

Return a concise markdown review with sections:

- Summary
- Findings
  - Critical
  - Important
  - Minor
- Verification Assessment
- Verdict
