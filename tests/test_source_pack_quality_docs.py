from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE_PACK_QUALITY_DOC = ROOT / "docs" / "source-pack-quality.md"


def _read_source_pack_quality_doc() -> str:
    return SOURCE_PACK_QUALITY_DOC.read_text(encoding="utf-8")


def _normalized(text: str) -> str:
    return " ".join(text.split()).casefold()


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
