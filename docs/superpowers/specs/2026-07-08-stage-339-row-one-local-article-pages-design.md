# Stage 339 ROW ONE First-Class Local Article Pages Design

## Objective

Stage 339 makes ROW ONE feel more like a complete daily fashion news website by generating first-class local article pages at `articles/<story-id>.html` for saved local article bodies that already exist in the current edition.

The current generated site has `articles/index.html` as an organized library and embeds local article bodies inside signal detail pages under `details/*.html#local-article-*`. That works, but it makes saved article reading feel like a secondary anchor inside a signal page. Stage 339 gives each saved local article its own local reading URL while keeping all existing signal detail anchors intact.

## User-Facing Result

When ROW ONE builds a site with saved local article sidecars:

- `articles/index.html` remains the daily saved article library.
- Each publishable saved local article also gets `articles/<story-id>.html`.
- The saved article library links to the first-class article page as the primary local reading action.
- The article page includes a professional article-style header, source/provenance metadata, bilingual UI controls, article map, paragraph evidence, digest, reader, brief, organized content sections, and full saved text.
- The article page links back to the ROW ONE story detail page and to the daily article library.
- Existing `details/*.html#local-article-*` anchors continue to work for all current modules.

## Scope

### In Scope

- Generate one HTML page per writable saved local article using existing `RowOneLocalArticle` sidecars and current `RowOneEdition` stories.
- Add a reusable template entry point for local article pages, reusing existing local article rendering helpers where possible.
- Add safe internal routes only: `articles/<story-id>.html`, `../details/<story-id>.html`, and same-page `#local-article-*` anchors.
- Update saved article library card actions so the primary read action opens the local article page, while existing detail-anchor links remain available for digest/evidence continuity.
- Add tests for page generation, route safety, library links, no JSON/app contract changes, latest-only cleanup compatibility, and CSS presence.
- Document the stage in `README.md`, `docs/row-one.md`, and workflow/doc guard tests.

### Out of Scope

- No new scraping, fetching, article extraction, platform APIs, connectors, LLM calls, translation service, image generation, ranking, scoring, market grouping, scheduling, deployment, or compliance-review feature.
- No change to `row-one-app/v7`, `row-one-manifest/v1`, `row-one-runtime/v1`, schema files, `data/edition.json`, `data/manifest.json`, or `data/runtime.json` contracts.
- No new JSON artifact such as `data/local-article-pages.json` or `data/saved-article-pages.json`.
- No deletion of existing detail-page local article sections or anchors.

## Architecture

Stage 339 stays inside the ROW ONE static-site render layer.

`render_row_one_site()` already builds `saved_article_library` and writes `articles/index.html`. Stage 339 extends the same article output phase so `_write_saved_article_library_page()` writes both:

1. `articles/index.html`
2. `articles/<safe-story-id>.html` for each current-edition story with a publishable `RowOneLocalArticle`

The article detail route uses the existing story id rather than source URL or article title, because story ids are already validated, stable, and used by `data/articles/<story-id>.json` sidecars. Route validation must reject unsafe story IDs and unsafe detail paths instead of canonicalizing arbitrary paths.

The renderer must compute one eligibility map before rendering article outputs. That map should contain only current-edition stories whose story id is safe, whose detail path validates, whose local article exists, whose `article.story_id` matches, and whose local article body renders non-empty. `articles/index.html` may link to `articles/<story-id>.html` only when the entry's validated detail path is present in this eligibility map. Direct template calls that do not provide the eligibility map must not invent first-class article-page links.

## Template Design

Add `render_local_article_page_html(edition, story, local_article)` in `templates.py`.

The template should:

- Use `../assets/row-one.css` and `../assets/row-one.js`.
- Use the same bilingual toggle markup as existing pages.
- Render a header with links to `../index.html`, `index.html`, and `../<story.detail_path>` after validating the detail path.
- Render source/provenance metadata through the existing `_render_local_article()` body where possible.
- Keep the local article section id and internal anchors stable: `#local-article`, `#local-article-reader`, `#local-article-digest`, `#local-article-paragraph-N`, `#local-article-content-section-N`, and `#local-article-paragraph-evidence`.
- Avoid outbound article URLs as primary navigation. If existing provenance includes an original URL, it remains the existing local article provenance behavior, not a new Stage 339 outbound article-page CTA.

The article page is a first-class local page, but it should not create a new app-facing contract surface.

## Link Model

Stage 339 introduces a local article HTML route helper in the render layer:

- Input: `RowOneStory.id`
- Validation: `safe_local_article_story_id(story.id)` must pass.
- Output: `articles/<story.id>.html`

From `articles/index.html`, links to local article pages are page-local relative paths such as `<story-id>.html`.

From `articles/<story-id>.html`, links use:

- `index.html` for the article library.
- `../index.html` for ROW ONE homepage.
- `../details/<story-id>.html` for the signal detail page.
- Same-page anchors for local article sections.

Existing library digest/evidence links to `../details/*.html#local-article-*` can remain for continuity, but the primary reader link should become `<story-id>.html`.

## Safety Invariants

- Only current-edition stories can receive article pages.
- `article.story_id` must equal `story.id`.
- `safe_local_article_story_id(story.id)` must pass.
- `story.detail_path` must pass existing detail-route validation before it is linked.
- Empty or skipped articles with no rendered paragraphs must not produce pages.
- Empty template output must not be written as an article page even if earlier eligibility checks passed.
- `articles/index.html` first-class article-page links must be allowlisted by the same eligibility map used to write `articles/<story-id>.html`.
- `articles/index.html` must not link to arbitrary external article routes for Stage 339.
- Generated article pages must not introduce JSON contract vocabulary into app/runtime/manifest payloads.

## Testing Strategy

Tests should verify:

- `render_row_one_site()` writes `articles/<story-id>.html` when a saved local article is publishable.
- The generated local article page contains local article reader/digest/map/body anchors and links back to the library and detail page.
- The article library card includes a primary link to `<story-id>.html`.
- Unsafe story ids, mismatched `article.story_id`, and empty article bodies do not generate article pages.
- Unsafe detail paths keep the existing render-level `ValueError` behavior from detail-page generation; Stage 339 should not weaken or mask that failure.
- Direct library template rendering does not emit first-class article-page links unless a generated-page allowlist is provided.
- `latest_only=True` cleanup removes stale article pages through the existing generated `articles/` directory cleanup.
- `data/edition.json`, `data/manifest.json`, and `data/runtime.json` contract versions remain unchanged and their serialized JSON text does not contain Stage 339 page vocabulary.
- CSS contains selectors for any new article-page shell classes.
- Existing detail-page anchors and article library behavior continue to pass.

## Documentation

Update:

- `README.md` stage history with Stage 339 boundaries.
- `docs/row-one.md` article library/local article page docs.
- `tests/test_row_one_docs.py` and `tests/test_workflows.py` with guard assertions that Stage 339 is generated-site-only and contract-stable.

## Definition of Done

Stage 339 is complete when:

- First-class local article pages are generated for publishable saved local articles.
- Library cards expose those pages as the primary local reading route.
- Existing detail-page local article anchors remain available.
- No JSON/app/runtime/manifest contract changes are introduced.
- Focused tests, full pytest, ruff, format check, lock check, release hygiene, first-run smoke, secret scan, Claude Code review, commit, and push all pass.
