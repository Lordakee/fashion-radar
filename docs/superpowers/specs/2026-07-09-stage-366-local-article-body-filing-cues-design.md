# Stage 366 Local Article Body Filing Cues Design

## Objective

Stage 366 adds generated-site-only **Local Article Body Filing Cues** inside each first-class ROW ONE local article page at `articles/<story-id>.html`. The cues appear inline in the saved local article body and label each rendered paragraph as either filed under existing organized content sections/items or unfiled saved text.

## Why This Node

Stages 354-365 added pre-body orientation: reading companion, section binder, key signals, and content segment cards. The remaining narrow gap is inside the saved body itself. When a reader reaches the full local article text, the page should show whether each saved paragraph is connected to the existing content organization or is still unfiled.

This is a better fit than a separate paragraph navigator because the page already has reader/digest/pre-body navigation. Body filing cues strengthen the local information organization without creating another redundant pre-body summary.

## Placement

Render cues only inside the saved local article body paragraphs on `articles/<story-id>.html`.

The cues are part of the existing `#local-article-body` paragraph stream:

- filed paragraphs show a compact "Filed under" cue with links back to existing `#local-article-content-section-N` anchors.
- unfiled paragraphs show a compact "Unfiled saved paragraph" cue.

The cues must not render on:

- `index.html`
- `articles/index.html`
- `details/<story-id>.html`
- generated app/runtime/manifest JSON payloads
- any new route family or sidecar artifact

## Data Sources

Use only existing in-memory render data already available to `_render_local_article_paragraphs(...)`:

- `RowOneLocalArticle.paragraphs`
- aligned `RowOneLocalArticle.paragraphs_zh` when present
- `RowOneLocalArticle.content_sections`
- existing section titles
- existing item labels
- existing item-level paragraph indices
- existing content-section anchors

No new database query, source collection, source fetch, extraction pass, LLM call, scoring pass, ranking pass, scheduler, deployment behavior, analytics behavior, recommendation behavior, personalization behavior, app-facing contract, schema, JSON artifact, or compliance-review behavior is introduced.

## Content Model

The cue model is render-only and private to `templates.py`.

Each rendered paragraph receives one cue:

- if one or more existing content-section items cite the paragraph, render up to three context links.
- each filed context link points to the existing content-section anchor and uses the item label when present, falling back to the section title when the item label is blank.
- if no valid content section/item references cite the paragraph, render a non-linked unfiled cue.

The existing Stage 342 paragraph context cue already labels cited paragraphs as "Used in". Stage 366 extends that paragraph-body surface by adding explicit unfiled-state coverage and clearer body filing semantics. It must not duplicate a full navigator or summary.

## Caps and Omission Rules

Use deterministic caps:

- maximum filed context links per paragraph: 3
- no excerpts or full paragraph duplication inside the cue

Render cues only for nonblank saved paragraphs that are already being rendered. Do not emit cue wrappers outside paragraph bodies.

## Safety and Escaping

All data-derived text must be normalized and escaped with existing helpers.

Links must be same-page content-section anchors only:

- `#local-article-content-section-N`

Paragraph index validation must reuse `_strict_valid_local_article_paragraph_indices(...)` for item-level paragraph indices so booleans, strings, negative indices, overflow indices, duplicate indices, and unrendered blank paragraphs cannot create filing links.

The feature must not accept outbound URLs, relative paths, traversal paths, JavaScript URLs, malformed anchors, or zero/leading-zero anchors.

## Styling

Add scoped CSS selectors under `.local-article-body-filing-cue`. The cue should be compact enough to live inside paragraph text:

- small uppercase label
- subdued filed/unfiled chip treatment
- same-page section links
- no new page-wide visual system

The cue must remain readable on mobile without changing local article layout.

## Documentation and Guardrails

Document Stage 366 in `README.md` and `docs/row-one.md` before Stage 365. The docs must say this is generated-site-only, article-page-only, and uses existing saved local article paragraphs and content-section references.

Add workflow and documentation guards so future changes do not convert this into:

- an app contract field
- a schema version change
- a JSON artifact
- a new route family
- homepage/library/detail-page feature
- fetch/extraction/scoring/ranking/LLM/scheduling/analytics/recommendation/personalization/compliance-review feature

## Non-Goals

- No `data/local-article-body-filing-cues.json`
- No `data/article-body-filing-cues.json`
- No `data/body-filing-cues.json`
- No `data/paragraph-filing-cues.json`
- No app-facing payload field
- No schema/runtime/manifest version bump
- No new route
- No homepage section
- No article library section
- No detail-page section
- No separate paragraph navigator
- No source collection, extraction, matching, scoring, ranking, LLM, connector, scheduler, deployment, analytics, personalization, recommendation, or compliance-review behavior

## Acceptance Criteria

- `render_local_article_page_html(...)` renders body filing cues inside `#local-article-body` for eligible saved paragraphs.
- Filed paragraphs link only to existing `#local-article-content-section-N` anchors.
- Item-level paragraph references use item labels when present and fall back to section titles when blank.
- Section-level filing meaning is derived from the item reference's parent section; the current `RowOneLocalArticleContentSection` model has no standalone `paragraph_indices` field.
- Unreferenced nonblank paragraphs render an "Unfiled saved paragraph" cue.
- Existing Stage 354/355/356/365 ordering remains intact.
- Existing local article paragraph anchors remain unchanged.
- HTML escaping prevents raw hostile text from rendering.
- Site generation writes cues only to `articles/<story-id>.html`.
- Contract JSON and generated artifacts do not contain Stage 366 names.
- Focused tests, full tests, lint, formatting, release hygiene, offline lock check, and diff check pass.
