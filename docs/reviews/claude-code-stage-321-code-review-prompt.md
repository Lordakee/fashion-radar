You are reviewing Stage 321 of the Fashion Radar / ROW ONE project.

Objective:
- Add a generated-site-only ROW ONE homepage Editorial Brief / 编辑正文 section.
- The section must improve local information organization by rendering up to 3 bilingual editorial cards from existing RowOneStory and RowOneLocalArticle data.
- This must remain HTML-only: do not add `editorial_brief` to edition/runtime/manifest JSON contracts, schemas, data files, collectors, connectors, LLM calls, image generation, deployment, or compliance behavior.

Implementation summary:
- `src/fashion_radar/row_one/templates.py`
  - Adds private `_EditorialBrief` / `_EditorialBriefItem` dataclasses and constants.
  - `render_index_html()` accepts optional `editorial_brief` and renders it after saved article content organization and before lead story.
  - Adds `_render_editorial_brief`, `_render_editorial_brief_card`, `_safe_editorial_brief_href`, and CSS.
  - Hrefs allow only existing validated detail paths plus local article paragraph/content-section fragments.
- `src/fashion_radar/row_one/render.py`
  - Builds `_EditorialBrief` from the lead usable story and matching local article.
  - Uses story editorial fields plus local article brief_sections when available.
  - Passes the object to `render_index_html()` only; no JSON serialization.
- Tests:
  - `tests/test_row_one_render.py` covers rendering, omission, escaping, link filtering, fallback, accepted fragments, cap, truncation, dedupe, empty items.
  - `tests/test_workflows.py` asserts the generated HTML contains the section and contract JSON does not contain `editorial_brief`.
  - `tests/test_row_one_docs.py`, `README.md`, and `docs/row-one.md` document the boundary.

Review the working tree diff against HEAD. Focus on:
1. Correctness of generated HTML behavior and bilingual content assembly.
2. Contract safety: no new JSON fields/artifacts or schema drift.
3. Link safety and escaping/XSS safety.
4. Whether tests actually protect the intended behavior.
5. Scope creep or coupling risks.

Commands already run before this review:
- `UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_render.py tests/test_workflows.py::test_write_row_one_site_files_writes_local_article_without_mutating_sqlite tests/test_row_one_docs.py -q` -> 168 passed.
- `UV_NO_CONFIG=1 uv --no-config run --frozen ruff check --fix src/fashion_radar/row_one/render.py src/fashion_radar/row_one/templates.py tests/test_row_one_render.py tests/test_workflows.py tests/test_row_one_docs.py` -> passed.
- `UV_NO_CONFIG=1 uv --no-config run --frozen ruff format src/fashion_radar/row_one/render.py src/fashion_radar/row_one/templates.py tests/test_row_one_render.py tests/test_workflows.py tests/test_row_one_docs.py` -> unchanged.
- `UV_NO_CONFIG=1 uv --no-config run --frozen ruff check` -> passed.
- `UV_NO_CONFIG=1 uv --no-config run --frozen ruff format --check` -> passed.
- `git diff --check` -> passed.

Return findings grouped by severity: Critical, Important, Minor. If no Critical/Important issues, say so explicitly. Do not rewrite the implementation; give actionable review findings only.
