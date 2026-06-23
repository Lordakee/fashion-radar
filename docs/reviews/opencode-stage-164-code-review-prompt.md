# Stage 164 Code Review Prompt

Review the Stage 164 implementation for Fashion Radar.

Return only the completed review body. Do not include process chatter, live tool
status, ANSI output, or command logs. Start the response exactly with:

```text
# Stage 164 Code Review
```

Objective:

Make human-readable lint table finding-count labels consistent across
source-pack, entity-pack, and community-signal lint surfaces.

Changed files:

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
  - Adds a focused docs grammar regression for `docs/community-signal-quality.md`.
- `docs/community-signal-quality.md`
  - Updates examples from `1 errors` to `1 error` where finding counts are shown.
- Stage 164 plan/review artifacts under `docs/superpowers/...` and
  `docs/reviews/opencode-stage-164-...`.

Scope boundaries:

- Human-readable lint table finding-count labels only.
- No JSON output changes.
- No lint model, severity, sorting, strict-mode, or CLI command flow changes.
- No row-count grammar changes such as `1 rows`.
- No historical spec/review archive rewrites.
- No social connectors, scraping, browser automation, platform APIs, login,
  cookies, monitoring, scheduling, source acquisition, demand proof, ranking,
  coverage verification, or compliance-review product features.

Plan review history:

- `docs/reviews/opencode-stage-164-plan-review.md`
  - No critical findings.
  - One important finding: directory singular test path/prefix mismatch.
- `docs/reviews/opencode-stage-164-plan-rereview.md`
  - Confirmed the important finding was fixed.
  - No critical or important findings remain.

RED evidence before implementation:

- `uv --no-config run --frozen pytest tests/test_entity_pack_lint.py::test_render_entity_pack_lint_table_singularizes_one_finding_count tests/test_entity_pack_lint.py::test_render_entity_pack_lint_table_keeps_plural_finding_counts -q`
- Result before implementation: 1 failed, 1 passed. Singular failed with
  `Findings: 1 errors, 1 warnings, 1 info`.
- `uv --no-config run --frozen pytest tests/test_community_signal_lint.py::test_render_community_signal_lint_table_singularizes_one_finding_count tests/test_community_signal_lint.py::test_render_community_signal_lint_table_keeps_plural_finding_counts tests/test_community_signal_lint.py::test_render_community_signal_directory_lint_table_singularizes_finding_counts tests/test_community_signal_lint.py::test_render_community_signal_directory_lint_table_keeps_plural_finding_counts -q`
- Result before implementation: 2 failed, 2 passed. Singular file and
  directory tests failed with fixed plural labels.
- `uv --no-config run --frozen pytest tests/test_cli_docs.py::test_community_signal_quality_docs_use_singular_one_finding_count_examples -q`
- Result before docs update: 1 failed because docs still showed `1 errors`.

GREEN evidence after implementation:

- Combined focused command for the seven new tests:
  `uv --no-config run --frozen pytest tests/test_entity_pack_lint.py::test_render_entity_pack_lint_table_singularizes_one_finding_count tests/test_entity_pack_lint.py::test_render_entity_pack_lint_table_keeps_plural_finding_counts tests/test_community_signal_lint.py::test_render_community_signal_lint_table_singularizes_one_finding_count tests/test_community_signal_lint.py::test_render_community_signal_lint_table_keeps_plural_finding_counts tests/test_community_signal_lint.py::test_render_community_signal_directory_lint_table_singularizes_finding_counts tests/test_community_signal_lint.py::test_render_community_signal_directory_lint_table_keeps_plural_finding_counts tests/test_cli_docs.py::test_community_signal_quality_docs_use_singular_one_finding_count_examples -q`
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

Review questions:

1. Does the implementation meet the Stage 164 objective?
2. Is the shared helper appropriately scoped and safe for source/entity/community renderers?
3. Do tests cover singular, plural, and source-pack regression risks?
4. Does directory per-file output change only finding-count grammar and not row-count grammar?
5. Are docs changes and docs tests sufficient?
6. Did any out-of-scope behavior change?
7. Are there any critical or important findings before release verification?

Return sections:

- Summary
- Findings
  - Critical
  - Important
  - Minor
- Verification Assessment
- Verdict
