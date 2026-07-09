# Stage 367 Saved Article Filing Inbox Plan Review

## Reviewer 1: Bohr

READY FOR IMPLEMENTATION

- No blockers found. The design and plan stay scoped to `articles/index.html` and explicitly exclude homepage, detail pages, first-class article pages, app JSON, schemas, runtime/manifest contracts, new routes, generated sidecars, and compliance behavior.
- Architecture is feasible. A small builder using `RowOneEdition`, current `RowOneLocalArticle` sidecars, existing local article hrefs, and item-level `paragraph_indices` matches the requested ROW ONE boundary.
- TDD is concrete enough. The plan has clear RED tests for builder behavior, renderer placement, CSS hooks, generated-contract denylist, artifact denylist, docs guards, and full verification commands.
- Key safety constraints are covered. Invalid indices, bool/string indices, negative/overflow values, blanks, duplicates, unsafe hrefs, escaping, and one-based paragraph anchors are all addressed.
- Clarification: artifact denylist should be interpreted as generated artifact path/name denylisting, not HTML content denylisting, because `articles/index.html` intentionally contains `saved-article-filing-inbox`.
- Minor test hygiene note: avoid brittle workflow guards that directly call other tests where a shared helper is cleaner.

## Reviewer 2: Turing

READY FOR IMPLEMENTATION WITH PLAN CORRECTIONS

- Stage 367 is feasible with a small isolated builder plus optional HTML view-model parameter.
- Prefer building the inbox inside `_write_saved_article_library_page(...)` after `_write_local_article_pages(...)` returns `article_page_hrefs_by_detail_path`; this keeps the scope tighter than passing another model through `render_row_one_site(...)`.
- Keep `render_saved_article_library_html(...)` parameter optional with a default to avoid breaking direct render tests.
- Use `model_construct()` or direct helper tests for invalid paragraph-index values because Pydantic may coerce/reject non-int values before the builder sees them.
- Renderer-side href validation must allow only `story-id.html#local-article-paragraph-N` and must not reuse the reading-queue digest href helper.
- Keep the filing inbox out of app/runtime/manifest payloads and avoid adding source collection, schemas, routes, or JSON artifacts.

## Implementation Decision

Proceed with Stage 367 using Turing's insertion-point correction: build the filing inbox inside `_write_saved_article_library_page(...)` from the already materialized local article href map, then render it only in `articles/index.html`.
