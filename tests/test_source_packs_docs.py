from __future__ import annotations

import json
from pathlib import Path

import yaml

from fashion_radar.source_packs import lint_source_pack

ROOT = Path(__file__).resolve().parents[1]
SOURCE_PACKS_DOC = ROOT / "docs" / "source-packs.md"
PUBLIC_SOURCE_PACK = ROOT / "configs" / "source-packs" / "fashion-public.example.yaml"


def _read_source_packs_doc() -> str:
    return SOURCE_PACKS_DOC.read_text(encoding="utf-8")


def _normalized(text: str) -> str:
    return " ".join(text.split()).casefold()


def _section(text: str, heading: str) -> str:
    marker = f"## {heading}"
    assert marker in text
    return text.split(marker, 1)[1].split("\n## ", 1)[0]


def _example_json_block(text: str) -> str:
    marker = "Example JSON shape:"
    assert marker in text
    after_marker = text.split(marker, 1)[1]
    fence = "```json"
    assert fence in after_marker
    after_fence = after_marker.split(fence, 1)[1]
    block, closing_fence, _ = after_fence.partition("```")
    assert closing_fence == "```"
    return block.strip()


def _public_pack_source_names_by_type(source_type: str) -> list[str]:
    data = yaml.safe_load(PUBLIC_SOURCE_PACK.read_text(encoding="utf-8"))
    assert isinstance(data, dict)
    sources = data.get("sources")
    assert isinstance(sources, list)

    names: list[str] = []
    for source in sources:
        assert isinstance(source, dict)
        if source.get("type") == source_type:
            name = source.get("name")
            assert isinstance(name, str)
            names.append(name)
    return names


def _public_pack_gdelt_source_names() -> list[str]:
    return _public_pack_source_names_by_type("gdelt")


def _public_pack_rss_source_names() -> list[str]:
    return _public_pack_source_names_by_type("rss")


def _backticked_values(text: str) -> list[str]:
    parts = text.split("`")
    assert len(parts) % 2 == 1
    return parts[1::2]


def _backticked_bullet_values(text: str) -> list[str]:
    values: list[str] = []
    for line in text.splitlines():
        line = line.strip()
        if not line.startswith("- "):
            continue
        bullet_values = _backticked_values(line)
        assert len(bullet_values) == 1
        values.append(bullet_values[0])
    return values


def test_source_packs_docs_keep_public_pack_source_boundary() -> None:
    section = _section(_read_source_packs_doc(), "Public Fashion Pack")
    normalized = _normalized(section)

    for phrase in (
        "configs/source-packs/fashion-public.example.yaml",
        "it uses only existing v0.1.0 source types",
        "`rss`",
        "`gdelt`",
        "keeps the rss entries conservative",
        "bounded gdelt lanes",
        "inside the configured source set",
        "20 enabled sources",
        "10 rss feeds followed by 10 gdelt query lanes",
        "rss article extraction disabled by default",
        "24-hour lookback",
        "100 max records",
        "one request per second",
        "it does not include google news rss, google trends, "
        "account-based source access, browser automation, access-control bypasses, "
        "paywall bypass, or private data collection.",
    ):
        assert phrase in normalized


def test_source_packs_docs_list_public_gdelt_sources_in_pack_order() -> None:
    section = _section(_read_source_packs_doc(), "GDELT Queries")
    documented_gdelt_sources = _backticked_bullet_values(section)

    assert documented_gdelt_sources == _public_pack_gdelt_source_names()


def test_source_packs_docs_list_public_rss_sources_in_pack_order() -> None:
    section = _section(_read_source_packs_doc(), "RSS Feeds")
    documented_rss_sources = _backticked_bullet_values(section)

    assert documented_rss_sources == _public_pack_rss_source_names()


def test_source_packs_docs_example_json_matches_public_pack_lint_output() -> None:
    payload = json.loads(_example_json_block(_read_source_packs_doc()))
    result = lint_source_pack(PUBLIC_SOURCE_PACK)
    documented_path = PUBLIC_SOURCE_PACK.relative_to(ROOT).as_posix()

    assert result.findings == []
    assert payload["path"] == documented_path
    assert payload["source_count"] == result.source_count
    assert payload["enabled_count"] == result.enabled_count
    assert payload["disabled_count"] == result.disabled_count
    assert payload["type_counts"] == result.type_counts
    assert payload["tag_counts"] == result.tag_counts
    assert payload["findings"] == []


def test_source_packs_docs_show_source_liveness_command_examples() -> None:
    text = _read_source_packs_doc()

    assert (
        "uv run fashion-radar source-liveness configs/source-packs/fashion-public.example.yaml"
    ) in text
    assert (
        "uv run fashion-radar source-liveness "
        "configs/source-packs/fashion-public.example.yaml --format json"
    ) in text


def test_source_packs_docs_record_stage_201_direct_endpoint_refresh() -> None:
    section = _section(_read_source_packs_doc(), "Source Availability")
    normalized = _normalized(section)

    for phrase in (
        "stage 201 planning on 2026-06-25",
        "direct rss endpoints",
        "fashionista",
        "fashion week daily",
        "the industry fashion",
        "highsnobiety",
        "wwd",
        "availability can change without notice",
    ):
        assert phrase in normalized


def test_source_packs_docs_describe_self_hosted_rsshub() -> None:
    section = _section(_read_source_packs_doc(), "Self-Hosted RSSHub")
    normalized = _normalized(section)

    for phrase in (
        "self-hosting",
        "docker run",
        "type: rsshub",
        "robots rules",
        "no demand proof and no platform coverage verification",
    ):
        assert phrase in normalized, f"missing {phrase!r}"
