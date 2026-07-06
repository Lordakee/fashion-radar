Review the Stage 316 design and implementation plan in `/home/ubuntu/fashion-radar`.

Files to review:
- `docs/superpowers/specs/2026-07-06-stage-316-row-one-local-article-content-organization-design.md`
- `docs/superpowers/plans/2026-07-06-stage-316-row-one-local-article-content-organization-plan.md`

Project goal:
- ROW ONE should become a useful daily fashion-news website that stores and presents organized article content locally, not just a link aggregator.
- Stages 310-315 already render saved local article bodies, briefs, coverage, observability, and readiness diagnostics.

Stage 316 proposed goal:
- Add a generated-site homepage content organization section built from existing saved local article `content_sections`.
- The feature should be deterministic, local-only, generated-site only, and should not collect sources, fetch article pages, call LLMs, alter scoring, activate connectors, add compliance-review features, or change generated app/manifest/runtime JSON contracts.

Technology and approach:
- New pure builder module: `src/fashion_radar/row_one/saved_article_content_organization.py`
- Wire through `render_row_one_site()` into `render_index_html()`
- Render homepage HTML only
- Tests in `tests/test_row_one_saved_article_content_organization.py`, `tests/test_workflows.py`, and `tests/test_row_one_docs.py`

Please evaluate:
1. Is the Stage 316 scope technically sound and aligned with moving from “links only” toward locally organized article content?
2. Does the plan preserve `row-one-app/v7`, manifest/runtime contracts, schemas, source collection, extraction, scoring, connectors, and compliance-review boundaries?
3. Are the proposed builder semantics deterministic and safe?
4. Are the tests sufficient to catch stale sidecars, mismatched article IDs, unsafe paths, invalid IDs, blank paragraphs, anchor drift, and contract creep?
5. Is the proposed homepage rendering insertion point appropriate?
6. Are there any blocking issues in the concrete file plan, test expectations, anchor targets, or docs guards?

Return findings first, ordered by severity. Mark any Critical or Important items that must be fixed before implementation. If no Critical/Important findings exist, say that explicitly and list Minor/Nit findings separately.
