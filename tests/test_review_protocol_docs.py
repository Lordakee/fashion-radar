from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
AGENTS = ROOT / "AGENTS.md"
REVIEW_PROTOCOL = ROOT / "docs" / "REVIEW_PROTOCOL.md"
UPLOAD_CHECKLIST = ROOT / "docs" / "github-upload-checklist.md"

ACTIVE_REVIEW_DOCS = [
    AGENTS,
    REVIEW_PROTOCOL,
    UPLOAD_CHECKLIST,
]

FORBIDDEN_ACTIVE_REVIEW_TERMS = (
    "local opencode",
    "opencode run",
    "zhipuai-coding-plan/glm-5.2",
    "GLM 5.2",
    "docs/reviews/opencode-stage-N",
)


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _section(text: str, heading: str) -> str:
    return text.split(f"## {heading}", 1)[1].split("\n## ", 1)[0]


def test_active_review_docs_use_claude_code_not_opencode() -> None:
    failures: list[str] = []

    for path in ACTIVE_REVIEW_DOCS:
        text = _read(path)
        for term in FORBIDDEN_ACTIVE_REVIEW_TERMS:
            if term in text:
                failures.append(f"{path.relative_to(ROOT)} still contains {term!r}")

    assert not failures, "\n".join(failures)


def test_active_review_protocol_documents_claude_code_gate() -> None:
    agents_text = _read(AGENTS)
    protocol_text = _read(REVIEW_PROTOCOL)
    naming_section = _section(protocol_text, "Review Record Naming")
    checklist_text = _read(UPLOAD_CHECKLIST)

    assert "Claude Code" in agents_text
    assert "--effort max" in agents_text
    assert "claude --effort max --permission-mode plan --no-session-persistence" in protocol_text

    review_record_names = (
        "claude-code-stage-N-plan-review.md",
        "claude-code-stage-N-code-review.md",
        "claude-code-stage-N-release-review.md",
    )
    for record_name in review_record_names:
        assert record_name in naming_section

    assert (
        naming_section.index(review_record_names[0])
        < naming_section.index(review_record_names[1])
        < naming_section.index(review_record_names[2])
    )

    rereview_record_names = (
        "claude-code-stage-N-plan-rereview.md",
        "claude-code-stage-N-code-rereview.md",
        "claude-code-stage-N-release-rereview.md",
    )
    for record_name in rereview_record_names:
        assert record_name in naming_section

    assert (
        naming_section.index(rereview_record_names[0])
        < naming_section.index(rereview_record_names[1])
        < naming_section.index(rereview_record_names[2])
    )

    assert "claude --effort max --permission-mode plan --no-session-persistence" in checklist_text
