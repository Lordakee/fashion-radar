Review the Stage 339 ROW ONE plan before implementation.

Repository: `/home/ubuntu/fashion-radar`

Stage 339 goal:

- Add generated-site-only first-class local article pages at
  `articles/<story-id>.html`.
- Reuse existing current-edition `RowOneLocalArticle` sidecars, saved local
  paragraphs, provenance, article maps, digest, reader, paragraph evidence,
  content sections, and existing detail-page routes.
- Keep `articles/index.html` as the daily saved article library and make the
  first-class local article page the primary local reading action from library
  cards.
- Preserve existing `details/*.html#local-article-*` anchors.

Review these files:

- `docs/superpowers/specs/2026-07-08-stage-339-row-one-local-article-pages-design.md`
- `docs/superpowers/plans/2026-07-08-stage-339-row-one-local-article-pages-plan.md`
- Current ROW ONE render/template context under `src/fashion_radar/row_one/`
- Current tests under `tests/test_row_one_render.py`, `tests/test_row_one_docs.py`,
  and `tests/test_workflows.py`

Scope boundaries:

- No scraping, fetching, article extraction, platform APIs, connectors, LLM
  calls, translation service, image generation, ranking, scoring, market
  grouping, scheduling, deployment, or compliance-review feature.
- No change to `row-one-app/v7`, `row-one-manifest/v1`,
  `row-one-runtime/v1`, schemas, `data/edition.json`, `data/manifest.json`,
  or `data/runtime.json` contracts.
- No new generated JSON artifact such as `data/local-article-pages.json`.
- No removal of existing detail-page local article sections or anchors.

Please answer:

1. Are the design and plan feasible against the current codebase?
2. Are there Critical or Important blockers before implementation?
3. Does the plan preserve the stated generated-site-only and contract-stability
   boundaries?
4. Are there missing tests or route-safety checks that should be added before
   coding?

Return findings first, grouped as Critical / Important / Minor. If there are no
Critical or Important findings, say so clearly and state whether implementation
may proceed.
