# Stage 222 Xiaohongshu Collector Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a `XiaohongshuCollector` that reads Xiaohongshu (小红书) notes via the external `xiaohongshu-mcp` server (MCP-over-HTTP, login managed by the user), mapping search results + note details into local `CollectedItem`s — the first social-platform acquisition path.

**Architecture:** New `SourceType.XIAOHONGSHU` ("xiaohongshu"), requiring `query` (search keyword), mirroring GDELT. New `src/fashion_radar/collectors/xiaohongshu.py` `XiaohongshuCollector` + a small MCP-over-HTTP JSON-RPC client (`XiaohongshuMcpClient`). A **fresh** `XiaohongshuMcpClient` is constructed per `collect()` call (short-lived runner lifecycle; not a shared singleton). The MCP handshake is the spec-required **3-step** lifecycle: (1) `initialize` request → server responds with capabilities, (2) client sends a `notifications/initialized` **notification** (`{"jsonrpc":"2.0","method":"notifications/initialized"}`, no `id`), (3) then `tools/call` is valid. After handshake: `call_tool("search_feeds", {keyword})` → note ids + per-note `xsec_token`, then `call_tool("get_feed_detail", {feed_id, xsec_token})` per result (bounded by `XiaohongshuSourceSettings.max_notes_per_run`) → title/desc/time → mapped to `CollectedItem` with `report_safe_snippet` on the description. `items_seen` = count of `search_feeds` results **pre-cap** (before the detail-fetch bound filters them), matching the `CollectorResult.success(items_seen=...)` contract — not the post-cap collected count. The client sends `Accept: application/json, text/event-stream` on each POST and inspects the response `Content-Type`: parse JSON directly for `application/json`, or read the SSE `data:` line JSON for `text/event-stream`. Fail-closed: endpoint unreachable / not-logged-in → `CollectorResult.skipped(reason="xiaohongshu_unavailable"|"login_required")`. Registered in `_default_collectors()`. No new Python dependency (uses core `httpx`); `xiaohongshu-mcp` is an external runtime the user installs/runs/logs into — Fashion Radar only talks to its local HTTP endpoint.

**Tech Stack:** Python 3.11, httpx (core), Pydantic, pytest, `uv --no-config run --frozen`, Claude Code + opencode (`glm-5.2 --variant max`) review.

## Credential model

`xiaohongshu-mcp` owns login (QR via its `xiaohongshu-login` tool; cookies persist in its own data dir). Fashion Radar never stores/handles cookies — it only points at the endpoint (configurable per-source via `XiaohongshuSourceSettings.endpoint`, default `http://localhost:18060/mcp`) and fail-closes if the server is missing or reports not-logged-in. The user's cookie material stays gitignored (existing `.gitignore` `cookies*`/`session*` + `check_release_hygiene.py` patterns). No `check_release_hygiene.py` change needed.

## Scope

**In scope:**
- `SourceType.XIAOHONGSHU` + `validate_source_target` branch (requires `query`).
- New `XiaohongshuSourceSettings` Pydantic sub-model on `SourceDefinition` (a `xiaohongshu:` field analogous to the existing `gdelt: GdeltSourceSettings`): `endpoint` (default `http://localhost:18060/mcp`) + `max_notes_per_run` (default cap). This is a **Pydantic model change, NOT a DB schema change** — required because `SourceDefinition` carries `ConfigDict(extra="forbid")`, so per-source endpoint configurability needs an explicit sub-model.
- `XiaohongshuMcpClient` (MCP JSON-RPC over HTTP, 3-step handshake: `initialize` request → server capabilities → `notifications/initialized` notification → `tools/call`; sends `Accept: application/json, text/event-stream` and parses by `Content-Type`) + `XiaohongshuCollector` (fresh client per `collect()`).
- Register in `_default_collectors()`; runner integration (no article enrichment for XIAOHONGSHU — items already carry extracted text; add XIAOHONGSHU to BOTH the runner line-73 article-extractor guard AND the line-97 enrichment-skip set, mirroring the existing HTML/SITEMAP two-set symmetry).
- Tests (`tests/test_collectors_xiaohongshu.py`): search→detail→CollectedItem happy path (mocked MCP), partial detail failures, fail-closed (endpoint error / login_required), bound cap, `report_safe_snippet` on description, published_at fallback.
- Docs: `docs/cli-reference.md`, `docs/source-packs.md` (xiaohongshu config example), `docs/architecture.md` (Collectors); docs-guard where natural.
- CHANGELOG `### Added`.

**Out of scope:** Instagram (Phase 3), X (4), YouTube (5); storing/rotating login cookies inside Fashion Radar; ToS enforcement (user responsibility, documented); any DB schema change; any new Python dependency; live end-to-end verification against a real `xiaohongshu-mcp` (the user performs that after install/login — field-name assumptions are documented for that verification).

## Field-mapping assumptions (to verify against a live xiaohongshu-mcp)

- `search_feeds(keyword)` result items: tolerant extraction of `feed_id` (keys tried: `feed_id`, `note_id`, `id`) and `xsec_token` (keys: `xsec_token`, `token`) — **`xsec_token` is per-note (extracted from each `search_feeds` item), NOT a global/session token** (the implementation includes a one-line comment to signal this intent); item `title` if present.
- `get_feed_detail(feed_id, xsec_token)` result: `title` (keys: `title`, `desc` fallback), description (keys: `desc`, `description`, `content`), note id (keys: `note_id`, `id`, `feed_id`), time (keys: `time`, `create_time`, `last_time`, `last_update_time`).
- `CollectedItem.url` = `https://www.xiaohongshu.com/explore/{note_id}`.
- **MCP transport:** `xiaohongshu-mcp` (streamable HTTP) may return either `Content-Type: application/json` (synchronous) or `text/event-stream` (SSE). The client sends `Accept: application/json, text/event-stream` and parses per Content-Type; if the live server returns SSE where the plan's mocked tests assume plain JSON, the Content-Type branch handles it. (If a future run reveals `xiaohongshu-mcp` is JSON-only, the SSE branch is dead code but harmless.)
These are documented assumptions; the mocked tests use representative shapes. A live run may need field-key tweaks (tracked as a follow-up after the user's first live test).

## Tasks (summary)

- **Task 0 (plan review):** Claude Code reviews (esp. MCP JSON-RPC shape + field assumptions + whether initialize-handshake is needed); opencode revises. `docs/reviews/claude-code-stage-222-plan-review.md`.
- **Task 1 (model + plumbing, RED→GREEN):** `SourceType.XIAOHONGSHU` + validator branch; add `XiaohongshuSourceSettings` Pydantic sub-model (`endpoint` default `http://localhost:18060/mcp`, `max_notes_per_run` default) + `xiaohongshu:` field on `SourceDefinition` (analogous to `gdelt: GdeltSourceSettings`) — Pydantic model change only, no DB/Pydantic `extra="forbid"` regression (existing source-model + config tests must stay green); register no-op collector; runner line-73 guard + line-97 enrichment-skip for XIAOHONGSHU. Reuse Stage 212 patterns.
- **Task 2 (MCP client + collector, RED→GREEN):** `XiaohongshuMcpClient` — 3-step handshake (`initialize` request → server capabilities → `notifications/initialized` notification with no `id` → `tools/call`); send `Accept: application/json, text/event-stream`, inspect response `Content-Type` and parse JSON directly or read the SSE `data:` line JSON; fresh short-lived client per `collect()`; mocked via httpx — + `XiaohongshuCollector` (search→detail→items, `items_seen` = pre-cap `search_feeds` count, fail-closed, bound by `XiaohongshuSourceSettings.max_notes_per_run`, `report_safe_snippet`, one-line comment that `xsec_token` is per-note). Mocked tests.
- **Task 3 (docs + changelog):** cli-reference, source-packs example, architecture; CHANGELOG.
- **Task 4 (focused + Claude Code code review + full gate + commit):** focused pytest, ruff, full gate, `claude --effort max ...` review, commit "Stage 222: Xiaohongshu collector via xiaohongshu-mcp", push.

## Verification

Focused: `tests/test_collectors_xiaohongshu.py tests/test_source_model.py tests/test_config.py tests/test_collectors_runner.py tests/test_collectors_html.py tests/test_collectors_sitemap.py`. Full gate. `git diff --exit-code -- uv.lock pyproject.toml` exits 0 (no new Python dep).

## Self-Review

- First social path; opt-in/use-at-your-own-risk framing already in docs (Stage 221).
- Fail-closed without the external tool/login; core CLI unaffected.
- No new Python dependency; `xiaohongshu-mcp` is external runtime.
- Field-mapping assumptions are explicit + documented for live verification (mocked tests validate collector logic, not the live API contract).
- Runner enrichment-skip extended to XIAOHONGSHU on both the line-73 extractor guard and the line-97 enrichment set (HTML/SITEMAP symmetry).
- MCP handshake is the full 3-step lifecycle (`initialize` → `notifications/initialized` → `tools/call`); client handles both `application/json` and `text/event-stream` responses via Content-Type inspection.
- `XiaohongshuSourceSettings` (Pydantic, not a DB schema change) makes endpoint + `max_notes_per_run` per-source configurable; fresh `XiaohongshuMcpClient` per `collect()`.
- `items_seen` is the pre-cap `search_feeds` result count; `xsec_token` is per-note (commented in impl).
