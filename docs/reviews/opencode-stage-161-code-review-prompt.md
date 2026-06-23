# Stage 161 Code Review Prompt

Review the Stage 161 implementation for Fashion Radar.

Return only the completed review body. Do not include process chatter, live tool
status, ANSI output, or command logs. Start the response exactly with:

```text
# Stage 161 Code Review
```

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

Objective:

Show deterministic source tag counts in the default human table output from
`fashion-radar source-pack-lint`.

Implementation summary:

- Added a RED renderer test for `Tags: gdelt=2, runway=1, shoes=1` between
  `Types:` and `Findings:`.
- Strengthened the public-pack CLI table smoke to assert `Tags:` is present.
- Added `Tags: {_format_counts(result.tag_counts)}` to
  `render_source_pack_lint_table(...)`.
- Updated `docs/source-pack-quality.md` table sample and summary bullet.

Verification already run:

```bash
uv --no-config run --frozen pytest tests/test_source_packs.py::test_render_source_pack_lint_table_includes_tag_counts tests/test_cli.py::test_source_pack_lint_prints_table_for_public_pack -q
# RED before implementation: 2 failed.
# GREEN after implementation: 2 passed.

uv --no-config run --frozen pytest tests/test_source_packs.py tests/test_cli.py -k "source_pack_lint" -q
# 8 passed, 301 deselected.

uv --no-config run --frozen pytest tests/test_source_pack_quality_docs.py tests/test_source_packs.py tests/test_cli.py -k "source_pack" -q
# 21 passed, 291 deselected.

uv --no-config run --frozen ruff check src/fashion_radar/source_packs.py tests/test_source_packs.py tests/test_cli.py
# All checks passed.

uv --no-config run --frozen ruff format --check src/fashion_radar/source_packs.py tests/test_source_packs.py tests/test_cli.py
# 3 files already formatted.
```

Review questions:

1. Does the renderer reuse existing `tag_counts` and `_format_counts(...)`?
2. Does the CLI table output include `Tags:` without changing JSON shape?
3. Are tests sufficient and scoped to source-pack lint output?
4. Does the docs update preserve local/read-only and non-data boundaries?
5. Are there any critical or important findings before release verification?

Return critical, important, and minor findings. If there are no blocking
findings, say so explicitly.
