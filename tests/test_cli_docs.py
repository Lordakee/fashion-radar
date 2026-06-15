from __future__ import annotations

import re
from pathlib import Path

import typer.main

from fashion_radar.cli import app

ROOT = Path(__file__).resolve().parents[1]
CLI_REFERENCE = ROOT / "docs" / "cli-reference.md"
UPLOAD_CHECKLIST = ROOT / "docs" / "github-upload-checklist.md"
README = ROOT / "README.md"

PATH_CONSISTENCY_DOCS = [
    ROOT / "README.md",
    ROOT / "docs" / "cli-reference.md",
    ROOT / "docs" / "manual-signal-import.md",
    ROOT / "docs" / "community-signal-import.md",
    ROOT / "docs" / "architecture.md",
    ROOT / "docs" / "trend-deltas.md",
    ROOT / "docs" / "candidate-discovery.md",
    ROOT / "docs" / "daily-digest.md",
    ROOT / "docs" / "scheduling.md",
    ROOT / "docs" / "data-retention.md",
    ROOT / "docs" / "entity-packs.md",
    ROOT / "docs" / "source-packs.md",
]

REQUIRED_FLAGS_BY_COMMAND = {
    "match": ("--config-dir", "--data-dir"),
    "report": ("--config-dir", "--data-dir", "--reports-dir", "--as-of"),
    "run": ("--config-dir", "--data-dir", "--reports-dir", "--as-of"),
    "candidates": ("--config-dir", "--data-dir", "--as-of"),
    "trends": ("--config-dir", "--data-dir", "--as-of"),
    "clean-old-data": ("--data-dir",),
}

FASHION_RADAR_COMMAND_RE = re.compile(
    r"(?:^|\s)"
    r"(?:(?:\"[^\"]*/fashion-radar\")|(?:'[^']*/fashion-radar')|(?:\S*/fashion-radar)|fashion-radar)"
    r"\s+(?P<name>[a-z0-9-]+)"
)


def _public_cli_commands() -> list[str]:
    click_app = typer.main.get_command(app)
    return sorted(
        name
        for name, command in click_app.commands.items()
        if not getattr(command, "hidden", False)
    )


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _upload_checklist_help_loop_commands() -> list[str]:
    text = _read(UPLOAD_CHECKLIST)
    match = re.search(
        r"for cmd in \\\n(?P<body>.*?)\ndo\n"
        r'\s+"\$tmp_env/venv/bin/fashion-radar" "\$cmd" --help\n',
        text,
        flags=re.DOTALL,
    )
    assert match is not None, "Installed-wheel help loop not found"
    body = match.group("body").replace("\\", " ")
    return sorted(token for token in body.split() if token)


def _bash_blocks(text: str) -> list[str]:
    return re.findall(r"```bash\n(.*?)\n```", text, flags=re.DOTALL)


def _shell_commands(block: str) -> list[str]:
    commands: list[str] = []
    current: list[str] = []
    for raw_line in block.splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if current:
            current.append(line.removesuffix("\\").strip())
        else:
            current = [line.removesuffix("\\").strip()]
        if not line.endswith("\\"):
            commands.append(" ".join(part for part in current if part))
            current = []
    if current:
        commands.append(" ".join(part for part in current if part))
    return commands


def _fashion_radar_commands(path: Path) -> list[str]:
    commands: list[str] = []
    for block in _bash_blocks(_read(path)):
        for command in _shell_commands(block):
            if FASHION_RADAR_COMMAND_RE.search(command):
                commands.append(command)
    return commands


def test_cli_reference_lists_every_public_command() -> None:
    text = _read(CLI_REFERENCE)

    for command in _public_cli_commands():
        assert f"`{command}`" in text

    assert "FASHION_RADAR_CONFIG_DIR" in text
    assert "FASHION_RADAR_DATA_DIR" in text
    assert "FASHION_RADAR_REPORTS_DIR" in text


def test_upload_checklist_help_loop_matches_public_commands() -> None:
    assert _upload_checklist_help_loop_commands() == _public_cli_commands()


def test_readme_links_current_cli_reference_not_historical_release_gate() -> None:
    text = _read(README)

    assert "[docs/cli-reference.md](docs/cli-reference.md)" in text
    assert "docs/release-gate-stage31.md" not in text


def test_repo_local_operational_examples_keep_path_flags_together() -> None:
    failures: list[str] = []
    for path in PATH_CONSISTENCY_DOCS:
        for command in _fashion_radar_commands(path):
            if "--help" in command:
                continue
            match = FASHION_RADAR_COMMAND_RE.search(command)
            if match is None:
                continue
            command_name = match.group("name")
            required_flags = REQUIRED_FLAGS_BY_COMMAND.get(command_name)
            if required_flags is None:
                continue
            missing = [flag for flag in required_flags if flag not in command]
            if missing:
                relative_path = path.relative_to(ROOT)
                failures.append(f"{relative_path}: {command!r} missing {missing}")

    assert not failures, "\n".join(failures)
