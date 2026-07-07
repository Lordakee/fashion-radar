# Stage 336 ROW ONE Saved Article Theme Digest Design

## Goal

Make `articles/index.html` more useful as a daily information-organizing page by
adding a generated-site-only "Saved Article Theme Digest" near the top of the
saved article library. The digest should summarize recurring themes from
already-saved local fashion text so a reader can quickly see where the day's
brand, product, person/designer, and source-structure signals concentrate
before opening individual source cards.

## Current Gap

Stages 326-335 turned the generated saved article library into a local reading
surface with source grouping, signal indexing, content groups, local excerpts,
and reading paths. The page now exposes saved local text and helps readers move
through it, but it still lacks a compact "what is this saved article set saying
today?" layer above the indexes.

The existing saved article content organization already carries the right source
material, and Stage 335 reading paths remain a downstream navigation surface.
Stage 336 should add a deterministic digest layer that organizes the saved
content-organization input into a concise local theme briefing without adding
new collection, extraction, ranking, LLM, or JSON contract behavior.

## Chosen Approach

Add a small private generated-site view model for saved article theme digest
cards:

- Build the digest from existing `RowOneSavedArticleLibrary`,
  `RowOneSavedArticleContentOrganization`, and the safe local anchors already
  present on content-organization cards.
- Keep the theme taxonomy deterministic and aligned with the existing content
  groups: Read First, People & Brands, Products, and Source Structure.
- Select capped cards from already-safe content-organization cards, then link
  only to existing generated detail-page anchors.
- Display compact theme cards after the saved article library hero and before
  saved signal index / reading paths / content organization.
- Keep all behavior generated-site-only and internal to the HTML renderer.

This gives ROW ONE a visible daily organizing layer for saved local content
without producing new summaries, changing the app payload, or publishing full
article bodies on the library index.

## Why A New Builder Instead Of Template-Only

The theme digest has selection behavior that should be directly testable:
dedupe, safe-route intersection, theme capping, item capping, source counts, and
safe anchor selection. Keeping those rules in a small builder such as
`saved_article_theme_digest.py` avoids burying product behavior in
`templates.py` and mirrors Stage 335's reading-path pattern.

The builder should stay private to the generated ROW ONE site. It should not
write files and should not be serialized into public app/runtime/manifest JSON.

## UI Behavior

When all sections exist, `articles/index.html` should render this order:

1. saved article library hero;
2. saved article theme digest;
3. saved signal index;
4. saved article reading paths;
5. saved article content organization;
6. source-grouped saved article library cards.

The theme digest section should include:

- bilingual section title:
  - `Saved Article Theme Digest`
  - `保存文章主题简报`
- a compact bilingual dek that frames the cards as recurring themes from the
  current saved local article set;
- up to four theme cards;
- each theme card should show theme title, theme dek, local-lead/source counts,
  capped local leads, safe detail-page links, and optional reference chips;
- no outbound article URLs;
- no full article body republication.

The digest should feel like a professional fashion-news desk briefing: dense,
editorial, and scannable. It should not become another large index or marketing
hero.

## Data Flow

1. `render_row_one_site()` already builds `saved_article_library`,
   `saved_article_content_organization`, and `saved_article_reading_paths`.
2. Stage 336 adds `build_row_one_saved_article_theme_digest()` and calls it with
   the existing saved article library and content organization objects.
3. `_write_saved_article_library_page()` receives the digest and passes it into
   `render_saved_article_library_html()`.
4. `render_saved_article_library_html()` renders the digest immediately after
   the hero.
5. The homepage and generated JSON contracts remain unchanged.

## Safety And Contract Boundaries

Do not change:

- `row-one-app/v7`
- `data/edition.json`
- `row-one-manifest/v1`
- `row-one-runtime/v1`
- JSON schemas
- `data/articles/<story-id>.json` sidecar schema
- source collection
- fetching
- matching
- extraction
- scoring
- ranking
- LLM behavior
- connector behavior
- scheduling
- deployment behavior
- market grouping
- domestic/international classification
- compliance-review product behavior

Do not add:

- full article republication on `articles/index.html`
- outbound article URLs in the theme digest
- new extraction or crawling behavior
- new summary generation behavior
- new social/community platform behavior
- `data/saved-article-theme-digest.json`
- any generated JSON contract for this section

Primary digest links must validate generated detail paths and
`#local-article-content-section-N` anchors before prefixing `../`. Optional
paragraph evidence links may be derived only from validated item
`paragraph_indices` and rendered as `#local-article-paragraph-N` anchors.
Unsafe routes, traversal, wrong fragments, and `javascript:` routes must omit the
unsafe item or unsafe link from the theme digest.

## Tests

Add tests that prove:

- the builder derives theme cards from existing saved article library/content
  organization inputs and omits empty input;
- the builder caps themes and items deterministically;
- duplicate detail/lead combinations collapse within a theme;
- unsafe or non-library-matching detail paths do not render;
- `articles/index.html` renders `Saved Article Theme Digest` /
  `保存文章主题简报` after the hero and before saved signal index;
- rendered cards show existing local leads, source counts, safe internal links,
  and optional reference chips;
- long local leads are truncated and escaped;
- generated JSON artifacts do not expose theme-digest vocabulary or local text;
- no `data/saved-article-theme-digest.json` file is generated;
- `README.md` and `docs/row-one.md` document the Stage 336 generated-site-only
  boundary.

## Out Of Scope

- No social/community platform expansion.
- No crawler/source work.
- No new article extraction dependency.
- No LLM-generated summaries.
- No full-article publication on the library index.
- No app contract change.
- No generated images.
- No broad ROW ONE visual redesign.
- No compliance-review functionality.
