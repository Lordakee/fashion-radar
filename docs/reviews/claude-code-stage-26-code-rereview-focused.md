Critical: None.

Important: None.

Minor: None.

Focused rereview notes:
- `normalized_phrase` is now only used as an internal local variable/parameter for matching via `candidate_key()` against `extract_candidate_phrases()` results.
- The public Pydantic models and JSON shape do not include `normalized_phrase`, `normalized_key`, `normalized_url`, or other normalized candidate internals.
- The table renderer only emits phrase/window/counts plus evidence `id`, `window`, `source_name`, `title`, `url`, `published_at`, and `collected_at`; no normalized internals are rendered.
- Tests now explicitly lock the JSON key order and forbid normalized/internal fields in both model and CLI JSON output.
- I did not identify any new blocking Stage 26 behavior such as writes, source acquisition, scraping/crawling, platform APIs, scheduling/watch-folder behavior, approval state, report/dashboard writes, or entity draft generation.
- `uv.lock` was treated as out of scope.

Verification note: `git diff --check` completed with no output. The focused pytest command required approval in this environment, so I relied on the already-provided successful verification plus code inspection for this rereview.

APPROVED FOR STAGE 26 COMMIT.
