from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCHEDULING_DOC = ROOT / "docs" / "scheduling.md"


def _read_scheduling_doc() -> str:
    return SCHEDULING_DOC.read_text(encoding="utf-8")


def _normalized(text: str) -> str:
    return " ".join(text.split()).casefold()


def _section(text: str, heading: str) -> str:
    marker = f"## {heading}"
    assert marker in text
    return text.split(marker, 1)[1].split("\n## ", 1)[0]


def test_scheduling_docs_keep_local_serial_run_boundary() -> None:
    normalized = _normalized(_read_scheduling_doc())

    for phrase in (
        "does not run a background daemon",
        "run the existing serial command",
        "`run` executes `collect -> match -> report` in one local process",
        "do not schedule overlapping runs against the same sqlite database",
        "if a previous run is still active, wait for it to finish",
    ):
        assert phrase in normalized


def test_scheduling_docs_keep_local_digest_handoff_boundary() -> None:
    normalized = _normalized(_read_scheduling_doc())

    for phrase in (
        "write local files such as `latest.md`, `latest.json`, and `report-index.json`",
        "do not send email, call webhooks, open a browser, or install a notification daemon",
        "local `.eml` handoff file",
        "you review yourself",
    ):
        assert phrase in normalized


def test_scheduling_docs_keep_schedule_example_print_only_boundary() -> None:
    examples_section = _section(_read_scheduling_doc(), "Generate Examples")
    normalized = _normalized(examples_section)

    for phrase in (
        "use `schedule-example` to print snippets",
        "does not install anything",
    ):
        assert phrase in normalized
