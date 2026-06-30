# Phase 3 — Social Acquisition (Instagram) Design

- **Date:** 2026-06-30
- **Status:** Complete — Phase 3 (Instagram) shipped as Stages 231-233. Phase 4 (X via twitter-cli) is next.
- **Shipped as:** a library import (`import instaloader`, optional via `try/except`, session reuse via `load_session_from_config`, lazy `itertools.islice` bounding) — NOT the subprocess-CLI design originally proposed in the Architecture/Credential/Tech-Stack sections below. Those sections describe the superseded approach and are retained for history; see the Stage 232 plan (`docs/superpowers/plans/2026-06-30-stage-232-instagram-collector-plan.md`) for the shipped design.
- **Review flow:** iron rule 2 (Claude Code primary; opencode `glm-5.2 --variant max` revises/fallback).

## Goal

Add direct acquisition from **Instagram** by wrapping the mature `instaloader` CLI (the user installs it and logs in once; Fashion Radar invokes it as a subprocess and parses its JSON metadata output). The social boundary was already evolved to opt-in/use-at-your-own-risk in Stage 221, so Phase 3 is the collector + docs (no further boundary reversal needed).

## Architecture

- New `SourceType.INSTAGRAM` ("instagram") requiring `query` (a hashtag like `#therow` or a username), mirroring the GDELT/Xiaohongshu query model.
- New `InstagramSourceSettings` (instaloader binary path override defaulting to PATH lookup; `login_user` for session reuse; `max_posts_per_run`; `target_type` ∈ {hashtag, profile}).
- New `src/fashion_radar/collectors/instagram.py` `InstagramCollector`:
  1. resolve the `instaloader` executable (PATH via `shutil.which`, or the configured path); fail-closed → `CollectorResult.skipped(reason="instaloader_unavailable")` if missing;
  2. run `instaloader <target> --login=<login_user> --no-pictures --no-videos --no-captions --no-video-thumbnails --metadata-json --no-compress-json -D <tmp_dir>` (bound by max_posts) in a temp dir; capture stdout/stderr/exit code;
  3. on a login/profile-private failure exit code → `CollectorResult.skipped(reason="login_required")`;
  4. parse each `*.json` metadata file → `CollectedItem` (url from shortcode `https://www.instagram.com/p/<shortcode>/`, title/caption via `report_safe_snippet`, published_at from the timestamp or run `started_at`);
  5. `CollectorResult.success(items=..., items_seen=<discovered count>)`.
- Registered in `_default_collectors()`; runner enrichment-skip set extended to include `INSTAGRAM` (items already carry extracted caption).

## Credential model

`instaloader` owns login (`instaloader --login=USER` persists a session file under the user's instaloader config dir, outside the repo). Fashion Radar only passes `--login=<login_user>` to reuse that session; it never stores or handles the password/session bytes. The session file stays outside the project tree (gitignored globally already). No `check_release_hygiene.py` change needed.

## Tech Stack

Python 3.11, stdlib `subprocess` + `shutil.which` + `tempfile` + `json`, Pydantic, pytest, `uv --no-config run --frozen`, Claude Code + opencode review. **No new Python dependency** — `instaloader` is an external CLI the user installs (`pip install instaloader`); Fashion Radar only shells out to it. No `pyproject.toml`/`uv.lock` change.

## Scope

**In:** `SourceType.INSTAGRAM` + `InstagramSourceSettings`; `InstagramCollector` (subprocess + JSON parse + fail-closed); runner dual-guard + registration; tests (mocked subprocess via a fake runner — no live Instagram, no login); docs (cli-reference, source-packs example, architecture, source-boundaries Opt-In); CHANGELOG.

**Out:** Xiaohongshu (done), X (Phase 4), YouTube (Phase 5); storing/rotating login inside Fashion Radar; ToS enforcement (user responsibility, documented); DB schema change; new Python dependency; live end-to-end verification (user runs first; JSON field assumptions documented).

## Staging

- **Stage 231 (3a):** `SourceType.INSTAGRAM` + `InstagramSourceSettings` + no-op collector stub + registration + runner dual-guard (plumbing; reuse Stage 212/222 patterns).
- **Stage 232 (3b):** real `InstagramCollector` (subprocess + JSON parse + fail-closed) + tests.
- **Stage 233 (3c):** Phase 3 docs + docs-guard + CHANGELOG; Phase 3 release verification + release review + wrap.

## Risks

- **ToS:** Instagram prohibits automated access; user accepts risk. Documented use-at-your-own-risk.
- **instaloader availability:** external CLI the user installs + logs into; Fashion Radar fail-closes without it.
- **instaloader JSON shape:** varies by version; tolerant parsing + documented live-verification assumption.
- **No new dependency:** keep instaloader external; no `pyproject.toml` change.

## Verification

Per-stage focused tests + full gate; Stage 233 adds packaging/installed-wheel smoke. `git diff --exit-code -- uv.lock pyproject.toml` must exit 0.
