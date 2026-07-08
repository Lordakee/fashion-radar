# Claude Code Stage 343 Code Review Prompt

You are reviewing completed Stage 343 code in `/home/ubuntu/fashion-radar`.
Use maximum reasoning. Operate read-only. Do not edit files.

## Goal
Stage 343 adds generated-site-only Saved Article Content Organization group summaries inside `articles/index.html`.

## Intended Scope
- Render one summary strip inside each saved article content organization group before the card grid.
- Reuse existing saved article content organization groups, existing organization cards, existing safe detail-path validation, existing card references, and existing paragraph indices.
- Show per-group metrics: saved card count, saved article count deduped by validated detail page path, source count deduped by normalized source name, and evidence paragraph count deduped by `(validated detail page path, strict paragraph index)`.
- Show capped first-seen reference chips, escaped and deduped by normalized `(name, type, label)`.
- Filter summary inputs with the same safe-card path rules used by cards.
- Keep this generated-site-only. Do not add app-facing contract fields, schemas, JSON artifacts, route families, source collection, extraction, ranking, scheduling, deployment, analytics, personalization, recommendation, or compliance-review functionality.

## Files to Review
- `src/fashion_radar/row_one/templates.py`
- `tests/test_row_one_render.py`
- `tests/test_workflows.py`
- `tests/test_row_one_docs.py`
- `README.md`
- `docs/row-one.md`
- Stage 343 plan/review artifacts under `docs/superpowers/` and `docs/reviews/`

## Verification Already Run
- `UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_render.py -q -k "content_organization_group_summary or saved_article_content_organization"` -> 9 passed
- `UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_docs.py tests/test_workflows.py -q` -> 77 passed

## Review Questions
1. Does the implementation meet the Stage 343 goal without broadening scope?
2. Are summary counts, dedupe rules, unsafe-card filtering, escaping, and capping technically correct?
3. Do tests cover same-article multi-section dedupe, unsafe-card filtering, escaping/capping, CSS selectors, docs, workflow contract boundaries, and artifact absence?
4. Are there any Critical or Important issues that should block commit/push?

Return a concise severity-labeled review. If there are no Critical or Important issues, state that Stage 343 is approved for commit and push.
