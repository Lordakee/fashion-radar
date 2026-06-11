# Claude Code Stage 3 Code Review

Date: 2026-06-11

Commit reviewed: `ac23386`

Reviewed range: `749f263..ac23386`

## Critical Findings

1. GDELT `seendate` parsing used `YYYYMMDDHHMMSS`, while the live GDELT Doc API
   uses `YYYYMMDDTHHMMSSZ`. This caused real GDELT article publication times to
   fall back to collection time, and the fixture masked the issue.

## Important Findings

1. Article extraction helpers were unit-tested but not wired into a collector
   run or persistence path.
2. `article.skip_on_robots_failure` was dead configuration, and robots
   unavailable vs robots disallowed were conflated.
3. The runner did not pass timing into collectors, so real run durations could
   be recorded as zero.

## Minor Findings

1. `items_stored` counts upserts, including updates to existing rows.
2. Expired unhealthy-source windows cleared `unhealthy_until` but did not reset
   `consecutive_failures`.
3. Missing robots.txt was reported as `robots_disallowed`.
4. HTTP 5xx retry handling had some readable-but-duplicated branching.

## Recommendation

Approved after fixes.

## Resolution

- Updated the GDELT fixture to use the real `YYYYMMDDTHHMMSSZ` date shape and
  updated the parser to support that format, with the previous compact format as
  a fallback.
- Wired article extraction into `collect_sources()` before item upsert. Extracted
  text replaces `CollectedItem.summary` only when extraction succeeds and returns
  a short configured snippet.
- Added a default per-source article extractor that creates a run-scoped
  `RobotsPolicyChecker`, preserving robots cache behavior within the source run.
- Removed the dead `skip_on_robots_failure` config field and sample YAML entries.
- Added structured robots checks that distinguish `robots_unavailable`,
  `robots_disallowed`, `invalid_url`, and `allowed`.
- Updated article extraction to report the structured robots reason and to skip
  before any network access when the optional article extractor dependency is
  unavailable.
- Updated the runner to pass `started_at` into timing-aware collectors and to use
  real finish times on failures.
- Reset `consecutive_failures` when clearing expired unhealthy-source windows.
- Left the `items_stored` upsert-vs-insert metric as a documented minor follow-up
  because `ItemRepository.upsert_item()` currently returns only an item id.

Fresh verification after fixes:

```text
.venv/bin/python -m pytest -q
84 passed in 1.27s

.venv/bin/python -m ruff check .
All checks passed!

.venv/bin/python -m ruff format --check .
46 files already formatted

uv lock --check
Resolved 84 packages in 3ms

uv sync --locked --dev --check
Would make no changes

UV_DEFAULT_INDEX=https://pypi.tuna.tsinghua.edu.cn/simple uv sync --frozen --dev --check
Would make no changes

uv build
Successfully built dist/fashion_radar-0.1.0.tar.gz
Successfully built dist/fashion_radar-0.1.0-py3-none-any.whl

Clean temporary venv wheel install via Tsinghua mirror:
fashion-radar --help displayed init and doctor commands
```
