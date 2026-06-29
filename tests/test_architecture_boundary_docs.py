from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ARCHITECTURE_DOC = ROOT / "docs" / "architecture.md"


def _read_architecture_doc() -> str:
    return ARCHITECTURE_DOC.read_text(encoding="utf-8")


def _markdown_section(text: str, heading: str) -> str:
    marker = f"\n{heading}\n"
    assert marker in f"\n{text}"
    return text.split(heading, 1)[1].split("\n## ", 1)[0]


def _normalized(text: str) -> str:
    return " ".join(text.split()).casefold()


def test_architecture_source_boundary_keeps_core_scope_and_local_import_limits() -> None:
    section = _markdown_section(_read_architecture_doc(), "## Source Boundary")
    normalized = _normalized(section)

    for phrase in (
        (
            "the core collector set is rss, rsshub-compatible feeds, "
            "gdelt, html seed-url collection, and sitemap discovery"
        ),
        "manual signal import is a local input path",
        "user-provided csv/json files",
        "not a connector or platform collector",
        "non-core platform collection is not part of v0.1.0",
        "source-boundaries.md",
    ):
        assert phrase in normalized
