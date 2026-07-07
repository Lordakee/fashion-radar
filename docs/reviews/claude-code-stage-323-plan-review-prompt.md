Review Stage 323 plan for Fashion Radar / ROW ONE.

Return a complete, concise review under 60 lines. Do not include long code
blocks. Lead with Critical and Important findings only. If there are no
unresolved Critical or Important findings, state that clearly.

Repo: /home/ubuntu/fashion-radar

Objective:
Make ROW ONE generated pages prioritize locally saved article reading when saved paragraphs exist, and let saved content-organization cards jump directly to supporting saved paragraphs. This directly supports the product goal that ROW ONE should organize and publish locally saved fashion/news content instead of acting only as a link list.

Technical approach:
- Generated ROW ONE HTML/CSS only.
- Add a private optional `local_articles_by_story_id` argument to `render_index_html()`.
- Pass the existing map from `render_row_one_site()` into the generated homepage render call.
- Render local-first CTA/badge HTML from existing `RowOneLocalArticle` paragraphs.
- Keep ordinary headline/detail links pointing to generated detail pages.
- Add detail-page local-first action before the external source action.
- Convert saved article content-organization cards from wrapping `<a>` elements to `<article>` containers with standalone links.
- Add safe evidence paragraph links from existing `card.paragraph_indices`.
- Keep all app/runtime/manifest JSON contracts unchanged.

Tech stack:
- Python
- Existing ROW ONE Pydantic models
- Existing string-rendered HTML/CSS in `src/fashion_radar/row_one/templates.py`
- Existing `render_row_one_site()` pipeline in `src/fashion_radar/row_one/render.py`
- pytest
- Ruff

Files to review:
- Spec: `docs/superpowers/specs/2026-07-07-stage-323-row-one-local-first-reading-design.md`
- Plan: `docs/superpowers/plans/2026-07-07-stage-323-row-one-local-first-reading-plan.md`
- Relevant existing code: `src/fashion_radar/row_one/templates.py`, `src/fashion_radar/row_one/render.py`
- Relevant existing tests: `tests/test_row_one_render.py`, `tests/test_workflows.py`, `tests/test_row_one_docs.py`

Hard boundaries:
- Do not change `row-one-app/v7`.
- Do not change `data/edition.json`.
- Do not add `local_first_read`, `local_read_path`, `saved_article_cta`, `evidence_paragraph_trail`, `paragraph_trail`, or new app payload fields.
- Do not change `row-one-manifest/v1`.
- Do not change `row-one-runtime/v1`.
- Do not change schemas or Pydantic models.
- Do not write a new JSON artifact.
- Do not add source collection, article fetching, extraction behavior, scoring, matching, ranking, LLM calls, translation calls, image generation, connectors, deployment behavior, scheduling behavior, or compliance-review product features.
- Do not rename story IDs, detail routes, local article reader anchors, paragraph anchors, or content-section anchors.
- Do not add dependencies.

Please review the plan for:
- feasibility and reasonableness
- technical correctness
- test coverage adequacy
- href safety
- no nested anchor risk
- JSON contract boundaries
- missing implementation steps
- any Critical or Important findings that must be fixed before implementation

Specific rereview focus:
- Prior review found that the plan incorrectly used nonexistent `story_id` and
  `section_key` constructor fields on `RowOneSavedArticleContentOrganizationCard`.
- Prior review found that the plan incorrectly used Pydantic `model_copy()` on a
  frozen dataclass.
- Prior review found that the bad-index safety card count assertion was wrong.
- Prior review found a mismatch between the homepage `local-read-action` test
  and implementation steps.
- Rereview found that Step 1 still asserted old `Read the brief` / `Read brief`
  CTA labels even when the only story has a local-first action.
- The plan has been revised to use `dataclasses.replace()`, valid dataclass
  fields, `#local-article` as the local-first target, homepage CTA classes, and
  negative assertions for the replaced old CTA labels.
Please verify those fixes and identify any remaining blockers.
