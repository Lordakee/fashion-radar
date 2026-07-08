# Stage 356 Saved Article Key Signals Design

## Goal

Improve each generated local article page (`articles/<story-id>.html`) with a
compact `Saved Article Key Signals` section that organizes already-saved article
text and existing ROW ONE metadata into reader-ready signals.

The feature should answer: why does this saved article matter, which brands are
present, which products are present, which people are present, and which
existing article themes help the reader scan the piece.

## Product Scope

- Add an optional `Saved Article Key Signals` section to generated local article
  pages.
- Render it after the Stage 355 local section binder when that binder exists,
  and always before the existing `#local-article` body when the key-signals
  section exists.
- Show compact groups, not another route or library:
  - `Why It Matters`;
  - `Brands`;
  - `Products`;
  - `People`;
  - `Themes`.
- Use only data already available to the local article page renderer.
- Use same-page paragraph or content-section fragment links only.

## Non-Goals

- No app contract, schema, runtime, manifest, or JSON artifact changes.
- No new article sidecars, generated data files, route families, or local
  storage behavior.
- No new scraping, source fetching, extraction, scoring, ranking, LLM calls,
  social connectors, scheduling, deployment, analytics, personalization,
  recommendation, or compliance-review behavior.
- No mutation of stored article text, paragraph indices, content sections,
  references, brief sections, or extracted source records.
- No outbound links or external article fetches.

## Data Sources

Reuse existing in-memory render inputs:

- `RowOneStory`
- `RowOneLocalArticle`
- `RowOneStory.why_it_matters`
- `RowOneLocalArticle.brief_sections`
- `RowOneLocalArticle.content_sections`
- `RowOneLocalArticle.content_sections[*].title`
- `RowOneLocalArticle.content_sections[*].key`
- `RowOneLocalArticle.content_sections[*].items`
- `RowOneLocalArticle.content_sections[*].items[*].label`
- `RowOneLocalArticle.content_sections[*].items[*].body`
- `RowOneLocalArticle.content_sections[*].items[*].references`
- `RowOneLocalArticle.content_sections[*].items[*].paragraph_indices`
- `RowOneLocalArticle.paragraphs`
- `RowOneLocalArticle.paragraphs_zh`

The builder must sanitize identity inputs with:

- `safe_local_article_story_id(story.id)`
- `story.id == local_article.story_id`

## Explicit Mapping

- `Why It Matters`:
  - prefer `local_article.brief_sections[key="why_it_matters"]`;
  - fall back to `story.why_it_matters` only when the local article has at least
    one nonblank saved paragraph and no nonblank local `why_it_matters` brief
    section;
  - evidence is optional and must never be invented for `story.why_it_matters`.
- `Brands`:
  - collect existing `content_sections[*].items[*].references`;
  - keep nonblank reference names whose
    `row_one_saved_article_reference_bucket(...)` result is `brands`;
  - attach readable support text from the first supporting content item body,
    item label, or section title when available.
- `Products`:
  - collect existing `content_sections[*].items[*].references`;
  - keep nonblank reference names whose bucket is `products`;
  - attach readable support text from the first supporting content item body,
    item label, or section title when available.
- `People`:
  - collect existing `content_sections[*].items[*].references`;
  - keep nonblank reference names whose bucket is `people`;
  - attach readable support text from the first supporting content item body,
    item label, or section title when available.
- `Themes`:
  - collect existing content section titles and item labels;
  - use content section keys only for stable support classification and
    content-section anchors, not as raw displayed theme labels;
  - skip theme labels that duplicate displayed brand, product, or people
    reference names;
  - do not infer or generate new theme labels.

## Rendering Rules

- Return `None` when `story.id != local_article.story_id`, when the story id is
  unsafe, or when no meaningful key-signal group can be built.
- A meaningful group contains at least one nonblank display statement, nonblank
  display reference name, nonblank display theme label, or validated
  paragraph/content-section support row; raw section keys alone are not
  meaningful.
- Deduplicate references within each group by normalized displayed reference
  name while preserving first-seen support metadata.
- Deduplicate theme labels by normalized displayed label while preserving
  first-seen order.
- Treat `paragraph_indices` as zero-based source paragraph indices; render
  anchors as one-based `#local-article-paragraph-N`.
- Skip boolean, negative, duplicate, out-of-range, and blank paragraph indices.
- Paragraph evidence can only come from validated
  `content_sections[*].items[*].paragraph_indices`.
- Use English paragraph excerpts from `paragraphs` and aligned Chinese excerpts
  from `paragraphs_zh` only when the lists are the same length and the
  corresponding Chinese paragraph is nonblank.
- Cap rendered references, themes, section support rows, and paragraph excerpts
  so the section remains compact.
- Compute total/support counts from the full eligible input before display caps
  when counts are exposed.
- Escape all rendered text in `templates.py`.

## Acceptance Criteria

- Local article pages can render key signals without changing site contracts or
  generated data artifacts.
- The key-signals section appears only on eligible
  `articles/<story-id>.html` pages.
- The key-signals section appears after `.saved-article-local-section-binder`
  when that section exists and before `id="local-article"` in all cases.
- The section includes readable local signals, not only links.
- All key-signal links are renderer-owned same-page fragment links.
- The feature does not alter Stage 319 detail `Signal Briefing`, Stage 349
  `Saved Article Signal Facets`, Stage 350 `Saved Article Daily Signal
  Leaderboard`, `articles/index.html`, the homepage, or generated data payloads.
- Tests cover builder selection, why-it-matters fallback, reference bucketing,
  theme extraction, invalid paragraph indices, caps, excerpt truncation,
  template rendering, generated-site integration, docs references, and workflow
  guard coverage.
