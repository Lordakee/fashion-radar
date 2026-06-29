# Stage 222Plan Review

**Verdict:** APPROVE_WITH_NITS

## Critical

None.

## Important

**1. Missing `initialized` notification in MCP handshake.**
The plan describes `initialize()` then `tools/call`, but the MCP spec requires a three-step lifecycle: (1) `initialize` request → server responds with capabilities, (2) client sends `{"jsonrpc":"2.0","method":"notifications/initialized"}` *(notification — no `id`)*, (3) then `tools/call` is valid. `xiaohongshu-mcp` is a Go implementation that likely enforces this. Omitting the notification will cause a protocol error on the live run. The implementation must include this step between `initialize` response and the first `tools/call`.

**2. Endpoint configurability contradicts `extra="forbid"` on `SourceDefinition`.**
The plan says the MCP endpoint is configurable (default `http://localhost:18060/mcp`) but also says "no schema change." `SourceDefinition` carries `ConfigDict(extra="forbid")`, so a configurable per-source endpoint requires a new `xiaohongshu: XiaohongshuSourceSettings` sub-model (analogous to the existing `gdelt: GdeltSourceSettings` field). This is a Pydantic model change, not a DB schema change — the distinction should be made explicit, and the plan's task list should include adding `XiaohongshuSourceSettings`. If the intent is instead to use a hardcoded default with no per-source override, document that explicitly and note it as a Phase 2c follow-up.

**3. MCP streamable HTTP may return `text/event-stream`, not `application/json`.**
Per the MCP streamable HTTP spec, the server may respond with either `Content-Type: application/json` (synchronous) or `text/event-stream` (SSE). The plan assumes plain JSON responses. If `xiaohongshu-mcp` returns SSE for tool results (even synchronous ones), a raw `response.json()` call will fail. The implementation should either (a) confirm via `Content-Type` inspection and handle both, or (b) document the assumption that `xiaohongshu-mcp` returns `application/json` and make it a live-verification item. At minimum, send `Accept: application/json, text/event-stream` in the POST header to comply with the spec.

## Nits

**N1. `items_seen` semantics.** Clarify that `items_seen` is the count of search-result notes returned by `search_feeds` (before the detail-fetch cap filters them), not the collected count. This matches the `CollectorResult.success(items_seen=...)` contract used in other collectors and should be explicit in the implementation spec.

**N2. `XiaohongshuMcpClient` re-init vs. singleton.** The plan says "initialize once" without specifying whether the client re-initializes on each `collect()` invocation or is shared across calls. Either is fine, but a fresh client per `collect()` call is safer given the short-lived runner lifecycle; note the choice explicitly so the test helpers mock the right scope.

**N3. Runner line-97 guard parity.** The plan mentions "enrichment-skip set + the line-73 guard." For completeness, confirm `XIAOHONGSHU` is also added to the line-97 guard (`source.type not in {SourceType.HTML, SourceType.SITEMAP}`). Functionally redundant since the extractor won't be created (line-73 guard), but the two-set symmetry matches how HTML/SITEMAP are handled and prevents a future regression if the initialization logic changes.

**N4. `xsec_token` association.** The tolerant token extraction (`xsec_token`, `token`) is sound. One implicit assumption: the token extracted from each `search_feeds` item is per-note, not a global session token. This is consistent with how `xiaohongshu-mcp` works, but worth one sentence of comment in the implementation to signal intent.

## Résumé

The design is well-structured: fail-closed skip pattern, tolerant field extraction, bound cap, `report_safe_snippet` on description, and no new Python dep are all correct. The three Important items — the missing `initialized` notification, the endpoint-configurability model gap, and the SSE/JSON response ambiguity — need to be addressed in Task 1-2 before the live verification step. None block plan approval; all are straightforward to resolve in implementation.
