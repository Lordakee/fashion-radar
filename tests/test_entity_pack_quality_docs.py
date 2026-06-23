from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from fashion_radar.entity_packs import lint_entity_pack, render_entity_pack_lint_table

ROOT = Path(__file__).resolve().parents[1]
ENTITY_PACK_QUALITY_DOC = ROOT / "docs" / "entity-pack-quality.md"
WATCHLIST_ENTITY_PACK = ROOT / "configs" / "entity-packs" / "fashion-watchlist.example.yaml"


def _read_entity_pack_quality_doc() -> str:
    return ENTITY_PACK_QUALITY_DOC.read_text(encoding="utf-8")


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


def _entity_pack_quality_table_sample() -> list[str]:
    block = _fenced_block_after(
        _read_entity_pack_quality_doc(),
        "Table output starts with a compact summary:",
        "text",
    )
    return block.splitlines()


def _entity_pack_quality_json_sample() -> dict[str, Any]:
    block = _fenced_block_after(
        _read_entity_pack_quality_doc(),
        "JSON output contains the same information in a stable shape",
        "json",
    )
    payload = json.loads(block)
    assert isinstance(payload, dict)
    return payload


def _json_ready_first_finding(result: Any) -> dict[str, Any]:
    assert result.findings
    payload = json.loads(result.findings[0].model_dump_json())
    assert isinstance(payload, dict)
    return payload


def test_entity_pack_quality_docs_keep_local_read_only_boundary() -> None:
    normalized = _normalized(_read_entity_pack_quality_doc())

    for phrase in (
        "checks one local entity yaml or entity-pack yaml file",
        "linting is local and read-only",
        "does not match items",
        "score entities",
        "inspect sqlite",
        "collect sources",
        "search social platforms",
        "fetch pages",
        "create config, data, report, digest, or workflow artifacts",
    ):
        assert phrase in normalized


def test_entity_pack_quality_docs_keep_non_claim_boundary() -> None:
    normalized = _normalized(_read_entity_pack_quality_doc())

    for phrase in (
        "not a hot-list, ranking, platform-wide signal, market-wide proof",
        "compliance review, audit workflow, or legal review",
        "does not know whether a brand, bag, shoe, celebrity outfit, "
        "or style phrase is popular today",
        "does not search instagram, tiktok, x, xiaohongshu, community tools, "
        "news sites, or exports",
        "local configuration quality signal",
        "not a ranking, hot-list, demand proof",
        "source acquisition workflow",
        "platform search",
        "social monitoring workflow",
        "compliance review, or audit result",
    ):
        assert phrase in normalized


def test_entity_pack_quality_table_sample_matches_watchlist_lint_prefix() -> None:
    sample_lines = _entity_pack_quality_table_sample()
    relative_pack_path = WATCHLIST_ENTITY_PACK.relative_to(ROOT)
    rendered_lines = render_entity_pack_lint_table(lint_entity_pack(relative_pack_path))

    assert sample_lines == rendered_lines[: len(sample_lines)]


def test_entity_pack_quality_json_sample_matches_watchlist_lint_counts() -> None:
    payload = _entity_pack_quality_json_sample()
    result = lint_entity_pack(WATCHLIST_ENTITY_PACK)
    documented_path = WATCHLIST_ENTITY_PACK.relative_to(ROOT).as_posix()

    assert payload["path"] == documented_path
    assert payload["entity_count"] == result.entity_count
    assert payload["alias_count"] == result.alias_count
    assert payload["type_counts"] == result.type_counts
    assert payload["tag_counts"] == result.tag_counts
    assert payload["category_tag_counts"] == result.category_tag_counts
    assert payload["accepted_without_context_aliases"] == result.accepted_without_context_aliases
    assert payload["context_gated_aliases"] == result.context_gated_aliases
    assert payload["safe_aliases"] == result.safe_aliases
    assert payload["product_parent_gated_aliases"] == result.product_parent_gated_aliases
    assert [finding["severity"] for finding in payload["findings"]] == ["warning"]
    assert payload["findings"][0] == _json_ready_first_finding(result)

    normalized = _normalized(_read_entity_pack_quality_doc())
    assert "abbreviated representative excerpt" in normalized
    assert "not the full findings list" in normalized
