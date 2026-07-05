# Claude Code Stage 304 Code Review Prompt

You are reviewing Stage 304 code changes for `/home/ubuntu/fashion-radar`.

Base commit: `37c3300`
Plan: `docs/superpowers/plans/2026-07-05-stage-304-row-one-source-backed-reference-excerpts-plan.md`
Plan reviews:
- `docs/reviews/claude-code-stage-304-plan-review.md`
- `docs/reviews/opencode-stage-304-plan-review.md`

Changed files to review:
- `src/fashion_radar/row_one/articles.py`
- `tests/test_row_one_articles.py`
- `tests/test_row_one_render.py`
- `tests/test_row_one_docs.py`
- `README.md`
- `docs/row-one.md`
- Stage 304 plan/review artifacts under `docs/superpowers/plans/` and `docs/reviews/`

Review objective:
- Confirm matched entity/designer/product reference cards use saved local article paragraph excerpts as `RowOneLocalArticleContentItem.body`.
- Confirm excerpt body matching is reference-name-only and does not use generic labels such as `bag`, `new`, or `tracked`.
- Confirm broad `paragraph_indices` badge matching still uses reference name plus label, preserving Stage 303 detail-page paragraph anchor behavior.
- Confirm unmatched or generic-label-only references retain deterministic `type / label` fallback body text.
- Confirm detail page HTML and `data/articles/<story-id>.json` publish source-backed reference excerpt bodies, while `data/edition.json` and `row-one-app/v7` remain unchanged.
- Confirm homepage Daily Local Intelligence behavior remains structurally stable and receives only richer existing `body` values, not new schema or homepage paragraph links.
- Confirm no app contract, dependency, source acquisition, scraping, social connector, scheduler, image, demand proof, platform coverage verification, or compliance-review product behavior was added.
- Confirm tests would fail for metadata-only body regressions, generic-label misleading excerpt regressions, paragraph-index regressions, and ambiguous detail-page render regressions.
- Confirm review artifacts are coherent and free of live-capture/tool-status noise.

Verification already run after latest changes:
- `UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_articles.py tests/test_row_one_render.py tests/test_row_one_docs.py tests/test_row_one_local_intelligence.py -q` -> `128 passed`
- `UV_NO_CONFIG=1 uv --no-config run --frozen pytest -q` -> `1991 passed`
- `UV_NO_CONFIG=1 uv --no-config run --frozen ruff check` -> passed
- `UV_NO_CONFIG=1 uv --no-config run --frozen ruff format --check` -> passed
- `UV_NO_CONFIG=1 uv --no-config run --frozen python scripts/check_release_hygiene.py` -> passed
- `UV_NO_CONFIG=1 uv lock --check` -> passed

Return:
- Verdict: APPROVE, APPROVE_WITH_NOTES, or BLOCK
- Critical issues
- Important issues
- Minor notes
