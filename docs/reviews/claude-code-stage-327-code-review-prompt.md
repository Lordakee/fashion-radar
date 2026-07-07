# Claude Code Stage 327 Code Review Prompt

Review the current uncommitted Stage 327 changes in `/home/ubuntu/fashion-radar`.

## Goal

Stage 327 adds a ROW ONE **Saved Signal Index / 本地信号索引** to the generated saved article library page. It should organize already saved local article references by fashion signals such as brands, designers, people, products, bags, shoes, and celebrities.

## Scope Boundaries

- The signal index must be embedded only inside existing `articles/index.html`, after the saved article library hero and before the source-grouped library grid.
- Do not add a standalone generated child page such as `saved-signal-index.html` or `articles/saved-signal-index.html`.
- Do not add a JSON sidecar such as `data/saved-signal-index.json`.
- Do not change `edition.json`, `manifest.json`, `runtime.json`, app contracts, schemas, Pydantic models, source collection, fetching, extraction, scoring, ranking, LLM, connectors, scheduling, deployment, or compliance-product behavior.
- Hrefs, filenames, fragments, classes, and ids must never be derived from display strings such as signal names, labels, source names, titles, or content-section titles.

## Main Files To Review

- `src/fashion_radar/row_one/saved_signal_index.py`
- `src/fashion_radar/row_one/render.py`
- `src/fashion_radar/row_one/templates.py`
- `tests/test_row_one_saved_signal_index.py`
- `tests/test_row_one_render.py`
- `tests/test_workflows.py`
- `tests/test_row_one_docs.py`
- `README.md`
- `docs/row-one.md`
- `docs/superpowers/specs/2026-07-07-stage-327-row-one-saved-signal-index-design.md`
- `docs/superpowers/plans/2026-07-07-stage-327-row-one-saved-signal-index-plan.md`

## Verified Locally Before Review

- `UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_saved_signal_index.py tests/test_row_one_render.py tests/test_workflows.py tests/test_row_one_docs.py -q`
  - Result: `231 passed`
- `UV_NO_CONFIG=1 uv --no-config run --frozen ruff check src/fashion_radar/row_one/saved_signal_index.py src/fashion_radar/row_one/templates.py src/fashion_radar/row_one/render.py tests/test_row_one_saved_signal_index.py tests/test_row_one_render.py tests/test_workflows.py tests/test_row_one_docs.py`
  - Result: `All checks passed!`
- `UV_NO_CONFIG=1 uv --no-config run --frozen ruff format --check src/fashion_radar/row_one/saved_signal_index.py src/fashion_radar/row_one/templates.py src/fashion_radar/row_one/render.py tests/test_row_one_saved_signal_index.py tests/test_row_one_render.py tests/test_workflows.py tests/test_row_one_docs.py`
  - Result: `7 files already formatted`

## Review Request

Please review as a code reviewer. Focus on:

1. Correctness of saved signal extraction, grouping, allowed reference types, strength ordering, support counts, paragraph-link behavior, and caps.
2. Safety of template rendering and href validation, especially unsafe path/fragment handling and display-string escaping.
3. Compliance with Stage 327 scope boundaries: embedded page only, no JSON/app contract/runtime/schema changes, no new child page.
4. Test strength and whether important edge cases are missing.
5. Any technical debt or maintainability concerns that should block this node.

Return findings first, ordered by severity: Critical, Important, Medium, Minor. Include exact file/line references and concrete fixes. If no Critical or Important issues remain, state that explicitly. Do not edit files.
