Review the current uncommitted Stage 335 implementation for Fashion Radar / ROW ONE.

Context:
- Repo: `/home/ubuntu/fashion-radar`
- Baseline: `origin/main`
- Stage 335 goal: add generated-site-only Saved Article Reading Paths inside
  `articles/index.html`.
- Implementation approach:
  - New private builder:
    `src/fashion_radar/row_one/saved_article_reading_paths.py`
  - Builder derives reading path view models from existing
    `RowOneSavedArticleLibrary` and `RowOneSavedArticleContentOrganization`.
  - Renderer passes reading paths only into the generated saved article library
    page.
  - Template renders capped local leads/snippets plus safe generated detail-page
    anchors after the saved signal index and before saved article content
    organization.
- Scope boundary: no app/runtime/manifest/schema/JSON contract changes; no
  `data/saved-article-reading-paths.json`; no full article publication on the
  library index; no collection, fetching, extraction, scoring, ranking, LLM,
  connector, scheduling, deployment, social/community, or compliance-review
  behavior changes.

Files expected to change:
- `src/fashion_radar/row_one/saved_article_reading_paths.py`
- `src/fashion_radar/row_one/render.py`
- `src/fashion_radar/row_one/templates.py`
- `tests/test_row_one_saved_article_reading_paths.py`
- `tests/test_row_one_render.py`
- `tests/test_row_one_docs.py`
- `README.md`
- `docs/row-one.md`
- Stage 335 plan/review docs under `docs/superpowers/` and `docs/reviews/`

Focused verification already run:
- `UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_saved_article_reading_paths.py -q`
- `UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_render.py -q -k "reading_path or saved_article_library or content_organization or row_one_css"`
- `UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_docs.py::test_row_one_docs_describe_stage_335_saved_article_reading_paths_boundary -q`
- `UV_NO_CONFIG=1 uv --no-config run --frozen ruff check src/fashion_radar/row_one/saved_article_reading_paths.py src/fashion_radar/row_one/render.py src/fashion_radar/row_one/templates.py tests/test_row_one_saved_article_reading_paths.py tests/test_row_one_render.py tests/test_row_one_docs.py`
- `UV_NO_CONFIG=1 uv --no-config run --frozen ruff format ...`

Please inspect the uncommitted diff and review for:
1. correctness of the reading-path builder, capping, dedupe, canonicalization,
   and partial-safe saved-library route behavior;
2. renderer/template safety for unsafe direct-render view models, including
   traversal, `javascript:`, wrong fragments, `section-0`, and `section-01`;
3. generated-site-only contract boundaries and JSON/app payload non-leakage;
4. whether the section avoids full article republication and only renders capped
   local leads/snippets;
5. test sufficiency and brittleness;
6. docs consistency and whether any plan/review artifact should not be committed.

Output format:
- Verdict: Ready / Needs fixes
- Critical issues
- Important issues
- Minor issues
- Required fixes before commit/push

Focus on actual blockers. Do not request compliance-review product features.
