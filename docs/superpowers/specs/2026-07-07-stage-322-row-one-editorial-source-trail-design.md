# Stage 322 ROW ONE Editorial Source Trail Design

## Goal

Add a generated-site-only `Editorial Source Trail / 编辑来源线索` layer inside the existing ROW ONE homepage `Editorial Brief / 编辑正文` cards. The trail should show where each editorial paragraph came from and give readers safe local jumps into existing saved article sections or paragraph anchors.

## User Value

Stage 321 made the homepage more narrative, but readers still need a clearer path from the prose back to the locally saved evidence. Stage 322 should improve `整理信息的能力` by making each editorial paragraph traceable to existing saved local article metadata, brief sections, content sections, and paragraph anchors without adding another large homepage section.

## Scope

- Render HTML only inside existing generated ROW ONE homepage Editorial Brief cards.
- Keep the homepage section order unchanged:
  - Daily Edit
  - Daily Local Intelligence
  - Saved Article Coverage
  - Saved Article Briefs
  - Saved Article Content Organization
  - Editorial Brief
  - lead story unchanged
- Use existing in-memory data:
  - `RowOneEdition`
  - `RowOneStory`
  - matching `RowOneLocalArticle`
  - existing `brief_sections`
  - existing `content_sections`
  - existing `paragraphs`
  - existing detail routes and local article anchors
- Add a compact trail to each generated editorial brief item when useful:
  - source/title context stays in the existing Editorial Brief metadata, not as a duplicate trail chip
  - the supporting brief-section label when the paragraph used one
  - the supporting local content-section or paragraph link when available
- Cap trails so cards stay compact.
- Escape all displayed text.
- Validate every href at render time with the same allowlist already used by Editorial Brief:
  - validated detail paths
  - `#local-article-paragraph-N`
  - `#local-article-content-section-N`
- Omit the trail when no useful source context exists.

## Non-Goals

- Do not add `editorial_source_trail`, `source_trail`, `editorial_brief_trail`, or any new field to `data/edition.json`.
- Do not change `row-one-app/v7`.
- Do not change `row-one-manifest/v1`.
- Do not change `row-one-runtime/v1`.
- Do not change schemas.
- Do not write a new JSON artifact.
- Do not add source collection, article fetching, scoring, matching, LLM calls, connectors, deployment behavior, image generation, or compliance-review product features.
- Do not rename detail routes, story IDs, local article paragraph anchors, or local article content-section anchors.
- Do not add dependencies.

## Recommended Approach

Extend the private render-only dataclasses introduced in Stage 321. Keep the objects in `templates.py` because they are only consumed by generated-site rendering and must not become a public app contract.

```python
@dataclass(frozen=True)
class _EditorialBriefTrailItem:
    label: LocalizedText
    href: str | None = None


@dataclass(frozen=True)
class _EditorialBriefItem:
    title: LocalizedText
    body: LocalizedText
    meta: LocalizedText | None = None
    href: str | None = None
    trail: tuple[_EditorialBriefTrailItem, ...] = ()
```

`render.py` should continue to build `_EditorialBrief` from `edition` and `local_articles_by_story_id`. Each of the three existing editorial cards should get deterministic trail items:

- `What changed today`
  - Keep source name and saved article title in the existing card metadata.
  - `What happened` trail link to the first saved paragraph when available, otherwise the existing detail page.
- `Why it matters`
  - `Why it matters` trail link to the existing detail page.
  - If local article content sections include a useful `entities`, `brand_signals`, or `takeaways` section, add the first available content-section trail link.
- `What to read locally`
  - `watch_next` trail link to the first saved paragraph when the section exists.
  - If `watch_next` is missing but saved paragraphs exist, show one `Saved paragraph 1 / 保存段落 1` trail chip.
  - Otherwise use the validated story detail route through the card's primary `Read locally / 本地阅读` action.

The template should render trail items as compact chips/links inside the existing card. To avoid nested interactive elements and keep one consistent card structure, all Editorial Brief cards should render as `<article class="editorial-brief-card">` containers. The primary local navigation moves from the old card-wrapping anchor to a standalone `<a class="editorial-brief-link">Read locally / 本地阅读</a>` action after the body/trail. It should never create external links. Unsafe hrefs should render as plain chips.

## Content Rules

- Use `LocalizedText` for all labels.
- Keep source/title context in the existing card metadata when at least one part is non-empty after cleanup.
- Do not render source/title context as a trail chip on the same card.
- Keep trail labels short:
  - `What happened / 发生了什么`
  - `Why it matters / 为什么重要`
  - `Saved paragraph 1 / 保存段落 1`
  - existing local content-section titles when available
- Cap trail items at `EDITORIAL_BRIEF_MAX_TRAIL_ITEMS = 3` per card.
- Deduplicate trail items by normalized localized label and safe href.
- Do not duplicate card body text inside the trail.
- Do not create a trail if the card has no useful source/local context beyond its primary card href.
- Preserve `trail` when deduplicating `_EditorialBriefItem` objects in the render builder.

## Link Safety

Reuse `_safe_editorial_brief_href(href)` in `templates.py`.

Allowed:

- `details/<validated-story>.html`
- `details/<validated-story>.html#local-article-paragraph-N`
- `details/<validated-story>.html#local-article-content-section-N`

Rejected:

- external URLs
- `javascript:` URLs
- path traversal
- unknown fragments
- empty hrefs

Unsafe trail hrefs render as non-link chips; unsafe primary card hrefs already render as plain article cards.

## Styling

Add compact styles to the existing Editorial Brief CSS:

- `.editorial-brief-trail`
- `.editorial-brief-trail-item`
- `.editorial-brief-trail a`
- `.editorial-brief-link`

The trail should sit below the paragraph/meta and above the standalone `Read locally / 本地阅读` action. It should wrap on narrow cards and collapse naturally under the existing `760px` breakpoint.

## Testing Requirements

- Render test: `render_row_one_site()` with a local article sidecar shows the Editorial Brief trail inside the existing `editorial-brief` section.
- Trail content test: verifies source/title context, bilingual labels, content-section link, and paragraph link.
- Omission test: verifies no trail block appears when no local sidecar/source context exists.
- Link safety test: verifies unsafe trail hrefs are rendered as plain chips, while safe paragraph/content-section hrefs render as links.
- Cap/dedupe test: verifies at most three trail items per card and duplicate labels/hrefs collapse.
- Workflow boundary test: generated HTML includes the source trail, while `edition`, `manifest`, and `runtime` JSON payloads do not include Stage 322 keys.
- CSS test: verifies the new selectors exist.
- Docs test: README and `docs/row-one.md` describe Stage 322 as generated-site-only and explicitly state no contract/schema/artifact/source/scoring/LLM/connector/compliance changes.

## Risks

- Homepage density: keep the trail inside existing Editorial Brief cards and cap items.
- Duplicate information: trail should show provenance and local jump points, not repeat the paragraph body.
- Link drift: every href is still validated at render time.
- Scope creep: do not add a new section, JSON contract field, collector, or summarization system in this node.

## Definition Of Done

- Stage 322 spec and plan are reviewed by Claude Code before implementation.
- Editorial Brief cards can show compact provenance/source trails from existing local article data.
- The feature is generated-site-only and keeps all JSON contracts stable.
- Focused tests, full tests, Ruff, lock check, and release hygiene pass.
- Claude Code code review has no unresolved Critical or Important findings.
- Changes are committed and pushed to `origin/main`.
