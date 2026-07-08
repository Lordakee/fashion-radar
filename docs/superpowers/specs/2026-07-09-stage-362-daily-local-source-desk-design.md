# Stage 362 Daily Local Source Desk Design

## Context

Stages 357-361 added several homepage generated-site sections that organize
already-saved local article content by key signals, momentum, heat, article
cards, and reading lanes. The remaining homepage gap is provenance: readers
can see what to read, but not which publications or sources are carrying the
day's downloaded local text.

## Goal

Add a generated-site-only homepage section named **Daily Local Source Desk**.
It should sit after Daily Local Article Reading Brief and before Saved Article
Content Organization. It should group current-edition saved local articles by
`RowOneLocalArticle.source_name`, summarize each source's saved local article
coverage, and link only to existing same-site local article pages and paragraph
anchors.

The feature should make ROW ONE feel more like a professional daily fashion
briefing desk: sources become visible editorial units, not just metadata on
individual cards.

## Non-Goals

- Do not add app-facing schema or payload fields.
- Do not create `data/daily-local-source-desk.json`,
  `data/local-source-desk.json`, or `data/source-desk.json`.
- Do not create new route families or standalone HTML artifacts.
- Do not alter `articles/index.html`, `articles/<story-id>.html`, or detail
  pages.
- Do not publish full articles on the homepage.
- Do not add outbound article URLs as primary navigation.
- Do not add fetching, extraction, scoring, ranking, LLM, connector,
  scheduling, deployment, analytics, personalization, recommendation, or
  compliance-review behavior.

## Design

The homepage renderer derives source groups from the current edition and
already-saved local articles. It stays in `templates.py` and reuses the same
generated story-id-to-local-article-page href map used by Stage 360 and Stage
361.

Eligibility for a source row requires:

- a current-edition story with a safe story id;
- a matching `RowOneLocalArticle` whose `story_id` equals the story id;
- at least one usable saved paragraph;
- a nonblank normalized source name;
- a safe supplied one-file `.html` article href whose filename stem equals the
  story id.

Source-name normalization is explicit and local to this presentation feature:

- normalized source name: `normalize_row_one_paragraph(article.source_name)`;
- grouping key: `normalized_source_name.casefold()`;
- display name: the first normalized source name seen for that grouping key in
  current-edition story order.

Each source group renders:

- source name;
- article count;
- saved paragraph count;
- body-source mix, using existing body-source labels deduped in source-story
  order and capped before the source dataclass is stored;
- top brand/product/designer chips from current-edition story references,
  deduped by normalized name, type, and label casefolded across all stories in
  the source group;
- up to two paired local article links, each labeled with story/local article
  titles and paired with one paragraph link;
- up to two paired paragraph links, labeled by paragraph number and using
  existing local article paragraph anchors.

The section does not render saved paragraph excerpts. Paragraph links point to
downloaded local text on the same site without republishing body text inside
the homepage source desk.

Groups are deterministic. Sort sources by:

1. article count descending;
2. saved paragraph count descending;
3. source display name case-insensitive ascending;
4. exact source display name ascending.

The final source-name key is a stable tiebreak for source names that are equal
after case-folding but differ in exact casing.

Cap the section at four source groups. Cap links and chips inside each source
group to keep the homepage compact.

## Rendering Boundary

The feature renders only inside homepage `index.html`. It must not write or
mutate:

- `articles/index.html`;
- `articles/<story-id>.html`;
- story detail pages;
- `data/edition.json`;
- `data/manifest.json`;
- `data/runtime.json`;
- local article sidecar JSON.

## Placement

When present, the section renders after:

- `.daily-local-article-reading-brief`

and before:

- `.saved-article-content-organization`

If Daily Local Article Reading Brief is absent, Daily Local Source Desk still
uses the same relative homepage slot before Saved Article Content Organization.

## Link Safety

The renderer never derives article links from story ids alone. It must use only
the supplied article href map and validate that each href:

- is a string;
- is already trimmed and contains no whitespace;
- does not begin with `.`, `/`, or `//`;
- is a single filename, not a nested path;
- ends in `.html`;
- has a filename stem equal to the story id;
- has a safe local article story id.

Rendered links must be same-site:

- `articles/<story-id>.html#local-article-digest`;
- `articles/<story-id>.html#local-article-paragraph-N`.

The renderer should expose concrete helper paths for these two link families
instead of accepting an arbitrary caller-supplied fragment string.

## Testing Strategy

Tests should follow Stage 360 and Stage 361 patterns:

- direct render test for source grouping, ordering, caps, counts, body-source
  labels, chips, same-site links, paragraph anchors, bilingual headings, and
  escaping, including reference-chip escaping and case-sensitive source-name
  tiebreaking;
- filtering test for unsafe story ids, mismatched article ids, missing
  articles, blank source names, empty paragraphs, unsafe hrefs, traversal,
  nested paths, whitespace hrefs, leading dots/slashes, leading double-slashes,
  and mismatched href stems;
- placement test after Daily Local Article Reading Brief and before Saved
  Article Content Organization;
- placement test when Daily Local Article Reading Brief is absent, proving the
  Source Desk still renders before Saved Article Content Organization;
- site-generation test proving homepage-only behavior and contract/artifact
  denylist;
- CSS selector test;
- docs boundary test in both README and `docs/row-one.md`;
- workflow generated-site-only guard test.

## Review Notes

This is intentionally a presentation layer. It does not discover sources,
score source authority, fetch new articles, or build cross-day source trends.
It organizes the already-downloaded local text by source so the daily website
has a clearer editorial provenance layer.
