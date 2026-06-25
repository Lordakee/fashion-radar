from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ENTITY_PACKS_DOC = ROOT / "docs" / "entity-packs.md"


def _read_entity_packs_doc() -> str:
    return ENTITY_PACKS_DOC.read_text(encoding="utf-8")


def _normalized(text: str) -> str:
    return " ".join(text.split()).casefold()


def test_entity_packs_docs_keep_local_matching_boundary() -> None:
    normalized = _normalized(_read_entity_packs_doc())

    for phrase in (
        "optional local configuration templates",
        "without changing fashion radar's runtime behavior",
        "only changes local entity matching",
        "does not add sources",
        "does not add ingestion",
        "does not add live collection",
        "does not prove demand",
        "does not rank brands",
        "does not verify platform coverage",
    ):
        assert phrase in normalized


def test_entity_packs_docs_keep_optional_sample_boundary() -> None:
    normalized = _normalized(_read_entity_packs_doc())

    for phrase in (
        "optional local sample",
        "checked-in synthetic community-signal rows",
        "local sample rows are synthetic",
        "not a hot-list, not a ranking",
        "not demand proof",
        "not platform coverage verification",
        "local files only",
        "no fetching urls",
        "no platform data collection",
        "no connectors",
    ):
        assert phrase in normalized


def test_entity_packs_docs_describe_explicit_context_gates() -> None:
    text = _read_entity_packs_doc()
    normalized = _normalized(text)

    assert "requires_context: true" in text
    assert "provide `context_terms`" in text
    assert "need surrounding fashion language" in normalized
    assert "instead of terms satisfied only by the alias text itself" in normalized
