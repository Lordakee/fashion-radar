from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DAILY_DIGEST_DOC = ROOT / "docs" / "daily-digest.md"


def _read_daily_digest_doc() -> str:
    return DAILY_DIGEST_DOC.read_text(encoding="utf-8")


def _normalized(text: str) -> str:
    return " ".join(text.split()).casefold()


def test_daily_digest_docs_keep_local_file_only_boundary() -> None:
    normalized = _normalized(_read_daily_digest_doc())

    for phrase in (
        "reads only the markdown and json report files",
        "does not collect sources",
        "open sqlite",
        "send email",
        "call webhooks",
        "open a browser",
        "install a notification daemon",
        "generated locally inside the configured reports directory",
    ):
        assert phrase in normalized


def test_daily_digest_docs_keep_eml_manual_review_boundary() -> None:
    normalized = _normalized(_read_daily_digest_doc())

    for phrase in (
        "write a local `.eml` file for manual review",
        "has no `to`, `cc`, or `bcc` headers",
        "fashion radar never sends it",
        "review source attribution",
        "before sharing a report or `.eml` file",
    ):
        assert phrase in normalized


def test_daily_digest_docs_keep_review_boundary_section() -> None:
    text = _read_daily_digest_doc()
    review_boundary = text.split("## Review Boundary", 1)[1]
    normalized = _normalized(review_boundary)

    for phrase in (
        "local observed signals",
        "configured source set",
        "imported local signals",
        "review aids",
        "not claims about demand outside that source set",
    ):
        assert phrase in normalized


def test_daily_digest_docs_note_brief_is_existing_report_content() -> None:
    normalized = _normalized(_read_daily_digest_doc())

    assert "daily brief" in normalized
    assert "daily brief is already-generated report content" in normalized
    assert "not a sending or llm summarization feature" in normalized
