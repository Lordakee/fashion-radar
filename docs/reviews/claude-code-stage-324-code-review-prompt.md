You are reviewing newly added Fashion Radar Stage 324 code before commit.

Repository: /home/ubuntu/fashion-radar
Branch: main

Stage 324 objective:
- Add a generated-site-only ROW ONE detail-page paragraph evidence index.
- The index maps existing saved local article paragraphs back to existing local article content sections, item labels, and references.
- It must use only existing `RowOneLocalArticle` data already passed to detail rendering.

Implementation summary:
- `src/fashion_radar/row_one/templates.py`
  - Adds private paragraph evidence dataclasses, constants, builder helpers, render helpers, and CSS.
  - Adds `_strict_valid_local_article_paragraph_indices()` to reject bool/non-int paragraph indices before fragment generation.
  - Renders `#local-article-paragraph-evidence` inside `#local-article`, after the local article map and before digest/reader/content blocks.
  - Adds an optional local map link to `#local-article-paragraph-evidence`.
- `tests/test_row_one_render.py`
  - Adds render, omission, invalid-index filtering, bool-helper, escaping, cap, and CSS selector tests.
- `tests/test_workflows.py`
  - Adds generated HTML marker checks and JSON-contract absence checks.
- `README.md`, `docs/row-one.md`, `tests/test_row_one_docs.py`
  - Adds Stage 324 generated-site boundary docs and test.
- Stage 324 spec/plan/review artifacts were added under `docs/superpowers/` and `docs/reviews/`.

Scope boundaries that must hold:
- No changes to `row-one-app/v7`, `row-one-manifest/v1`, `row-one-runtime/v1`.
- No app JSON, manifest JSON, runtime JSON, schema, Pydantic model, or new artifact fields.
- No source collection, fetching, extraction, scoring, ranking, LLM, translation, image generation, connector, scheduling, deployment, or compliance-review product behavior.
- No new dependencies.

Verification already run:
- `UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_render.py -k "paragraph_evidence or local_article_map_styles" -q`: 7 passed.
- `UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_workflows.py -k "row_one" -q`: 1 passed.
- `UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_docs.py -q`: 47 passed.
- `UV_NO_CONFIG=1 uv --no-config run --frozen ruff check .`: passed.
- `UV_NO_CONFIG=1 uv --no-config run --frozen ruff format --check .`: passed.
- `UV_NO_CONFIG=1 uv lock --check`: passed.
- `UV_NO_CONFIG=1 uv --no-config run --frozen python scripts/check_release_hygiene.py`: passed.
- `git diff --check`: passed.
- `UV_NO_CONFIG=1 uv --no-config run --frozen pytest -q`: 2151 passed.

Review focus:
1. Correctness of paragraph evidence mapping, caps, dedupe, escaping, and local anchors.
2. Whether tests adequately cover the new behavior.
3. Whether generated-site-only and JSON-contract boundaries are preserved.
4. Whether docs/review artifacts are clean enough to commit.
5. Any regression risk in existing ROW ONE render paths.

Return:
- Critical findings, if any.
- Important findings, if any.
- Minor suggestions, if any.
- Final verdict: approved to commit, or not approved until specified changes are fixed.

Do not implement code. This is a read-only code review.
