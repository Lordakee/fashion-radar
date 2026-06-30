# Stage 232 Plan Review

**Verdict:** APPROVE_WITH_NITS

## Critical
None.

## Important

1. **Fail-closed only covers session load, not lazy iteration.** instaloader is lazy: `Hashtag.from_name(...).get_all_posts()` / `Profile.from_username(...).get_posts()` are generators, and login/connection failures (`LoginRequiredException`, `ConnectionException`, `QueryReturnedBadRequestException`, 401/redirect-to-login) most often surface *during iteration*, not at `load_session_from_config`. The plan classifies `login_required` only on the login step. As written, an auth failure mid-iteration would bubble to the runner and be recorded as **failed**, not **skipped** — violating the fail-closed contract the plan claims. Mirror Xiaohongshu: wrap the iteration (and the `from_name`/`from_username` construction) in `try/except`, and classify by exception text/type into `login_required` vs `instaloader_unavailable` (xiaohongshu.py:165-174 is the template). Worth listing explicit instaloader exception types in the field-mapping section.

2. **`instaloader_path` becomes a dead field under the library approach.** It exists in `InstagramSourceSettings` (source.py:69, committed in Stage 231 for the *subprocess* spec) and means "binary path override." With a Python import you cannot point at a binary, so the field is vestigial. `extra="forbid"` means users can still set it and it will be silently ignored — confusing. Since the plan's scope says "no schema change," the field stays; the plan should at minimum **document it as unused under the library approach** (and ideally note a follow-up to drop it). Flagging because it's the concrete artifact of the spec→plan deviation and isn't addressed anywhere in the plan.

## Nits

1. **`get_all_posts()` vs `get_posts()` ordering.** Plan notes the older-API fallback but not the strategy. State it: try `get_all_posts`, fall back to `get_posts` on `AttributeError` — and confirm which `target_type` uses which (Hashtag has both historically; Profile only `get_posts`).
2. **`Post.url` assumption is shaky.** instaloader `Post` has no stable public `.url`; the plan already constructs `https://www.instagram.com/p/<shortcode>/` from `.shortcode`, which is correct. Drop `.url` from the documented API assumptions to avoid implying a non-existent attribute.
3. **Prefer `.date_utc` over `.date`.** `Post.date` is local/naive in several versions; `.date_utc` is the tz-aware UTC value. Lead with `.date_utc`, fall back to `.date`. Also note: these are `datetime` objects, not strings, so the published_at path differs slightly from Xiaohongshu's `parse_datetime_utc(str(raw))` — ensure a tz-aware UTC datetime before falling back to `started_at`.
4. **Anonymous (no `login_user`) hashtag access** is heavily throttled/blocked by Instagram now. Not a plan defect (fail-closed covers it), but worth a one-line doc note so users aren't surprised by empty/skipped runs without a session.

## Summary

The library-vs-subprocess deviation is **sound and the better call**: the optional `try/except ImportError` mirrors `article.py` exactly, keeps instaloader out of `pyproject.toml`/`uv.lock`, and `itertools.islice(posts, max_posts_per_run)` is a genuinely cleaner bound than the CLI (no per-count flag) plus avoids temp-dir JSON parsing. Env coupling (instaloader must live in the same interpreter) is acceptable for a local-first, user-installed, opt-in tool. The credential model is correct — `load_session_from_config(login_user)` reuses the user's `instaloader --login` session and Fashion Radar never touches passwords/session bytes. Contracts check out: `CollectorResult.skipped(reason=...)` exists (base.py:93), `report_safe_snippet` exists (report.py:13), the published_at fallback mirrors Xiaohongshu, and runner registration + dual enrichment-skip for `INSTAGRAM` are already wired (runner.py:81,107). The monkeypatch-the-module test strategy is the right isolation for a module-level optional import. Scope is clean (no pyproject/uv.lock/schema change; Xiaohongshu done; X/YouTube deferred). Address the two Important items — classify auth failures that surface during lazy iteration as `skipped`, and document the now-vestigial `instaloader_path` — and this is ready to implement.
