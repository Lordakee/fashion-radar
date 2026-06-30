# Stage 252 YouTube Collector Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans.

**Goal:** Replace the Stage 251 no-op `YouTubeCollector` stub with a real collector that reads YouTube search metadata via the user-installed `yt-dlp` CLI (`ytsearch<N>:<query> --dump-json`), fail-closed, bounded, mapping videos into `CollectedItem`s. No login needed (public data).

**Architecture:** `src/fashion_radar/collectors/youtube.py` resolves the `yt-dlp` executable (`shutil.which("yt-dlp")` or `YouTubeSourceSettings.ytdlp_path`); fail-closed → `skipped("ytdlp_unavailable")` if missing. It runs `subprocess.run(argv=["yt-dlp", f"{settings.search_prefix}{settings.max_videos_per_run}:{source.query}", "--dump-json", "--no-warnings", "--skip-download"], timeout=source.http.timeout_seconds, capture_output=True)` — the search argument MUST use the configured `settings.search_prefix` (NOT a hardcoded `"ytsearch"`), so `"ytsearchdate"` (date-sorted) vs `"ytsearch"` (relevance) is respected; timeout = `source.http.timeout_seconds` (same as Twitter `twitter.py:54,88`). Capture stdout/stderr/returncode. Non-zero exit → `skipped("ytdlp_unavailable")` (public data, no login path). Parse yt-dlp `--dump-json` JSON-**lines** line-by-line — yt-dlp emits one JSON object per line (NOT a single JSON blob like Twitter `twitter.py:97-111`): `for line in stdout.strip().splitlines(): json.loads(line)`, skipping malformed lines (`json.JSONDecodeError: continue`). Each parsed video → `CollectedItem` (url `webpage_url`/`original_url` or `https://www.youtube.com/watch?v=<id>`, title, summary = `report_safe_snippet(description)`, published_at parsed from `upload_date` with `datetime.strptime(upload_date, "%Y%m%d").replace(tzinfo=UTC)` FIRST — yt-dlp's `upload_date` is the stable documented `YYYYMMDD` format, NOT a fallback; do NOT try `parse_datetime_utc` first (it expects ISO8601 and fails on `YYYYMMDD`); on parse error fall back to run `started_at`). `CollectorResult.success(items=..., items_seen=<parsed count>)`. Injectable `runner` for offline tests (mirrors Twitter Stage 242).

**Tech Stack:** Python 3.11, stdlib `subprocess` + `shutil.which` + `json`, Pydantic, pytest, `uv --no-config run --frozen`, Claude Code + opencode review. No new Python dependency (yt-dlp is external).

## Credential model

**No login/credentials** — yt-dlp reads public YouTube metadata. Fashion Radar only shells out + parses. No `check_release_hygiene.py` change.

## Scope

**In:** real `YouTubeCollector` (subprocess + JSON-lines parse + fail-closed + bound + report_safe_snippet + upload_date YYYYMMDD parse); tests (mocked subprocess via injectable runner); docs (Stage 253).

**Out:** login/cookies; media download; ToS enforcement; DB schema change; pyproject/uv.lock change; live verification (user's first live run; yt-dlp `--dump-json` schema documented — it's stable).

## Field-mapping (yt-dlp `--dump-json`, stable)

- `id` (video id), `title`, `upload_date` (`YYYYMMDD` string), `channel`/`uploader`, `webpage_url`/`original_url`, `description`.
- `upload_date` `YYYYMMDD` → datetime: parse FIRST with `datetime.strptime(upload_date, "%Y%m%d").replace(tzinfo=UTC)` (yt-dlp's stable documented format, NOT a fallback); do NOT try `parse_datetime_utc` first — it expects ISO8601 and fails on `"20240615"`. On `ValueError`/`None`/empty, fall back to run `started_at`.

## Tasks (summary)

- **Task 0 (plan review):** Claude Code; opencode revises. `docs/reviews/claude-code-stage-252-plan-review.md`.
- **Task 1 (collector, RED→GREEN):** real `YouTubeCollector` with injectable `runner`; argv MUST use the configured prefix: `["yt-dlp", f"{settings.search_prefix}{settings.max_videos_per_run}:{source.query}", "--dump-json", "--no-warnings", "--skip-download"]` (NOT hardcoded `"ytsearch"`); JSON parse is line-by-line (`for line in stdout.strip().splitlines(): json.loads(line)`, skip malformed lines) — NOT a single `json.loads(stdout)` blob; tests for success (JSON-lines parse), bound, ytdlp_unavailable (missing binary), ytdlp_unavailable (non-zero exit), report_safe_snippet, published_at from `upload_date` + fallback (must cover malformed `upload_date` edge cases: `"20241399"`, `""`, `None` → fallback to `started_at`).
- **Task 2 (focused + Claude Code code review + full gate + commit):** "Stage 252: YouTube collector via yt-dlp".

## Verification

Focused: `tests/test_collectors_youtube.py tests/test_source_model.py tests/test_collectors_runner.py`. Full gate. `git diff --exit-code -- uv.lock pyproject.toml` exits 0.

## Self-Review

- External CLI (no pyproject change); fail-closed without yt-dlp / on error; no login (public data).
- Clean bounding via `ytsearch<N>`; report_safe_snippet; published_at from upload_date; injectable runner for offline tests.
- yt-dlp `--dump-json` schema is stable; documented.
