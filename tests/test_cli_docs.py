from __future__ import annotations

import json
import re
import shlex
from pathlib import Path

import typer.main
from typer.testing import CliRunner

from fashion_radar.cli import app
from fashion_radar.community_handoff_manifest import build_community_handoff_manifest
from fashion_radar.community_signal_profile import build_community_signal_profile
from fashion_radar.dashboard.app import DASHBOARD_TAB_LABELS

ROOT = Path(__file__).resolve().parents[1]
CLI_REFERENCE = ROOT / "docs" / "cli-reference.md"
COMMUNITY_SIGNAL_IMPORT_DOC = ROOT / "docs" / "community-signal-import.md"
UPLOAD_CHECKLIST = ROOT / "docs" / "github-upload-checklist.md"
README = ROOT / "README.md"
TREND_DELTAS_DOC = ROOT / "docs" / "trend-deltas.md"
DASHBOARD_DOC = ROOT / "docs" / "dashboard.md"
ARCHITECTURE_DOC = ROOT / "docs" / "architecture.md"
SOURCE_BOUNDARIES_DOC = ROOT / "docs" / "source-boundaries.md"
ENTITY_PACKS_DOC = ROOT / "docs" / "entity-packs.md"
AGENTS_DOC = ROOT / "AGENTS.md"
CHANGELOG = ROOT / "CHANGELOG.md"
FIRST_RUN_DOC = ROOT / "docs" / "first-run.md"
CI_WORKFLOW = ROOT / ".github" / "workflows" / "ci.yml"
COMMUNITY_TOOL_HANDOFF_TEMPLATE_PATHS = (
    "examples/community-tool-handoff.example.csv",
    "examples/community-tool-handoff.example.json",
)
COMMUNITY_TOOL_HANDOFF_DIRECTORY_PATHS = (
    "examples/community-tool-handoff-directory.example/README.md",
    "examples/community-tool-handoff-directory.example/csv/community-tool-a.csv",
    "examples/community-tool-handoff-directory.example/csv/community-tool-b.csv",
    "examples/community-tool-handoff-directory.example/json/community-tool-a.json",
    "examples/community-tool-handoff-directory.example/json/community-tool-b.json",
)

PATH_CONSISTENCY_DOCS = [
    ROOT / "README.md",
    ROOT / "docs" / "first-run.md",
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
    "heat-movers": ("--config-dir", "--data-dir", "--as-of"),
    "trends": ("--config-dir", "--data-dir", "--as-of"),
    "clean-old-data": ("--data-dir",),
}

STAGE_DOCS_COMMANDS = (
    "external-tool-adapters",
    "external-tool-readiness",
    "external-tool-template",
    "external-tool-workflow",
    "heat-movers",
)
HEAT_MOVERS_MENTION_DOCS = (
    README,
    TREND_DELTAS_DOC,
    DASHBOARD_DOC,
    CLI_REFERENCE,
    ARCHITECTURE_DOC,
    UPLOAD_CHECKLIST,
    CHANGELOG,
)
HEAT_MOVERS_BOUNDARY_DOCS = (
    README,
    TREND_DELTAS_DOC,
    DASHBOARD_DOC,
    CLI_REFERENCE,
    ARCHITECTURE_DOC,
    SOURCE_BOUNDARIES_DOC,
    AGENTS_DOC,
)
HEAT_MOVERS_BOUNDARY_MENTION_DOCS = (
    UPLOAD_CHECKLIST,
    CHANGELOG,
)
HEAT_MOVERS_SECTION_DOCS = (
    README,
    TREND_DELTAS_DOC,
    DASHBOARD_DOC,
    CLI_REFERENCE,
    ARCHITECTURE_DOC,
    SOURCE_BOUNDARIES_DOC,
    AGENTS_DOC,
)
HEAT_MOVERS_REQUIRED_BOUNDARY_PHRASES = (
    "local observed heat movement",
    "configured source set",
    "configured sources and imported local signals",
    "needs review",
    "no demand proof",
    "no platform coverage verification",
)
HEAT_MOVERS_CLI_FLAGS = (
    "--config-dir",
    "--data-dir",
    "--as-of",
    "--baseline-as-of",
    "--limit",
    "--format",
    "--include-cooling",
)
HEAT_MOVERS_FORBIDDEN_POSITIVE_CLAIMS = (
    "hottest",
    "viral",
    "market-wide trend",
    "platform-wide popularity",
    "verified demand",
    "top social trend",
)
IMPORTED_REVIEW_WORKFLOW_DOCS = (
    README,
    ROOT / "docs" / "community-signal-import.md",
    CLI_REFERENCE,
    ARCHITECTURE_DOC,
    SOURCE_BOUNDARIES_DOC,
    UPLOAD_CHECKLIST,
    ROOT / "docs" / "manual-signal-import.md",
    ROOT / "docs" / "community-signal-quality.md",
    CHANGELOG,
)
IMPORTED_REVIEW_WORKFLOW_REQUIRED_PHRASES = (
    "imported-review-workflow",
    "read-only imported-candidates step",
    "candidate phrase review",
    "final read-only heat-movers step",
    "local observed heat movement",
    "configured sources and imported local signals",
    "no demand proof",
    "no platform coverage verification",
)
IMPORTED_ENTITY_EVIDENCE_DOCS = (
    README,
    CLI_REFERENCE,
    ROOT / "docs" / "community-signal-import.md",
    ROOT / "docs" / "community-signal-quality.md",
    SOURCE_BOUNDARIES_DOC,
    ARCHITECTURE_DOC,
    DASHBOARD_DOC,
    UPLOAD_CHECKLIST,
)
IMPORTED_ENTITY_EVIDENCE_BOUNDARY_MENTION_DOCS = (
    AGENTS_DOC,
    CHANGELOG,
)
IMPORTED_ENTITY_EVIDENCE_REQUIRED_PHRASES = (
    "imported-entity-evidence",
    "local read-only",
    "imported-only",
    "manual_import",
    "privacy-safe",
    "retained local rows",
    "review_imported_entity_evidence",
    "no scraping",
    "no browser automation",
    "no platform apis",
    "no account or cookie",
)
IMPORTED_ENTITY_EVIDENCE_SAFE_FIELDS = (
    "window",
    "id",
    "source_name",
    "title",
    "url",
    "published_at",
    "collected_at",
)

EXTERNAL_TOOL_WORKFLOW_STEP_NAMES = (
    "inspect_adapter_registry",
    "check_external_tool_readiness",
    "print_adapter_template_json",
    "print_signal_profile",
    "print_handoff_manifest",
    "print_handoff_workflow",
    "lint_export_directory",
    "preview_candidate_phrases",
    "review_handoff_readiness",
    "dry_run_directory_import",
    "import_directory_signals",
    "print_post_import_review",
)

EXTERNAL_TOOL_WORKFLOW_BOUNDARY_PHRASES = (
    "local",
    "print-only",
    "workflow metadata",
    "not importable handoff rows",
    "producer-facing wrapper around existing local commands",
    "sanitized CSV/JSON local file handoff",
    "user-controlled external/community tools",
    "inspect directories",
    "read handoff files",
    "import rows",
    "open SQLite",
    "create artifacts",
    "not platform collection",
    "no connectors",
    "no scraping",
    "no browser automation",
    "no platform APIs",
    "no monitoring",
    "no scheduling",
    "no source acquisition",
    "no demand proof",
    "no ranking",
    "no coverage verification",
)

EXTERNAL_TOOL_WORKFLOW_DOCS = (
    README,
    ROOT / "docs" / "community-signal-import.md",
    ROOT / "docs" / "community-signal-quality.md",
    CLI_REFERENCE,
    UPLOAD_CHECKLIST,
    ROOT / "docs" / "source-boundaries.md",
    ROOT / "docs" / "architecture.md",
    ROOT / "AGENTS.md",
    ROOT / "CHANGELOG.md",
)

EXTERNAL_TOOL_READINESS_DOCS = (
    README,
    CLI_REFERENCE,
    ROOT / "docs" / "community-signal-import.md",
    ROOT / "docs" / "community-signal-quality.md",
    ROOT / "docs" / "source-boundaries.md",
    ROOT / "docs" / "architecture.md",
    ROOT / "docs" / "github-upload-checklist.md",
    ROOT / "AGENTS.md",
    ROOT / "CHANGELOG.md",
)

EXTERNAL_TOOL_READINESS_BOUNDARY_PHRASES = (
    "local read-only",
    "command availability only",
    "user-controlled external/community tools",
    "sanitized CSV/JSON local file handoff",
    "no scraping",
    "no browser automation",
    "no platform APIs",
    "no account/session/cookie/token behavior",
    "no monitoring",
    "no scheduling",
    "no source acquisition",
    "no demand proof",
    "no ranking",
    "no coverage verification",
    "no compliance-review product feature",
)

EXTERNAL_TOOL_ADAPTER_DOC_ROWS = (
    "| `rednote_mcp` | Rednote MCP Export | `rednote` | `json` | `*.json` |",
    ("| `xiaohongshu_crawler` | Xiaohongshu Crawler Export | `xiaohongshu` | `csv` | `*.csv` |"),
    "| `instaloader` | Instaloader Export | `instagram` | `json` | `*.json` |",
    "| `tiktok_api` | TikTok-Api Export | `tiktok` | `json` | `*.json` |",
    "| `yt_dlp` | yt-dlp Metadata Export | `media` | `json` | `*.json` |",
    "| `x_search_export` | X Search Export | `x` | `csv` | `*.csv` |",
    ("| `generic_community_export` | Generic Community Export | `community` | `csv` | `*.csv` |"),
)

FIRST_RUN_EXTERNAL_ADAPTER_SMOKE_PHRASE = (
    "The automated first-run smoke also validates the external-tool adapter "
    "registry JSON contract from `external-tool-adapters --format json` across "
    "all seven adapters."
)

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


def _documented_public_cli_commands() -> list[str]:
    return sorted({*_public_cli_commands(), *STAGE_DOCS_COMMANDS})


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _normalized_doc_text(path: Path) -> str:
    return " ".join(_read(path).split())


def _normalized_text(text: str) -> str:
    return " ".join(text.split())


def _assert_markdown_link_to_path(text: str, path: str) -> None:
    assert re.search(
        rf"\[[^\]]+\]\((?:\.\./)?{re.escape(path)}\)",
        text,
    ), f"Missing markdown link for {path}"


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


def _markdown_section(text: str, heading: str) -> str:
    marker = f"\n{heading}\n"
    assert marker in f"\n{text}"
    return text.split(heading, 1)[1].split("\n## ", 1)[0]


def _markdown_section_matching_heading(text: str, heading_pattern: str) -> str:
    heading = re.search(
        rf"^(?P<marker>#+)\s+.*{heading_pattern}.*$",
        text,
        flags=re.IGNORECASE | re.MULTILINE,
    )
    assert heading is not None, f"Missing markdown heading matching {heading_pattern!r}"
    level = len(heading.group("marker"))
    rest = text[heading.end() :]
    next_heading = re.search(rf"^#{{1,{level}}}\s+", rest, flags=re.MULTILINE)
    end = heading.end() + next_heading.start() if next_heading is not None else len(text)
    return text[heading.start() : end]


def _heat_movers_section(path: Path) -> str:
    return _markdown_section_matching_heading(_read(path), r"heat[- ]movers?")


def _dashboard_current_tab_labels() -> list[str]:
    section = _markdown_section_matching_heading(_read(DASHBOARD_DOC), r"current tabs")
    return [
        line.removeprefix("- ").strip() for line in section.splitlines() if line.startswith("- ")
    ]


def _first_json_payload_from_section(text: str, heading: str) -> dict[str, object]:
    section = _markdown_section(text, heading)
    match = re.search(r"```json\n(?P<payload>.*?)\n```", section, flags=re.DOTALL)
    assert match is not None
    payload = json.loads(match.group("payload"))
    assert isinstance(payload, dict)
    return payload


def _first_run_setup_commands() -> list[str]:
    section = _markdown_section(_read(FIRST_RUN_DOC), "## Prepare A Source Checkout")
    return [
        command
        for block in _bash_blocks(section)
        for command in _shell_commands(block)
        if (match := FASHION_RADAR_COMMAND_RE.search(command)) is not None
        and match.group("name") in {"init", "migrate-db", "doctor"}
    ]


def _first_run_reset_commands() -> list[str]:
    section = _markdown_section(_read(FIRST_RUN_DOC), "## Reset The Repo-Local Sample")
    return [command for block in _bash_blocks(section) for command in _shell_commands(block)]


def _first_run_dashboard_commands() -> list[str]:
    section = _markdown_section(_read(FIRST_RUN_DOC), "## Inspect The Sample In The Dashboard")
    return [
        command
        for block in _bash_blocks(section)
        for command in _shell_commands(block)
        if (match := FASHION_RADAR_COMMAND_RE.search(command)) is not None
        and match.group("name") == "dashboard"
    ]


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
    normalized = _normalized_doc_text(CLI_REFERENCE)

    for command in _public_cli_commands():
        assert f"`{command}`" in text

    assert "FASHION_RADAR_CONFIG_DIR" in text
    assert "FASHION_RADAR_DATA_DIR" in text
    assert "FASHION_RADAR_REPORTS_DIR" in text
    assert "deterministic sample-output gate" in text
    assert "validates deterministic sample output content" in normalized


def test_upload_checklist_help_loop_matches_documented_commands() -> None:
    assert _upload_checklist_help_loop_commands() == _documented_public_cli_commands()


def test_heat_movers_public_docs_are_linked_and_bounded() -> None:
    for path in HEAT_MOVERS_MENTION_DOCS:
        assert "heat-movers" in _read(path), f"{path.relative_to(ROOT)} missing heat-movers"

    for path in HEAT_MOVERS_BOUNDARY_DOCS:
        section = _heat_movers_section(path)
        normalized = _normalized_text(section).casefold()
        for phrase in HEAT_MOVERS_REQUIRED_BOUNDARY_PHRASES:
            assert phrase in normalized, f"{path.relative_to(ROOT)} missing {phrase!r}"

    for path in HEAT_MOVERS_BOUNDARY_MENTION_DOCS:
        normalized = _normalized_text(_read(path)).casefold()
        for phrase in HEAT_MOVERS_REQUIRED_BOUNDARY_PHRASES:
            assert phrase in normalized, f"{path.relative_to(ROOT)} missing {phrase!r}"


def test_heat_movers_sections_do_not_make_positive_scope_claims() -> None:
    for path in HEAT_MOVERS_SECTION_DOCS:
        section = _heat_movers_section(path)
        normalized = _normalized_text(section).casefold()
        for claim in HEAT_MOVERS_FORBIDDEN_POSITIVE_CLAIMS:
            assert claim not in normalized, f"{path.relative_to(ROOT)} uses {claim!r}"


def test_heat_movers_required_flags_match_repo_local_path_contract() -> None:
    assert REQUIRED_FLAGS_BY_COMMAND["heat-movers"] == (
        "--config-dir",
        "--data-dir",
        "--as-of",
    )


def test_heat_movers_cli_reference_lists_public_flags() -> None:
    section = _heat_movers_section(CLI_REFERENCE)

    for flag in HEAT_MOVERS_CLI_FLAGS:
        assert flag in section


def test_heat_movers_upload_checklist_help_loop_includes_command() -> None:
    assert "heat-movers" in _upload_checklist_help_loop_commands()


def test_dashboard_docs_current_tab_order_matches_app_labels() -> None:
    assert _dashboard_current_tab_labels() == list(DASHBOARD_TAB_LABELS)


def test_imported_review_workflow_docs_include_candidate_review_and_heat_handoff() -> None:
    for path in IMPORTED_REVIEW_WORKFLOW_DOCS:
        normalized = _normalized_doc_text(path).casefold()
        for phrase in IMPORTED_REVIEW_WORKFLOW_REQUIRED_PHRASES:
            assert phrase in normalized, f"{path.relative_to(ROOT)} missing {phrase!r}"


def test_imported_entity_evidence_docs_are_bounded_and_privacy_safe() -> None:
    for path in IMPORTED_ENTITY_EVIDENCE_DOCS:
        normalized = _normalized_doc_text(path).casefold()
        for phrase in IMPORTED_ENTITY_EVIDENCE_REQUIRED_PHRASES:
            assert phrase in normalized, f"{path.relative_to(ROOT)} missing {phrase!r}"

    for path in IMPORTED_ENTITY_EVIDENCE_BOUNDARY_MENTION_DOCS:
        normalized = _normalized_doc_text(path).casefold()
        for phrase in (
            "imported-entity-evidence",
            "local read-only",
            "imported-only",
            "manual_import",
            "privacy-safe",
            "retained local rows",
            "review_imported_entity_evidence",
            "no scraping",
            "no browser automation",
            "no platform apis",
            "account or cookie",
        ):
            assert phrase in normalized, f"{path.relative_to(ROOT)} missing {phrase!r}"

    cli_reference = _normalized_doc_text(CLI_REFERENCE).casefold()
    for field in IMPORTED_ENTITY_EVIDENCE_SAFE_FIELDS:
        assert field in cli_reference


def test_upload_checklist_installed_workflow_json_check_uses_installed_python() -> None:
    checklist = _read(UPLOAD_CHECKLIST)

    assert '"$tmp_env/venv/bin/python" - "$tmp_run/imported-review-workflow.json" <<' in checklist
    assert 'workflow_json = Path(sys.argv[1]).read_text(encoding="utf-8")' in checklist
    assert 'assert payload["step_count"] == 7' in checklist
    assert 'assert payload["steps"][3]["name"] == "review_imported_entity_evidence"' in checklist
    assert 'assert payload["steps"][4]["name"] == "review_imported_candidate_phrases"' in checklist
    assert 'assert payload["steps"][-1]["name"] == "review_local_heat_movers"' in checklist


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
    first_run_doc = _read(FIRST_RUN_DOC)
    source_command = "UV_NO_CONFIG=1 uv run python scripts/check_first_run_smoke.py --repo-root ."
    installed_command = (
        '"$tmp_env/venv/bin/python" scripts/check_first_run_smoke.py --repo-root . '
        '--python "$tmp_env/venv/bin/python" --installed'
    )

    for text in (checklist, ci_workflow, readme, first_run_doc):
        assert source_command in text
        assert "scripts/check_first_run_smoke.py" in text

    for text in (checklist, ci_workflow, readme, first_run_doc):
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


def test_readme_links_first_run_guide() -> None:
    text = _read(README)
    documentation = text.split("## Documentation", 1)[1].split("\n## ", 1)[0]

    assert FIRST_RUN_DOC.exists()
    assert "[docs/first-run.md](docs/first-run.md)" in text
    assert "[docs/first-run.md](docs/first-run.md)" in documentation
    assert "Reset repo-local sample output" in text


def test_readme_distinguishes_source_checkout_from_package_smoke() -> None:
    text = _read(README)

    assert "source checkout" in text
    assert "local wheel" in text
    assert "does not publish to PyPI" in text
    assert "[docs/github-upload-checklist.md](docs/github-upload-checklist.md)" in text


def test_readme_documents_manual_sample_flow_and_automated_smoke_boundary() -> None:
    text = _read(README)
    normalized = _normalized_doc_text(README)
    manual_flow = text.split("### Manual Repo-Local Sample Flow", 1)[1].split(
        "### Automated First-Run Smoke",
        1,
    )[0]

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

    assert (
        "deterministic sample is expected to produce matched report and trend signals "
        "for `The Row`, `The Row Margaux`, and `Ballet Flats`"
    ) in normalized
    for term in (
        "validates that sample rows import as community signals",
        "match the starter entities `The Row`, `The Row Margaux`, and `Ballet Flats`",
        "appear in the dated report",
        "produce matching entity trend deltas",
        "keep untracked candidates empty under starter config",
        FIRST_RUN_EXTERNAL_ADAPTER_SMOKE_PHRASE,
    ):
        assert term in normalized
    assert manual_flow.index("uv run fashion-radar match --config-dir") < manual_flow.index(
        "uv run fashion-radar imported-signals-summary"
    )
    assert manual_flow.index("uv run fashion-radar match --config-dir") < manual_flow.index(
        "uv run fashion-radar imported-signals --data-dir"
    )


def test_first_run_guide_documents_paths_outputs_dashboard_reset_and_boundaries() -> None:
    text = _read(FIRST_RUN_DOC)
    normalized = _normalized_doc_text(FIRST_RUN_DOC)
    manual_flow = text.split("## Manual Repo-Local Sample Flow", 1)[1].split(
        "## Inspect The Sample In The Dashboard",
        1,
    )[0]

    for term in (
        "Choose Your First Run",
        "Run first-run commands from the repository root",
        "Manual Repo-Local Sample Flow",
        'AS_OF="2026-06-13T12:00:00Z"',
        "examples/community-signals.example.csv",
        "community-candidates examples/community-signals.example.csv",
        "import-signals examples/community-signals.example.csv",
        "reports/fashion-radar-2026-06-13.md",
        "reports/fashion-radar-2026-06-13.json",
        "data/fashion-radar.sqlite",
        "data/fashion-radar.sqlite-wal",
        "data/fashion-radar.sqlite-shm",
        "configs/sources.yaml",
        "configs/entities.yaml",
        "configs/scoring.yaml",
        "Automated First-Run Smoke",
        "source checkout",
        "installed wheel",
        "--installed",
        "First-run sample smoke passed.",
        "should not create files under repo `data/` or `reports/`",
        "browser automation",
        "account login",
        "cookies/sessions",
        "source/platform connectors",
        "external services",
        "community-handoff-workflow",
        "community-signal-lint-dir",
        "community-candidates-dir",
        "import-signals-dir",
        "uv run fashion-radar dashboard --config-dir",
        "http://127.0.0.1:8501",
        "Reset The Repo-Local Sample",
        "Before reset, confirm you are at the repository root",
        "deletes local experiment state",
        "keeps `data/README.md` and `reports/README.md`",
    ):
        assert term in text

    for term in (
        "temporary config, data, report, and export directories",
        "does not run live collection",
        "does not run `collect`, `run`, or `dashboard`",
    ):
        assert term in normalized
    assert (
        "deterministic sample is expected to produce matched report and trend signals "
        "for `The Row`, `The Row Margaux`, and `Ballet Flats`"
    ) in normalized
    for term in (
        "validates that sample rows import as community signals",
        "match the starter entities `The Row`, `The Row Margaux`, and `Ballet Flats`",
        "appear in the dated report",
        "produce matching entity trend deltas",
        "keep untracked candidates empty under starter config",
        FIRST_RUN_EXTERNAL_ADAPTER_SMOKE_PHRASE,
    ):
        assert term in normalized
    assert manual_flow.index("uv run fashion-radar match --config-dir") < manual_flow.index(
        "uv run fashion-radar imported-signals-summary"
    )
    assert manual_flow.index("uv run fashion-radar match --config-dir") < manual_flow.index(
        "uv run fashion-radar imported-signals --data-dir"
    )


def test_readme_documents_optional_watchlist_local_sample() -> None:
    text = _read(README)
    normalized = _normalized_doc_text(README)

    for term in (
        "Optional Expanded Watchlist Sample",
        "examples/community-signals.watchlist.example.csv",
        "Community Watchlist Sample",
        (
            "cp configs/entity-packs/fashion-watchlist.example.yaml "
            '"$tmp_watchlist/configs/entities.yaml"'
        ),
        "community-signal-lint examples/community-signals.watchlist.example.csv",
        "import-signals examples/community-signals.watchlist.example.csv",
        'uv run fashion-radar match --config-dir "$tmp_watchlist/configs"',
        'uv run fashion-radar report --config-dir "$tmp_watchlist/configs"',
        'uv run fashion-radar trends --config-dir "$tmp_watchlist/configs"',
    ):
        assert term in text

    for term in (
        "optional local sample does not fetch URLs",
        "does not collect platform data",
        "does not prove demand",
        "does not rank brands",
        "does not verify platform coverage",
        "does not add connectors",
    ):
        assert term in normalized


def test_first_run_guide_documents_optional_watchlist_local_sample() -> None:
    text = _read(FIRST_RUN_DOC)
    normalized = _normalized_doc_text(FIRST_RUN_DOC)

    for term in (
        "Optional Expanded Watchlist Sample",
        "examples/community-signals.watchlist.example.csv",
        "Community Watchlist Sample",
        "fashion-watchlist.example.yaml",
        "Khaite",
        "Alaia Le Teckel",
        "Miu Miu Arcadie",
        "Mary Jane Shoes",
        "Boho Revival",
    ):
        assert term in text

    for term in (
        "optional local sample does not fetch URLs",
        "does not collect platform data",
        "does not prove demand",
        "does not rank brands",
        "does not verify platform coverage",
        "does not add connectors",
    ):
        assert term in normalized


def test_entity_pack_docs_link_optional_watchlist_sample_to_local_pack() -> None:
    text = _read(ENTITY_PACKS_DOC)
    normalized = _normalized_doc_text(ENTITY_PACKS_DOC)

    for term in (
        "Try The Optional Local Sample",
        "examples/community-signals.watchlist.example.csv",
        "Community Watchlist Sample",
        (
            "cp configs/entity-packs/fashion-watchlist.example.yaml "
            '"$tmp_watchlist/configs/entities.yaml"'
        ),
        "uv run fashion-radar entity-pack-lint configs/entity-packs/fashion-watchlist.example.yaml",
        (
            "uv run fashion-radar community-signal-lint "
            "examples/community-signals.watchlist.example.csv"
        ),
    ):
        assert term in text

    for term in (
        "local sample rows are synthetic",
        "not a hot-list",
        "not a ranking",
        "not demand proof",
        "not platform coverage verification",
    ):
        assert term in normalized


def test_github_upload_checklist_mentions_watchlist_sample_archive_guard() -> None:
    text = _read(UPLOAD_CHECKLIST)
    normalized = _normalized_doc_text(UPLOAD_CHECKLIST)

    assert "examples/community-signals.watchlist.example.csv" in text
    assert "Package archive checks require" in text
    assert "optional watchlist sample" in normalized


def test_upload_checklist_documents_first_run_smoke_boundary() -> None:
    text = _read(UPLOAD_CHECKLIST)
    normalized = _normalized_doc_text(UPLOAD_CHECKLIST)

    assert "First-run sample smoke passed." in text
    for term in (
        "Both first-run smokes use checked-in sample files and temporary config, data, "
        "report, and export directories only.",
        "They do not run `collect`, `run`, `dashboard`, scheduler/monitoring commands, "
        "scraping/crawling, browser automation, account login, cookies/sessions, "
        "source/platform connectors, platform automation, or external services.",
    ):
        assert term in normalized

    for term in (
        "scraping/crawling",
        "browser automation",
        "account login",
        "cookies/sessions",
        "source/platform connectors",
        "platform automation",
        "external services",
    ):
        assert term in text
    assert (
        "The smoke also validates sample rows, matched starter entities, report content, "
        "trend deltas, empty untracked candidates, and directory handoff dry-run counts."
    ) in normalized


def test_community_import_docs_promote_checked_in_example_import() -> None:
    text = _read(COMMUNITY_SIGNAL_IMPORT_DOC)

    assert 'AS_OF="2026-06-13T12:00:00Z"' in text
    assert "import-signals examples/community-signals.example.csv" in text
    assert "community-candidates examples/community-signals.example.csv" in text
    assert 'tmp_run="$(mktemp -d)"' in text
    assert (
        'cp examples/community-signals.example.csv "$tmp_run/exports/community-signals.csv"' in text
    )


def test_community_signal_import_docs_describe_external_tool_contract_parity() -> None:
    text = _read(COMMUNITY_SIGNAL_IMPORT_DOC)
    normalized = _normalized_doc_text(COMMUNITY_SIGNAL_IMPORT_DOC).casefold()

    for term in (
        "External Tool Contract Parity",
        "community-signal-profile",
        "external-tool-adapters",
        "external-tool-template",
        "external-tool-workflow",
        "external-tool-readiness",
        "field mappings",
    ):
        assert term in text

    for term in (
        "dry-run import guidance remains separate from real import guidance",
        "json/csv template output remains importable rows only",
        "local handoff guidance",
        "not platform collection",
        "does not add connectors",
        "does not prove demand",
        "does not rank sources",
        "does not verify platform coverage",
    ):
        assert term in normalized


def test_community_signal_profile_docs_are_linked() -> None:
    readme = _read(README)
    cli_reference = _read(CLI_REFERENCE)
    import_doc = _read(COMMUNITY_SIGNAL_IMPORT_DOC)
    quality_doc = _read(ROOT / "docs" / "community-signal-quality.md")
    boundaries = _read(ROOT / "docs" / "source-boundaries.md")

    for text in (readme, cli_reference, import_doc, quality_doc, boundaries):
        assert "community-signal-profile" in text

    assert "examples/community-signal-profile.example.json" in import_doc
    assert "producer contract" in import_doc
    assert "does not read handoff files or directories" in import_doc
    assert "does not read handoff files or directories" in boundaries


def test_community_handoff_manifest_docs_are_linked_and_warn_about_storage() -> None:
    readme = _read(README)
    cli_reference = _read(CLI_REFERENCE)
    import_doc = _read(ROOT / "docs" / "community-signal-import.md")
    checklist = _read(UPLOAD_CHECKLIST)
    boundaries = _read(ROOT / "docs" / "source-boundaries.md")

    for text in (readme, cli_reference, import_doc, checklist, boundaries):
        assert "community-handoff-manifest" in text

    storage_warning_terms = (
        "Do not save this manifest as a matched handoff file",
        'using `--pattern "*.json"`',
        "outside the matched export directory",
        "excluded filename/pattern",
    )
    for term in storage_warning_terms:
        assert term in import_doc

    assert "Directory Manifest" in import_doc
    assert "community-handoff-manifest/v1" in import_doc
    assert "producer_profile_command" in import_doc
    assert "suggested_filename" in import_doc
    manifest_section = _markdown_section(import_doc, "## Directory Manifest")
    for field in (
        "account_id",
        "author_handle",
        "cookie",
        "direct_message",
        "follower_count",
        "full_post_body",
        "image_url",
        "profile_url",
        "raw_comment",
        "session",
        "token",
        "video_url",
    ):
        assert f'"{field}"' in manifest_section
    for field in ("cookies", "sessions", "tokens"):
        assert f'"{field}"' not in manifest_section
    assert '"$tmp_env/venv/bin/fashion-radar" community-handoff-manifest --help' in checklist
    assert (
        '"$tmp_env/venv/bin/fashion-radar" community-handoff-manifest "$tmp_run/missing ? # & %"'
    ) in checklist


def test_community_handoff_manifest_docs_show_current_profile_example_paths_only() -> None:
    import_doc = _read(ROOT / "docs" / "community-signal-import.md")
    manifest_payload = _first_json_payload_from_section(import_doc, "## Directory Manifest")

    assert manifest_payload["example_paths"] == build_community_signal_profile().example_paths
    assert manifest_payload["directory_example_paths"] == list(
        COMMUNITY_TOOL_HANDOFF_DIRECTORY_PATHS
    )
    manifest_keys = list(manifest_payload)
    assert manifest_keys.index("directory_example_paths") == (
        manifest_keys.index("example_paths") + 1
    )
    for path in COMMUNITY_TOOL_HANDOFF_DIRECTORY_PATHS:
        assert path not in manifest_payload["example_paths"]


def test_directory_example_paths_are_machine_readable_and_documented() -> None:
    profile = build_community_signal_profile()
    manifest = build_community_handoff_manifest(
        directory=Path("exports"),
        config_dir=Path("configs"),
        data_dir=Path("data"),
        input_format="csv",
        pattern="*.csv",
        as_of="2026-06-13T12:00:00Z",
        source_name="Community Tool Export",
    )

    assert tuple(profile.directory_example_paths) == COMMUNITY_TOOL_HANDOFF_DIRECTORY_PATHS
    assert profile.directory_example_paths == manifest.directory_example_paths

    field_docs = (
        README,
        ROOT / "docs" / "community-signal-import.md",
        ROOT / "docs" / "community-signal-quality.md",
        CLI_REFERENCE,
        SOURCE_BOUNDARIES_DOC,
        ARCHITECTURE_DOC,
        UPLOAD_CHECKLIST,
        CHANGELOG,
    )
    path_docs = (
        README,
        ROOT / "docs" / "community-signal-import.md",
        ROOT / "docs" / "community-signal-quality.md",
        CLI_REFERENCE,
        UPLOAD_CHECKLIST,
        CHANGELOG,
    )

    for path in field_docs:
        normalized = _normalized_doc_text(path).casefold()
        assert "directory_example_paths" in normalized

    for path in path_docs:
        normalized = _normalized_doc_text(path).casefold()
        for relative_path in COMMUNITY_TOOL_HANDOFF_DIRECTORY_PATHS:
            assert relative_path.casefold() in normalized


def test_external_community_tool_handoff_template_docs_are_linked_and_bounded() -> None:
    readme = _read(README)
    import_doc = _read(ROOT / "docs" / "community-signal-import.md")
    checklist = _read(UPLOAD_CHECKLIST)
    boundaries = _read(ROOT / "docs" / "source-boundaries.md")
    architecture = _read(ROOT / "docs" / "architecture.md")
    agents = _read(ROOT / "AGENTS.md")
    changelog = _read(ROOT / "CHANGELOG.md")

    for text in (readme, import_doc, checklist):
        for path in COMMUNITY_TOOL_HANDOFF_TEMPLATE_PATHS:
            _assert_markdown_link_to_path(text, path)

    boundary_terms = (
        "external tool handoff template",
        "sanitized CSV/JSON",
        "user-controlled external/community tools",
        "not platform collection",
        "connectors",
        "scraping",
        "browser automation",
        "platform APIs",
        "monitoring",
        "scheduling",
        "source acquisition",
        "demand proof",
        "ranking",
        "coverage verification",
    )
    for doc_text in (readme, import_doc, boundaries, architecture):
        normalized = _normalized_text(doc_text).casefold()
        for term in boundary_terms:
            assert term.casefold() in normalized

    normalized_agents = _normalized_text(agents).casefold()
    assert "external community tool handoff" in normalized_agents
    assert "sanitized CSV/JSON".casefold() in normalized_agents
    for term in (
        "connectors",
        "scraping",
        "browser automation",
        "platform APIs",
        "monitoring",
        "scheduling",
        "source acquisition",
        "demand proof",
        "ranking",
        "coverage verification",
    ):
        assert term.casefold() in normalized_agents

    normalized_changelog = _normalized_text(changelog).casefold()
    assert "external tool handoff templates" in normalized_changelog
    for path in COMMUNITY_TOOL_HANDOFF_TEMPLATE_PATHS:
        assert path in normalized_changelog


def test_external_community_tool_directory_example_docs_are_linked_and_bounded() -> None:
    readme = _read(README)
    import_doc = _read(ROOT / "docs" / "community-signal-import.md")
    checklist = _read(UPLOAD_CHECKLIST)
    boundaries = _read(ROOT / "docs" / "source-boundaries.md")
    architecture = _read(ROOT / "docs" / "architecture.md")
    agents = _read(ROOT / "AGENTS.md")
    changelog = _read(ROOT / "CHANGELOG.md")

    for text in (readme, import_doc, checklist):
        for path in COMMUNITY_TOOL_HANDOFF_DIRECTORY_PATHS:
            _assert_markdown_link_to_path(text, path)

    boundary_terms = (
        "external community tool export directory examples",
        "sanitized CSV/JSON",
        "not platform collection",
        "connectors",
        "scraping",
        "browser automation",
        "platform APIs",
        "monitoring",
        "scheduling",
        "source acquisition",
        "demand proof",
        "ranking",
        "coverage verification",
    )
    for doc_text in (readme, import_doc, boundaries, architecture, agents):
        normalized = _normalized_text(doc_text).casefold()
        for term in boundary_terms:
            assert term.casefold() in normalized

    normalized_changelog = _normalized_text(changelog).casefold()
    assert "external community tool export directory examples" in normalized_changelog
    for path in COMMUNITY_TOOL_HANDOFF_DIRECTORY_PATHS:
        assert path.casefold() in normalized_changelog


def test_external_tool_adapter_registry_docs_are_linked_and_bounded() -> None:
    readme = _read(README)
    import_doc = _read(ROOT / "docs" / "community-signal-import.md")
    quality_doc = _read(ROOT / "docs" / "community-signal-quality.md")
    cli_reference = _read(CLI_REFERENCE)
    checklist = _read(UPLOAD_CHECKLIST)
    boundaries = _read(ROOT / "docs" / "source-boundaries.md")
    architecture = _read(ROOT / "docs" / "architecture.md")
    agents = _read(ROOT / "AGENTS.md")
    changelog = _read(ROOT / "CHANGELOG.md")
    readiness_preflight_terms = (
        "external-tool-readiness",
        "optional local read-only preflight command",
        "itself remains print-only",
        "does not run readiness or perform PATH lookup",
    )

    for text in (
        readme,
        import_doc,
        quality_doc,
        cli_reference,
        checklist,
        boundaries,
        architecture,
        agents,
        changelog,
    ):
        normalized = _normalized_text(text).casefold()
        assert "external-tool-adapters" in normalized
        assert "external social/community tool adapter registry" in normalized
        assert "local producer-discovery registry" in normalized
        for term in readiness_preflight_terms:
            assert term.casefold() in normalized

    for command in (
        "fashion-radar external-tool-adapters --format table",
        "fashion-radar external-tool-adapters --format json",
    ):
        assert command in cli_reference
        assert command in checklist

    for doc_path, doc_text in ((README, readme), (CLI_REFERENCE, cli_reference)):
        normalized = _normalized_text(doc_text)
        for row in EXTERNAL_TOOL_ADAPTER_DOC_ROWS:
            assert row in normalized, f"{doc_path.relative_to(ROOT)} missing {row!r}"

    assert "external-tool-adapters" in _upload_checklist_help_loop_commands()
    assert '"$tmp_env/venv/bin/fashion-radar" external-tool-adapters --help' in checklist
    assert '"$tmp_env/venv/bin/fashion-radar" external-tool-adapters --format json' in checklist

    boundary_terms = (
        "local",
        "print-only",
        "sanitized CSV/JSON local file handoff",
        "user-controlled external/community tools",
        "not platform collection",
        "no connectors",
        "no scraping",
        "no browser automation",
        "no platform APIs",
        "no monitoring",
        "no scheduling",
        "no source acquisition",
        "no demand proof",
        "no ranking",
        "no coverage verification",
    )
    for doc_text in (readme, import_doc, quality_doc, boundaries, architecture, agents):
        normalized = _normalized_text(doc_text).casefold()
        for term in boundary_terms:
            assert term.casefold() in normalized

    normalized_changelog = _normalized_text(changelog).casefold()
    for term in boundary_terms:
        assert term.casefold() in normalized_changelog


def test_external_tool_template_docs_are_linked_and_bounded() -> None:
    readme = _read(README)
    import_doc = _read(ROOT / "docs" / "community-signal-import.md")
    quality_doc = _read(ROOT / "docs" / "community-signal-quality.md")
    cli_reference = _read(CLI_REFERENCE)
    checklist = _read(UPLOAD_CHECKLIST)
    boundaries = _read(ROOT / "docs" / "source-boundaries.md")
    architecture = _read(ROOT / "docs" / "architecture.md")
    agents = _read(ROOT / "AGENTS.md")
    changelog = _read(ROOT / "CHANGELOG.md")

    for text in (
        readme,
        import_doc,
        quality_doc,
        cli_reference,
        checklist,
        boundaries,
        architecture,
        agents,
        changelog,
    ):
        normalized = _normalized_text(text).casefold()
        assert "external-tool-template" in normalized
        assert "adapter-specific template rows" in normalized
        assert "sanitized CSV/JSON local file handoff".casefold() in normalized

    for command in (
        "fashion-radar external-tool-template --adapter instaloader --format table",
        "fashion-radar external-tool-template --adapter instaloader --format json",
        "fashion-radar external-tool-template --adapter instaloader --format csv",
    ):
        assert command in cli_reference
        assert command in checklist

    assert "external-tool-template" in _upload_checklist_help_loop_commands()
    assert '"$tmp_env/venv/bin/fashion-radar" external-tool-template --help' in checklist
    assert (
        '"$tmp_env/venv/bin/fashion-radar" external-tool-template '
        "--adapter instaloader --format json"
    ) in checklist

    boundary_terms = (
        "local",
        "print-only",
        "sanitized CSV/JSON local file handoff",
        "user-controlled external/community tools",
        "not platform collection",
        "no connectors",
        "no scraping",
        "no browser automation",
        "no platform APIs",
        "no monitoring",
        "no scheduling",
        "no source acquisition",
        "no demand proof",
        "no ranking",
        "no coverage verification",
    )
    for doc_text in (readme, import_doc, quality_doc, boundaries, architecture, agents):
        normalized = _normalized_text(doc_text).casefold()
        for term in boundary_terms:
            assert term.casefold() in normalized

    normalized_changelog = _normalized_text(changelog).casefold()
    for term in boundary_terms:
        assert term.casefold() in normalized_changelog


def test_external_tool_workflow_docs_are_linked_and_bounded() -> None:
    for path in EXTERNAL_TOOL_WORKFLOW_DOCS:
        text = _read(path)
        normalized = _normalized_text(text).casefold()
        assert "external-tool-workflow" in normalized, path.relative_to(ROOT)
        for term in EXTERNAL_TOOL_WORKFLOW_BOUNDARY_PHRASES:
            assert term.casefold() in normalized, f"{path.relative_to(ROOT)} missing {term!r}"


def test_external_tool_workflow_docs_include_examples_and_steps() -> None:
    cli_reference = _read(CLI_REFERENCE)
    checklist = _read(UPLOAD_CHECKLIST)
    import_doc = _read(ROOT / "docs" / "community-signal-import.md")

    for command in (
        "fashion-radar external-tool-workflow --adapter instaloader --format table",
        "fashion-radar external-tool-workflow --adapter instaloader --format json",
    ):
        assert command in cli_reference
        assert command in checklist

    assert "external-tool-workflow" in _upload_checklist_help_loop_commands()
    assert '"$tmp_env/venv/bin/fashion-radar" external-tool-workflow --help' in checklist
    assert (
        '"$tmp_env/venv/bin/fashion-radar" external-tool-workflow '
        "--adapter instaloader --format json"
    ) in checklist

    for step_name in EXTERNAL_TOOL_WORKFLOW_STEP_NAMES:
        assert step_name in import_doc


def test_external_tool_readiness_docs_are_linked_and_bounded() -> None:
    for path in EXTERNAL_TOOL_READINESS_DOCS:
        text = _read(path)
        normalized = _normalized_text(text).casefold()
        assert "external-tool-readiness" in normalized, path.relative_to(ROOT)
        assert "external tool readiness" in normalized, path.relative_to(ROOT)
        for phrase in EXTERNAL_TOOL_READINESS_BOUNDARY_PHRASES:
            assert phrase.casefold() in normalized, f"{path.relative_to(ROOT)} missing {phrase!r}"


def test_external_tool_readiness_upload_checklist_help_loop_and_smoke() -> None:
    checklist = _read(UPLOAD_CHECKLIST)

    assert "external-tool-readiness" in _upload_checklist_help_loop_commands()
    assert '"$tmp_env/venv/bin/fashion-radar" external-tool-readiness --help' in checklist
    assert (
        '"$tmp_env/venv/bin/fashion-radar" external-tool-readiness '
        "--adapter instaloader --format json"
    ) in checklist
    assert (
        '"$tmp_env/venv/bin/fashion-radar" external-tool-readiness --adapter rednote_mcp'
    ) in checklist
    assert "scripts/check_first_run_smoke.py" in checklist


def test_community_handoff_check_dir_docs_are_linked_and_bounded() -> None:
    readme = _read(README)
    import_doc = _read(ROOT / "docs" / "community-signal-import.md")
    cli_reference = _read(CLI_REFERENCE)
    checklist = _read(UPLOAD_CHECKLIST)
    boundaries = _read(ROOT / "docs" / "source-boundaries.md")
    architecture = _read(ROOT / "docs" / "architecture.md")
    agents = _read(ROOT / "AGENTS.md")
    changelog = _read(ROOT / "CHANGELOG.md")

    for text in (readme, import_doc, cli_reference, checklist):
        assert "community-handoff-check-dir" in text

    boundary_terms = (
        "local-only handoff readiness report",
        "matched local regular files and local config",
        "does not import rows",
        "no SQLite",
        "no config/data/report/dashboard/digest artifacts",
        "fetch URLs",
        "login",
        "platform APIs",
        "download media",
        "browser automation",
        "scrape/crawl",
        "monitor",
        "watch",
        "schedule",
        "connectors",
        "source acquisition",
        "demand proof",
        "ranking",
        "coverage verification",
        "entity generation",
        "compliance",
        "policy",
        "authorization",
        "safety-review",
    )
    for doc_text in (readme, import_doc, boundaries, architecture, agents):
        normalized = _normalized_text(doc_text).casefold()
        assert "community-handoff-check-dir" in normalized
        for term in boundary_terms:
            assert term.casefold() in normalized

    normalized_changelog = _normalized_text(changelog).casefold()
    assert "community-handoff-check-dir" in normalized_changelog
    assert "local-only handoff readiness report" in normalized_changelog

    workflow_docs = (readme, import_doc, cli_reference, checklist, boundaries, architecture)
    workflow_required_terms = (
        "review_handoff_readiness",
        "local-only handoff readiness report",
        "before importing rows",
        "does not execute commands",
    )
    for doc_text in workflow_docs:
        normalized = _normalized_text(doc_text).casefold()
        for term in workflow_required_terms:
            assert term.casefold() in normalized

    profile_command_names = [
        FASHION_RADAR_COMMAND_RE.search(command).group("name")
        for command in build_community_signal_profile().recommended_commands
    ]
    assert "community-handoff-check-dir" not in profile_command_names

    manifest_payload = _first_json_payload_from_section(import_doc, "## Directory Manifest")
    documented_step_text: list[str] = []
    for step in manifest_payload["workflow"]["steps"]:
        if isinstance(step, str):
            documented_step_text.append(step)
        else:
            documented_step_text.extend(str(step.get(field, "")) for field in ("name", "command"))
    assert any("review_handoff_readiness" in text for text in documented_step_text)
    assert any("community-handoff-check-dir" in text for text in documented_step_text)

    generated_manifest = build_community_handoff_manifest(
        directory=Path("exports"),
        config_dir=Path("configs"),
        data_dir=Path("data"),
        input_format="csv",
        pattern="*.csv",
        as_of="2026-06-13T12:00:00Z",
        source_name="Community Tool Export",
    )
    generated_step_text = [
        text for step in generated_manifest.workflow.steps for text in (step.name, step.command)
    ]
    assert any("review_handoff_readiness" in text for text in generated_step_text)
    assert any("community-handoff-check-dir" in text for text in generated_step_text)


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


def test_community_signal_import_doc_keeps_profile_recommended_command_order() -> None:
    text = _read(ROOT / "docs" / "community-signal-import.md")
    flow_section = text.split("## Producer Profile", 1)[1].split("## Boundary", 1)[0]
    normalized_flow = " ".join(flow_section.split())
    assert (
        "The JSON profile's `recommended_commands` list is the exact producer-facing sequence."
    ) in normalized_flow
    assert (
        "preserve the same lint, preview, dry-run import, import, and review order."
    ) in normalized_flow

    profile_command_names = []
    for command in build_community_signal_profile().recommended_commands:
        match = FASHION_RADAR_COMMAND_RE.search(command)
        assert match is not None
        profile_command_names.append(match.group("name"))
    documented_names = []
    for block in _bash_blocks(flow_section):
        for command in _shell_commands(block):
            match = FASHION_RADAR_COMMAND_RE.search(command)
            if match is not None and match.group("name") in profile_command_names:
                documented_names.append(match.group("name"))

    position = 0
    for expected in profile_command_names:
        while position < len(documented_names) and documented_names[position] != expected:
            position += 1
        assert position < len(documented_names), (
            f"{expected!r} from profile recommended_commands is missing or out of order"
        )
        position += 1


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


def test_first_run_guide_setup_commands_use_repo_local_paths() -> None:
    setup_commands = _first_run_setup_commands()

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


def test_first_run_guide_dashboard_command_uses_repo_local_paths() -> None:
    commands = _first_run_dashboard_commands()

    assert commands == [
        'uv run fashion-radar dashboard --config-dir "$PWD/configs" '
        '--data-dir "$PWD/data" --reports-dir "$PWD/reports" '
        "--host 127.0.0.1 --port 8501"
    ]


def test_first_run_guide_reset_commands_are_narrow_file_deletions() -> None:
    assert _first_run_reset_commands() == [
        "test -f pyproject.toml && test -d examples && { rm -f configs/sources.yaml; "
        "rm -f configs/entities.yaml; rm -f configs/scoring.yaml; "
        "rm -f data/fashion-radar.sqlite; rm -f data/fashion-radar.sqlite-wal; "
        "rm -f data/fashion-radar.sqlite-shm; "
        "rm -f reports/fashion-radar-2026-06-13.md; "
        "rm -f reports/fashion-radar-2026-06-13.json; }",
    ]


def test_first_run_guide_setup_commands_smoke(tmp_path: Path) -> None:
    runner = CliRunner()

    for command in _first_run_setup_commands():
        parts = [part.replace("$PWD", str(tmp_path)) for part in shlex.split(command)]
        assert parts[:3] == ["uv", "run", "fashion-radar"]

        result = runner.invoke(app, parts[3:])

        assert result.exit_code == 0, result.output


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
