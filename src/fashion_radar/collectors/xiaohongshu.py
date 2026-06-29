from __future__ import annotations

import json
from datetime import UTC, datetime
from typing import Any, Protocol

import httpx

from fashion_radar.collectors.base import CollectorResult
from fashion_radar.models.item import CollectedItem
from fashion_radar.models.report import report_safe_snippet
from fashion_radar.models.source import SourceDefinition
from fashion_radar.utils.dates import parse_datetime_utc


class XiaohongshuMcpError(RuntimeError):
    """Raised when the xiaohongshu-mcp endpoint cannot be reached or returns an error."""


class _HttpPoster(Protocol):
    def post(
        self, url: str, *, json: dict[str, Any], headers: dict[str, str]
    ) -> httpx.Response: ...


class XiaohongshuMcpClient:
    """Minimal MCP-over-HTTP (streamable) JSON-RPC client for xiaohongshu-mcp."""

    def __init__(self, endpoint: str, client: _HttpPoster) -> None:
        self._endpoint = endpoint
        self._client = client
        self._id = 0

    def initialize(self) -> None:
        self._request(
            {
                "jsonrpc": "2.0",
                "id": self._next_id(),
                "method": "initialize",
                "params": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {},
                    "clientInfo": {"name": "fashion-radar", "version": "0.1.0"},
                },
            }
        )
        # MCP lifecycle: send the initialized notification (no id) before tools/call.
        self._request({"jsonrpc": "2.0", "method": "notifications/initialized"})

    def call_tool(self, name: str, arguments: dict[str, Any]) -> Any:
        payload = self._request(
            {
                "jsonrpc": "2.0",
                "id": self._next_id(),
                "method": "tools/call",
                "params": {"name": name, "arguments": arguments},
            }
        )
        return _extract_tool_result(payload)

    def close(self) -> None:
        if hasattr(self._client, "close"):
            self._client.close()

    def _next_id(self) -> int:
        self._id += 1
        return self._id

    def _request(self, payload: dict[str, Any]) -> dict[str, Any]:
        try:
            response = self._client.post(
                self._endpoint,
                json=payload,
                headers={"Accept": "application/json, text/event-stream"},
            )
        except Exception as exc:
            raise XiaohongshuMcpError(f"MCP request failed: {exc}") from exc
        return _parse_mcp_response(response)


def _parse_mcp_response(response: httpx.Response) -> dict[str, Any]:
    if response.status_code >= 400:
        raise XiaohongshuMcpError(f"MCP HTTP {response.status_code}")
    content_type = response.headers.get("content-type", "")
    if "text/event-stream" in content_type:
        data = _parse_sse(response.text)
        if isinstance(data, dict) and data.get("error"):
            raise XiaohongshuMcpError(f"MCP error: {data['error']}")
        return data if isinstance(data, dict) else {}
    text = response.text
    if not text.strip():
        return {}
    try:
        parsed = json.loads(text)
    except ValueError as exc:
        raise XiaohongshuMcpError(f"MCP non-JSON response: {exc}") from exc
    if isinstance(parsed, dict) and parsed.get("error"):
        raise XiaohongshuMcpError(f"MCP error: {parsed['error']}")
    return parsed if isinstance(parsed, dict) else {}


def _parse_sse(text: str) -> dict[str, Any] | None:
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("data:"):
            raw = stripped[len("data:") :].strip()
            try:
                parsed = json.loads(raw)
            except ValueError:
                continue
            if isinstance(parsed, dict):
                return parsed
    return None


def _extract_tool_result(payload: dict[str, Any]) -> Any:
    result = payload.get("result")
    if not isinstance(result, dict):
        return result
    content = result.get("content")
    if isinstance(content, list) and content:
        first = content[0]
        if isinstance(first, dict) and first.get("type") == "text":
            text_value = first.get("text") or ""
            try:
                return json.loads(text_value)
            except ValueError:
                return text_value
    return result


class XiaohongshuCollector:
    """Collector for ``xiaohongshu`` sources via the external xiaohongshu-mcp server.

    The user installs/runs/logs into xiaohongshu-mcp separately; Fashion Radar only
    reads results over its local MCP HTTP endpoint. Fail-closed (skipped) when the
    endpoint is unreachable, errors, or reports a login problem. Opt-in,
    use-at-your-own-risk; provides no demand proof and no platform coverage
    verification.
    """

    def collect(
        self,
        source: SourceDefinition,
        *,
        started_at: datetime | None = None,
        mcp_client: XiaohongshuMcpClient | None = None,
    ) -> CollectorResult:
        started_at = started_at or datetime.now(tz=UTC)
        settings = source.xiaohongshu
        owns_client = mcp_client is None
        if mcp_client is None:
            mcp_client = XiaohongshuMcpClient(
                settings.endpoint,
                httpx.Client(
                    timeout=source.http.timeout_seconds,
                    headers={"User-Agent": source.http.user_agent},
                ),
            )
        try:
            try:
                mcp_client.initialize()
            except XiaohongshuMcpError:
                return _skipped(source, "xiaohongshu_unavailable", started_at)
            try:
                search_raw = mcp_client.call_tool("search_feeds", {"keyword": source.query})
            except XiaohongshuMcpError as exc:
                lowered = str(exc).lower()
                reason = (
                    "login_required"
                    if any(keyword in lowered for keyword in ("login", "logged"))
                    else "xiaohongshu_unavailable"
                )
                return _skipped(source, reason, started_at)
            notes = _coerce_note_list(search_raw)
            bounded = notes[: settings.max_notes_per_run]
            items: list[CollectedItem] = []
            for note in bounded:
                note_id = _first(note, ("feed_id", "note_id", "id"))
                # xsec_token is per-note (carried by each search result item).
                xsec_token = _first(note, ("xsec_token", "token"))
                if not note_id:
                    continue
                try:
                    detail = mcp_client.call_tool(
                        "get_feed_detail",
                        {"feed_id": note_id, "xsec_token": xsec_token},
                    )
                except XiaohongshuMcpError:
                    detail = None
                mapped = _map_note(source, note, detail, started_at)
                if mapped is not None:
                    items.append(mapped)
            return CollectorResult.success(
                source,
                items=items,
                started_at=started_at,
                items_seen=len(notes),
            )
        finally:
            if owns_client:
                mcp_client.close()


def _skipped(source: SourceDefinition, reason: str, started_at: datetime) -> CollectorResult:
    return CollectorResult.skipped(source, reason=reason, started_at=started_at)


def _coerce_note_list(raw: Any) -> list[dict[str, Any]]:
    if isinstance(raw, list):
        return [item for item in raw if isinstance(item, dict)]
    if isinstance(raw, dict):
        for key in ("data", "notes", "items", "feeds", "results"):
            value = raw.get(key)
            if isinstance(value, list):
                return [item for item in value if isinstance(item, dict)]
    return []


def _first(mapping: dict[str, Any], keys: tuple[str, ...]) -> Any:
    for key in keys:
        value = mapping.get(key)
        if value not in (None, ""):
            return value
    return None


def _map_note(
    source: SourceDefinition,
    note: dict[str, Any],
    detail: Any,
    started_at: datetime,
) -> CollectedItem | None:
    detail = detail if isinstance(detail, dict) else {}
    note_id = _first(detail, ("note_id", "id", "feed_id")) or _first(
        note, ("feed_id", "note_id", "id")
    )
    if not note_id:
        return None
    title = _first(detail, ("title",)) or _first(note, ("title",)) or f"Xiaohongshu note {note_id}"
    description = _first(detail, ("desc", "description", "content")) or _first(
        note, ("desc", "description")
    )
    # xiaohongshu-mcp field name varies by version; try the common keys.
    raw_time = _first(detail, ("time", "create_time", "last_time", "last_update_time"))
    url = f"https://www.xiaohongshu.com/explore/{note_id}"
    return CollectedItem(
        source_name=source.name,
        source_type=source.type,
        url=url,
        title=title,
        published_at=_published_at(raw_time, started_at),
        summary=report_safe_snippet(description),
    )


def _published_at(raw: Any, fallback: datetime) -> datetime:
    if raw:
        try:
            return parse_datetime_utc(str(raw))
        except Exception:
            return fallback
    return fallback
