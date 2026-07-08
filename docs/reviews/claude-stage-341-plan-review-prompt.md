# Claude Code Review Prompt: Stage 341 Plan

Please review the Stage 341 plan for the Fashion Radar / ROW ONE project.

## Objective

Stage 341 should add a generated HTML-only local article information panel to first-class `articles/<story-id>.html` pages. The panel should help readers scan already-saved local article text by showing source/body/paragraph/section metrics, section cards, reference chips, and safe page-local links.

## Proposed Technical Approach

- Tech stack: Python 3.12, existing ROW ONE dataclasses/models, static HTML/CSS templates, pytest, ruff, uv.
- Primary implementation file: `src/fashion_radar/row_one/templates.py`.
- Add `_render_local_article_information_panel(edition, story, local_article, section_title)`.
- Call it from `render_local_article_page_html()` before the existing local article section.
- Render only generated HTML/CSS and same-page `#local-article-*` links.
- Add tests in `tests/test_row_one_render.py`.
- Add docs/workflow guards in `README.md`, `docs/row-one.md`, `tests/test_row_one_docs.py`, and `tests/test_workflows.py`.

## Files To Review

- `docs/superpowers/specs/2026-07-08-stage-341-row-one-local-article-information-panel-design.md`
- `docs/superpowers/plans/2026-07-08-stage-341-row-one-local-article-information-panel-plan.md`

## Review Questions

1. Is the plan technically feasible within the current ROW ONE template/render pipeline?
2. Is `render_local_article_page_html()` the right insertion point?
3. Does the plan stay generated-site-only without schema, contract, sidecar, model, render.py, extraction, ranking, scheduling, deployment, analytics, personalization, recommendation, or compliance-review scope creep?
4. Are the proposed local-anchor, escaping, dedupe, cap, and strict paragraph-index rules sufficient?
5. Are the tests enough to catch unsafe links, escaped content, invalid paragraph indices, contract drift, and CSS coverage?
6. Are there any simpler or safer implementation boundaries before coding?

## Expected Output

Return:

- Approved / Not approved.
- Critical issues, if any.
- Important issues, if any.
- Minor suggestions, if any.
- A short recommendation for implementation.
