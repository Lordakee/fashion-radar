# Claude Code Review Request — Stage 320 ROW ONE Homepage Daily Edit

Please review the current uncommitted Stage 320 changes in `/home/ubuntu/fashion-radar`.

## Goal

Stage 320 adds a generated-site-only ROW ONE homepage `Daily Edit / 今日编辑简报` section. The section should make the homepage more useful as an information-organizing surface, not just a link directory.

## Intended Scope

- Render HTML only in `render_index_html()`.
- Insert Daily Edit after `signal_synthesis` and before `daily_local_intelligence`.
- Reuse only existing payload data:
  - `edition_brief`
  - `signal_synthesis`
  - `daily_digest.briefing_topics`
  - `daily_digest.blocks`
  - existing story-directory/detail href payloads
- Keep links internal and safe.
- Escape all payload strings.
- Omit the section when `app_payload` is missing or unusable.

## Explicit Non-Goals

- Do not add `daily_edit` or `daily_information_layer` to `data/edition.json`.
- Do not change `row-one-app/v7`, manifest/runtime contract versions, schemas, source collection, fetching, scoring, LLM calls, connectors, or image generation.
- Do not add compliance-review product features.
- Do not add dependencies.

## Files To Review

- `src/fashion_radar/row_one/templates.py`
- `tests/test_row_one_render.py`
- `tests/test_workflows.py`
- `tests/test_row_one_docs.py`
- `README.md`
- `docs/row-one.md`
- `docs/superpowers/specs/2026-07-07-stage-320-row-one-homepage-daily-edit-design.md`
- `docs/superpowers/plans/2026-07-07-stage-320-row-one-homepage-daily-edit-plan.md`

## Verification Already Run

- `UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_render.py::test_render_row_one_site_includes_daily_edit_section tests/test_row_one_render.py::test_render_row_one_site_places_daily_edit_before_daily_local_intelligence tests/test_row_one_render.py::test_render_row_one_site_omits_daily_edit_without_usable_payload tests/test_row_one_render.py::test_render_row_one_site_escapes_daily_edit_payload_values tests/test_row_one_render.py::test_render_row_one_site_daily_edit_uses_briefing_topic_fallback tests/test_row_one_render.py::test_render_row_one_site_daily_edit_uses_digest_block_read_next tests/test_row_one_render.py::test_row_one_css_includes_daily_edit_styles -q`
- `UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_render.py tests/test_workflows.py::test_write_row_one_site_files_writes_local_article_without_mutating_sqlite tests/test_row_one_docs.py -q`
- `UV_NO_CONFIG=1 uv --no-config run --frozen ruff check --fix src/fashion_radar/row_one/templates.py tests/test_row_one_render.py tests/test_workflows.py tests/test_row_one_docs.py README.md docs/row-one.md`
- `UV_NO_CONFIG=1 uv --no-config run --frozen ruff format src/fashion_radar/row_one/templates.py tests/test_row_one_render.py tests/test_workflows.py tests/test_row_one_docs.py`
- `UV_NO_CONFIG=1 uv --no-config run --frozen ruff check`
- `UV_NO_CONFIG=1 uv --no-config run --frozen ruff format --check`
- `git diff --check`

## Review Requested

Please identify Critical or Important issues first. Focus on:

1. Whether the implementation matches the Stage 320 scope and non-goals.
2. Whether the fallback logic is technically sound and maintainable.
3. Whether escaping and safe href behavior are adequate.
4. Whether the tests protect the generated-site-only boundary and JSON contract boundary.
5. Whether documentation accurately describes the feature without implying schema/source/fetching changes.

Return a concise review with severity, file references, and any required fixes.
