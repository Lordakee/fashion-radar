from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ENTITY_PACK_QUALITY_DOC = ROOT / "docs" / "entity-pack-quality.md"


def _read_entity_pack_quality_doc() -> str:
    return ENTITY_PACK_QUALITY_DOC.read_text(encoding="utf-8")


def _normalized(text: str) -> str:
    return " ".join(text.split()).casefold()


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
