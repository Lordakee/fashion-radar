# Stage 316 ROW ONE Local Article Content Organization Design

## Goal

Make ROW ONE feel more like a local fashion-news site by organizing existing
saved article text into a scan-first content organization surface on the
generated homepage. The feature should help readers see what the local article
bodies actually contain before clicking through, without adding source
collection, fetching article pages, changing app JSON contracts, or calling an
LLM.

## Current Evidence

Stages 310-315 already made saved local article bodies visible and diagnosable:

- `data/articles/<story-id>.json` sidecars hold saved local paragraphs and
  `content_sections`.
- Detail pages render the saved text reader, saved text digest, and existing
  article map from each sidecar.
- Homepage surfaces already include saved article coverage and saved article
  briefs.
- Stage 315 added `row-one article-readiness`, which can explain why sidecars
  are or are not generated for the selected config/site.

The remaining gap is homepage organization depth: the homepage still mostly
summarizes saved-article availability and a few briefs. It does not yet present
a dedicated scan-first view of the article-body sections across the day.

## Architecture

Add Stage 316 as a generated-site presentation layer over existing
`RowOneLocalArticle.content_sections`.

Create a small builder module:

- `src/fashion_radar/row_one/saved_article_content_organization.py`

The builder consumes:

- `RowOneEdition`
- current `local_articles_by_story_id`

It returns dataclasses for a homepage section that groups current saved local
article bodies by existing sidecar section type:

- read-first / takeaways
- people, brands, and designers
- products, bags, and shoes
- source structure / brand signals

The output is rendered only into `index.html` through `render_index_html()`.
It is not written to `data/edition.json`, `data/manifest.json`,
`data/runtime.json`, schemas, SQLite, or any new generated JSON artifact.

## Recommended Approach

### Approach A: Homepage Content Organization Section

Add one homepage section after saved article briefs. It aggregates up to four
organization groups from existing sidecar `content_sections`, with each group
containing capped story cards that link to the matching local article digest or
content-section anchors on detail pages.

This is the recommended approach because it directly addresses the user goal:
the site shows organized content, not just links. It is deterministic,
local-only, and fits existing presentation patterns.

### Approach B: Detail-Only Enhancement

Improve only story detail pages by adding more section anchors and labels. This
is lower risk but less useful: users still need to click into individual
stories before seeing what the day contains.

### Approach C: Add A New JSON Contract Surface

Expose the organization in app-facing JSON. This is too broad for Stage 316
because it changes client contracts and schema surfaces. It should be deferred
until the generated-site presentation proves useful.

## Functional Requirements

1. Build a `RowOneSavedArticleContentOrganization` object from the current
   edition and current local article sidecars.
2. Include only stories from the current edition.
3. Exclude stale sidecars, mismatched `article.story_id`, invalid story IDs,
   unsafe detail paths, and articles with no nonblank saved paragraphs.
4. Organize only existing `content_sections`; do not invent references,
   summaries, products, or people.
5. Preserve zero-based paragraph indices internally and link only to existing
   detail anchors:
   - `#local-article-digest`
   - `#local-article-content-section-N`
   - `#local-article-paragraph-N`
   Here `N` for content-section anchors is the zero-based position from
   `enumerate(article.content_sections)`. Card paragraph indices should
   aggregate and dedupe valid paragraph indices from all usable items in the
   selected content section while preserving first-seen order.
6. Cap the homepage surface deterministically:
   - at most four organization groups
   - at most four cards per group
   - at most four chips/references per card
7. Keep section order deterministic:
   - `takeaways`
   - `entities`
   - `product_signals`
   - `brand_signals`
8. Render the organization only on the generated homepage.
9. Omit the homepage section cleanly when no publishable saved articles have
   usable `content_sections`.
10. Do not change `row-one-app/v7`, `data/edition.json`,
    `row-one-manifest/v1`, `data/manifest.json`, `row-one-runtime/v1`,
    `data/runtime.json`, schemas, detail routes, paragraph anchors, source
    collection, article fetching, scoring, LLM calls, connectors, or compliance
    review behavior.

## Data Model

Add frozen dataclasses:

```python
@dataclass(frozen=True)
class RowOneSavedArticleContentOrganizationCard:
    title: LocalizedText
    source_name: str
    section_title: LocalizedText
    section_label: LocalizedText
    lead: LocalizedText
    detail_path: str
    paragraph_indices: tuple[int, ...] = ()
    references: tuple[RowOneReference, ...] = ()

@dataclass(frozen=True)
class RowOneSavedArticleContentOrganizationGroup:
    key: str
    title: LocalizedText
    dek: LocalizedText
    cards: list[RowOneSavedArticleContentOrganizationCard]

@dataclass(frozen=True)
class RowOneSavedArticleContentOrganization:
    article_count: int
    group_count: int
    groups: list[RowOneSavedArticleContentOrganizationGroup]
```

`section_title` is the edition-level section title, such as `Top Stories`.
`section_label` is the saved local article content-section title, such as
`Takeaways` or `Products`.

## Rendering

Update `render_index_html()` to accept:

```python
saved_article_content_organization: RowOneSavedArticleContentOrganization | None = None
```

Render after saved article briefs and before the normal story sections. The
section copy should be bilingual and concise:

- EN title: `Saved Article Content Organization`
- ZH title: `保存正文内容整理`
- EN dek: `A scan-first map of the existing saved article sections behind today's stories.`
- ZH dek: `基于今日故事背后已保存正文栏目生成的速览地图。`

Cards should link to the safest available target:

1. `detail_path#local-article-content-section-N` when the card maps to a valid
   content-section index.
2. `detail_path#local-article-digest` when section anchor is not available.

Group dek copy should be deterministic:

- Read First: `Key takeaways from saved articles` / `保存正文中的关键要点`
- People & Brands: `Brands, people, and designers mentioned` / `正文提到的品牌、人物与设计师`
- Products: `Bags, shoes, and product signals` / `包袋、鞋履与产品信号`
- Source Structure: `Source structure and brand-signal context` / `来源结构与品牌信号背景`

## Testing

Add `tests/test_row_one_saved_article_content_organization.py`:

- Current-edition filtering and sidecar hygiene.
- Group ordering and card caps.
- Takeaway/entity/product/brand-signal section organization.
- Multi-item content sections aggregate and dedupe valid paragraph indices in
  first-seen order.
- Mismatched `article.story_id`, unsafe detail path, invalid story ID, blank
  paragraphs, and stale sidecar exclusion.
- Empty `content_sections` returns `None`.

Extend `tests/test_workflows.py` around the existing ROW ONE local article
workflow test:

- Generated `index.html` includes the new homepage section.
- `data/edition.json` remains `row-one-app/v7`.
- No `local article content organization` fields are added to `edition.json`,
  `manifest.json`, or `runtime.json`.

Extend `tests/test_row_one_docs.py`:

- Stage 316 docs guard after Stage 315 and before Stage 310.
- Positive phrases proving the feature is generated-site only.
- Forbidden phrases covering contract/version drift, source collection,
  scoring, LLM calls, connectors, and compliance review.

## Verification

Required implementation-node commands:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest \
  tests/test_row_one_saved_article_content_organization.py \
  tests/test_workflows.py \
  tests/test_row_one_docs.py -q

UV_NO_CONFIG=1 uv --no-config run --frozen ruff check
UV_NO_CONFIG=1 uv --no-config run --frozen ruff format --check
UV_NO_CONFIG=1 uv --no-config run --frozen pytest -q
UV_NO_CONFIG=1 uv lock --check
UV_NO_CONFIG=1 uv --no-config run --frozen python scripts/check_release_hygiene.py
```

Manual smoke after implementation:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen fashion-radar row-one build \
  --config-dir configs \
  --data-dir data \
  --reports-dir reports \
  --output-dir reports/row-one/site \
  --latest-only
```

Then inspect that `reports/row-one/site/index.html` contains the saved article
content organization section and that `data/edition.json` remains unchanged as
the app contract.

## Non-Goals

- No config migration.
- No article fetching or extraction changes.
- No source collection changes.
- No social/community connector activation.
- No LLM summaries.
- No compliance-review feature.
- No schema/app contract changes.
- No new generated JSON artifact.

## Self-Review

- No placeholders remain.
- Scope is one generated-site presentation feature.
- The design directly moves ROW ONE toward locally organized content.
- The feature is additive and contract-safe.
- The tests are focused on deterministic local sidecars and homepage rendering.
