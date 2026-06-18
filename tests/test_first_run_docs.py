from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FIRST_RUN_DOC = ROOT / "docs" / "first-run.md"


def _read_first_run_doc() -> str:
    return FIRST_RUN_DOC.read_text(encoding="utf-8")


def _normalized(text: str) -> str:
    return " ".join(text.split()).casefold()


def _section(text: str, heading: str) -> str:
    marker = f"## {heading}"
    assert marker in text
    return text.split(marker, 1)[1].split("\n## ", 1)[0]


def test_first_run_docs_keep_local_sample_boundary() -> None:
    boundary = _section(_read_first_run_doc(), "Boundary")
    normalized = _normalized(boundary)

    for phrase in (
        "first-run sample does not run live collection",
        "automated smoke does not run `collect`, `run`, or `dashboard`",
        "should not create files under repo `data/` or `reports/`",
        "does not perform browser automation, account login, cookies/sessions",
        "source/platform connectors, scraping, platform automation, monitoring",
        "scheduling, or external services",
        "candidate and trend outputs are local sample content checks from the checked-in example",
        "not proof of demand",
        "not platform coverage",
        "not source ranking",
    ):
        assert phrase in normalized
