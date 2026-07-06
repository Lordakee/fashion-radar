# Stage 318 ROW ONE Detail Continue Reading Rail Design

## Objective

Stage 318 improves ROW ONE generated detail pages with a professional
`Continue Reading / 继续阅读` rail after the evidence trail. The rail should keep
readers inside the generated daily edition by recommending up to three related
detail pages from the same edition.

## User Value

ROW ONE detail pages now contain stronger local article content, but they still
end abruptly after the evidence trail. A fashion news site should give readers a
clear next read. Stage 318 adds an internal reading path that is based on the
current edition rather than external links.

## Scope

This is a generated-site detail-page presentation enhancement only.

It reuses:

- existing `RowOneEdition.stories`
- existing `RowOneSection` labels
- existing `RowOneStory.detail_path`
- existing story summaries and editorial takeaways
- existing generated detail pages

It does not change:

- `row-one-app/v7`
- `data/edition.json`
- `row-one-manifest/v1`
- `data/manifest.json`
- `row-one-runtime/v1`
- `data/runtime.json`
- schemas
- detail routes
- paragraph anchors
- source collection
- article fetching/extraction
- scoring
- connectors
- LLM calls
- compliance-review product behavior

It does not write a new JSON artifact.

## Related Story Selection

For each detail page:

1. Exclude the current story by `story.id`.
2. Prioritize other stories with the same `section_key`, preserving edition order.
3. Fill remaining slots from other sections, preserving edition order.
4. Skip stories with unsafe `detail_path`.
5. Skip duplicate target detail paths.
6. Cap at three cards.
7. Omit the rail entirely when no related cards remain.

## Link Rules

Detail pages are written inside `details/`, while `RowOneStory.detail_path` is
stored as `details/<file>.html`. Continue-reading links should therefore use the
validated detail filename, e.g. `other-story-1234567890.html`, so links resolve
as siblings from the current detail page.

## Card Content

Each card should include:

- section label from `edition.sections`
- story headline
- source name
- a short cleaned excerpt from `story.summary.en`, falling back to
  `story.editorial_takeaway.en`
- bilingual spans for section label and excerpt when available

All visible values must be escaped.

## Implementation Shape

Modify only `src/fashion_radar/row_one/templates.py` for production behavior.

Suggested helpers:

- `DETAIL_CONTINUE_READING_MAX_ITEMS = 3`
- `DETAIL_CONTINUE_READING_EXCERPT_CHARS = 120`
- `_render_detail_continue_reading(edition, story)`
- `_detail_continue_reading_stories(edition, story)`
- `_detail_continue_reading_href(detail_path)`
- `_detail_continue_reading_excerpt(text)`

Render order:

```text
Evidence Trail
Continue Reading
```

The rail should be after the evidence trail and before the closing `</article>`.

## Test Strategy

Add focused render tests in `tests/test_row_one_render.py`:

- same-section related stories appear before fallback stories
- current story is excluded
- unsafe detail paths are skipped
- duplicate target paths are skipped
- rail caps at three cards
- rail is omitted for one-story editions
- card text is escaped
- links use sibling filenames, not `details/...` paths

Extend generated-site workflow boundary in `tests/test_workflows.py`:

- generated detail page contains the continue-reading rail
- SQLite item row, item matches, and item count remain unchanged
- `edition.json`, `manifest.json`, and `runtime.json` contract versions remain pinned
- generated contract payloads do not contain a Stage 318-only key
- top-level `data/*.json` allowlist remains unchanged

Extend docs boundary in `tests/test_row_one_docs.py`:

- add Stage 318 docs guard
- update Stage 317 slice to end at Stage 318
- preserve forbidden-phrase guards for schema, contract, collection, scoring,
  connector, LLM, and compliance drift

