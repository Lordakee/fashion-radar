from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
AGENTS = ROOT / "AGENTS.md"
REVIEW_PROTOCOL = ROOT / "docs" / "REVIEW_PROTOCOL.md"
UPLOAD_CHECKLIST = ROOT / "docs" / "github-upload-checklist.md"
FULL_PROJECT_REVIEW = ROOT / "docs" / "reviews" / "opencode-full-project-review.md"

ACTIVE_REVIEW_DOCS = [
    AGENTS,
    REVIEW_PROTOCOL,
    UPLOAD_CHECKLIST,
]

ACTIVE_OPENCODE_COMMAND = "opencode run --model zhipuai-coding-plan/glm-5.2 --variant max"
OPTIONAL_CLAUDE_CODE_COMMAND = "claude --effort max --permission-mode plan --no-session-persistence"
REVIEW_CAPTURE_HYGIENE_REQUIRED_PHRASES = (
    "review capture hygiene",
    "capture the completed reviewer output",
    "directly into the target review record",
    "do not commit live-capture stubs",
    "do not commit tool status lines such as `Wrote`",
    "one coherent review body",
    "one verdict",
    "do not duplicate approval phrases",
    "if the review times out, record the timeout honestly",
)


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _section(text: str, heading: str) -> str:
    return text.split(f"## {heading}", 1)[1].split("\n## ", 1)[0]


def _normalized_text(text: str) -> str:
    return " ".join(text.split())


DIRECT_OPENCODE_REVIEW_REDIRECT = re.compile(
    r"opencode\s+run\b[^\n]*(?:\\\n[^\n]*)*"
    r"\s(?:&>>|&>|1>>|1>|>>|>)\s*(?:\\\n\s*)?"
    r"[\"']?(?:\./)?docs/reviews/opencode-stage-N-"
    r"(?:plan|code|release)-(?:review|rereview)\.md[\"']?",
    re.IGNORECASE,
)


def _direct_opencode_review_redirect(text: str) -> re.Match[str] | None:
    return DIRECT_OPENCODE_REVIEW_REDIRECT.search(text)


def test_direct_opencode_review_redirect_regex_catches_shell_variants() -> None:
    command = "opencode run --model zhipuai-coding-plan/glm-5.2 --variant max"
    unsafe_examples = (
        f"{command} >docs/reviews/opencode-stage-N-plan-review.md",
        f"{command} >> docs/reviews/opencode-stage-N-code-rereview.md",
        f'{command} 1> "./docs/reviews/opencode-stage-N-release-review.md"',
        f"{command} &> 'docs/reviews/opencode-stage-N-plan-rereview.md'",
        f'{command} \\\n  --dir /home/ubuntu/fashion-radar "prompt" '
        "> docs/reviews/opencode-stage-N-release-review.md",
    )
    for example in unsafe_examples:
        assert _direct_opencode_review_redirect(example), example

    safe_example = """tmp_review="$(mktemp)"
opencode run --model zhipuai-coding-plan/glm-5.2 --variant max \\
  --dir /home/ubuntu/fashion-radar "prompt" > "$tmp_review"
sed -n '1,260p' "$tmp_review"
cp "$tmp_review" docs/reviews/opencode-stage-N-release-review.md
"""
    assert not _direct_opencode_review_redirect(safe_example)


def test_active_review_docs_document_local_opencode_gate() -> None:
    failures: list[str] = []

    for path in ACTIVE_REVIEW_DOCS:
        normalized = _normalized_text(_read(path))
        normalized_lower = normalized.casefold()
        for term in (
            "local opencode",
            ACTIVE_OPENCODE_COMMAND,
            "zhipuai-coding-plan/glm-5.2",
            "--variant max",
            "docs/reviews/opencode-stage-N",
        ):
            if term.casefold() not in normalized_lower:
                failures.append(f"{path.relative_to(ROOT)} is missing {term!r}")

    assert not failures, "\n".join(failures)


def test_active_review_protocol_documents_opencode_gate_and_claude_alternate() -> None:
    agents_text = _read(AGENTS)
    protocol_text = _read(REVIEW_PROTOCOL)
    naming_section = _section(protocol_text, "Review Record Naming")
    checklist_text = _read(UPLOAD_CHECKLIST)
    normalized_protocol = _normalized_text(protocol_text)
    normalized_checklist = _normalized_text(checklist_text)

    assert ACTIVE_OPENCODE_COMMAND in _normalized_text(agents_text)
    assert "reasoning effort to `xhigh`" in _normalized_text(agents_text)
    assert ACTIVE_OPENCODE_COMMAND in normalized_protocol
    assert ACTIVE_OPENCODE_COMMAND in normalized_checklist
    assert OPTIONAL_CLAUDE_CODE_COMMAND in normalized_protocol
    assert "optional alternate" in normalized_protocol.casefold()
    assert "historical audit records" not in protocol_text
    assert "older `opencode-*` records" not in protocol_text

    review_record_names = (
        "opencode-stage-N-plan-review.md",
        "opencode-stage-N-code-review.md",
        "opencode-stage-N-release-review.md",
    )
    for record_name in review_record_names:
        assert record_name in naming_section

    assert (
        naming_section.index(review_record_names[0])
        < naming_section.index(review_record_names[1])
        < naming_section.index(review_record_names[2])
    )

    rereview_record_names = (
        "opencode-stage-N-plan-rereview.md",
        "opencode-stage-N-code-rereview.md",
        "opencode-stage-N-release-rereview.md",
    )
    for record_name in rereview_record_names:
        assert record_name in naming_section

    assert (
        naming_section.index(rereview_record_names[0])
        < naming_section.index(rereview_record_names[1])
        < naming_section.index(rereview_record_names[2])
    )

    optional_claude_names = (
        "claude-code-stage-N-plan-review.md",
        "claude-code-stage-N-code-review.md",
        "claude-code-stage-N-release-review.md",
        "claude-code-stage-N-plan-rereview.md",
        "claude-code-stage-N-code-rereview.md",
        "claude-code-stage-N-release-rereview.md",
    )
    for record_name in optional_claude_names:
        assert record_name in protocol_text


def test_review_protocol_docs_document_capture_hygiene() -> None:
    agents_text = _read(AGENTS)
    protocol_text = _read(REVIEW_PROTOCOL)
    checklist_text = _read(UPLOAD_CHECKLIST)
    agents_section = _section(agents_text, "Review Gates")
    assert "## Review Capture Hygiene" in protocol_text
    protocol_section = _section(protocol_text, "Review Capture Hygiene")
    checklist_section = _section(checklist_text, "Final Review")
    failures: list[str] = []

    for label, text in (
        ("docs/REVIEW_PROTOCOL.md##Review Capture Hygiene", protocol_section),
        ("docs/github-upload-checklist.md##Final Review", checklist_section),
    ):
        normalized = _normalized_text(text).casefold()
        for phrase in REVIEW_CAPTURE_HYGIENE_REQUIRED_PHRASES:
            if phrase.casefold() not in normalized:
                failures.append(f"{label} is missing {phrase!r}")

    assert "opencode-stage-N-plan-review.md" in protocol_section
    assert "opencode-stage-N-code-review.md" in protocol_section
    assert "opencode-stage-N-release-review.md" in protocol_section
    assert "opencode-stage-N-release-review.md" in checklist_section
    redirect_failures: list[str] = []
    for path in ACTIVE_REVIEW_DOCS:
        text = _read(path)
        if match := _direct_opencode_review_redirect(text):
            redirect_failures.append(
                f"{path.relative_to(ROOT)} documents direct opencode final-file "
                f"redirection: {match.group(0)!r}"
            )

    assert not redirect_failures, "\n".join(redirect_failures)
    normalized_agents = _normalized_text(agents_section).casefold()
    for phrase in (
        "completed review output",
        "live-capture stubs",
        "duplicated or truncated text",
        "tool-status messages",
        "empty output",
    ):
        assert phrase.casefold() in normalized_agents
    assert not failures, "\n".join(failures)


def test_full_project_review_follow_up_status_tracks_completed_stages() -> None:
    text = _read(FULL_PROJECT_REVIEW)
    status = _section(text, "Current Follow-Up Status")
    normalized = _normalized_text(status).casefold()

    for phrase in (
        "Stage 188 fixed the proxy-sensitive tests and redirected roadmap docs.",
        "Stage 189 fixed review-capture hygiene gaps",
        "Stage 190 added source-liveness diagnostics for configured public sources.",
        "Stage 191 added the Daily Brief Heat Narrative",
        "source coverage",
        "matching quality",
        "trend/heat explanation",
    ):
        assert phrase.casefold() in normalized

    assert "is intended to" not in normalized
    assert "next product node should implement source-liveness diagnostics" not in normalized
