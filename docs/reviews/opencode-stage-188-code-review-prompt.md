# Stage 188 Code Review Prompt

Review the Stage 188 implementation for `/home/ubuntu/fashion-radar`.

Return only the final review body, starting with:

```text
# Stage 188 Code Review
```

Files to review:

- `tests/test_collectors_runner.py`
- `tests/test_workflows.py`
- `README.md`
- `docs/PROJECT_BRIEF.md`
- `docs/architecture.md`
- `docs/REVIEW_PROTOCOL.md`
- `CHANGELOG.md`
- `docs/reviews/opencode-stage-188-plan-review.md`
- `docs/reviews/opencode-full-project-review.md`

Implementation summary:

- Kept the proxy fix test-side only.
- Updated `tests/test_collectors_runner.py` so its local `_rss_source(...)`
  helper defaults to `article={"enabled": False}` via payload merging.
- Updated `tests/test_workflows.py` so
  `test_collect_configured_sources_uses_injected_collectors` explicitly pins the
  synthetic proxy env and disables article extraction on its source fixture.
- Added
  `test_collect_configured_sources_with_injected_collectors_ignores_proxy_env`
  as a workflow seam guard in final GREEN form.
- Updated roadmap-facing docs to freeze further external/community handoff
  expansion for now and re-prioritize source coverage, source health, matching
  quality, and optional summarization.
- Did not modify runtime proxy behavior in `src/`.

TDD and focused verification already run:

- Under synthetic proxy env, the 4 pre-existing failing tests were RED while the
  new workflow seam guard was GREEN.
- After the test-side fix, the 5-test focused set passed.
- Under synthetic proxy env:
  `uv --no-config run --frozen pytest tests/test_collectors_runner.py tests/test_workflows.py -q`
  passed with `11 passed`.
- `uv --no-config run --frozen ruff check tests/test_collectors_runner.py tests/test_workflows.py`
  passed.
- `uv --no-config run --frozen ruff format --check tests/test_collectors_runner.py tests/test_workflows.py`
  passed.

Review questions:

1. Is the test-side-only proxy fix the smallest sound correction?
2. Do the updated tests actually guard the failure seam identified in the full
   project review without changing runtime behavior?
3. Are the roadmap/documentation corrections appropriately scoped and aligned
   with the product brief and full-project review?
4. Does the implementation avoid re-expanding the frozen external/community
   handoff surface?
5. Is there any technical or roadmap correction still needed before full
   release-gate verification?

Report findings under Critical, Important, and Minor. Critical or Important
findings must include exact file/line references and concrete fixes. If the
implementation is acceptable, say it is approved for release-gate verification.
