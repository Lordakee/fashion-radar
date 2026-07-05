# Claude Code Stage 307 Code Review Prompt

You are reviewing Stage 307 for `/home/ubuntu/fashion-radar`.

Base SHA: `f774eff`

Current working tree files changed:
- `README.md`
- `docs/row-one.md`
- `src/fashion_radar/row_one/local_intelligence.py`
- `src/fashion_radar/row_one/templates.py`
- `tests/test_row_one_docs.py`
- `tests/test_row_one_local_intelligence.py`
- `tests/test_row_one_render.py`
- `docs/reviews/claude-code-stage-307-plan-review-prompt.md`
- `docs/reviews/claude-code-stage-307-plan-review.md`
- `docs/reviews/claude-code-stage-307-plan-rereview-prompt.md`
- `docs/reviews/claude-code-stage-307-plan-rereview.md`
- `docs/reviews/claude-code-stage-307-code-review-prompt.md`
- `docs/superpowers/plans/2026-07-05-stage-307-row-one-local-evidence-drilldowns-plan.md`

Stage 307 requirements:
- Let ROW ONE homepage Daily Local Intelligence cards link directly to exact saved local article paragraph evidence.
- Preserve `row-one-app/v7`, sidecar JSON shapes, local article models, and detail-page local article rendering contracts.
- Fix aggregate local-intelligence detail-path/source alignment so a reference aggregate points to the same generated detail page as the selected body/segment/paragraph source.
- Replace full-card Daily Local Intelligence anchors with non-anchor cards plus explicit same-site saved-text and paragraph links; do not introduce nested anchors.
- Expand safe local href validation only for generated `#local-article-paragraph-N` anchors under safe `details/*.html` paths.
- Add minimal CSS for the new action/paragraph-link anchors so the homepage does not regress to default browser link styling.
- Filter Daily Local Intelligence paragraph indices against actually publishable local article paragraphs before writing `data/local-intelligence.json` or rendering homepage links.
- Keep local article bodies out of `data/edition.json`; Daily Local Intelligence remains a separate optional sidecar artifact.
- Keep scope limited to local article intelligence organization, renderer links, docs/tests, and review artifacts. Do not add collectors, platform integrations, LLM/image calls, scheduler/server changes, dependency changes, schema/app contract bumps, sidecar schemas, visual redesign, or compliance-review product features.

Important prior audit finding already addressed:
- A read-only audit found homepage paragraph drilldowns could point at anchors the detail page would not render. The implementation now filters `paragraph_indices` against non-empty article paragraphs in `src/fashion_radar/row_one/local_intelligence.py` before emitting Daily Local Intelligence items/segments. Please verify this fix is sufficient and does not suppress valid source-backed paragraph links.

Verification already run before this review:
- `UV_NO_CONFIG=1 uv --no-config run --frozen pytest -q tests/test_row_one_local_intelligence.py tests/test_row_one_render.py tests/test_row_one_docs.py`: 108 passed
- `UV_NO_CONFIG=1 uv --no-config run --frozen ruff check src/fashion_radar/row_one/local_intelligence.py src/fashion_radar/row_one/templates.py tests/test_row_one_local_intelligence.py tests/test_row_one_render.py tests/test_row_one_docs.py`: passed
- `UV_NO_CONFIG=1 uv --no-config run --frozen ruff format --check src/fashion_radar/row_one/local_intelligence.py src/fashion_radar/row_one/templates.py tests/test_row_one_local_intelligence.py tests/test_row_one_render.py tests/test_row_one_docs.py`: passed
- `UV_NO_CONFIG=1 uv --no-config run --frozen pytest -q`: 2007 passed
- `UV_NO_CONFIG=1 uv --no-config run --frozen ruff check`: passed
- `UV_NO_CONFIG=1 uv --no-config run --frozen ruff format --check`: passed
- `UV_NO_CONFIG=1 uv --no-config run --frozen python scripts/check_release_hygiene.py`: passed
- `UV_NO_CONFIG=1 uv lock --check`: passed

Review objective:
- Inspect the current working-tree diff from `f774eff`.
- Identify Critical or Important issues that must be fixed before commit/push.
- Check the requirements above against the implementation and tests.
- Specifically verify:
  1. no nested-anchor homepage markup;
  2. safe local href validation accepts only `#local-article` and positive one-based `#local-article-paragraph-N` fragments on valid generated detail paths;
  3. aggregate body/segment/paragraph source and `detail_path` remain aligned;
  4. paragraph drilldown links only target publishable local article paragraphs;
  5. `data/edition.json` and app schema contract remain unchanged;
  6. review artifacts are coherent and free of terminal session chatter.

Return only structured markdown with:
- Verdict: APPROVE, APPROVE_WITH_NOTES, or BLOCK
- Critical issues
- Important issues
- Minor notes
- Required fixes before commit

End with the exact line: `REVIEW_COMPLETE`
