# Phase 5 — Social Acquisition (YouTube) Design

- **Date:** 2026-06-30
- **Status:** Active mainline. Phases 1–4 complete at `1502387`.
- **Review flow:** iron rule 2 (Claude Code primary; opencode `glm-5.2 --variant max` revises/fallback); superpowers writing-plans → executing-plans.

## Goal

Add direct acquisition from **YouTube** by wrapping the mature `yt-dlp` CLI (the user installs it; Fashion Radar invokes it as a subprocess for search + metadata JSON). YouTube public data needs **no login**. The social boundary is already opt-in/use-at-your-own-risk (Stage 221), so Phase 5 is collector + docs.

## Architecture

- New `SourceType.YOUTUBE` ("youtube"), requiring `query`, mirroring GDELT/Xiaohongshu/Instagram/Twitter.
- New `YouTubeSourceSettings` (`ytdlp_path` override defaulting to PATH lookup; `max_videos_per_run`; `search_prefix` default `"ytsearch"`).
- New `src/fashion_radar/collectors/youtube.py` `YouTubeCollector`:
  1. resolve the `yt-dlp` executable (`shutil.which("yt-dlp")` or `YouTubeSourceSettings.ytdlp_path`); fail-closed → `skipped("ytdlp_unavailable")` if missing;
  2. run `yt-dlp "ytsearch<N>:<query>" --dump-json --no-warnings --skip-download` (subprocess, capture stdout/stderr/returncode, bounded timeout) — one JSON object per line;
  3. on non-zero exit → `skipped("ytdlp_unavailable")` (no login path needed for public YouTube, but keep fail-closed);
  4. parse each JSON line (tolerant: `id`, `title`, `upload_date` `YYYYMMDD`, `channel`/`uploader`/`channel_id`, `webpage_url`/`original_url`, `description`) → `CollectedItem` (url `https://www.youtube.com/watch?v=<id>`, title, summary = `report_safe_snippet(description)`, published_at from `upload_date` or run `started_at`);
  5. `CollectorResult.success(items=..., items_seen=<parsed count>)`.
- Registered in `_default_collectors()`; runner enrichment-skip set extended to `YOUTUBE`.

## Credential model

**No login/credentials needed** — yt-dlp reads public YouTube metadata for search/dump-json. Fashion Radar only shells out + parses; no cookies/account. (This is why YouTube is the easiest target.) No `check_release_hygiene.py` change.

## Tech Stack

Python 3.11, stdlib `subprocess` + `shutil.which` + `json`, Pydantic, pytest, `uv --no-config run --frozen`, Claude Code + opencode review. **No new Python dependency** — `yt-dlp` is an external CLI the user installs (`pipx install yt-dlp`); Fashion Radar shells out. No `pyproject.toml`/`uv.lock` change.

## Scope

**In:** `SourceType.YOUTUBE` + `YouTubeSourceSettings`; `YouTubeCollector` (subprocess + JSON-lines parse + fail-closed + bound); runner dual-guard + registration; tests (mocked subprocess via injectable runner — no live YouTube); docs (cli-reference, source-packs example, architecture, source-boundaries Opt-In); CHANGELOG; Phase 5 release.

**Out:** login/cookies (none needed); media download (metadata only); ToS enforcement (user responsibility, documented); DB schema change; new Python dependency; live verification (user's first live run; yt-dlp JSON shape documented — though yt-dlp's `--dump-json` schema is very stable).

## Field-mapping (yt-dlp `--dump-json`, stable)

- `id` (video id), `title`, `upload_date` (`YYYYMMDD` string), `channel`/`uploader`, `webpage_url`/`original_url`, `description`.
- `upload_date` `YYYYMMDD` → parse to the 1st of the month at 00:00 UTC (day precision only) or fall back to `started_at`.

## Staging

- **Stage 251 (5a):** `SourceType.YOUTUBE` + `YouTubeSourceSettings` + no-op collector stub + registration + runner dual-guard (plumbing; reuse Stage 241 pattern).
- **Stage 252 (5b):** real `YouTubeCollector` (yt-dlp subprocess + JSON-lines parse + fail-closed) + tests.
- **Stage 253 (5c):** Phase 5 docs + docs-guard + CHANGELOG; Phase 5 release verification + release review + wrap (also the final mainline wrap).

## Risks

- **ToS:** YouTube ToS on automated access; user accepts risk. Documented use-at-your-own-risk.
- **yt-dlp availability:** external CLI the user installs; fail-closed without it. No login needed for public metadata.
- **yt-dlp JSON shape:** `--dump-json` is stable; tolerant parsing + documented assumption regardless.
- **No new dependency:** keep yt-dlp external; no `pyproject.toml` change.

## Verification

Per-stage focused tests + full gate; Stage 253 adds packaging/installed-wheel smoke + the final mainline consolidated gate. `git diff --exit-code -- uv.lock pyproject.toml` must exit 0.
