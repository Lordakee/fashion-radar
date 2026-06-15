from __future__ import annotations

import re
import shlex
from pathlib import Path

import typer.main
from typer.testing import CliRunner

from fashion_radar.cli import app

ROOT = Path(__file__).resolve().parents[1]
CLI_REFERENCE = ROOT / "docs" / "cli-reference.md"
UPLOAD_CHECKLIST = ROOT / "docs" / "github-upload-checklist.md"
README = ROOT / "README.md"
CI_WORKFLOW = ROOT / ".github" / "workflows" / "ci.yml"

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


def _readme_quickstart_commands() -> list[str]:
    text = _read(README)
    assert "## Quickstart" in text
    quickstart = text.split("## Quickstart", 1)[1].split("\n## ", 1)[0]
    return [command for block in _bash_blocks(quickstart) for command in _shell_commands(block)]


def _quickstart_fashion_radar_commands(names: set[str]) -> list[str]:
    commands: list[str] = []
    for command in _readme_quickstart_commands():
        match = FASHION_RADAR_COMMAND_RE.search(command)
        if match is not None and match.group("name") in names:
            commands.append(command)
    return commands


def _quickstart_cli_args(command: str, tmp_path: Path) -> list[str]:
    match = FASHION_RADAR_COMMAND_RE.search(command)
    assert match is not None
    command_name = match.group("name")
    assert '--data-dir "$PWD/data"' in command
    if command_name in {"init", "doctor"}:
        assert '--config-dir "$PWD/configs"' in command
        assert '--reports-dir "$PWD/reports"' in command
    parts = [part.replace("$PWD", str(tmp_path)) for part in shlex.split(command)]
    assert parts[:3] == ["uv", "run", "fashion-radar"]
    return parts[3:]


def test_cli_reference_lists_every_public_command() -> None:
    text = _read(CLI_REFERENCE)

    for command in _public_cli_commands():
        assert f"`{command}`" in text

    assert "FASHION_RADAR_CONFIG_DIR" in text
    assert "FASHION_RADAR_DATA_DIR" in text
    assert "FASHION_RADAR_REPORTS_DIR" in text


def test_upload_checklist_help_loop_matches_public_commands() -> None:
    assert _upload_checklist_help_loop_commands() == _public_cli_commands()


def test_package_archive_smoke_command_is_documented_and_in_ci() -> None:
    checklist = _read(UPLOAD_CHECKLIST)
    ci_workflow = _read(CI_WORKFLOW)
    hygiene_command = "UV_NO_CONFIG=1 uv run python scripts/check_release_hygiene.py --repo-root ."
    build_command = 'UV_NO_CONFIG=1 uv build --out-dir "$tmp_build"'
    archive_command = 'UV_NO_CONFIG=1 uv run python scripts/check_package_archives.py "$tmp_build"'
    module_help_command = '"$tmp_env/venv/bin/python" -m fashion_radar --help'

    for text in (checklist, ci_workflow):
        assert hygiene_command in text
        assert build_command in text
        assert archive_command in text
        assert module_help_command in text
        assert "scripts/check_release_hygiene.py" in text
        assert "scripts/check_package_archives.py" in text


def test_first_run_smoke_command_is_documented_and_in_ci() -> None:
    checklist = _read(UPLOAD_CHECKLIST)
    ci_workflow = _read(CI_WORKFLOW)
    readme = _read(README)
    source_command = "UV_NO_CONFIG=1 uv run python scripts/check_first_run_smoke.py --repo-root ."
    installed_command = (
        '"$tmp_env/venv/bin/python" scripts/check_first_run_smoke.py --repo-root . '
        '--python "$tmp_env/venv/bin/python" --installed'
    )

    for text in (checklist, ci_workflow, readme):
        assert source_command in text
        assert "scripts/check_first_run_smoke.py" in text

    for text in (checklist, ci_workflow, readme):
        assert installed_command in text


def test_upload_checklist_documents_release_hygiene_excludes() -> None:
    text = _read(UPLOAD_CHECKLIST)

    for term in (
        ".env.local",
        "cookies",
        "account/session files",
        "private source exports",
        ".codegraph",
        "generated runtime configs",
        "local SQLite databases",
        "local credential config",
    ):
        assert term in text


def test_readme_links_current_cli_reference_not_historical_release_gate() -> None:
    text = _read(README)

    assert "[docs/cli-reference.md](docs/cli-reference.md)" in text
    assert "docs/release-gate-stage31.md" not in text


def test_readme_distinguishes_source_checkout_from_package_smoke() -> None:
    text = _read(README)

    assert "source checkout" in text
    assert "local wheel" in text
    assert "does not publish to PyPI" in text
    assert "[docs/github-upload-checklist.md](docs/github-upload-checklist.md)" in text


def test_readme_documents_manual_sample_flow_and_automated_smoke_boundary() -> None:
    text = _read(README)

    for term in (
        "Manual Repo-Local Sample Flow",
        "manual flow writes to the repo-local `data/` and `reports/` directories",
        'AS_OF="2026-06-13T12:00:00Z"',
        "examples/community-signals.example.csv",
        "community-candidates examples/community-signals.example.csv",
        "import-signals examples/community-signals.example.csv",
        "reports/fashion-radar-2026-06-13.md",
        "reports/fashion-radar-2026-06-13.json",
        "Automated First-Run Smoke",
        "source checkout",
        "installed wheel",
        "--installed",
        "temporary config, data,",
        "report, and export directories",
        "should not create files under repo `data/` or `reports/`",
        "does not run live collection",
    ):
        assert term in text


def test_community_import_docs_promote_checked_in_example_import() -> None:
    text = _read(ROOT / "docs" / "community-signal-import.md")

    assert 'AS_OF="2026-06-13T12:00:00Z"' in text
    assert "import-signals examples/community-signals.example.csv" in text
    assert "community-candidates examples/community-signals.example.csv" in text
    assert 'tmp_run="$(mktemp -d)"' in text
    assert (
        'cp examples/community-signals.example.csv "$tmp_run/exports/community-signals.csv"' in text
    )


def test_community_import_docs_keep_deterministic_review_commands_fixed() -> None:
    text = _read(ROOT / "docs" / "community-signal-import.md")
    review_section = text.split("## Review After Import", 1)[1].split("## Boundary", 1)[0]

    assert 'AS_OF="2026-06-13T12:00:00Z"' in review_section
    assert "$(date -u" not in review_section

    deterministic_markers = (
        "examples/community-signals.example.csv",
        '"$tmp_run/exports"',
    )
    community_doc = ROOT / "docs" / "community-signal-import.md"
    for command in _fashion_radar_commands(community_doc):
        if any(marker in command for marker in deterministic_markers):
            assert "$(date -u" not in command


def test_readme_quickstart_setup_commands_use_repo_local_paths() -> None:
    setup_commands = _quickstart_fashion_radar_commands({"init", "migrate-db", "doctor"})

    command_names = [
        FASHION_RADAR_COMMAND_RE.search(command).group("name") for command in setup_commands
    ]
    assert command_names == ["init", "migrate-db", "doctor"]
    for command in setup_commands:
        match = FASHION_RADAR_COMMAND_RE.search(command)
        assert match is not None
        command_name = match.group("name")
        assert '--data-dir "$PWD/data"' in command
        if command_name in {"init", "doctor"}:
            assert '--config-dir "$PWD/configs"' in command
            assert '--reports-dir "$PWD/reports"' in command


def test_readme_quickstart_setup_commands_smoke(tmp_path: Path) -> None:
    setup_commands = _quickstart_fashion_radar_commands({"init", "migrate-db", "doctor"})
    runner = CliRunner()

    for command in setup_commands:
        result = runner.invoke(app, _quickstart_cli_args(command, tmp_path))
        assert result.exit_code == 0, result.output

    config_dir = tmp_path / "configs"
    data_dir = tmp_path / "data"
    reports_dir = tmp_path / "reports"
    doctor_args = _quickstart_cli_args(setup_commands[-1], tmp_path)
    doctor_result = runner.invoke(app, doctor_args)
    assert doctor_result.exit_code == 0, doctor_result.output
    assert f"Configuration directory: {config_dir}" in doctor_result.output
    assert f"Data directory: {data_dir}" in doctor_result.output
    assert f"Reports directory: {reports_dir}" in doctor_result.output
    assert (config_dir / "sources.yaml").exists()
    assert (config_dir / "entities.yaml").exists()
    assert (config_dir / "scoring.yaml").exists()
    assert (data_dir / "fashion-radar.sqlite").exists()
    assert reports_dir.exists()
    assert not any(reports_dir.iterdir())


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
