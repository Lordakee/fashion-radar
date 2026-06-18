from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DASHBOARD_DOC = ROOT / "docs" / "dashboard.md"


def _read_dashboard_doc() -> str:
    return DASHBOARD_DOC.read_text(encoding="utf-8")


def _normalized(text: str) -> str:
    return " ".join(text.split()).casefold()


def test_dashboard_docs_keep_local_inspection_boundary() -> None:
    normalized = _normalized(_read_dashboard_doc())

    for phrase in (
        "optional streamlit app for inspecting local fashion radar state",
        "reads local sqlite/report state",
        "does not collect sources",
        "does not run entity matching",
        "does not generate reports",
        "does not make network requests on import or refresh",
    ):
        assert phrase in normalized


def test_dashboard_docs_keep_trend_readonly_boundary() -> None:
    normalized = _normalized(_read_dashboard_doc())

    for phrase in (
        "computes the trend deltas tab from existing local sqlite state",
        "not from external services",
        "trend reads verify schema read-only",
        "do not initialize, migrate, or write trend tables",
    ):
        assert phrase in normalized


def test_dashboard_docs_keep_local_security_boundary() -> None:
    normalized = _normalized(_read_dashboard_doc())

    for phrase in (
        "defaults to `127.0.0.1:8501`",
        "has no authentication layer",
        "intended for local use",
        "do not bind `--host 0.0.0.0`",
        "no scraping, no browser automation, no platform apis",
        "no account or cookie work",
    ):
        assert phrase in normalized


def test_dashboard_docs_keep_warning_and_staleness_boundary() -> None:
    normalized = _normalized(_read_dashboard_doc())

    for phrase in (
        "Invalid or missing trend config shows a concise dashboard warning without "
        "creating the data directory or database.",
        "If the local database has not been initialized or has no retained items, "
        "the tab shows an empty-state message without creating the data directory "
        "or database.",
        "Reads candidate signals from the latest report JSON when that file is available.",
        "The Candidate Signals tab reads the latest generated report JSON.",
        "If the latest report was generated before the latest collection, local "
        "import, or matching run, the tab may be stale until a new report is written.",
    ):
        assert phrase.casefold() in normalized
