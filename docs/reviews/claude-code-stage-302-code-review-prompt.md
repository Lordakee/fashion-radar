# Claude Code Stage 302 Code Review Prompt

You are reviewing Stage 302 code changes for `/home/ubuntu/fashion-radar`.

Base commit: `0f591ab`
Plan: `docs/superpowers/plans/2026-07-05-stage-302-row-one-local-intelligence-segments-plan.md`
Plan reviews:
- `docs/reviews/claude-code-stage-302-plan-review.md`
- `docs/reviews/opencode-stage-302-plan-review.md`

Changed files to review:
- `src/fashion_radar/row_one/models.py`
- `src/fashion_radar/row_one/local_intelligence.py`
- `src/fashion_radar/row_one/templates.py`
- `tests/test_row_one_local_intelligence.py`
- `tests/test_row_one_render.py`
- `tests/test_row_one_docs.py`
- `README.md`
- Stage 302 plan/review artifacts under `docs/superpowers/plans/` and `docs/reviews/`

Review objective:
- Confirm the implementation matches Stage 302: Daily Local Intelligence items now carry compact nested local article segments into the homepage and `data/local-intelligence.json`.
- Confirm `data/edition.json` and `row-one-app/v7` remain stable and do not include local article segment payloads.
- Check source attribution and local-first boundaries: no scraping, social connectors, source acquisition, demand proof, platform coverage verification, app UI work, paywall bypass, or compliance-review product features.
- Check builder correctness: segment caps, matched reference segment preference, later stronger match upgrade, product/entity same-name separation, deterministic sorting, no full `paragraphs` list copied into daily intelligence items.
- Check template correctness: all nested segment labels, bodies, refs, and metadata are escaped; safe href behavior remains intact; markup/CSS is reasonable.
- Check tests are meaningful and would fail for the above regressions.

Verification already run after the latest changes:
- `UV_NO_CONFIG=1 uv --no-config run --frozen pytest -q` -> `1989 passed`
- `UV_NO_CONFIG=1 uv --no-config run --frozen ruff check` -> passed
- `UV_NO_CONFIG=1 uv --no-config run --frozen ruff format --check` -> passed
- `UV_NO_CONFIG=1 uv --no-config run --frozen python scripts/check_release_hygiene.py` -> passed
- `UV_NO_CONFIG=1 uv lock --check` -> passed

Return:
- Verdict: APPROVE, APPROVE_WITH_NOTES, or BLOCK
- Critical issues
- Important issues
- Minor notes
