from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANUAL_SIGNAL_IMPORT_DOC = ROOT / "docs" / "manual-signal-import.md"


def _read_manual_signal_import_doc() -> str:
    return MANUAL_SIGNAL_IMPORT_DOC.read_text(encoding="utf-8")


def _normalized(text: str) -> str:
    return " ".join(text.split()).casefold()


def _section(text: str, heading: str) -> str:
    marker = f"## {heading}"
    assert marker in text
    return text.split(marker, 1)[1].split("\n## ", 1)[0]


def test_manual_signal_import_docs_keep_privacy_boundary() -> None:
    privacy_boundary = _section(_read_manual_signal_import_doc(), "Privacy Boundary")
    normalized = _normalized(privacy_boundary)

    for phrase in (
        "do not import private comments",
        "account ids",
        "cookies",
        "author profiles",
        "follower lists",
        "images, videos",
        "private or sensitive material",
        "keep imported rows limited to conservative metadata",
        "allowed to process and review locally",
    ):
        assert phrase in normalized
