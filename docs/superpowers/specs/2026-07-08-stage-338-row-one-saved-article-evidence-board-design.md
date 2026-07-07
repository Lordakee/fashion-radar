# Stage 338 ROW ONE Saved Article Paragraph Evidence Board Design

## Goal

Make `articles/index.html` more useful as a professional ROW ONE editorial desk by adding a generated-site-only "Saved Article Paragraph Evidence Board". The board should organize capped local paragraph excerpts that are already referenced by saved article content sections, so readers can see the actual evidence paragraphs behind the day's saved article organization without leaving the generated site.

## Current Gap

Stages 332-337 added saved article content groups, text-source provenance, local excerpts, reading paths, a theme digest, and a reference atlas. The library page now exposes themes, references, and read-first routes, but it still lacks a compact cross-article surface for the actual saved paragraph evidence behind those structures.

The existing saved local sidecars already provide:

- `RowOneEdition.stories`, which is the authoritative mapping from current-edition story id to generated `details/<slug>.html` route;
- `RowOneLocalArticle.story_id`;
- `RowOneLocalArticle.paragraphs`;
- `RowOneLocalArticle.content_sections`;
- `RowOneLocalArticleContentItem.paragraph_indices`;
- `RowOneLocalArticleContentItem.references`;
- existing detail-page `#local-article-paragraph-N` anchors.

Stage 338 should organize only this existing local data. It should not scan article bodies for new matches, infer new claims, summarize with an LLM, fetch external content, or add a new JSON contract.

## Chosen Approach

Add a private generated-site builder for a saved article paragraph evidence board:

- Build from existing `RowOneEdition`, `RowOneSavedArticleLibrary`, `RowOneSavedArticleContentOrganization`, and current-edition `local_articles_by_story_id`.
- Use `RowOneSavedArticleContentOrganization` cards as the board's group spine, preserving the existing group order and keys: `takeaways`, `entities`, `product_signals`, `brand_signals`.
- Use `RowOneEdition.stories` to build a validated `detail_path -> story_id` map, then require each matched local article to agree with that story id.
- Select only paragraph indices already attached to content-organization cards.
- Resolve each content-section route back to `article.content_sections[section_number - 1]`, then attach only references from content items whose `paragraph_indices` include the paragraph being rendered. Fall back to card references only if the section can be resolved but no item-level references match.
- Intersect cards with a canonical saved-library detail-path allowlist; a saved library entry contributes a detail path only when its safe digest, reader, and evidence routes all resolve to the same base detail path.
- Render capped paragraph excerpts with local generated detail-page paragraph links.
- Render the board only on `articles/index.html`, after Saved Article Reading Paths and before Saved Article Content Organization.

This gives ROW ONE a true local content organization layer: not only links and reference chips, but a concise evidence board based on already-saved paragraphs.

## UI Behavior

When all sections exist, `articles/index.html` should render this order:

1. saved article library hero;
2. saved article theme digest;
3. saved article reference atlas;
4. saved signal index;
5. saved article reading paths;
6. saved article paragraph evidence board;
7. saved article content organization;
8. source-grouped saved article library cards.

The evidence board section should include:

- bilingual section title:
  - `Saved Article Paragraph Evidence Board`
  - `保存文章段落证据板`
- a compact bilingual dek explaining that the board shows capped local paragraph excerpts already referenced by saved article sections;
- up to four groups, following existing content-organization groups;
- up to three paragraph evidence cards per group;
- each evidence card should include:
  - source name;
  - saved article title;
  - section label;
  - paragraph number;
  - capped paragraph excerpt;
  - safe local paragraph link;
  - optional existing reference chips from the supporting content item.

The board should read like an editorial evidence desk: concise, local, source-aware, and directly anchored to the saved detail pages. It should not republish full articles or become a ranking, scoring, or external trend product.

## Evidence Selection

Build evidence cards from existing content-organization cards and current-edition local article sidecars:

1. Build a current-edition route map from `edition.stories`. Accept only stories with safe generated detail paths.
2. Build a local article map by detail path. Include an article only when:
   - `local_articles_by_story_id[story.id]` exists;
   - `article.story_id == story.id`;
   - `story.detail_path` is safe;
   - the story detail path is present in the saved-library allowlist.
3. Build a saved-library allowlist. For each saved library entry, validate `reader_path`, `digest_path`, and `evidence_path` with their expected fragments and include the entry only when all safe base detail paths agree.
4. Iterate content-organization groups in existing group order.
5. For each card, validate that its `detail_path` is a generated local content-section route matching `#local-article-content-section-N`; reject traversal, absolute paths, missing fragments, wrong fragments, section `0`, and zero-padded section numbers.
6. Resolve the content-section number to `article.content_sections[number - 1]`. If the section does not exist, omit the card.
7. For each card paragraph index:
   - accept only real integers, not booleans;
   - require the paragraph index to exist in `article.paragraphs`;
   - require the paragraph text to be non-empty after trimming;
   - dedupe by group key, detail path, and paragraph index.
8. Attach references from content-section items whose own paragraph indices include the paragraph index. Dedupe references by normalized name/type/label and cap them for display. Fall back to deduped card references only if no item-level reference matches.
9. Cap groups at four and cards at three per group.
10. Omit the board when no valid evidence cards remain.

Paragraph excerpt text should be capped for index-page readability. Use a deterministic character cap and append the ASCII suffix `...` only when text is truncated. Because local saved paragraphs are currently single text strings, render the same excerpt in both language spans unless a future local article model adds bilingual paragraph bodies.

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
- outbound article URLs in the evidence board
- new extraction or crawling behavior
- new summary generation behavior
- new social/community platform behavior
- `data/saved-article-evidence-board.json`
- any generated JSON contract for this section

Primary board links must validate generated detail paths and `#local-article-paragraph-N` anchors before prefixing `../`. Unsafe routes, traversal, wrong fragments, `javascript:` routes, missing local articles, mismatched saved library paths, zero or zero-padded paragraph fragments, and invalid paragraph indices must omit the unsafe evidence card or unsafe link from the board.

## Tests

Add tests that prove:

- the builder derives evidence groups from existing saved article library/content organization/local article data and omits empty input;
- the builder uses `RowOneEdition.stories` to resolve safe detail paths to current-edition local articles;
- saved library entries with mismatched safe digest/reader/evidence base routes do not authorize a detail path;
- paragraph evidence cards use only explicit paragraph indices from existing content-organization cards;
- boolean, missing, duplicate, and out-of-range paragraph indices are rejected or deduped deterministically;
- unsafe or non-library-matching detail paths do not contribute evidence cards;
- excerpt text is capped with `...` and does not publish full long paragraphs on the library index;
- item-level references are attached when the paragraph index can be matched;
- fallback card references are used only when no item-level reference matches;
- `articles/index.html` renders `Saved Article Paragraph Evidence Board` / `保存文章段落证据板` after reading paths and before content organization;
- rendered board cards show source, title, section label, paragraph number, safe local paragraph links, and reference chips when available;
- the homepage does not render the board;
- generated JSON artifacts and workflow contracts do not expose evidence-board vocabulary or local paragraph text;
- no `data/saved-article-evidence-board.json` file is generated;
- `README.md` and `docs/row-one.md` document the Stage 338 generated-site-only boundary.

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
- No ranking, trend score, heat score, or external popularity claim.
