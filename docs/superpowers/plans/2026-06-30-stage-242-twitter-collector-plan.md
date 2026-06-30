# Stage 242 Twitter Collector Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans.

**Goal:** Replace the Stage 241 no-op `TwitterCollector` stub with a real collector that reads X/Twitter search results via the user-installed `twitter-cli` CLI (subprocess + JSON parse), fail-closed, bounded, mapping tweets into `CollectedItem`s.

**Architecture:** `src/fashion_radar/collectors/twitter.py` resolves the `twitter` executable (`shutil.which("twitter")` or `TwitterSourceSettings.twitter_cli_path`); fail-closed → `skipped("twitter_cli_unavailable")` if missing. It runs `twitter search "<query>" -n <max_tweets_per_run> --json` via `subprocess.run` (capture stdout/stderr/returncode, bounded timeout). Non-zero exit with login/cookie/auth/401 in stderr/stdout → `skipped("login_required")`; other non-zero → `skipped("twitter_cli_unavailable")`. JSON stdout is parsed tolerantly (list of tweets, or `{"tweets": [...]}`); each tweet → `CollectedItem` (url from tweet id+user or a direct url field; title = first line of text; summary = `report_safe_snippet(text)`; published_at from created_at/date/time or run `started_at`). `CollectorResult.success(items=..., items_seen=<parsed count>)`. The user is logged into x.com in their browser so twitter-cli reads the cookie session — Fashion Radar handles no cookies. Runner registration + dual-guard already in place (Stage 241).

**Tech Stack:** Python 3.11, stdlib `subprocess` + `shutil.which` + `json`, Pydantic, pytest, `uv --no-config run --frozen`, Claude Code + opencode review. No new Python dependency (twitter-cli is an external CLI).

## Credential model

`twitter-cli` reads the user's x.com browser cookie session (the user is logged into x.com). Fashion Radar only shells out + parses output — no cookie/password handling. No `check_release_hygiene.py` change.

## Scope

**In:** real `TwitterCollector` (subprocess + JSON parse + fail-closed + bound + report_safe_snippet); tests (mocked subprocess via an injectable `runner` — no live X, no cookie); docs (Stage 243).

**Out:** Xiaohongshu/Instagram (done), YouTube (Phase 5); cookie handling; ToS enforcement; DB schema change; pyproject/uv.lock change; live verification (user's first live run; twitter-cli JSON shape documented).

## Field-mapping assumptions (twitter-cli, to verify live)

- Command: `twitter search "<query>" -n <N> --json`. Flags vary by version; `-n` count + `--json` output are the documented conventions.
- JSON: a list of tweet objects, or `{"tweets": [...]}`. Tweet keys tried: `id`/`tweet_id`/`status_id`, `text`/`full_text`/`content`, `created_at`/`date`/`time`, `user`/`username`/`screen_name` (str or `{"screen_name": ...}`), direct `url`.
Tolerant parsing + documented live-verification assumption (mirrors Xiaohongshu/Instagram).

## Tasks (summary)

- **Task 0 (plan review):** Claude Code (esp. subprocess injection for testing + auth classification + JSON assumptions); opencode revises. `docs/reviews/claude-code-stage-242-plan-review.md`.
- **Task 1 (collector, RED→GREEN):** real `TwitterCollector` with injectable `runner` (default subprocess.run); tests for success, bound, twitter_cli_unavailable (missing binary), login_required (auth error exit), twitter_cli_unavailable (other error exit), report_safe_snippet, published_at fallback, list-vs-{"tweets":[]} shapes.
- **Task 2 (focused + Claude Code code review + full gate + commit):** "Stage 242: Twitter collector via twitter-cli".

## Verification

Focused: `tests/test_collectors_twitter.py tests/test_source_model.py tests/test_collectors_runner.py`. Full gate. `git diff --exit-code -- uv.lock pyproject.toml` exits 0.

## Self-Review

- External CLI (no pyproject change); fail-closed without twitter-cli / on auth error; no cookie handling.
- Clean bounding via `-n`; report_safe_snippet; published_at fallback; injectable runner for offline tests.
- twitter-cli JSON assumptions explicit + documented for live verification.
