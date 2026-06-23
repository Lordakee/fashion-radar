# Stage 162 Code Review Prompt

Review the Stage 162 implementation for Fashion Radar.

Return only the completed review body. Do not include process chatter, live tool
status, ANSI output, or command logs. Start the response exactly with:

```text
# Stage 162 Code Review
```

Changed files:

- `src/fashion_radar/source_packs.py`
- `tests/test_source_packs.py`
- `docs/superpowers/specs/2026-06-23-stage-162-source-pack-lint-finding-count-grammar-design.md`
- `docs/superpowers/plans/2026-06-23-stage-162-source-pack-lint-finding-count-grammar-plan.md`
- `docs/reviews/opencode-stage-162-plan-review-prompt.md`
- `docs/reviews/opencode-stage-162-plan-review.md`
- `docs/reviews/opencode-stage-162-code-review-prompt.md`

Objective:

Make the `source-pack-lint` human table summary use singular labels for exactly
one finding and plural labels otherwise.

Implementation summary:

- Updated the Stage 161 `Tags: none` renderer test to expect `1 warning`.
- Added direct renderer tests for `1 error, 1 warning, 1 info` and
  `2 errors, 2 warnings, 2 info`.
- Added `_format_finding_count(...)` local to `source_packs.py`.
- Updated only `render_source_pack_lint_table(...)` to use the local helper.
- Left entity-pack and community-signal lint output intentionally untouched.

Verification already run:

```bash
uv --no-config run --frozen pytest tests/test_source_packs.py::test_render_source_pack_lint_table_shows_none_for_empty_tag_counts tests/test_source_packs.py::test_render_source_pack_lint_table_singularizes_one_finding_count tests/test_source_packs.py::test_render_source_pack_lint_table_keeps_plural_finding_counts -q
# RED before implementation: 2 failed, 1 passed.

uv --no-config run --frozen pytest tests/test_source_packs.py::test_render_source_pack_lint_table_includes_tag_counts tests/test_source_packs.py::test_render_source_pack_lint_table_shows_none_for_empty_tag_counts tests/test_source_packs.py::test_render_source_pack_lint_table_singularizes_one_finding_count tests/test_source_packs.py::test_render_source_pack_lint_table_keeps_plural_finding_counts tests/test_cli.py::test_source_pack_lint_prints_table_for_public_pack -q
# 5 passed.

uv --no-config run --frozen pytest tests/test_source_packs.py tests/test_source_pack_quality_docs.py -q
# 17 passed.

uv --no-config run --frozen pytest tests/test_cli.py -q -k "source_pack_lint"
# 7 passed, 291 deselected.

uv --no-config run --frozen ruff check src/fashion_radar/source_packs.py tests/test_source_packs.py tests/test_source_pack_quality_docs.py tests/test_cli.py
# All checks passed.

uv --no-config run --frozen ruff format --check src/fashion_radar/source_packs.py tests/test_source_packs.py tests/test_source_pack_quality_docs.py tests/test_cli.py
# 4 files already formatted.
```

Review questions:

1. Does source-pack table output now render `1 error`, `1 warning`, and
   `1 info` while preserving `0 errors`, `0 warnings`, and `0 info`?
2. Are source-pack JSON output, lint semantics, strict-mode behavior, and CLI
   command flow unchanged?
3. Are tests sufficient and scoped to source-pack lint output?
4. Are entity-pack and community-signal lint outputs intentionally untouched?
5. Are there any critical or important findings before release verification?

Return critical, important, and minor findings. If there are no blocking
findings, say so explicitly.
