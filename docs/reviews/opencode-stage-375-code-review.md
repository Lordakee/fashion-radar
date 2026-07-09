# Stage 375 Local Article Content Health - opencode Code Review

## Critical

None. The implementation is functionally correct, read-only, generated-site-only,
and the analyzer's anchor contract matches the article-page renderer.

## Important

1. `docs/reviews/opencode-stage-375-code-rereview.md` is not recorded yet.

   Plan Task 9 Step 4 requires matching rereviews after Critical/Important fixes.
   Claude Code's initial code review raised Important findings; the code and tests
   now address them, and `docs/reviews/claude-code-stage-375-code-rereview.md`
   confirms resolution. Record the matching opencode rereview before commit.

## Minor

1. `test_content_health_discovery_ignores_unsafe_sidecar_stems` writes
   `unsafe.html` under `data/articles/`, but discovery only reads `*.json`.
   The relevant unsafe-stem coverage is `unsafe story.json`; the `.html` fixture
   line is dead setup.

2. `name.lower()` in the shared HTML id parser is redundant because Python's
   `HTMLParser` lowercases attribute names before `handle_starttag`, but it is
   harmless and defensively correct.

3. The human content-health line reuses the saved-local-article count formatter
   while `article_count` means renderable sidecars for content health. This
   divergence is spec-sanctioned and limited to read-only ops discovery.

## Verified Correct

- Renderer/analyzer anchor parity is correct: paragraph anchors use original
  one-based non-empty paragraph positions, content-section anchors use one-based
  content-section positions, and the shared section/body anchors match the
  renderer.
- The strict `row-one status` path builds content health from already validated
  `article_sidecars`, so it does not run loose discovery.
- The analyzer is read-only and generated-site-only; site generation does not
  invoke content health.
- Ops-check treats `missing` as attention with a deduplicated refresh action,
  while `ready` and `not_applicable` are non-blocking as specified.
- Generated app/runtime/manifest contracts and generated JSON/page artifacts are
  unchanged.
- Focused tests, full tests, ruff, and format checks were verified during review.
