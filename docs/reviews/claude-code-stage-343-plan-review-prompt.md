# Claude Code Stage 343 Plan Review Prompt

You are reviewing a planned development node in `/home/ubuntu/fashion-radar`.
Use maximum reasoning. Operate read-only. Do not edit files.

## Objective

Review Stage 343 before implementation. The goal is to add generated-site-only
Saved Article Content Organization group summary strips inside `articles/index.html`.
Each non-empty organization group should show a compact overview before its card
grid: saved-card count, saved-article count, source count, evidence paragraph
count, and capped recurring reference chips.

## Proposed Architecture

- Python renderer-only change in `src/fashion_radar/row_one/templates.py`.
- Reuse existing `RowOneSavedArticleContentOrganizationGroup.cards`, card
  `detail_path`, card `references`, and card `paragraph_indices`.
- Reuse `_safe_saved_article_content_organization_href`,
  `_prefixed_saved_article_content_organization_href`,
  `_render_saved_article_content_organization_ref_chip`, existing escaping, and
  existing `normalize_row_one_paragraph` conventions.
- Insert the summary in `_render_saved_article_content_organization_group()`
  between group header and group card grid.
- Add CSS under `.saved-article-content-organization-summary*`.
- Add render tests, docs boundary tests, workflow no-artifact/no-contract guards,
  and docs paragraphs.

## Tech Stack

Python 3.12, pytest, ruff, uv, existing ROW ONE dataclasses/models and HTML
string templates. No new dependencies.

## Implementation Method

Follow the plan in:

`docs/superpowers/plans/2026-07-08-stage-343-saved-article-content-organization-group-summary-plan.md`

and the design in:

`docs/superpowers/specs/2026-07-08-stage-343-saved-article-content-organization-group-summary-design.md`

## Scope Boundaries

This stage must not add cross-article recommendation rails, article downloading,
social-platform collection, external tool adapters, scraping, browser automation,
platform APIs, account/cookie/token behavior, ranking, demand proof, analytics,
personalization, recommendation, compliance-review functionality, new JSON
artifacts, new routes, or app contract changes. It only improves generated ROW
ONE saved article library HTML from existing local organization data.

## Review Questions

1. Is the plan technically reasonable for the existing renderer architecture?
2. Are the proposed tests sufficient and correctly scoped?
3. Are there hidden compatibility risks around safe href filtering, evidence
   paragraph dedupe, reference dedupe/cap/escaping, or content organization
   ordering?
4. Does the plan accidentally imply new contracts, artifacts, source collection,
   social platform collection, recommendation behavior, or compliance-review
   behavior?
5. What critical or important changes are required before implementation?

Return a concise review with severity-labeled findings. If there are no
critical or important blockers, state that the plan is approved for
implementation.
