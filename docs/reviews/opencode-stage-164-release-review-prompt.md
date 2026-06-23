# Stage 164 Release Review Prompt

You are reviewing Stage 164 for release readiness in `/home/ubuntu/fashion-radar`.

Return only the completed review body. Do not include process chatter, live tool
status, ANSI output, or command logs. Start the response exactly with:

```text
# Stage 164 Release Review
```

## Objective

Make human-readable lint table finding-count labels consistent across
source-pack, entity-pack, and community-signal lint surfaces.

## Changed Files

- `src/fashion_radar/lint_formatting.py`
  - Adds `format_count_label(...)`.
  - Adds `format_finding_counts(...)`.
- `src/fashion_radar/source_packs.py`
  - Uses `format_finding_counts(...)` while preserving Stage 162 behavior.
  - Removes the local `_format_finding_count(...)`.
- `src/fashion_radar/entity_packs.py`
  - Uses `format_finding_counts(...)` in the human `Findings:` summary.
- `src/fashion_radar/community_signals.py`
  - Uses `format_finding_counts(...)` in single-file and directory aggregate
    `Findings:` summaries.
  - Uses `format_finding_counts(...)` in directory per-file finding counts.
- `tests/test_entity_pack_lint.py`
  - Adds singular and plural direct renderer tests.
- `tests/test_community_signal_lint.py`
  - Adds single-file singular/plural direct renderer tests.
  - Adds directory aggregate/per-file singular/plural direct renderer tests.
- `tests/test_cli_docs.py`
  - Adds docs grammar regression coverage.
- `docs/community-signal-quality.md`
  - Updates examples from `1 errors` to `1 error` where finding counts are shown.
- Stage 164 spec, plan, plan review, plan rereview, and code review artifacts.

## Scope Boundaries

- Human-readable lint table finding-count labels only.
- No JSON output changes.
- No lint model, severity, sorting, strict-mode, or CLI command flow changes.
- No row-count grammar changes such as `1 rows`.
- No historical spec/review archive rewrites.
- No social connectors, scraping, browser automation, platform APIs, login,
  cookies, monitoring, scheduling, source acquisition, demand proof, ranking,
  coverage verification, or compliance-review product features.

## Review History

- Plan review: `docs/reviews/opencode-stage-164-plan-review.md`
  - No critical findings.
  - One important finding: directory singular test path/prefix mismatch.
- Plan rereview: `docs/reviews/opencode-stage-164-plan-rereview.md`
  - Confirmed the important finding was fixed.
  - No critical or important findings remain.
- Code review: `docs/reviews/opencode-stage-164-code-review.md`
  - No critical or important findings.
  - Minor future-stage notes only.
- Read-only subagent diff review:
  - No findings.
  - Confirmed the diff is limited to human-readable lint finding-count labels
    plus docs/tests.

## Verification Evidence

RED before implementation:

- `uv --no-config run --frozen pytest tests/test_entity_pack_lint.py::test_render_entity_pack_lint_table_singularizes_one_finding_count tests/test_entity_pack_lint.py::test_render_entity_pack_lint_table_keeps_plural_finding_counts -q`
- Result before implementation: 1 failed, 1 passed.
- `uv --no-config run --frozen pytest tests/test_community_signal_lint.py::test_render_community_signal_lint_table_singularizes_one_finding_count tests/test_community_signal_lint.py::test_render_community_signal_lint_table_keeps_plural_finding_counts tests/test_community_signal_lint.py::test_render_community_signal_directory_lint_table_singularizes_finding_counts tests/test_community_signal_lint.py::test_render_community_signal_directory_lint_table_keeps_plural_finding_counts -q`
- Result before implementation: 2 failed, 2 passed.
- `uv --no-config run --frozen pytest tests/test_cli_docs.py::test_community_signal_quality_docs_use_singular_one_finding_count_examples -q`
- Result before docs update: 1 failed.

GREEN after implementation:

- Combined focused command for seven new tests.
- Result: 7 passed.
- `uv --no-config run --frozen pytest tests/test_source_packs.py tests/test_entity_pack_lint.py tests/test_community_signal_lint.py -q`
- Result: 128 passed.
- `uv --no-config run --frozen pytest tests/test_cli.py -q -k "source_pack_lint or entity_pack_lint or community_signal_lint"`
- Result: 33 passed, 265 deselected.
- `uv --no-config run --frozen pytest tests/test_cli_docs.py -q -k "community_signal_quality"`
- Result: 1 passed, 67 deselected.
- `uv --no-config run --frozen ruff check src/fashion_radar/lint_formatting.py src/fashion_radar/source_packs.py src/fashion_radar/entity_packs.py src/fashion_radar/community_signals.py tests/test_source_packs.py tests/test_entity_pack_lint.py tests/test_community_signal_lint.py tests/test_cli_docs.py`
- Result: All checks passed.
- `uv --no-config run --frozen ruff format --check src/fashion_radar/lint_formatting.py src/fashion_radar/source_packs.py src/fashion_radar/entity_packs.py src/fashion_radar/community_signals.py tests/test_source_packs.py tests/test_entity_pack_lint.py tests/test_community_signal_lint.py tests/test_cli_docs.py`
- Result: 8 files already formatted.

Full release gate:

- `env -u all_proxy -u ALL_PROXY -u http_proxy -u HTTP_PROXY -u https_proxy -u HTTPS_PROXY -u no_proxy -u NO_PROXY uv --no-config run --frozen pytest -q`
- Result: 1333 passed.
- `uv --no-config run --frozen python scripts/check_first_run_smoke.py --repo-root .`
- Result: First-run sample smoke passed.
- `uv --no-config run --frozen python scripts/check_release_hygiene.py --repo-root .`
- Result: Release hygiene checks passed.
- `uv --no-config run --frozen ruff check .`
- Result: All checks passed.
- `uv --no-config run --frozen ruff format --check .`
- Result: 143 files already formatted.
- `env -u UV_DEFAULT_INDEX -u UV_INDEX_URL -u UV_EXTRA_INDEX_URL UV_NO_CONFIG=1 uv lock --check`
- Result: Resolved 84 packages in 4ms.
- `git diff --check`
- Result: clean.
- `rg -n 'ghp_[A-Za-z0-9]+' .`
- Result: no matches.
- `git config --get-all http.https://github.com/.extraheader`
- Result: no configured extraheader.

## Review Questions

Please answer:

1. Does the final diff meet the Stage 164 objective?
2. Are tests sufficient for source/entity/community singular/plural behavior
   and source-pack regression risk?
3. Did directory per-file output change only finding-count grammar and not
   row-count grammar?
4. Are docs changes and review artifacts clean enough to commit?
5. Did any out-of-scope behavior change?
6. Are there any critical or important findings before commit and push?

Return sections:

- Summary
- Findings
  - Critical
  - Important
  - Minor
- Verification Assessment
- Verdict
