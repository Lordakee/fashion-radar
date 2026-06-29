# Phase 2 — Social Acquisition (Xiaohongshu) Design

- **Date:** 2026-06-30
- **Status:** Active mainline (project owner overturned the no-social-scraping boundary; Phase 2 = first social platform).
- **Predecessor:** Phase 1 (web acquisition) complete at `2c389d0`.
- **Review flow:** iron rule 2 (Claude Code primary reviewer; opencode `glm-5.2 --variant max` revises/fallback). Each stage: plan → Claude Code plan review → opencode revision → TDD implement → Claude Code code review → commit/push.

## Goal

Add direct acquisition from **Xiaohongshu (小红书)** by wrapping the mature `xiaohongshu-mcp` project (Go MCP-over-HTTP server with its own QR-login + cookie state), and reverse the project's documented social-scraping ban to allow opt-in, user-login-required, use-at-your-own-risk social collection. Instagram / X / YouTube remain deferred to Phases 3-5.

## Context & Roadmap (recap)

| Phase | Target | Wrapped tool | Login | Status |
|---|---|---|---|---|
| 1 | Official sites & news (RSS/HTML/sitemap) | feedparser + trafilatura + RSSHub | No | **Complete** (`2c389d0`) |
| **2** | **Xiaohongshu** | **`xiaohongshu-mcp`** (MCP HTTP) | **Yes (QR, managed by the tool)** | **This spec** |
| 3 | Instagram | `instaloader` | Yes | Planned |
| 4 | X / Twitter | `twitter-cli` (cookie) | Yes | Deferred |
| 5 | YouTube | `yt-dlp` | No | Deferred |

## Architecture

### Credential model

`xiaohongshu-mcp` manages its own login (a separate `xiaohongshu-login` tool performs QR login and persists cookies in its own data directory). Fashion Radar **does not handle login or store cookies itself**; it only:
- configures the `xiaohongshu-mcp` endpoint (default `http://localhost:18060/mcp`),
- requires the user to have run the login tool once (Fashion Radar fail-closes with a clear `login_required`/`endpoint_unavailable` skip if the endpoint is not reachable or reports not-logged-in),
- ensures any local cookie/session material stays gitignored (already covered by `.gitignore` `cookies*`/`session*` patterns + `scripts/check_release_hygiene.py`, which scans only tracked + untracked-unignored files — gitignored auth material is excluded).

So the credential model is a **convention + config field**, not new storage code. No change to `check_release_hygiene.py` is required for correctness; if desired, a later hardening can add an explicit allow-listed credentials directory.

### Xiaohongshu collector

- New `SourceType.XIAOHONGSHU` ("xiaohongshu") + a `query` (search keyword) or `queries` list, mirroring GDELT's query model.
- New `src/fashion_radar/collectors/xiaohongshu.py` `XiaohongshuCollector` that:
  1. builds an MCP HTTP client (JSON-RPC over HTTP via `httpx`) targeting the configured endpoint,
  2. calls `search_feeds(keyword=...)` → discovers note ids + `xsec_token`,
  3. calls `get_feed_detail(feed_id, xsec_token)` for each (bounded) → title/desc/engagement,
  4. maps each to a `CollectedItem` (`source_name=<configured>`, `source_type=XIAOHONGSHU`, `url` from the note, `title`, `summary` from description (report-safe), `published_at` from the note time or run `started_at`),
  5. returns `CollectorResult.success(items=..., items_seen=...)`.
- Fail-closed: endpoint unreachable / not-logged-in → `CollectorResult.skipped(reason="xiaohongshu_unavailable"|"login_required")`.
- Registered in `_default_collectors()`; runner integration reuses the existing health/run recording (no special enrichment — Xiaohongshu items already carry extracted text).

### MCP HTTP wrapper

A small `src/fashion_radar/collectors/xiaohongshu_mcp.py` (or inline) JSON-RPC client: `call_tool(name, arguments) -> result` over HTTP POST to the endpoint (MCP "streamable HTTP"). This is the only new external integration; it uses `httpx` (already a core dep). Tests mock the HTTP layer (no live MCP server, no login) — same pattern as the trafilatura/`article` tests.

### Boundary reversal

The no-social-scraping ban lives in a **bounded** set of places (verified): docs-guard assertions in `tests/test_project_brief_docs.py` (≈6), `tests/test_source_boundaries_docs.py` (1), `tests/test_architecture_boundary_docs.py` (1); and prose in `AGENTS.md`, `README.md`, `docs/source-boundaries.md`, `docs/architecture.md`, `docs/PROJECT_BRIEF.md`. The reversal rewrites these to: **social-platform collection is now an opt-in, user-login-required, use-at-your-own-risk capability** (Phase 2 adds Xiaohongshu; IG/X/YouTube follow). Boundary caveats retained: users respect each platform's ToS at their own risk; signals are local-observed only; no demand proof; no platform coverage verification; login material stays local/gitignored.

## Tech Stack

Python 3.11, httpx (core), Pydantic, pytest, `uv --no-config run --frozen`, Claude Code + opencode review. `xiaohongshu-mcp` is an **external runtime dependency the user installs/runs separately** (not a Python package dependency of Fashion Radar) — Fashion Radar only needs `httpx` to talk to its MCP HTTP endpoint. No new Python dependency, no `pyproject.toml`/`uv.lock` change.

## Scope (Phase 2)

**In:** `SourceType.XIAOHONGSHU`; `XiaohongshuCollector` + MCP HTTP wrapper; runner registration; boundary reversal in the 5 docs + the ~8 docs-guard assertions; config example; CHANGELOG; review artifacts.

**Out:** Instagram (Phase 3), X (4), YouTube (5); storing/rotating login cookies inside Fashion Radar (the wrapped tool owns login); any DB schema change; any new Python dependency; paywall/ToS enforcement (user responsibility, documented).

## Staging (sub-stages)

- **Stage 221 (2a) — Boundary reversal:** rewrite the social ban in the 5 docs + update the ~8 docs-guard assertions to the opt-in/use-at-your-own-risk framing. Docs + tests only; authorizes the rest.
- **Stage 222 (2b) — Xiaohongshu collector:** `SourceType.XIAOHONGSHU`, MCP HTTP wrapper, `XiaohongshuCollector`, runner registration, tests (mocked MCP), docs/config example, CHANGELOG.
- **Stage 223 (2c) — Phase 2 release wrap:** consolidated gate (incl. packaging/installed-wheel smoke), Phase 2 release review, CHANGELOG/spec wrap.

## Risks

- **ToS / legal:** Xiaohongshu prohibits automated access; the user accepts this risk ("推翻边界"). Documented as use-at-your-own-risk; no ToS enforcement in code.
- **xiaohongshu-mcp availability:** external binary the user must install/run/login; Fashion Radar fail-closes without it.
- **Boundary-reversal churn:** bounded (~8 assertions + 5 docs) but touches project identity — careful, review-gated.
- **No new dependency:** keep `xiaohongshu-mcp` external (runtime), talk to it over HTTP; do not add it to `pyproject.toml`.

## Verification

Per-stage focused tests + full gate; Stage 223 adds packaging/installed-wheel smoke. `git diff --exit-code -- uv.lock pyproject.toml` must exit 0 (no new Python dep).
