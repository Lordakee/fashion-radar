You are reviewing Stage 322 of Fashion Radar / ROW ONE.

Objective:
- Add a generated-site-only Editorial Source Trail inside existing ROW ONE homepage Editorial Brief cards.
- The trail uses existing saved local article source names, titles, brief sections, content sections, paragraph anchors, and safe detail routes.
- This must not add JSON contract fields, schema changes, source collection, fetching, scoring, LLM calls, connectors, image generation, deployment behavior, or compliance-review product features.

Review the current working tree diff against HEAD. Focus on:
1. Generated-site-only boundary: no new app/runtime/manifest JSON fields or schemas.
2. Correctness of trail labels, caps, dedupe, omission, and bilingual rendering.
3. Link safety: all hrefs must go through existing safe detail/paragraph/content-section allowlists.
4. XSS safety: all displayed text must be escaped.
5. Test coverage: render, omission, unsafe links, cap/dedupe, workflow boundary, docs, CSS.
6. Scope creep or duplicated homepage content.

Commands already run:
- Stage 322 focused pytest suite.
- `UV_NO_CONFIG=1 uv --no-config run --frozen ruff check --fix ...` on touched source/tests.
- `UV_NO_CONFIG=1 uv --no-config run --frozen ruff format ...` on touched source/tests.
- `UV_NO_CONFIG=1 uv --no-config run --frozen ruff check`.
- `UV_NO_CONFIG=1 uv --no-config run --frozen ruff format --check`.
- `git diff --check`.

Return findings grouped by Critical, Important, Minor. If no Critical/Important issues remain, say so explicitly.
