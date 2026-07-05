# Claude Code Stage 306 Code Review Prompt

You are reviewing Stage 306 for `/home/ubuntu/fashion-radar`.

Base SHA: `294730c`

Current working tree files changed:
- `README.md`
- `docs/row-one.md`
- `src/fashion_radar/row_one/articles.py`
- `tests/test_row_one_articles.py`
- `tests/test_row_one_docs.py`
- `tests/test_row_one_local_intelligence.py`
- `docs/reviews/claude-code-stage-306-plan-review-prompt.md`
- `docs/reviews/claude-code-stage-306-plan-review.md`
- `docs/reviews/opencode-stage-306-plan-review-prompt.md`
- `docs/reviews/opencode-stage-306-plan-review.md`
- `docs/superpowers/plans/2026-07-05-stage-306-row-one-signal-dense-takeaways-plan.md`
- `docs/reviews/claude-code-stage-306-code-review-prompt.md`

Stage 306 requirements:
- Improve ROW ONE local article `takeaways` so they prioritize saved source paragraphs containing explicit brand, designer, person, bag, shoe, or product references.
- Preserve the existing section key `takeaways`, model schema, app contract, renderer contract, and paragraph index behavior.
- Preserve fallback behavior: when no explicit source paragraph signal matches, use the first three non-empty source paragraphs.
- Keep appended editorial context available for local article body enrichment, but do not let appended context outrank real saved source paragraphs in source-backed takeaways.
- Avoid short single-token false positives such as `Row` matching ordinary phrases like `front row`, while preserving multi-word brand names such as `The Row`.
- Compile signal regex patterns once per story/takeaway selection, not repeatedly per paragraph/term.
- Keep scope limited to local article organization logic, tests, docs, and review artifacts. Do not add collectors, scraping/platform integrations, LLM/image calls, scheduler/server changes, dependency changes, schema changes, UI redesign, or compliance-review product features.

Verification already run before this review:
- `UV_NO_CONFIG=1 uv --no-config run --frozen pytest -q tests/test_row_one_articles.py -k 'front_row_short_ref or appended_context'`: 2 passed
- `UV_NO_CONFIG=1 uv --no-config run --frozen pytest -q tests/test_row_one_articles.py tests/test_row_one_local_intelligence.py tests/test_row_one_docs.py`: 74 passed
- `UV_NO_CONFIG=1 uv --no-config run --frozen ruff check src/fashion_radar/row_one/articles.py tests/test_row_one_articles.py tests/test_row_one_local_intelligence.py tests/test_row_one_docs.py`: passed
- `UV_NO_CONFIG=1 uv --no-config run --frozen ruff format --check src/fashion_radar/row_one/articles.py tests/test_row_one_articles.py tests/test_row_one_local_intelligence.py tests/test_row_one_docs.py`: passed
- `UV_NO_CONFIG=1 uv --no-config run --frozen pytest -q`: 2001 passed
- `UV_NO_CONFIG=1 uv --no-config run --frozen ruff check`: passed
- `UV_NO_CONFIG=1 uv --no-config run --frozen ruff format --check`: passed
- `UV_NO_CONFIG=1 uv --no-config run --frozen python scripts/check_release_hygiene.py`: passed
- `UV_NO_CONFIG=1 uv lock --check`: passed

Review objective:
- Inspect the current working-tree diff from `294730c`.
- Identify Critical or Important issues that must be fixed before commit/push.
- Check the Stage 306 requirements above against the implementation and tests.
- Check that the two audit risks from the prior review are resolved:
  1. short single-token refs such as `Row` should not promote `front row`;
  2. appended editorial context should not outrank real saved source paragraphs in source-backed takeaways.
- Check review artifacts are coherent and free of terminal session chatter.

Return only structured markdown with:
- Verdict: APPROVE, APPROVE_WITH_NOTES, or BLOCK
- Critical issues
- Important issues
- Minor notes
- Required fixes before commit

End with the exact line: `REVIEW_COMPLETE`
