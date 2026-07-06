# Stage 321 ROW ONE Editorial Brief Design

## Goal

Add a generated-site-only ROW ONE homepage `Editorial Brief / 编辑正文` section that turns existing saved article and story data into short readable editorial paragraphs, so the site feels like a daily fashion briefing rather than a set of links and cards.

## User Value

The user asked for the webpage to organize information locally instead of sending readers out to source links. Stage 320 added scan-first Daily Edit cards. Stage 321 should add a more narrative content layer: a compact editor-written-style body assembled deterministically from existing local saved content, story summaries, signal context, references, and safe detail routes.

## Scope

- Render HTML only on the generated ROW ONE homepage.
- Place the section after `saved_article_content_organization` and before the lead story.
- Use existing in-memory data passed to the generated site renderer:
  - `RowOneEdition`
  - existing `RowOneStory` summaries, editorial takeaways, signal context, reader path, references, detail paths, and evidence counts
  - existing saved local article sidecars already loaded as `local_articles_by_story_id`
  - existing saved local article brief sections, content sections, paragraph counts, and paragraph anchors
- Build up to three editorial paragraphs:
  - `What changed today / 今日变化`
  - `Why it matters / 为什么重要`
  - `What to read locally / 本地阅读路径`
- Include up to three internal links into existing detail pages or saved paragraph anchors.
- Escape all displayed text.
- Validate all internal hrefs with existing detail-route and paragraph-anchor helpers.
- Omit the section when no usable story or local article content exists.

## Non-Goals

- Do not add `editorial_brief`, `daily_information_layer`, or any new top-level field to `data/edition.json`.
- Do not change `row-one-app/v7`.
- Do not change `row-one-manifest/v1` or `row-one-runtime/v1`.
- Do not change schemas, app payload builders, runtime payloads, manifest payloads, story IDs, detail routes, paragraph anchors, source collection, fetching, extraction, scoring, LLM calls, connectors, image generation, or deployment behavior.
- Do not add compliance-review product features.
- Do not add dependencies.

## Recommended Approach

Add small private frozen dataclasses inside `templates.py` for the generated-site-only data object, then pass that typed object to `render_index_html()` as a private optional argument. Keep the object out of all JSON artifacts. The builder in `render.py` should import those render-layer dataclasses from `templates.py`; `templates.py` must not import from `render.py`, preserving the existing one-way import graph. The builder should stay deterministic and prefer existing saved local article content, then fall back to existing story text when saved article content is limited.

The data boundary should be typed, not a raw `dict[str, object]` contract:

```python
@dataclass(frozen=True)
class _EditorialBriefItem:
    title: LocalizedText
    body: LocalizedText
    meta: LocalizedText | None = None
    href: str | None = None


@dataclass(frozen=True)
class _EditorialBrief:
    items: tuple[_EditorialBriefItem, ...]
```

The builder should create `_EditorialBrief` / `_EditorialBriefItem` objects and the template render helpers should accept those objects so text typing remains explicit and stable. Final href validation still happens at render time through `_safe_editorial_brief_href()`.

The homepage renderer should add:

```text
saved_article_content_organization
editorial_brief
lead_story
```

This placement keeps the section in the local article/story organization area and gives readers a prose briefing before the main story card.

## Content Rules

- The lead story selection rule is deterministic: choose the first story with a non-empty `editorial_takeaway` or `summary`, preserving edition story order. If no story has usable text, omit the section.
- `What changed today` should combine the lead story editorial takeaway or summary with the saved local article `what_happened` brief-section body when present and non-duplicate. Supporting saved article title/source context should render as metadata.
- `Why it matters` should prefer story `why_it_matters`, then `signal_context`, then saved article brief sections named `why_it_matters`.
- `What to read locally` should prefer saved article brief sections named `watch_next`, then fall back to story `reader_path`. It should point readers to existing saved article paragraph anchors when paragraphs exist, otherwise to the validated story detail route.
- Each paragraph must be bilingual using `LocalizedText`.
- The section should cap the combined final body text at `EDITORIAL_BRIEF_BODY_EXCERPT_CHARS = 220` after cleanup and append `…` when text is truncated, matching existing ROW ONE excerpt behavior.
- Duplicate or empty paragraphs should be skipped. Empty means both localized strings are blank or whitespace-only after cleanup. Duplicate means cleaned localized body strings match exactly after `clean_row_one_text()`.

## Link Safety

- Allow only existing validated detail-page hrefs returned by `validated_row_one_detail_relative_path()`, plus existing local article paragraph/content-section fragments:
  - `details/<validated-story>.html`
  - `details/<validated-story>.html#local-article-paragraph-N`
  - `details/<validated-story>.html#local-article-content-section-N`
- Treat `validated_row_one_detail_relative_path()` returning `None` as rejection; it does not raise.
- Reject external URLs, `javascript:` URLs, path traversal, and unknown fragments.
- Render unsafe or missing links as plain text, not as external links.

## Styling

Use a restrained editorial layout consistent with ROW ONE:

- Section class: `editorial-brief`
- Header with bilingual title and dek
- Prose body cards or paragraphs with compact metadata
- Internal action links styled like existing generated-site sections
- Mobile layout collapses to one column under the existing `760px` breakpoint

## Testing Requirements

- Rendering test asserts the homepage includes `Editorial Brief` and `编辑正文`, with three expected paragraph labels and internal detail/paragraph links.
- Omission test asserts no section renders without usable story/local article content.
- Escaping/link-safety test injects markup, external links, and unsafe fragments.
- Fallback test asserts the section can render from story text when no saved local article exists.
- Cap test asserts only the first three editorial items render.
- Ordering test asserts `saved-article-content-organization` appears before `editorial-brief`, and `editorial-brief` appears before `lead-story`.
- Workflow test asserts generated HTML includes the section while `edition`, `manifest`, and `runtime` JSON payloads do not include `editorial_brief` or `daily_information_layer`.
- Docs test asserts README and `docs/row-one.md` describe the Stage 321 generated-site-only boundary.
- CSS test asserts the new selectors and mobile breakpoint exist.

## Risks

- `templates.py` is already large. Keep helpers private, small, and localized to the generated-site rendering path.
- Saved article data can be missing or sparse. The section must omit itself or fall back to story text without throwing.
- The feature must not imply generated editorial claims beyond existing local data. Copy should describe it as a local editorial brief built from saved sources and story summaries.

## Definition Of Done

- Stage 321 spec and plan are reviewed by Claude Code before implementation.
- The generated homepage has a local prose section that organizes existing saved article/story data.
- No JSON contract, schema, source collection, fetching, scoring, LLM, connector, or compliance behavior changes.
- Focused tests, full tests, Ruff, lock check, and release hygiene pass.
- Claude Code code review has no unresolved Critical or Important findings.
- Changes are committed and pushed to `origin/main`.
