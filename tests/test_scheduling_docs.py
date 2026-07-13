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


def test_scheduling_docs_keep_row_one_refresh_retention_boundary() -> None:
    row_one_section = _section(_read_scheduling_doc(), "ROW ONE Daily Site")
    normalized = _normalized(row_one_section)

    for phrase in (
        "row one scheduled refresh runs the single refresh command",
        "the command is `fashion-radar row-one refresh`",
        "prunes stale dated report and site artifacts",
        (
            "by default, it also prunes sqlite items older than the retention window after "
            "generating the current edition"
        ),
        "the default row one sqlite item retention window is 1 day",
        (
            "standalone `fashion-radar clean-old-data` remains for manual or "
            "non-row one data retention"
        ),
    ):
        assert phrase in normalized

    assert "--latest-only" not in row_one_section
    assert "fashion-radar run" not in row_one_section
    assert "leaves all sqlite cleanup entirely to clean-old-data" not in normalized
    assert (
        "a non-skipped sqlite retention failure returns a nonzero exit status after report "
        "and site output is written." in normalized
    )


def test_scheduling_docs_describe_stage_389_row_one_systemd_operations() -> None:
    row_one_section = _section(_read_scheduling_doc(), "ROW ONE Daily Site")
    normalized = _normalized(row_one_section)

    for phrase in (
        "`row-one schedule --mode systemd`",
        "`row-one install-local`",
        "`row-one-refresh.service`",
        "`row-one-refresh.timer`",
        "`row-one-serve.service`",
        "fashion radar does not invoke `systemctl` or `loginctl`",
        "unattended user-systemd operation requires manual lingering verification",
        "an authorized operator may be needed to enable lingering under host policy",
        'loginctl show-user "$user" -p linger',
        'loginctl enable-linger "$user"',
        "systemctl --user daemon-reload",
        "systemctl --user enable --now row-one-refresh.timer",
        "systemctl --user enable --now row-one-serve.service",
        "systemctl --user status row-one-refresh.timer row-one-serve.service",
        "--host",
        "--port",
    ):
        assert phrase in normalized
