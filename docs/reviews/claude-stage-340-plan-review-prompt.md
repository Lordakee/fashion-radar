# Claude Code Review Prompt: Stage 340 Plan

Please review the Stage 340 plan for the Fashion Radar / ROW ONE project.

## Objective

Stage 340 should add a deterministic saved article paragraph quality gate for ROW ONE local article bodies. The goal is to filter high-confidence extraction boilerplate before saved local article paragraphs are written to existing sidecars and rendered into local pages.

## Proposed Technical Approach

- Tech stack: Python 3.12, existing ROW ONE dataclasses/models, deterministic regex/string filtering, pytest, ruff, uv.
- Primary implementation file: `src/fashion_radar/row_one/articles.py`.
- Add a private predicate such as `_publishable_local_article_paragraph(paragraph: str) -> bool`.
- Call it inside `text_to_local_article_paragraphs()` after paragraph normalization and before `max_chars` accounting.
- Keep low-quality paragraphs from consuming the article character budget.
- Preserve short valid fashion-news paragraphs.
- Reuse existing fallback behavior: extracted text with zero publishable paragraphs should flow to `summary_fallback` with `no_publishable_paragraphs`.
- Do not change app/runtime/manifest schemas or add JSON artifacts.

## Files To Review

- `docs/superpowers/specs/2026-07-08-stage-340-row-one-saved-article-paragraph-quality-gate-design.md`
- `docs/superpowers/plans/2026-07-08-stage-340-row-one-saved-article-paragraph-quality-gate-plan.md`

## Review Questions

1. Is the plan technically feasible within the current ROW ONE local article pipeline?
2. Is `text_to_local_article_paragraphs()` the right insertion point for this quality gate?
3. Are the proposed filter rules conservative enough to avoid dropping terse valid fashion-news paragraphs?
4. Are fallback behavior, paragraph-index alignment, and `paragraphs_zh` alignment covered well enough?
5. Does the plan avoid schema, app contract, scraping, source collection, ranking, social connector, scheduling, deployment, and compliance-review scope creep?
6. Are the tests sufficient to catch false positives, false negatives, and contract drift?

## Expected Output

Return:

- Approved / Not approved.
- Critical issues, if any.
- Important issues, if any.
- Minor suggestions, if any.
- A short recommendation for implementation.
