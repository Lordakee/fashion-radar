# Stage 222 Code Review

**Verdict:** APPROVE_WITH_NITS

## Critical

None.

## Important

None.

## Nits

**1. `_parse_mcp_response` — SSE branch skips error-key check** (`xiaohongshu.py:85-87`)

The JSON branch at line 95 raises `XiaohongshuMcpError` on `parsed.get("error")`, but the SSE branch returns the raw dict unconditionally. If the server ever sends a JSON-RPC error via SSE (e.g. `{"error": {"message": "user not logged in"}}`), `_extract_tool_result` would get `result=None`, `_coerce_note_list(None)` → `[]`, and the collector would return `SUCCESS` with 0 items instead of `SKIPPED(login_required)`. Consistent fix:

```python
if "text/event-stream" in content_type:
    data = _parse_sse(response.text)
    if isinstance(data, dict) and data.get("error"):
        raise XiaohongshuMcpError(f"MCP error: {data['error']}")
    return data if isinstance(data, dict) else {}
```

**2. `max_notes_per_run` has no upper bound** (`source.py:61`)

`GdeltSourceSettings.max_records` uses `le=250`; `max_notes_per_run` only has `gt=0`. Add a reasonable cap (e.g. `le=200`) for consistency and to prevent runaway API calls on a misconfigured source.

**3. `_HttpPoster` parameter name shadows `json` module** (`xiaohongshu.py:21-23`)

The `post` signature's `json: dict[str, Any]` parameter shadows the top-level `import json`. Works at runtime but is a linting trap. Rename to `payload` in the Protocol (and `_request`'s call site) to avoid confusion.

**4. `_map_note` time field fallback list is undocumented** (`xiaohongshu.py:242`)

`("time", "create_time", "last_time", "last_update_time")` is a guess at xiaohongshu-mcp's field names. A brief inline comment (`# xiaohongshu-mcp field name varies by version`) would make the intent clear and help future maintainers.

## Résumé

Solid implementation. The3-step MCP handshake is correct, both runner guards include XIAOHONGSHU, fail-closed / login-required / cap / items_seen / report_safe_snippet / published_at fallback are all properly implemented, and test coverage is thorough across all required scenarios. The SSE error path (nit 1) is the only behavioral gap worth addressing before the next release.
