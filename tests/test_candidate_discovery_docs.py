from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CANDIDATE_DISCOVERY_DOC = ROOT / "docs" / "candidate-discovery.md"


def _read_candidate_discovery_doc() -> str:
    return CANDIDATE_DISCOVERY_DOC.read_text(encoding="utf-8")


def _normalized(text: str) -> str:
    return " ".join(text.split()).casefold()


def _section(text: str, heading: str) -> str:
    marker = f"## {heading}"
    assert marker in text
    return text.split(marker, 1)[1].split("\n## ", 1)[0]


def test_candidate_discovery_docs_keep_no_source_expansion_boundary() -> None:
    boundaries = _section(_read_candidate_discovery_doc(), "Boundaries")
    normalized = _normalized(boundaries)

    for phrase in (
        "candidate discovery adds no collectors",
        "no new source types",
        "no external inference calls",
        "no background network reads",
        "configured sources and imported local signals",
        "observed phrases that need review",
    ):
        assert phrase in normalized


def test_candidate_discovery_docs_explain_report_score_components() -> None:
    reports = _section(_read_candidate_discovery_doc(), "Reports And Dashboard")
    normalized = _normalized(reports)

    for phrase in (
        "candidate score components",
        "mentions, growth, and source-diversity terms",
        "local observed review aids",
    ):
        assert phrase in normalized
