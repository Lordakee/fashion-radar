from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE_BOUNDARIES_DOC = ROOT / "docs" / "source-boundaries.md"


def _read_source_boundaries_doc() -> str:
    return SOURCE_BOUNDARIES_DOC.read_text(encoding="utf-8")


def _normalized(text: str) -> str:
    return " ".join(text.split()).casefold()


def _section(text: str, heading: str) -> str:
    marker = f"## {heading}"
    assert marker in text
    return text.split(marker, 1)[1].split("\n## ", 1)[0]


def test_source_boundaries_docs_keep_storage_boundary() -> None:
    storage_boundaries = _section(
        _read_source_boundaries_doc(),
        "Storage Boundaries",
    )
    normalized = _normalized(storage_boundaries)

    for phrase in (
        "Default storage should be conservative:",
        "Store source URLs, titles, publication timestamps, source names, "
        "optional local `platform` provenance labels for imported rows, short "
        "summaries, entity matches, tags, counts, and scores.",
        "Avoid storing full article text by default.",
        "Avoid storing original images or videos.",
        "Avoid storing user comments as redistributable assets.",
        "Preserve source links so users can read original content on the source site.",
        "Display source attribution beside representative items.",
        "Add attribution footer to generated reports.",
        "Skip extraction for known paywalled domains unless the source itself provides "
        "permitted metadata.",
    ):
        assert phrase.casefold() in normalized
