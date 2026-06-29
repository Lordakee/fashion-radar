# Phase 2 Release Review (Stage 223)
**Verdict:** APPROVE_WITH_NITS

## Critical

None.

## Important

**Field-name caveat is code-only, not user-facing.** The design spec (§ Verification) says "field-name assumptions are documented for the user's first live run." `xiaohongshu.py:244` carries the inline comment (`# xiaohongshu-mcp field name varies by version; try the common keys.`) and the multi-key fallback logic is robust (`_first(detail, ("time", "create_time", "last_update_time", ...))` etc.). But `docs/source-packs.md` — the natural first-run reference for Xiaohongshu config — has no prose warning that MCP response field names can vary by version and that the user should inspect raw output on first live use. The spec promised a user-facing caveat; it landed as a code comment only. Acceptable to ship (the fallback logic defends against it), but worth a one-sentence addition to the source-packs Xiaohongshu section before or at Stage 223 close.

## Nits

1. **`cookies*.db` absent from `.gitignore`.** Current patterns cover `cookies*.txt`, `cookies*.json`, `session*.json`. SQLite-backed cookie stores (`.db`) are common in Go/browser tooling. The real-world risk is low because `xiaohongshu-mcp` stores its session in its own data directory outside the project tree, but the pattern gap is worth filling for defence-in-depth.

2. **Login-error heuristic is a substring match on English keywords.** `xiaohongshu.py:169-173` classifies a `search_feeds` error as `login_required` iff `"login"` or `"logged"` appears in the lowercased message, otherwise `xiaohongshu_unavailable`. Both outcomes are skips with distinct log reasons, so a misclassification has no data-loss consequence; this is documentation-level only. Consider a follow-on hardening (e.g. HTTP401 status, or a known MCP error code) if `xiaohongshu-mcp` exposes one.

3. **`_parse_sse` returns `None` on no matching data line, but `_parse_mcp_response` falls through to `return data if isinstance(data, dict) else {}`** — so an all-comment SSE body yields `{}`, which is silently treated as a successful empty response rather than an error. Acceptable for current mock-test coverage; worth a note if SSE becomes the dominant transport.

## Résumé

Stages 221 and 222 together deliver a coherent, well-bounded opt-in Xiaohongshu collector. The boundary reversal is consistently framed across all five targeted docs and the boundary-guard tests. Fashion Radar stores no cookies; credential ownership is cleanly delegated to `xiaohongshu-mcp`. The collector is fail-closed on both unreachable-endpoint and not-logged-in paths. No new Python dependency and no DB schema change, consistent with the gate results. The one Important finding — missing user-facing field-name caveat in `source-packs.md` — is a documentation gap rather than a code defect, and the multi-key fallback logic already mitigates the runtime risk. No release-blocking defect found.
