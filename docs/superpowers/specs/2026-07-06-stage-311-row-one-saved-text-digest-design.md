# Stage 311 ROW ONE Saved Text Digest Design

## Objective

Add a ROW ONE detail-page saved text digest that organizes locally saved article
content into a scan-first, reader-facing summary inside the generated web page.
This advances the product from "saved text is locally readable" to "saved text
is locally organized" without adding new collection, model, schema, or network
surfaces.

## User Need

The user wants ROW ONE to present fashion information as a professional daily
site rather than a list of outbound links. Stage 310 made saved local text
readable in-page. Stage 311 should make the saved text easier to understand at
a glance: a reader should immediately see the lead saved point, relevant
brands/people/designers, relevant bags/shoes/products, and where to continue in
the local saved text.

## Current Context

ROW ONE already writes optional `data/articles/<story-id>.json` sidecars with:

- `paragraphs` and optional aligned `paragraphs_zh`;
- `brief_sections`;
- `content_sections` such as `takeaways`, `entities`, `product_signals`, and
  `brand_signals`;
- references and paragraph indices that point to existing
  `#local-article-paragraph-N` anchors.

Stage 310 renders a saved text reader from existing paragraphs. Stage 311 should
reuse the same sidecar data and should not create a new data contract.

## Recommended Approach

Implement a template-only `Saved Text Digest / 保存正文整理` block in
`src/fashion_radar/row_one/templates.py`.

The block should render inside the existing `#local-article` section after the
local article map and before the saved text reader. It should be built from
existing `RowOneLocalArticle` fields and should be omitted only when there are
no nonblank saved paragraphs.

The digest should include up to four compact cards:

- `Read First / 先读`: the first organized takeaway item body when available,
  falling back to the first nonblank saved paragraph. It links to valid existing
  paragraph anchors when paragraph indices exist.
- `People & Brands / 品牌与人物`: deduped references from `entities` sections.
- `Products / 产品`: deduped references from `product_signals` sections.
- `Source Map / 来源结构`: source name, saved paragraph count, and organized
  section count.

The existing `brand_signals` content section remains visible in the existing
organized content cards and is intentionally not duplicated as a separate
digest card in this stage.

Plain saved-text articles with no structured `content_sections` should still
render a useful digest using the first saved paragraph and source map, but they
should continue to omit the structured local article map.

## Boundaries

Stage 311 is generated-site presentation only.

It must not:

- add source collection;
- add scraping, browser automation, platform APIs, cookies, proxy, CAPTCHA, or
  paywall behavior;
- add LLM calls, translation services, image generation, or scheduling;
- change `row-one-app/v7`;
- change `data/edition.json`;
- change `row-one-manifest/v1`;
- change `row-one-runtime/v1`;
- change JSON schemas;
- change detail routes;
- change paragraph anchors;
- add scoring or demand proof.

The digest may appear in generated detail-page HTML and static CSS only. The
source sidecar `data/articles/<story-id>.json` remains the existing source of
truth and is not extended.

## Deferred Follow-Up

A homepage saved-article coverage index is a useful next-stage candidate. It
would inventory the current day's saved article sidecars by source, ROW ONE
section, saved paragraph count, organized section count, and surfaced
references. That broader corpus-level homepage view is intentionally deferred
so Stage 311 can stay focused on organizing one saved article's content where
the local paragraphs are already rendered.

## Rendering Contract

The digest block should use stable anchors and classes:

- `id="local-article-digest"`
- `class="local-article-digest"`
- `aria-label="Saved text digest"`
- title spans:
  - English: `Saved Text Digest`
  - Chinese: `保存正文整理`
- map chip:
  - `href="#local-article-digest"`
  - English: `Digest`
  - Chinese: `整理`

Map chip order for structured local articles:

1. Brief, when present
2. Digest, when rendered
3. Reader, when rendered
4. Content-section chips
5. Saved text

The digest should appear before `#local-article-reader`, before
`#local-article-brief`, and before `#local-article-body`.

## Data Selection Rules

Read First:

- Prefer the first item in the `takeaways` content section with a nonblank body.
- Preserve bilingual body text when the item body is a `LocalizedText`.
- Use valid paragraph indices only; invalid or blank-paragraph indices are
  ignored.
- If no takeaway body exists, use the first nonblank saved paragraph and its
  aligned zh paragraph when `paragraphs_zh` length matches `paragraphs`.
- Truncate display text with the existing `_meta_description(..., limit=160)`
  helper, preserving the existing Unicode ellipsis behavior.

References:

- `People & Brands` reads references from `content_sections` with key
  `entities`.
- `Products` reads references from `content_sections` with key
  `product_signals`.
- Deduplicate by `normalize_row_one_paragraph(name).casefold()`, stripped
  casefolded `type`, and stripped casefolded `label`, while preserving
  first-seen order.
- Limit each reference list to four chips.
- Escape every rendered value.
- Omit an empty reference card if no references exist.

Source Map:

- Always render when the digest exists.
- Show source name, saved paragraph count, and organized section count.
- Counts are derived from existing nonblank paragraphs and existing
  `content_sections`.

## Testing Strategy

Use TDD during implementation.

Add focused rendering tests in `tests/test_row_one_render.py` for:

- structured local article digest rendering from `takeaways`, `entities`, and
  `product_signals`;
- plain local articles getting a digest without a map;
- digest fallback to first saved paragraph;
- dedupe, escaping, invalid paragraph-index filtering, and truncation;
- map chip order;
- CSS selectors;
- contract stability: no digest content in `data/edition.json` and no contract
  version changes.

Add docs coverage in `tests/test_row_one_docs.py` for Stage 311 boundary text in
both README and `docs/row-one.md`.

## Verification

Implementation should pass:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_render.py tests/test_row_one_docs.py -q
UV_NO_CONFIG=1 uv --no-config run --frozen pytest -q
UV_NO_CONFIG=1 uv --no-config run --frozen ruff check
UV_NO_CONFIG=1 uv --no-config run --frozen ruff format --check
UV_NO_CONFIG=1 uv lock --check
UV_NO_CONFIG=1 uv --no-config run --frozen python scripts/check_release_hygiene.py
UV_NO_CONFIG=1 uv --no-config run --frozen fashion-radar row-one build --as-of 2026-07-06T04:00:00Z --output-dir reports/row-one/site --latest-only
UV_NO_CONFIG=1 uv --no-config run --frozen fashion-radar row-one status --site-dir reports/row-one/site --json
```

Expected status contracts remain:

- `row-one-app/v7`
- `row-one-manifest/v1`
- `row-one-runtime/v1`
