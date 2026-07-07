You are reviewing newly added Fashion Radar Stage 325 code before commit.

Repository: /home/ubuntu/fashion-radar
Branch: main

Stage 325 objective:
- Close three non-blocking Stage 324 paragraph evidence polish items:
  1. omit an empty refs wrapper when a paragraph evidence support item has no references
  2. fallback to the English body excerpt when `item.body.zh` is blank or whitespace-only
  3. explicitly test that the local article map links to `#local-article-paragraph-evidence`

Implementation summary:
- `tests/test_row_one_render.py`
  - Adds an explicit map slice assertion for `href="#local-article-paragraph-evidence"`.
  - Adds a generated-detail test proving no `<div></div>` reference wrapper is rendered for `references=[]`.
  - Adds a generated-detail test proving whitespace-only `body.zh` falls back to escaped English body text.
- `src/fashion_radar/row_one/templates.py`
  - Adds `_local_article_paragraph_evidence_body_text()`.
  - Uses normalized English fallback for blank/whitespace-only Chinese evidence body text.
  - Renders the reference wrapper only when rendered reference chips exist.
- Stage 325 spec/plan and plan review artifacts were added under `docs/superpowers/` and `docs/reviews/`.

Scope boundaries that must hold:
- No changes to `row-one-app/v7`, `row-one-manifest/v1`, `row-one-runtime/v1`.
- No app JSON, manifest JSON, runtime JSON, schema, Pydantic model, or new artifact fields.
- No source collection, fetching, extraction, scoring, ranking, LLM, translation, image generation, connector, scheduling, deployment, or compliance-review product behavior.
- No new dependencies.

Verification already run:
- `UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_render.py -k "paragraph_evidence" -q`: 8 passed.
- `UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_workflows.py -k "row_one" -q`: 1 passed.
- `UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_docs.py -q`: 47 passed.
- `UV_NO_CONFIG=1 uv lock --check`: passed.
- `UV_NO_CONFIG=1 uv --no-config run --frozen ruff check .`: passed.
- `UV_NO_CONFIG=1 uv --no-config run --frozen ruff format --check .`: passed.
- `git diff --check`: passed.
- secret marker scan for `ghp_...` and `sk-...`: no hits.
- `UV_NO_CONFIG=1 uv --no-config run --frozen pytest -q`: 2153 passed.
- `UV_NO_CONFIG=1 uv --no-config run --frozen python scripts/check_release_hygiene.py`: passed.

Review focus:
1. Correctness of the body fallback and reference wrapper rendering.
2. Whether tests cover the Stage 324 minor review items.
3. Whether generated-site-only and JSON-contract boundaries are preserved.
4. Any regression risk in existing ROW ONE detail render paths.

Return:
- Critical findings, if any.
- Important findings, if any.
- Minor suggestions, if any.
- Final verdict: approved to commit, or not approved until specified changes are fixed.

Do not implement code. This is a read-only code review.
