# Stage 344 ROW ONE Saved Article Organization Coverage Matrix Design

## Objective

Stage 344 improves `articles/index.html` with a generated-site-only Saved
Article Organization Coverage Matrix. The matrix shows, article by article, how
each saved local article participates across existing Saved Article Content
Organization groups.

## Product Gap

ROW ONE now has local article pages, reading improvements, information panels,
paragraph context cues, evidence boards, reading paths, a reference atlas, a
theme digest, and group summaries. Stage 343 explains each organization group,
but readers still need to scan repeated cards to understand which saved articles
have broad organization coverage across read-first, people/brands, products, and
source-structure groupings.

The matrix closes that gap by making cross-group coverage visible at a glance. It
is an information-organization layer, not a recommendation rail and not another
collection feature.

## Architecture

This is a generated-site-only rendering change in
`src/fashion_radar/row_one/templates.py`. It reuses
`RowOneSavedArticleContentOrganization.groups`, existing group cards, existing
safe detail-path validation, existing paragraph indices, and existing references.
It does not create new models, schemas, app-facing JSON artifacts, route
families, source collection, extraction, ranking, scheduling, deployment,
analytics, personalization, recommendation, or compliance-review behavior.

The implementation should add a private renderer near
`_render_saved_article_content_organization()`:

- `_render_saved_article_organization_coverage_matrix(organization, href_prefix)`

The content organization section inserts the matrix after its section header and
before the existing group list. If no safe organization cards exist, the matrix
returns an empty string and the existing group cards render as they do today.

## Rendering Behavior

The matrix should group safe organization cards by validated detail page path in
first-seen article order. Each article row should show:

- article title from the first safe card for that detail path
- normalized source name
- distinct organization group chips for the groups where that article appears
- saved section/card count for that article
- strict evidence paragraph count, deduped by paragraph index within that article
- capped first-seen reference chips, deduped by normalized `(name, type, label)`
- a safe internal link to the first organized section for that article

The matrix should sit visually inside the Saved Article Content Organization
section, before the existing group grids. It should use bilingual labels where
the surrounding section does and should escape all rendered text.

## Sanitization And Caps

Only cards accepted by `_safe_saved_article_content_organization_href()` should
contribute to the matrix. The matrix should use the validated detail page path as
the article key, ignoring fragments for article-level grouping. Evidence counts
must accept only strict integer paragraph indices; bools, strings, negative
values, and duplicates must not inflate counts. References must be normalized,
escaped, deduped, and capped to a small fixed number in first-seen card order.

Rows should be capped to keep the library page scan-friendly. The cap should be
deterministic and preserve first-seen article order from the current
organization data.

## Out Of Scope

Stage 344 does not add article downloading, social-platform collection, external
tool adapters, scraping, browser automation, platform APIs, account/cookie/token
behavior, ranking, demand proof, heat scoring, analytics, personalization,
recommendation, compliance review, new JSON artifacts, new route families, app
contract changes, or outbound article URLs as primary navigation. It only
improves the generated ROW ONE saved article library HTML from existing local
organization data.

## Acceptance Criteria

- `articles/index.html` renders one Saved Article Organization Coverage Matrix
  before the existing Saved Article Content Organization group grids when safe
  organization cards exist.
- Rows are grouped by validated saved article detail page path, not by section
  fragment.
- Each row shows factual organization coverage: group chips, saved section count,
  evidence paragraph count, and capped reference chips.
- Unsafe card paths do not contribute to rows, counts, references, or links.
- Paragraph evidence counts ignore bool, non-int, negative, and duplicate indices.
- Reference chips are escaped, deduped, and capped.
- Documentation states the generated-site-only boundary for Stage 344.
- Workflow tests confirm no app-facing contract keys, schemas, route families, or
  JSON/HTML artifact files are created for this matrix.
