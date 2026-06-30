# Stage 232 Instagram Collector Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the Stage 231 no-op `InstagramCollector` stub with a real collector that reads Instagram posts via the user-installed `instaloader` library (login session reused), bounded per run, fail-closed, mapping posts into `CollectedItem`s.

**Architecture:** `src/fashion_radar/collectors/instagram.py` imports `instaloader` behind a `try/except ImportError` (optional, like `trafilatura` in `article.py`) — `instaloader` is **not** added to `pyproject.toml`; the user `pip install instaloader` separately. `InstagramCollector.collect`: bind `started_at`; if `instaloader is None` → `skipped("instaloader_unavailable")`; build `instaloader.Instaloader()`; if `instagram.login_user` set, reuse the saved session via `L.load_session_from_config(login_user)` (the user created it with `instaloader --login=<user>`); on login failure → `skipped("login_required")`.

**instaloader is lazy:** auth/connection failures (`LoginRequiredException`, `ConnectionException`, `QueryReturnedBadRequestException`, 401/redirect-to-login) most often surface during `Hashtag.from_name(L.context, name)` / `Profile.from_username(L.context, name)` construction and `get_all_posts()` / `get_posts()` iteration — **not** only at `load_session_from_config`. So both the `from_name`/`from_username` construction **and** the post iteration are wrapped in `try/except` that classifies the exception (by type + lowered message text) into `login_required` (auth/login/401) vs `instaloader_unavailable` (other) and returns `CollectorResult.skipped(...)` — mirroring `xiaohongshu.py:165-174`. An auth failure mid-iteration must surface as `skipped`, never bubble to the runner as `failed`.

Posts are bounded with `itertools.islice(..., max_posts_per_run)`; each `Post` maps to a `CollectedItem` (url `https://www.instagram.com/p/<shortcode>/`, caption via `report_safe_snippet`, published_at from `Post.date_utc` — a tz-aware UTC `datetime`; fall back to `.date` coerced to tz-aware UTC, then `started_at`). Runner registration + dual-guard already in place (Stage 231).

**Deviation from Phase 3 spec (for Claude Code review):** the spec proposed the instaloader *CLI subprocess*; this plan uses the *library import* instead because (a) clean `max_posts_per_run` bounding via `islice` (the CLI has no count limit), and (b) no temp-dir JSON parsing. Still no `pyproject.toml` change (optional import, user-installed). If CC prefers the subprocess approach, revise.

**Tech Stack:** Python 3.11, `instaloader` (optional external, user-installed), Pydantic, pytest, `uv --no-config run --frozen`, Claude Code + opencode review.

## Credential model

`instaloader` owns login: the user runs `instaloader --login=<user>` once (interactive password prompt), which persists a session file under the instaloader config dir (outside the repo, gitignored). Fashion Radar only calls `L.load_session_from_config(login_user)` to reuse it — it never sees/handles the password. No password/session bytes in Fashion Radar.

## Scope

**In:** real `InstagramCollector` (optional import, session reuse, hashtag/profile iteration, bound, fail-closed, `report_safe_snippet`); tests (mocked `instaloader` module — no live Instagram, no login); docs (Stage 233).

**Out:** Xiaohongshu (done), X (Phase 4), YouTube (Phase 5); storing/handling passwords; ToS enforcement; DB schema change; `pyproject.toml`/`uv.lock` change; live verification (user's first live run; instaloader API assumptions documented).

## Field-mapping assumptions (instaloader API, to verify live)

- `instaloader.Instaloader()` constructor; `L.load_session_from_config(username)` to reuse a saved session.
- Hashtag: `instaloader.Hashtag.from_name(L.context, name)` → `.get_all_posts()` (older API: `.get_posts()`). Profile: `instaloader.Profile.from_username(L.context, name)` → `.get_posts()`.
- **Iteration strategy:** try `.get_all_posts()`, fall back to `.get_posts()` on `AttributeError` (Hashtag historically has both; Profile uses `.get_posts()` only).
- `Post` attributes: `.shortcode`, `.caption` (text or None), `.date_utc` (tz-aware UTC `datetime` — lead with this), `.date` (fallback; may be local/naive in some versions). These are `datetime` objects, not strings, so the published_at path differs from Xiaohongshu's `parse_datetime_utc(str(raw))`: ensure a tz-aware UTC datetime before falling back to `started_at`. URL is built from `.shortcode` → `https://www.instagram.com/p/<shortcode>/`; do **not** rely on a `Post.url` attribute (no stable public attribute exists).
- **Exception types to classify:** `instaloader.exceptions.LoginRequiredException`, `ConnectionException`, `QueryReturnedBadRequestException` (plus 401 / redirect-to-login, by message text) → `login_required`; any other instaloader exception → `instaloader_unavailable`.

These vary by instaloader version; tolerant extraction + documented live-verification assumption (mirrors the Xiaohongshu approach).

## Notes

- **`instaloader_path` is unused/ignored under the library approach.** `InstagramSourceSettings.instaloader_path` (added in Stage 231 for the *subprocess* spec, `source.py:69`) means "binary path override." A Python `import instaloader` cannot be pointed at a binary, so the field is vestigial here; it remains a defined field (so `extra="forbid"` still accepts it) but is silently ignored at runtime. Out of scope to remove in 232 (plan scope is no schema change) — **follow-up:** drop `instaloader_path` in a later schema-cleanup stage.
- **Anonymous (no `login_user`) hashtag access** is heavily throttled/blocked by Instagram now. Empty or `skipped` runs without a session are expected; the fail-closed path covers it.

## Tasks (summary)

- **Task 0 (plan review):** Claude Code (esp. library-vs-subprocess deviation + instaloader API assumptions); opencode revises. `docs/reviews/claude-code-stage-232-plan-review.md`.
- **Task 1 (collector, RED→GREEN):** real `InstagramCollector` (mocked instaloader via monkeypatch of `fashion_radar.collectors.instagram.instaloader`); tests for success (hashtag + profile), bound cap, instaloader-unavailable skipped, login_required skipped — at session load **and** surfaced lazily during `Hashtag.from_name` / `Profile.from_username` construction and `get_all_posts` / `get_posts` iteration (classify by exception type + message text, mirror `xiaohongshu.py:165-174`; assert it returns `skipped`, not `failed`), report_safe_snippet, published_at fallback.
- **Task 2 (focused + Claude Code code review + full gate + commit):** "Stage 232: Instagram collector via instaloader".

## Verification

Focused: `tests/test_collectors_instagram.py tests/test_source_model.py tests/test_collectors_runner.py`. Full gate. `git diff --exit-code -- uv.lock pyproject.toml` exits 0.

## Self-Review

- Optional import (no pyproject change); fail-closed without instaloader; session reuse only (no password handling).
- **Lazy-iteration fail-closed:** `Hashtag.from_name` / `Profile.from_username` construction and `get_all_posts` / `get_posts` iteration are wrapped in `try/except`; exceptions classified into `login_required` (auth/login/401) vs `instaloader_unavailable` and returned as `skipped` — never allowed to bubble to the runner as `failed` (mirrors `xiaohongshu.py:165-174`).
- Clean bounding via islice; report_safe_snippet on caption; published_at from `.date_utc` (tz-aware UTC `datetime`) with `started_at` fallback.
- Instaloader API assumptions explicit + documented for live verification; `instaloader_path` documented as vestigial under the library approach; anonymous-hashtag throttling noted.
- Runner integration already done in 231.
