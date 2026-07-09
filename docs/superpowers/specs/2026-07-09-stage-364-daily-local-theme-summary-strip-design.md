# Stage 364 Daily Local Theme Summary Strip Design

## Context

Stages 357-363 added homepage sections that organize already-saved local article bodies by key signals, momentum, heat, article capsules, reading lanes, source provenance, and source-by-bucket coverage. Those sections make the ROW ONE homepage navigable, but readers still need a compact editorial strip that turns the existing saved local content organization into a readable daily theme summary before they reach the full Saved Article Content Organization grid.

## Goal

Add a generated-site-only homepage section named **Daily Local Theme Summary Strip**. It should sit after Daily Local Coverage Map and before Saved Article Content Organization. It should summarize the current edition's existing saved article content organization groups as compact theme cards using only already-downloaded local article text, existing group titles/deks, existing card leads, existing card references, existing source names, generated local article page routes, and existing local article content-section or paragraph anchors.

The feature should make ROW ONE feel more like a finished daily fashion briefing: the homepage gives readers a quick theme-level digest of what the saved local text says, with safe same-site links into locally saved article pages, without asking the user to leave the generated site.

## Non-Goals

- Do not add app-facing schema or payload fields.
- Do not create `data/daily-local-theme-summary-strip.json`, `data/local-theme-summary-strip.json`, or `data/theme-summary-strip.json`.
- Do not create new route families or standalone HTML artifacts.
- Do not alter `articles/index.html`, `articles/<story-id>.html`, or detail pages.
- Do not publish full articles on the homepage.
- Do not add outbound article URLs as primary navigation.
- Do not call or extend `build_row_one_saved_article_theme_digest`; this feature derives directly from existing organization cards and local article page href maps.
- Do not add fetching, extraction, scoring, ranking, LLM, connector, scheduling, deployment, analytics, personalization, recommendation, or compliance-review behavior.

## Design

The homepage renderer derives a theme summary strip from:

- existing `RowOneSavedArticleContentOrganization` groups and cards;
- already-saved local articles for current-edition stories;
- generated local article page hrefs keyed by safe detail path;
- existing card leads, source names, references, paragraph indices, and detail-path fragments.

Each rendered theme card corresponds to one eligible organization group. A group is eligible when at least one card can be resolved to:

- a safe `details/<story-id>.html` detail path;
- a current saved local article whose `story_id` matches the detail-path story id;
- at least one usable local paragraph;
- a safe generated local article page href supplied by the site renderer;
- either a renderable `#local-article-content-section-N` fragment or a fallback safe paragraph anchor.

Each theme card renders:

- bilingual group title;
- a short bilingual summary line derived from the existing group dek when present, otherwise from the first eligible card lead;
- card count, source count, local article count, and saved paragraph count;
- up to five deduped reference chips from existing card references;
- up to two same-site links into local article page anchors.

The strip is deterministic and compact. Sort themes by:

1. eligible card count descending;
2. local article count descending;
3. saved paragraph count descending;
4. original organization group order ascending.

Cap the strip at four theme cards. Cap references and links per theme to keep the homepage readable. Truncate long lead/summary text to a short excerpt; do not render saved paragraph bodies or full article content in this section.

## Rendering Boundary

The feature renders only inside homepage `index.html`. It must not write or mutate:

- `articles/index.html`;
- `articles/<story-id>.html`;
- story detail pages;
- `data/edition.json`;
- `data/manifest.json`;
- `data/runtime.json`;
- local article sidecar JSON.

## Placement

When present, the section renders after:

- `.daily-local-coverage-map`

and before:

- `.saved-article-content-organization`

If Daily Local Coverage Map is absent, Daily Local Theme Summary Strip still uses the same relative homepage slot before Saved Article Content Organization.

## Link Safety

The renderer must not derive local article hrefs from story ids alone. It must use only the generated detail-path-to-local-article-page href map passed by the site renderer and validate resulting hrefs as same-site local article routes.

Rendered links must be same-site:

- `articles/<story-id>.html#local-article-content-section-N`; or
- `articles/<story-id>.html#local-article-paragraph-N` when a content-section anchor is unavailable.

Unsafe absolute paths, nested paths, traversal, whitespace hrefs, mismatched story ids, missing local articles, empty local articles, blank source names, malformed fragments, and unrenderable content-section anchors are filtered out.

## Testing Strategy

Tests should follow Stage 360-363 patterns:

- direct render test for theme grouping, ordering, caps, counts, source/reference dedupe, lead/dek truncation, same-site local links, bilingual headings, and escaping;
- filtering test for unsafe detail paths, unsafe local article hrefs, missing local articles, mismatched local article story ids, empty paragraphs, blank source names, and invalid paragraph indices;
- placement test after Daily Local Coverage Map and before Saved Article Content Organization;
- placement test when Daily Local Coverage Map is absent, proving the theme strip still renders before Saved Article Content Organization;
- site-generation test proving homepage-only behavior and generated contract/artifact denylist;
- CSS selector test;
- docs boundary test in README and `docs/row-one.md`;
- workflow generated-site-only guard test.

## Review Notes

This is intentionally a presentation-layer digest, not a new summarization system. The section should use deterministic snippets, counts, references, and safe local links from content that already exists on disk. It should not infer new themes, call an LLM, fetch content, or create a new data contract.
