# Claude Code Stage 305 Code Review Prompt

You are reviewing Stage 305 for /home/ubuntu/fashion-radar.

Base SHA: e75254c167470b247a808ae25068ff52e8eda35f
Current working tree files changed:
README.md
docs/row-one.md
src/fashion_radar/row_one/templates.py
tests/test_row_one_docs.py
tests/test_row_one_render.py

Stage 305 requirements:
- Add a detail-page-only ROW ONE local article map inside #local-article for structured saved local articles.
- Map links must target renderer-owned deterministic anchors: #local-article-brief, #local-article-content-section-N, and #local-article-body.
- Preserve Stage 303 paragraph anchors exactly: local-article-paragraph-{index + 1}.
- Plain paragraph-only local articles get id="local-article-body" but do not render a one-link map.
- Brief-only local articles render Brief and Full saved text links, without content-section dead links.
- Homepage Daily Local Intelligence must not receive detail-only local article fragments.
- Escape all model-supplied text in map links and existing local article surfaces.
- Keep scope template/CSS/docs/tests only; no schema, app contract, dependency, source acquisition, scheduler, scraping, image generation, or compliance-review product feature changes.

Verification already run before this review:
- UV_NO_CONFIG=1 uv --no-config run --frozen pytest [7 focused Stage 305 tests] -q: 7 passed
- UV_NO_CONFIG=1 uv --no-config run --frozen ruff check src/fashion_radar/row_one/templates.py tests/test_row_one_render.py tests/test_row_one_docs.py: passed
- UV_NO_CONFIG=1 uv --no-config run --frozen ruff format --check src/fashion_radar/row_one/templates.py tests/test_row_one_render.py tests/test_row_one_docs.py: 3 files already formatted
- UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_render.py tests/test_row_one_docs.py -q: 93 passed

Review objective:
- Inspect the current working-tree diff from e75254c167470b247a808ae25068ff52e8eda35f.
- Identify Critical or Important issues that must be fixed before commit/push.
- Check test coverage against the requirements above.
- Check review artifacts are coherent and free of terminal session chatter.

Return only structured markdown with:
- Verdict: APPROVE, APPROVE_WITH_NOTES, or BLOCK
- Critical issues
- Important issues
- Minor notes
- Required fixes before commit
End with the exact line: REVIEW_COMPLETE
