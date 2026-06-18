from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SECURITY_DOC = ROOT / "SECURITY.md"


def _read_security_doc() -> str:
    return SECURITY_DOC.read_text(encoding="utf-8")


def _normalized(text: str) -> str:
    return " ".join(text.split()).casefold()


def _section(text: str, heading: str) -> str:
    marker = f"## {heading}"
    assert marker in text
    return text.split(marker, 1)[1].split("\n## ", 1)[0]


def test_security_docs_keep_redaction_boundary() -> None:
    redaction = _section(_read_security_doc(), "Redaction")
    normalized = _normalized(redaction)

    for phrase in (
        "When reporting:",
        "replace tokens, cookies, and secrets with `[REDACTED]`",
        "redact private URLs and local paths if needed",
        "trim logs to the relevant error",
        "do not attach SQLite databases, generated reports, browser profiles, "
        "or account/session files",
    ):
        assert phrase.casefold() in normalized
