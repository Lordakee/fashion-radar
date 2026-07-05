# Claude Code Stage 303 Code Review Prompt

You are reviewing Stage 303 code changes for `/home/ubuntu/fashion-radar`.

Base commit: `212a70a`
Plan: `docs/superpowers/plans/2026-07-05-stage-303-row-one-local-article-paragraph-anchors-plan.md`
Plan reviews:
- `docs/reviews/claude-code-stage-303-plan-review.md`
- `docs/reviews/claude-code-stage-303-plan-rereview.md`
- `docs/reviews/opencode-stage-303-plan-review.md`
- `docs/reviews/opencode-stage-303-plan-rereview.md`

Changed files to review:
- `src/fashion_radar/row_one/templates.py`
- `tests/test_row_one_render.py`
- `tests/test_row_one_docs.py`
- `README.md`
- Stage 303 plan/review artifacts under `docs/superpowers/plans/` and `docs/reviews/`

Review objective:
- Confirm the implementation matches Stage 303: detail-page local article body paragraphs get stable `local-article-paragraph-N` IDs, and detail-page content-section paragraph metadata links to valid rendered paragraphs.
- Confirm paragraph indices use original zero-based `RowOneLocalArticle.paragraphs` positions, not compacted rendered positions.
- Confirm invalid, blank, duplicate, and out-of-range paragraph indices are handled safely.
- Confirm homepage Daily Local Intelligence paragraph metadata remains plain text and no nested paragraph links are added to homepage cards.
- Confirm `data/edition.json`, `data/local-intelligence.json`, and `row-one-app/v7` are unchanged by this stage.
- Confirm all generated anchors/hrefs are deterministic and all user/source-controlled text remains escaped.
- Check tests are meaningful and would fail for the named regressions.
- Check review artifacts are coherent and free of live-capture/tool-status noise.

Verification already run after the latest changes:
- `UV_NO_CONFIG=1 uv --no-config run --frozen pytest -q` -> `1990 passed`
- `UV_NO_CONFIG=1 uv --no-config run --frozen ruff check` -> passed
- `UV_NO_CONFIG=1 uv --no-config run --frozen ruff format --check` -> passed
- `UV_NO_CONFIG=1 uv --no-config run --frozen python scripts/check_release_hygiene.py` -> passed
- `UV_NO_CONFIG=1 uv lock --check` -> passed

Return:
- Verdict: APPROVE, APPROVE_WITH_NOTES, or BLOCK
- Critical issues
- Important issues
- Minor notes
