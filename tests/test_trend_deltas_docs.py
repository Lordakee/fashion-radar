from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TREND_DELTAS_DOC = ROOT / "docs" / "trend-deltas.md"


def _read_trend_deltas_doc() -> str:
    return TREND_DELTAS_DOC.read_text(encoding="utf-8")


def _normalized(text: str) -> str:
    return " ".join(text.split()).casefold()


def _section(text: str, heading: str) -> str:
    marker = f"## {heading}"
    assert marker in text
    return text.split(marker, 1)[1].split("\n## ", 1)[0]


def test_trend_deltas_docs_keep_what_is_compared_boundary() -> None:
    what_is_compared = _section(_read_trend_deltas_doc(), "What Is Compared")
    normalized = _normalized(what_is_compared)

    for phrase in (
        "Entity deltas reuse the same local heat scoring used by reports.",
        "Candidate deltas reuse candidate discovery snapshots.",
        "configured `candidate_discovery` settings",
        "not a complete raw phrase inventory.",
        "`current_mentions` is the current comparison snapshot's current-window mention count.",
        "`baseline_mentions` is the baseline comparison snapshot's current-window mention count.",
        "Scoring's internal baseline-window counts are exposed only as "
        "`current_internal_baseline_mentions` and "
        "`baseline_internal_baseline_mentions`.",
        "Existing signals are labeled `rising` or `cooling` only when score and "
        "mention movement agree.",
        "Mixed-direction movement is `stable`.",
        "These statuses are local observed signals for review, not market-wide rankings.",
    ):
        assert phrase.casefold() in normalized


def test_trend_deltas_docs_note_heat_narrative_remains_review_oriented() -> None:
    heat_narrative = _section(_read_trend_deltas_doc(), "Heat Narrative")
    normalized = _normalized(heat_narrative)

    assert "heat narrative" in normalized
    assert "local observed" in normalized
    assert "review-oriented" in normalized
    assert "configured sources and imported local signals" in normalized
    assert "needs review" in normalized
    assert "it provides no demand proof and no platform coverage verification." in normalized
    assert "market-wide ranking" not in normalized
