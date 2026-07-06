You are re-reviewing Stage 321 of the Fashion Radar / ROW ONE project after fixes from the first code review.

Objective:
- Add a generated-site-only ROW ONE homepage Editorial Brief / 编辑正文 section.
- The section renders up to 3 bilingual editorial cards from existing RowOneStory and RowOneLocalArticle data.
- This remains HTML-only: no `editorial_brief` JSON contract field, no schema changes, no source collection/fetching/extraction/scoring/LLM/deployment/compliance changes.

First review Important findings and fixes:
1. Duplicate deduplication across render/template boundary.
   - Fixed by keeping dedupe in `render.py` builder only. Template now renders the passed payload and caps item count.
2. Triple truncation and unclear `_EditorialBriefItem.body` invariant.
   - Fixed by removing builder truncation. Template truncates body text once at render time.
3. Misleading link-filter test.
   - Fixed by removing the cap-driven negative assertion and adding explicit paragraph-fragment accept and unknown-fragment reject tests.

Please review the current working tree diff against HEAD again. Focus on:
1. Whether the first review's Critical/Important concerns are actually resolved.
2. Whether the current generated-site-only boundary is still intact.
3. Link safety and escaping/XSS safety.
4. Whether the revised tests are aligned to the correct layer.
5. Any new regressions introduced by the fixes.

Fresh commands run after fixes:
- `UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_render.py tests/test_workflows.py::test_write_row_one_site_files_writes_local_article_without_mutating_sqlite tests/test_row_one_docs.py -q` -> 170 passed.
- `UV_NO_CONFIG=1 uv --no-config run --frozen ruff check --fix src/fashion_radar/row_one/render.py src/fashion_radar/row_one/templates.py tests/test_row_one_render.py tests/test_workflows.py tests/test_row_one_docs.py` -> passed.
- `UV_NO_CONFIG=1 uv --no-config run --frozen ruff format src/fashion_radar/row_one/render.py src/fashion_radar/row_one/templates.py tests/test_row_one_render.py tests/test_workflows.py tests/test_row_one_docs.py` -> formatted one file.
- `UV_NO_CONFIG=1 uv --no-config run --frozen ruff check` -> passed.
- `UV_NO_CONFIG=1 uv --no-config run --frozen ruff format --check` -> passed.
- `git diff --check` -> passed.

Return findings grouped by severity: Critical, Important, Minor. If no Critical/Important issues remain, say so explicitly. Give actionable findings only.
