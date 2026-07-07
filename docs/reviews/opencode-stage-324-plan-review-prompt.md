You are reviewing Fashion Radar Stage 324 before implementation as the local fallback reviewer under the project review protocol.

Repository: /home/ubuntu/fashion-radar
Branch: main
Model: zhipuai-coding-plan/glm-5.2, variant max

User goal:
- ROW ONE should publish and organize locally saved fashion-news article content, not only provide links.
- This node should continue the staged workflow and must preserve existing JSON contracts and generated-site boundaries.

Stage 324 objective:
- Add a generated-site-only ROW ONE detail-page paragraph evidence index.
- It should map existing saved local article paragraphs back to existing organized local article content sections, item labels, and references.
- It must use only existing `RowOneLocalArticle` data already passed to detail rendering.

Architecture and tech stack:
- Python.
- Existing ROW ONE Pydantic models.
- Existing string-rendered HTML/CSS in `src/fashion_radar/row_one/templates.py`.
- Existing `render_row_one_site()` pipeline.
- pytest and Ruff.
- No new dependencies.

Files to review:
- `docs/superpowers/specs/2026-07-07-stage-324-row-one-paragraph-evidence-index-design.md`
- `docs/superpowers/plans/2026-07-07-stage-324-row-one-paragraph-evidence-index-plan.md`
- Existing implementation context:
  - `src/fashion_radar/row_one/templates.py`
  - `tests/test_row_one_render.py`
  - `tests/test_workflows.py`
  - `tests/test_row_one_docs.py`
  - `README.md`
  - `docs/row-one.md`
  - `AGENTS.md`

Review focus:
1. Is the Stage 324 goal useful and correctly scoped after Stage 323 local-first reading?
2. Is the design generated-site-only, with no contract/schema/model/source/acquisition/LLM/connector/scheduling/deployment/compliance-review scope drift?
3. Is the proposed implementation technically reasonable for the current code in `templates.py`?
4. Are the planned tests executable against the current project patterns?
5. Are there missing edge cases around paragraph-index validation, escaping, caps, dedupe, local anchors, or JSON contract boundaries?
6. Are there any conflicts with `AGENTS.md` or `docs/REVIEW_PROTOCOL.md`?

Return:
- Critical findings, if any.
- Important findings, if any.
- Minor suggestions, if any.
- A final verdict: approved to implement, or not approved until specified changes are made.

Do not implement code. This is a read-only plan review.
