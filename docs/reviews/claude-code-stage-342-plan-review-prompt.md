# Claude Code Stage 342 Plan Review Prompt

You are reviewing a planned development node in `/home/ubuntu/fashion-radar`.
Use maximum reasoning. Operate read-only. Do not edit files.

## Objective

Review Stage 342 before implementation. The goal is to add generated-site-only
saved paragraph context cues to ROW ONE local article pages. Each saved paragraph
that is cited by existing `RowOneLocalArticle.content_sections[*].items[*].paragraph_indices`
should show a compact cue linking back to the relevant page-local organized
content section.

## Proposed Architecture

- Python renderer-only change in `src/fashion_radar/row_one/templates.py`.
- Add any support type near the existing local article paragraph support models.
- Reuse existing `RowOneLocalArticle.content_sections`, `paragraph_indices`,
  `_strict_valid_local_article_paragraph_indices`,
  `_local_article_rendered_paragraph_indices`,
  `_local_article_paragraph_anchor`, and `_local_article_content_section_anchor`.
- Preserve existing `id="local-article-paragraph-N"` anchors and bilingual text
  spans in `_render_local_article_paragraphs(article)`.
- Add escaped, capped, deduped context cues that use page-local
  `#local-article-content-section-N` links.
- Keep generated-site workflow coverage positive for article-page HTML and
  negative for app-facing JSON/contracts/artifacts.
- Add CSS under `.local-article-paragraph-context*`.
- Add render tests, docs boundary tests, workflow no-artifact/no-contract guards,
  and docs paragraphs.

## Tech Stack

Python 3.12, pytest, ruff, uv, existing ROW ONE Pydantic models and HTML string
templates. No new dependencies.

## Implementation Method

Follow the plan in:

`docs/superpowers/plans/2026-07-08-stage-342-row-one-saved-paragraph-context-cues-plan.md`

and the design in:

`docs/superpowers/specs/2026-07-08-stage-342-row-one-saved-paragraph-context-cues-design.md`

## Scope Boundaries

This stage must not add article downloading, social-platform collection,
external tool adapters, scraping, browser automation, platform APIs,
account/cookie/token behavior, ranking, demand proof, analytics,
personalization, recommendation, compliance-review functionality, new JSON
artifacts, or app contract changes. It only improves the generated ROW ONE
website for already-saved local article paragraphs.

## Review Questions

1. Is the plan technically reasonable for the existing renderer architecture?
2. Are the proposed tests sufficient and correctly scoped?
3. Are there hidden compatibility risks around paragraph indices, blank
   paragraphs, bilingual rendering, escaping, or anchor links?
4. Does the plan accidentally imply new contracts, artifacts, extraction, social
   platform collection, or compliance-review behavior?
5. What critical or important changes are required before implementation?

Return a concise review with severity-labeled findings. If there are no
critical or important blockers, state that the plan is approved for
implementation.
