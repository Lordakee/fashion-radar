from __future__ import annotations

import json
from datetime import UTC, datetime

from fashion_radar.collectors.base import CollectorRunStatus
from fashion_radar.collectors.xiaohongshu import XiaohongshuCollector, XiaohongshuMcpClient
from fashion_radar.models.source import SourceDefinition, SourceType

JSON = "application/json"


class _FakeResponse:
    def __init__(self, status_code: int, text: str, content_type: str = JSON) -> None:
        self.status_code = status_code
        self.text = text
        self.headers = {"content-type": content_type}


def _json_rpc(result, *, error=None) -> str:
    if error is not None:
        return json.dumps({"jsonrpc": "2.0", "id": 1, "error": error})
    return json.dumps({"jsonrpc": "2.0", "id": 1, "result": result})


def _text_tool(value) -> dict:
    return {"content": [{"type": "text", "text": json.dumps(value)}]}


def _ok(text: str, content_type: str = JSON):
    return (200, text, content_type)


class FakeMcpHttp:
    def __init__(self, responses) -> None:
        self._responses = list(responses)
        self.calls = []

    def post(self, url, *, json, headers):
        self.calls.append(json.get("method"))
        if not self._responses:
            raise AssertionError("unexpected extra MCP POST")
        status, text, ctype = self._responses.pop(0)
        return _FakeResponse(status, text, ctype)

    def close(self):
        pass


def _xhs_source(**overrides):
    payload = {"name": "XHS", "type": SourceType.XIAOHONGSHU, "query": "the row"}
    payload.update(overrides)
    return SourceDefinition(**payload)


def _client_with(responses):
    return XiaohongshuMcpClient("http://localhost:18060/mcp", FakeMcpHttp(responses))


def _search_detail_responses(notes, details):
    responses = [
        _ok(_json_rpc({"capabilities": {}})),
        _ok(""),
        _ok(_json_rpc(_text_tool(notes))),
    ]
    for detail in details:
        responses.append(_ok(_json_rpc(_text_tool(detail))))
    return responses


def test_xiaohongshu_collector_maps_search_and_detail_into_items():
    notes = [
        {"feed_id": "abc", "xsec_token": "tok1", "title": "Note A"},
        {"feed_id": "def", "xsec_token": "tok2", "title": "Note B"},
    ]
    details = [
        {"note_id": "abc", "title": "Note A", "desc": "desc A", "time": "2026-06-11T08:00:00Z"},
        {"note_id": "def", "title": "Note B", "desc": "desc B", "time": "2026-06-11T09:00:00Z"},
    ]
    client = _client_with(_search_detail_responses(notes, details))

    result = XiaohongshuCollector().collect(
        _xhs_source(), started_at=datetime(2026, 6, 11, 12, 0, tzinfo=UTC), mcp_client=client
    )

    assert result.status.status == CollectorRunStatus.SUCCESS
    assert result.status.items_seen == 2
    assert [item.url for item in result.items] == [
        "https://www.xiaohongshu.com/explore/abc",
        "https://www.xiaohongshu.com/explore/def",
    ]
    assert result.items[0].title == "Note A"
    assert result.items[0].summary == "desc A"
    assert result.items[0].published_at == datetime(2026, 6, 11, 8, 0, tzinfo=UTC)


def test_xiaohongshu_collector_skips_when_endpoint_unavailable():
    class FailingHttp:
        def post(self, url, *, json, headers):
            raise ConnectionError("refused")

        def close(self):
            pass

    client = XiaohongshuMcpClient("http://localhost:18060/mcp", FailingHttp())

    result = XiaohongshuCollector().collect(
        _xhs_source(), started_at=datetime(2026, 6, 11, 12, 0, tzinfo=UTC), mcp_client=client
    )

    assert result.status.status == CollectorRunStatus.SKIPPED
    assert result.status.error_message == "xiaohongshu_unavailable"
    assert result.items == []


def test_xiaohongshu_collector_skips_login_required_when_search_reports_login_error():
    responses = [
        _ok(_json_rpc({"capabilities": {}})),
        _ok(""),
        _ok(_json_rpc(None, error={"message": "user not logged in"})),
    ]
    client = _client_with(responses)

    result = XiaohongshuCollector().collect(
        _xhs_source(), started_at=datetime(2026, 6, 11, 12, 0, tzinfo=UTC), mcp_client=client
    )

    assert result.status.status == CollectorRunStatus.SKIPPED
    assert result.status.error_message == "login_required"


def test_xiaohongshu_collector_bounds_notes_to_max_per_run():
    notes = [{"feed_id": f"id{n}", "xsec_token": f"t{n}"} for n in range(5)]
    details = [{"note_id": f"id{n}", "title": f"Title {n}"} for n in range(5)]
    client = _client_with(_search_detail_responses(notes, details))

    result = XiaohongshuCollector().collect(
        _xhs_source(xiaohongshu={"max_notes_per_run": 3}),
        started_at=datetime(2026, 6, 11, 12, 0, tzinfo=UTC),
        mcp_client=client,
    )

    assert result.status.items_seen == 5
    assert len(result.items) == 3


def test_xiaohongshu_collector_keeps_note_when_detail_fails():
    notes = [
        {"feed_id": "abc", "xsec_token": "tok1", "title": "Note A", "desc": "search desc"},
        {"feed_id": "def", "xsec_token": "tok2", "title": "Note B"},
    ]
    responses = [
        _ok(_json_rpc({"capabilities": {}})),
        _ok(""),
        _ok(_json_rpc(_text_tool(notes))),
        _ok(_json_rpc(_text_tool({"note_id": "abc", "title": "Note A", "desc": "detail desc"}))),
        _ok(_json_rpc(None, error={"message": "boom"})),
    ]
    client = _client_with(responses)

    result = XiaohongshuCollector().collect(
        _xhs_source(), started_at=datetime(2026, 6, 11, 12, 0, tzinfo=UTC), mcp_client=client
    )

    assert [item.url for item in result.items] == [
        "https://www.xiaohongshu.com/explore/abc",
        "https://www.xiaohongshu.com/explore/def",
    ]
    assert result.items[0].summary == "detail desc"
    assert result.items[1].title == "Note B"


def test_xiaohongshu_collector_parses_sse_search_response():
    notes = [{"feed_id": "abc", "xsec_token": "tok1", "title": "Note A"}]
    detail = {"note_id": "abc", "title": "Note A"}
    sse_body = "event: message\ndata: " + _json_rpc(_text_tool(notes)) + "\n\n"
    responses = [
        _ok(_json_rpc({"capabilities": {}})),
        _ok(""),
        _ok(sse_body, "text/event-stream"),
        _ok(_json_rpc(_text_tool(detail))),
    ]
    client = _client_with(responses)

    result = XiaohongshuCollector().collect(
        _xhs_source(), started_at=datetime(2026, 6, 11, 12, 0, tzinfo=UTC), mcp_client=client
    )

    assert result.status.status == CollectorRunStatus.SUCCESS
    assert [item.url for item in result.items] == ["https://www.xiaohongshu.com/explore/abc"]


def test_xiaohongshu_mcp_client_initialize_runs_three_step_handshake():
    captured = []

    class Http:
        def post(self, url, *, json, headers):
            captured.append(json.get("method"))
            return _FakeResponse(200, _json_rpc({"capabilities": {}}) if json.get("id") else "")

        def close(self):
            pass

    XiaohongshuMcpClient("http://localhost:18060/mcp", Http()).initialize()

    assert captured == ["initialize", "notifications/initialized"]
