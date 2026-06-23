from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from fashion_radar.source_packs import lint_source_pack, render_source_pack_lint_table

ROOT = Path(__file__).resolve().parents[1]
SOURCE_PACK_QUALITY_DOC = ROOT / "docs" / "source-pack-quality.md"
PUBLIC_SOURCE_PACK = ROOT / "configs" / "source-packs" / "fashion-public.example.yaml"


def _read_source_pack_quality_doc() -> str:
    return SOURCE_PACK_QUALITY_DOC.read_text(encoding="utf-8")


def _normalized(text: str) -> str:
    return " ".join(text.split()).casefold()


def _fenced_block_after(text: str, marker: str, language: str) -> str:
    assert marker in text
    after_marker = text.split(marker, 1)[1]
    fence = f"```{language}"
    assert fence in after_marker
    after_fence = after_marker.split(fence, 1)[1]
    block, closing_fence, _ = after_fence.partition("```")
    assert closing_fence == "```"
    return block.strip()


def _source_pack_quality_table_sample() -> list[str]:
    block = _fenced_block_after(
        _read_source_pack_quality_doc(),
        "Table output starts with a compact summary:",
        "text",
    )
    return block.splitlines()


def _source_pack_quality_json_sample() -> dict[str, Any]:
    block = _fenced_block_after(
        _read_source_pack_quality_doc(),
        "JSON output contains the same information in a stable shape",
        "json",
    )
    payload = json.loads(block)
    assert isinstance(payload, dict)
    return payload


def test_source_pack_quality_docs_keep_local_read_only_boundary() -> None:
    normalized = _normalized(_read_source_pack_quality_doc())

    for phrase in (
        "linting is local and read-only",
        "does not fetch sources",
        "check live feed availability",
        "collect source items",
        "open sqlite",
        "create config, data, report, or workflow artifacts",
        "not a compliance, audit, policy, or source-terms review workflow",
    ):
        assert phrase in normalized


def test_source_pack_quality_json_docs_keep_non_data_boundary() -> None:
    normalized = _normalized(_read_source_pack_quality_doc())

    for phrase in (
        "json output does not include fetched data, collected items",
        "database state, source contents, or account data",
    ):
        assert phrase in normalized


def test_source_pack_quality_docs_keep_availability_and_demand_boundaries() -> None:
    normalized = _normalized(_read_source_pack_quality_doc())

    for phrase in (
        "the lint command does not fetch article pages",
        "should not be described as proof of demand outside it",
        "checks the configured yaml file only",
        "does not know whether a feed is live today",
        "whether a gdelt query will return records",
        "local configuration quality signal, not as a source availability guarantee",
    ):
        assert phrase in normalized


def test_source_pack_quality_table_sample_matches_public_pack_lint_prefix() -> None:
    sample_lines = _source_pack_quality_table_sample()
    relative_pack_path = PUBLIC_SOURCE_PACK.relative_to(ROOT)
    rendered_lines = render_source_pack_lint_table(lint_source_pack(relative_pack_path))

    assert sample_lines == rendered_lines[: len(sample_lines)]


def test_source_pack_quality_json_sample_matches_public_pack_lint_output() -> None:
    payload = _source_pack_quality_json_sample()
    result = lint_source_pack(PUBLIC_SOURCE_PACK)
    documented_path = PUBLIC_SOURCE_PACK.relative_to(ROOT).as_posix()

    assert payload["path"] == documented_path
    assert payload["source_count"] == result.source_count
    assert payload["enabled_count"] == result.enabled_count
    assert payload["disabled_count"] == result.disabled_count
    assert payload["type_counts"] == result.type_counts
    assert payload["tag_counts"] == result.tag_counts
    assert payload["findings"] == []
    assert result.findings == []
