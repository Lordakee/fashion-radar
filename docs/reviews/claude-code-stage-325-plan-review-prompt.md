You are reviewing Fashion Radar Stage 325 before implementation.

Repository: /home/ubuntu/fashion-radar
Branch: main

Stage 325 objective:
- Close three non-blocking Stage 324 code-review polish items for the generated ROW ONE detail-page paragraph evidence index:
  1. omit empty reference wrappers when a paragraph evidence support item has no references
  2. fallback to the English item body excerpt when `item.body.zh` is blank
  3. explicitly test the local article map link to `#local-article-paragraph-evidence`

Architecture and tech stack:
- Python.
- Existing ROW ONE Pydantic models.
- Existing string-rendered HTML/CSS in `src/fashion_radar/row_one/templates.py`.
- Existing `render_detail_html()` tests in `tests/test_row_one_render.py`.
- pytest and Ruff.
- No new dependencies.

Files to review:
- `docs/superpowers/specs/2026-07-07-stage-325-row-one-paragraph-evidence-polish-design.md`
- `docs/superpowers/plans/2026-07-07-stage-325-row-one-paragraph-evidence-polish-plan.md`
- Existing context:
  - `src/fashion_radar/row_one/templates.py`
  - `tests/test_row_one_render.py`
  - `docs/reviews/claude-code-stage-324-code-review.md`
  - `AGENTS.md`

Review focus:
1. Is this a valid small Stage 325 after Stage 324?
2. Is the plan generated-site-only, with no JSON/model/schema/source/acquisition/LLM/connector/scheduling/deployment/compliance scope drift?
3. Are the planned failing tests executable against current code?
4. Is the proposed implementation technically reasonable and minimal?
5. Are there any missing edge cases or review-protocol conflicts?

Return:
- Critical findings, if any.
- Important findings, if any.
- Minor suggestions, if any.
- A final verdict: approved to implement, or not approved until specified changes are made.

Do not implement code. This is a read-only plan review.
