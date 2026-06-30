# Phase 4 — Social Acquisition (X / Twitter) Design

- **Date:** 2026-06-30
- **Status:** Complete — Phase 4 (Twitter/X) shipped as Stages 241-243. Phase 5 (YouTube via yt-dlp) is next.
- **Review flow:** iron rule 2 (Claude Code primary; opencode `glm-5.2 --variant max` revises/fallback); superpowers writing-plans → executing-plans.

## Goal

Add direct acquisition from **X / Twitter** by wrapping the mature `twitter-cli` CLI (the user installs it and is logged into x.com in their browser; Fashion Radar invokes it as a subprocess and parses its JSON search output). The social boundary is already opt-in/use-at-your-own-risk (Stage 221), so Phase 4 is collector + docs.

## Architecture

- New `SourceType.TWITTER` ("twitter"), requiring `query` (search query), mirroring GDELT/Xiaohongshu/Instagram.
- New `TwitterSourceSettings` (`twitter_cli_path` override defaulting to PATH lookup; `max_tweets_per_run`; optional `output_format` default "json").
- New `src/fashion_radar/collectors/twitter.py` `TwitterCollector`:
  1. resolve the `twitter` executable (`shutil.which("twitter")` or configured path); fail-closed → `CollectorResult.skipped(reason="twitter_cli_unavailable")` if missing;
  2. run `twitter search "<query>" -n <max_tweets_per_run> --json` (subprocess, capture stdout/stderr/exit code); the user is logged into x.com in their browser so twitter-cli reads the cookie session — Fashion Radar handles no cookies itself;
  3. on an auth/cookie failure (non-zero exit, error text mentioning login/cookie/auth/401) → `CollectorResult.skipped(reason="login_required")`;
  4. parse the JSON output (tolerant: list of tweet dicts; keys tried for id/text/created_at/url/user) → `CollectedItem` (url `https://x.com/<user>/status/<id>` or tweet url, title = first line of text, summary = `report_safe_snippet(text)`, published_at from created_at or run `started_at`);
  5. `CollectorResult.success(items=..., items_seen=<parsed count>)`.
- Registered in `_default_collectors()`; runner enrichment-skip set extended to `TWITTER`.

## Credential model

`twitter-cli` reads the user's x.com browser cookie session (the user is logged into x.com). Fashion Radar only shells out to `twitter` and parses output — it never handles cookies/credentials. No password/cookie bytes in Fashion Radar; no `check_release_hygiene.py` change.

## Tech Stack

Python 3.11, stdlib `subprocess` + `shutil.which` + `json`, Pydantic, pytest, `uv --no-config run --frozen`, Claude Code + opencode review. **No new Python dependency** — `twitter-cli` is an external CLI the user installs (`pipx install twitter-cli`); Fashion Radar shells out. No `pyproject.toml`/`uv.lock` change.

## Scope

**In:** `SourceType.TWITTER` + `TwitterSourceSettings`; `TwitterCollector` (subprocess + JSON parse + fail-closed); runner dual-guard + registration; tests (mocked subprocess — no live X, no cookie); docs (cli-reference, source-packs example, architecture, source-boundaries Opt-In); CHANGELOG; Phase 4 release.

**Out:** Xiaohongshu/Instagram (done), YouTube (Phase 5); storing/handling cookies; ToS enforcement (user responsibility, documented); DB schema change; new Python dependency; live verification (user's first live run; twitter-cli JSON shape assumptions documented).

## Field-mapping assumptions (twitter-cli JSON, to verify live)

- Command: `twitter search "<query>" -n <N> --json`. (Flags vary by twitter-cli version; `-n` count + `--json` output are the documented conventions.)
- JSON output: a list of tweet objects, or `{"tweets": [...]}`. Tolerant extraction: tweet `id`/`tweet_id`/`status_id`, `text`/`full_text`/`content`, `created_at`/`date`/`time`, `user`/`username`/`screen_name`, and a direct `url` if present.
These vary by twitter-cli version; tolerant parsing + documented live-verification assumption (mirrors Xiaohongshu/Instagram).

## Staging

- **Stage 241 (4a):** `SourceType.TWITTER` + `TwitterSourceSettings` + no-op collector stub + registration + runner dual-guard (plumbing; reuse Stage 231 pattern).
- **Stage 242 (4b):** real `TwitterCollector` (subprocess + JSON parse + fail-closed) + tests.
- **Stage 243 (4c):** Phase 4 docs + docs-guard + CHANGELOG; Phase 4 release verification + release review + wrap.

## Risks

- **ToS:** X prohibits automated access; user accepts risk. Documented use-at-your-own-risk.
- **twitter-cli availability/auth:** external CLI the user installs + is logged into x.com; Fashion Radar fail-closes without it/auth.
- **twitter-cli JSON shape:** varies by version; tolerant parsing + documented live-verification assumption.
- **No new dependency:** keep twitter-cli external; no `pyproject.toml` change.

## Verification

Per-stage focused tests + full gate; Stage 243 adds packaging/installed-wheel smoke. `git diff --exit-code -- uv.lock pyproject.toml` must exit 0.
