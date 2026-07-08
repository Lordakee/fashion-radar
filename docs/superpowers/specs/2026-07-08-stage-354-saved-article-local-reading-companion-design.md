# Stage 354 Saved Article Local Reading Companion Design

## Goal

Improve each generated local article page (`articles/<story-id>.html`) with a
local reading companion that helps readers understand the saved article in the
context of the day's saved article library.

The feature should make local pages feel like first-class ROW ONE reading
surfaces, not just article text dumps or outbound link holders.

## Product Scope

- Add an optional `Saved Article Local Reading Companion` section to local article
  pages.
- Render it after `Local Article Information` and before the full saved article
  body.
- Show:
  - the current article's saved-library context;
  - local article text-source status;
  - the best same-day organization group that contains the article;
  - a small "read next locally" list linking to other generated local article
    pages when available;
  - same-page anchors for digest, reader, evidence, and content sections.
- Keep all navigation local-first. Use generated `articles/*.html` pages where
  they exist, with detail-page anchors only as fallback.

## Non-Goals

- No app contract, schema, runtime, manifest, or JSON artifact changes.
- No new scraping, source fetching, social connectors, LLM calls, ranking
  systems, personalization, analytics, scheduling, deployment, or compliance
  review behavior.
- No mutation of stored article text, paragraph indices, content sections, or
  extracted source records.
- No outbound links as the primary navigation target.

## Data Sources

Reuse existing in-memory render inputs:

- `RowOneStory`
- `RowOneLocalArticle`
- `RowOneSavedArticleLibrary`
- `RowOneSavedArticleContentOrganization`
- `local_article_page_hrefs_by_detail_path`

The builder must sanitize all route-derived inputs with existing helpers:

- `safe_local_article_story_id`
- `validated_row_one_detail_relative_path`
- `safe_row_one_detail_fragment_href`

## Rendering Rules

- Return `None` when the current story cannot be matched safely to a saved
  library entry or when no meaningful companion rows can be built.
- Prefer links to `articles/<story-id>.html#local-article-digest`.
- Fall back to `../details/<detail>.html#local-article-content-section-N` only
  when a local article page is unavailable.
- Cap companion rows so the page remains focused.
- Deduplicate by canonical detail path.
- Escape all rendered text in `templates.py`.

## Acceptance Criteria

- Local article pages can render the companion without changing site contracts.
- The companion appears only on eligible generated article pages.
- Companion links are safe, local-first, and deduped.
- Tests cover builder selection, safe-link filtering, template rendering, site
  integration, docs references, and workflow guard coverage.
