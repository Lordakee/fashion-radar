# Stage 232 Code Review

**Verdict:** APPROVE

## Critical
None.

## Important
None.

## Nits

1. **No test coverage for posts without shortcode.** `_map_post` returns `None` when `shortcode` is missing (instagram.py:100-101), which means `items_seen` can exceed `len(items)`. This is probably correct behavior (we fetched N posts but couldn't map M of them), but no test exercises this path. Edge-case enough to be optional, but worth noting.

2. **Broad exception handling in `_as_utc`.** The `except Exception` catch-all (instagram.py:131-132) is very permissive. Given it returns the fallback, this is defensible for robustness, but it would silently swallow unexpected errors in date parsing.

## Summary

Excellent implementation that correctly addresses all six verification requirements and both Important items from the plan review. The optional import pattern matches `article.py` exactly. The fail-closed contract is sound: `instaloader_unavailable` when missing, `login_required` on session load failure, and critically **lazy-iteration failures are wrapped and classified** (instagram.py:47-50) via `_classify()` that checks exception text for auth keywords — mirroring `xiaohongshu.py` as specified. Session reuse is clean (`load_session_from_config` only, no password handling). Bounding via `islice(max_posts_per_run)`, `report_safe_snippet` on caption, `date_utc`-first published_at with tz-aware coercion and `started_at` fallback, and first-line-or-shortcode title all implemented correctly. `_iter_posts` uses `source.query` and `source.instagram.target_type` (not `settings.query`). Test coverage is comprehensive: hashtag/profile success, bound, unavailable, login at session + at iteration, connection error at iteration, no-date fallback, long-caption truncation. The monkeypatch strategy properly simulates instaloader's lazy behavior. Defensive cleanup in the `finally` block. No schema/lock/pyproject changes. Ready to ship.
