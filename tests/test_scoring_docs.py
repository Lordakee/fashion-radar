from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCORING_DOC = ROOT / "docs" / "scoring.md"


def _read_scoring_doc() -> str:
    return SCORING_DOC.read_text(encoding="utf-8")


def _normalized(text: str) -> str:
    return " ".join(text.split()).casefold()


def _section(text: str, heading: str) -> str:
    marker = f"## {heading}"
    assert marker in text
    return text.split(marker, 1)[1].split("\n## ", 1)[0]


def test_scoring_docs_keep_limits_boundary() -> None:
    limits = _section(_read_scoring_doc(), "Limits")
    normalized = _normalized(limits)

    for phrase in (
        "Scores only reflect configured sources and imported local signals.",
        "Candidate signals only reflect configured sources and imported local signals.",
        "Trend deltas only reflect configured sources and imported local signals.",
        "Candidate deltas are limited by configured candidate discovery thresholds.",
        "Counts use collected time, not necessarily publication time.",
        "Dashboard mention tabs show mention counts, while candidate signal views read "
        "the latest report JSON.",
        "There is no image/video or external engagement analysis in v0.1.0.",
    ):
        assert phrase.casefold() in normalized


def test_scoring_docs_explain_candidate_score_components() -> None:
    candidate_signals = _section(_read_scoring_doc(), "Candidate Signals")
    normalized = _normalized(candidate_signals)

    for phrase in (
        "weighted_mention_component",
        "growth_component",
        "source_diversity_component",
        "not demand proof",
        "not platform coverage verification",
        "candidate score components intentionally omit the tracked-entity high-weight source term.",
    ):
        assert phrase in normalized
