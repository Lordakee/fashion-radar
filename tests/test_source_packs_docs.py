from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE_PACKS_DOC = ROOT / "docs" / "source-packs.md"


def _read_source_packs_doc() -> str:
    return SOURCE_PACKS_DOC.read_text(encoding="utf-8")


def _normalized(text: str) -> str:
    return " ".join(text.split()).casefold()


def _section(text: str, heading: str) -> str:
    marker = f"## {heading}"
    assert marker in text
    return text.split(marker, 1)[1].split("\n## ", 1)[0]


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
        "it does not include google news rss, google trends, "
        "account-based source access, browser automation, access-control bypasses, "
        "paywall bypass, or private data collection.",
    ):
        assert phrase in normalized
