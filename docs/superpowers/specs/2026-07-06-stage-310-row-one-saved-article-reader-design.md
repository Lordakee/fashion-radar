# Stage 310 ROW ONE Saved Article Reader Design

## Context

The user wants ROW ONE to present fashion information inside the generated web
page, not only as links out to other sites. Recent stages already added local
article sidecars, detail-page local article sections, paragraph anchors, a local
article map, paragraph drilldowns, and homepage Daily Local Intelligence
clustering. Stage 310 should therefore deepen the in-page reading experience
without rebuilding collection, changing ranking, or changing app-facing JSON
contracts.

The current pipeline already stores optional generated-site sidecars under
`data/articles/<story-id>.json` and renders matching saved paragraphs on each
story detail page. The implementation should work only with the existing
`RowOneLocalArticle.paragraphs`, `paragraphs_zh`, `brief_sections`, and
`content_sections` fields.

## Requirements

- Add a more explicit in-page saved text reader surface to ROW ONE detail
  pages so users can scan the saved local article content without opening the
  original external URL.
- Keep source attribution and provenance visible near the saved text.
- Keep saved local article content out of `data/edition.json`.
- Keep `row-one-app/v7`, `row-one-manifest/v1`, `row-one-runtime/v1`, detail
  routes, paragraph anchors, story IDs, schemas, collection, matching, ranking,
  and scoring unchanged.
- Do not add network calls, source collection, browser automation, external APIs,
  LLM calls, image generation, translation services, or compliance-review
  product features.
- Do not redesign the ROW ONE visual system. Add small, restrained markup/CSS
  that follows existing local-article patterns.
- Avoid republishing unbounded external articles. The reader presents the
  already retained, capped saved local text controlled by
  `row_one_article.max_chars`, with attribution and existing provenance.

## Explored Approaches

### Approach A: Template-only saved text reader index

Render a compact "Saved Text Reader" block inside the existing local article
section. It lists each rendered saved paragraph as a numbered in-page reader
segment with a short excerpt and links to the existing
`#local-article-paragraph-N` anchors. It also adds a local article map chip for
the reader block. This uses only existing sidecar fields and existing detail
HTML.

Trade-offs: Fast, low-risk, and directly improves in-page reading. It does not
create new structured data for app clients, which is acceptable because the
requirement is the generated website and the app contract must stay stable.

### Approach B: New sidecar reader JSON

Generate a new `data/article-reader/<story-id>.json` artifact with paragraph
excerpts, section mapping, and reader metadata, then render it into detail pages.

Trade-offs: Cleaner separation if a future app consumes article-reader data, but
it adds another artifact and verification surface before there is a proven app
consumer. It also increases release-hygiene and schema documentation work.

### Approach C: Homepage article-reader previews

Expand homepage Daily Local Intelligence cards to include more saved paragraph
previews and richer summaries.

Trade-offs: Helpful later, but the homepage is already dense and Stage 309 just
polished that area. The user's immediate complaint is that clicking titles should
show content locally, so detail-page reader depth is the better next step.

## Recommended Design

Use Approach A.

Add a deterministic saved text reader inside the existing
`_render_local_article()` detail-page section:

- `id="local-article-reader"` with class `local-article-reader`.
- A compact title:
  - English: `Saved Text Reader`
  - Chinese: `保存正文阅读`
- A short metadata line derived from existing local fields:
  - English example: `2 saved paragraphs from Vogue Business`
  - Chinese example: `来自 Vogue Business 的 2 个保存段落`
- A numbered ordered list of rendered paragraph excerpts. Each item links to the
  already existing `#local-article-paragraph-N` anchor. The excerpt is a cleaned,
  normalized, escaped preview of the saved paragraph capped at a deterministic
  length.
- If `paragraphs_zh` aligns one-to-one with `paragraphs`, render bilingual
  excerpt spans. If it does not align, render a single plain excerpt, matching
  the current body paragraph fallback.
- Skip blank paragraphs and do not generate links for non-rendered paragraph
  positions.
- Insert the reader after the existing local article map and before the
  brief/content cards/body. This preserves the current local-article navigation
  order while giving the user a saved-text overview before the existing saved
  text.
- Add a `Reader` / `阅读` chip to the local article map when structured content
  exists. Plain local articles still get the reader block even if they do not get
  the structured map, so the in-page content improvement applies broadly.
- Rename the existing map chip from `Full saved text` / `完整保存正文` to
  `Saved text` / `保存正文` without changing `#local-article-body`. The retained
  sidecar text can include extracted source text, fallback story summary, or
  appended ROW ONE context, so the UI should not imply every saved paragraph is
  reproduced from an external article.

## Data Flow

`render_row_one_site()` passes `local_articles_by_story_id` to
`render_detail_html()`. `render_detail_html()` passes a `RowOneLocalArticle` into
`_render_local_article()`. Stage 310 stays inside `templates.py`:

1. `_render_local_article()` keeps all reader/map/brief/content/body rendering
   inside the existing local article section.
2. `_render_local_article_reader(article)` derives valid paragraph excerpts from
   `article.paragraphs` and optionally `article.paragraphs_zh`.
3. `_render_local_article_map(article)` gains a `Reader` chip that links to
   `#local-article-reader` when the reader block exists.
4. The existing saved text remains rendered with the existing
   `#local-article-paragraph-N` anchors.

No saved reader data is added to `data/edition.json`; the existing
`data/articles/<story-id>.json` sidecar remains the authoritative local article
payload.

## Error Handling And Safety

- Empty or whitespace-only paragraphs are ignored.
- Paragraph excerpts are normalized and HTML-escaped.
- Existing unsafe external URL handling remains unchanged.
- If Chinese paragraphs are missing or misaligned, the reader uses the same plain
  source-text fallback as the current local article body renderer.
- No anchors are renamed. Existing links to `#local-article-paragraph-N` keep
  working.

## Testing

Add focused tests in `tests/test_row_one_render.py`:

- Structured local article detail pages render the reader block, reader map chip,
  numbered paragraph excerpt links, and preserve existing body anchors.
- Plain local articles without `brief_sections` or `content_sections` still
  render the reader block and existing saved text, while retaining the existing behavior
  that no structured local article map appears.
- Blank paragraphs are skipped in the reader index just as they are skipped in
  the body.
- Excerpts are escaped and capped, so unsafe markup does not render as HTML and
  long paragraphs do not make the reader index unwieldy.

Update `README.md`, `docs/row-one.md`, and `tests/test_row_one_docs.py` to
document that Stage 310 adds a generated-site detail-page reader surface only,
without app/schema/source/scoring changes.

## Acceptance Criteria

- Clicking into a ROW ONE story with a local article shows an in-page saved text
  reader before the existing saved text.
- Reader links jump to the existing paragraph anchors on the same detail page.
- `data/edition.json` remains free of local article paragraphs and reader
  excerpts.
- `row-one status` still reports `row-one-app/v7`,
  `row-one-manifest/v1`, and `row-one-runtime/v1`.
- Full test, lint, lock, release-hygiene, generated-site build, and generated-site
  status checks pass under the existing frozen/no-config uv workflow.
