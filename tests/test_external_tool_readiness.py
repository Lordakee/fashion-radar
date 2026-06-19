from __future__ import annotations

import shlex
from pathlib import Path

import pytest
from pydantic import ValidationError

from fashion_radar import external_tool_readiness as readiness_module
from fashion_radar.external_tool_adapters import build_external_tool_adapter_registry
from fashion_radar.external_tool_readiness import (
    EXTERNAL_TOOL_READINESS_BOUNDARIES,
    ExternalToolReadiness,
    build_external_tool_readiness,
    render_external_tool_readiness_table,
)


def test_readiness_has_stable_contract_checks_and_steps() -> None:
    readiness = build_external_tool_readiness(
        adapter_id="instaloader",
        directory=Path("./exports"),
        config_dir=Path("./configs"),
        data_dir=Path("./data"),
        as_of="2026-06-13T12:00:00Z",
        which=lambda command: "/usr/bin/instaloader" if command == "instaloader" else None,
    )
    payload = readiness.model_dump(mode="json")

    assert list(payload) == [
        "contract_version",
        "execution_mode",
        "adapter_id",
        "display_name",
        "platform_label",
        "directory",
        "input_format",
        "pattern",
        "as_of",
        "config_dir",
        "data_dir",
        "source_name",
        "checks",
        "step_count",
        "steps",
        "boundaries",
    ]
    assert readiness.contract_version == "external-tool-readiness/v1"
    assert readiness.execution_mode == "local_read_only"
    assert readiness.adapter_id == "instaloader"
    assert readiness.display_name == "Instaloader Export"
    assert readiness.platform_label == "instagram"
    assert readiness.directory == "exports"
    assert readiness.input_format == "json"
    assert readiness.pattern == "*.json"
    assert readiness.as_of == "2026-06-13T12:00:00+00:00"
    assert readiness.config_dir == "configs"
    assert readiness.data_dir == "data"
    assert readiness.source_name == "Instaloader Export"
    assert readiness.step_count == 7
    assert [check.name for check in readiness.checks] == ["upstream_command"]
    assert list(payload["checks"][0]) == [
        "name",
        "status",
        "command",
        "path",
        "detail",
        "install_hint",
    ]
    assert readiness.checks[0].status == "found"
    assert readiness.checks[0].command == "instaloader"
    assert readiness.checks[0].path == "/usr/bin/instaloader"
    assert "https://pypi.tuna.tsinghua.edu.cn/simple instaloader" in (
        readiness.checks[0].install_hint
    )
    assert [step.name for step in readiness.steps] == [
        "inspect_adapter_registry",
        "print_adapter_template_json",
        "print_external_tool_workflow",
        "print_signal_profile",
        "lint_export_directory",
        "review_handoff_readiness",
        "dry_run_directory_import",
    ]
    assert [step.suggested_effect for step in readiness.steps] == [
        "print_only",
        "print_only",
        "print_only",
        "print_only",
        "read_only",
        "read_only",
        "read_only",
    ]
    assert list(payload["steps"][0]) == [
        "order",
        "name",
        "purpose",
        "command",
        "suggested_effect",
    ]


def test_readiness_defaults_to_generic_adapter_and_not_applicable_command_check() -> None:
    readiness = build_external_tool_readiness(
        adapter_id=None,
        directory=Path("./handoff"),
        config_dir=Path("./configs"),
        data_dir=Path("./data"),
        as_of="2026-06-13T12:00:00Z",
    )

    assert readiness.adapter_id == "generic_community_export"
    assert readiness.input_format == "csv"
    assert readiness.pattern == "*.csv"
    assert readiness.source_name == "Generic Community Export"
    assert readiness.checks[0].status == "not_applicable"
    assert readiness.checks[0].command is None
    assert readiness.checks[0].path is None


def test_readiness_uses_lazy_shutil_which_lookup(monkeypatch: pytest.MonkeyPatch) -> None:
    calls: list[str] = []

    def fake_which(command: str) -> str | None:
        calls.append(command)
        return f"/mock/bin/{command}"

    monkeypatch.setattr(readiness_module.shutil, "which", fake_which)

    readiness = build_external_tool_readiness(
        adapter_id="yt_dlp",
        directory=Path("./exports"),
        config_dir=Path("./configs"),
        data_dir=Path("./data"),
        as_of="2026-06-13T12:00:00Z",
    )

    assert calls == ["yt-dlp"]
    assert readiness.checks[0].status == "found"
    assert readiness.checks[0].path == "/mock/bin/yt-dlp"


@pytest.mark.parametrize(
    ("adapter_id", "expected_command", "expected_status", "expected_hint"),
    [
        ("rednote_mcp", "rednote-mcp", "missing", "npmmirror"),
        (
            "xiaohongshu_crawler",
            "xiaohongshu-crawler",
            "missing",
            "upstream xiaohongshu-crawler docs",
        ),
        (
            "instaloader",
            "instaloader",
            "missing",
            "https://pypi.tuna.tsinghua.edu.cn/simple instaloader",
        ),
        ("tiktok_api", None, "not_applicable", "TikTokApi"),
        ("yt_dlp", "yt-dlp", "missing", "https://pypi.tuna.tsinghua.edu.cn/simple yt-dlp"),
        ("x_search_export", None, "not_applicable", "AnySearch/snscrape"),
        ("xpoz_mcp", None, "not_applicable", "XPOZ MCP"),
        ("generic_community_export", None, "not_applicable", "sanitized local export"),
    ],
)
def test_readiness_upstream_command_mapping(
    adapter_id: str,
    expected_command: str | None,
    expected_status: str,
    expected_hint: str,
) -> None:
    readiness = build_external_tool_readiness(
        adapter_id=adapter_id,
        directory=Path("./exports"),
        config_dir=Path("./configs"),
        data_dir=Path("./data"),
        as_of="2026-06-13T12:00:00Z",
        which=lambda _command: None,
    )

    check = readiness.checks[0]

    assert check.name == "upstream_command"
    assert check.command == expected_command
    assert check.status == expected_status
    assert expected_hint in check.install_hint


def test_readiness_commands_use_overrides_and_shell_quote_values() -> None:
    readiness = build_external_tool_readiness(
        adapter_id="x_search_export",
        directory=Path("exports ? # & %"),
        config_dir=Path("config ? # & %"),
        data_dir=Path("data ? # & %"),
        as_of="2026-06-13T12:00:00Z",
        input_format="json",
        pattern="*.handoff.json",
        source_name="Local Desk Export",
        which=lambda _command: None,
    )
    commands = {step.name: step.command for step in readiness.steps}

    assert commands["inspect_adapter_registry"] == (
        "fashion-radar external-tool-adapters --adapter x_search_export "
        "--directory 'exports ? # & %' --config-dir 'config ? # & %' "
        "--data-dir 'data ? # & %' --as-of 2026-06-13T12:00:00+00:00 "
        "--format table"
    )
    assert commands["print_adapter_template_json"] == (
        "fashion-radar external-tool-template --adapter x_search_export "
        "--directory 'exports ? # & %' --config-dir 'config ? # & %' "
        "--data-dir 'data ? # & %' --as-of 2026-06-13T12:00:00+00:00 "
        "--format json"
    )
    assert commands["print_external_tool_workflow"] == (
        "fashion-radar external-tool-workflow --adapter x_search_export "
        "--directory 'exports ? # & %' --config-dir 'config ? # & %' "
        "--data-dir 'data ? # & %' --as-of 2026-06-13T12:00:00+00:00 "
        "--input-format json --pattern '*.handoff.json' "
        "--source-name 'Local Desk Export' --format table"
    )
    assert commands["print_signal_profile"] == (
        "fashion-radar community-signal-profile --format json"
    )
    assert commands["lint_export_directory"] == (
        "fashion-radar community-signal-lint-dir 'exports ? # & %' "
        "--input-format json --pattern '*.handoff.json' "
        "--source-name 'Local Desk Export' --strict"
    )
    assert commands["review_handoff_readiness"] == (
        "fashion-radar community-handoff-check-dir 'exports ? # & %' "
        "--input-format json --pattern '*.handoff.json' "
        "--config-dir 'config ? # & %' --as-of 2026-06-13T12:00:00+00:00 "
        "--source-name 'Local Desk Export' --strict"
    )
    assert commands["dry_run_directory_import"] == (
        "fashion-radar import-signals-dir 'exports ? # & %' --format json "
        "--pattern '*.handoff.json' --source-name 'Local Desk Export' "
        "--data-dir 'data ? # & %' --imported-at 2026-06-13T12:00:00+00:00 "
        "--dry-run"
    )


def test_readiness_dry_run_step_includes_imported_at_for_deterministic_command() -> None:
    readiness = build_external_tool_readiness(
        adapter_id="instaloader",
        directory=Path("./exports"),
        config_dir=Path("./configs"),
        data_dir=Path("./data"),
        as_of="2026-06-13T12:00:00Z",
        which=lambda _command: None,
    )

    command = next(
        step.command for step in readiness.steps if step.name == "dry_run_directory_import"
    )
    parts = shlex.split(command)

    assert parts[0:2] == ["fashion-radar", "import-signals-dir"]
    assert parts[parts.index("--imported-at") + 1] == "2026-06-13T12:00:00+00:00"
    assert parts[-1] == "--dry-run"


def test_readiness_blank_overrides_fall_back_to_adapter_defaults() -> None:
    readiness = build_external_tool_readiness(
        adapter_id="x_search_export",
        directory=Path("./exports"),
        config_dir=Path("./configs"),
        data_dir=Path("./data"),
        as_of="2026-06-13T12:00:00Z",
        pattern="   ",
        source_name="   ",
        which=lambda _command: None,
    )

    assert readiness.pattern == "*.csv"
    assert readiness.source_name == "X Search Export"


def test_readiness_rejects_unknown_adapter_and_invalid_as_of() -> None:
    with pytest.raises(ValueError, match="Unknown external tool adapter: missing"):
        build_external_tool_readiness(
            adapter_id="missing",
            directory=Path("./exports"),
            config_dir=Path("./configs"),
            data_dir=Path("./data"),
            as_of="2026-06-13T12:00:00Z",
        )

    with pytest.raises(ValueError):
        build_external_tool_readiness(
            adapter_id="instaloader",
            directory=Path("./exports"),
            config_dir=Path("./configs"),
            data_dir=Path("./data"),
            as_of="not-a-date",
        )


def test_readiness_table_renderer_sanitizes_cells_and_prints_sections() -> None:
    readiness = ExternalToolReadiness(
        contract_version="external-tool-readiness/v1",
        execution_mode="local_read_only",
        adapter_id="tool|one",
        display_name="Tool | One",
        platform_label="platform|one",
        directory="./exports",
        input_format="csv",
        pattern="*.csv",
        as_of="2026-06-13T12:00:00+00:00",
        config_dir="./configs",
        data_dir="./data",
        source_name="Source | One",
        checks=[
            {
                "name": "upstream_command",
                "status": "missing",
                "command": "tool-one",
                "path": None,
                "detail": "Command | not found\non PATH.",
                "install_hint": "Install | from\nupstream docs.",
            }
        ],
        step_count=1,
        steps=[
            {
                "order": 1,
                "name": "lint_export_directory",
                "purpose": "Read | local\rstate.",
                "command": (
                    "fashion-radar community-signal-lint-dir ./exports "
                    "--source-name 'A | B'\n--strict"
                ),
                "suggested_effect": "read_only",
            }
        ],
        boundaries=["Does not run | generated\ncommands."],
    )

    assert render_external_tool_readiness_table(readiness) == [
        "External tool readiness.",
        "Contract version: external-tool-readiness/v1",
        "Execution mode: local_read_only",
        "Commands were not executed.",
        "Adapter: tool/one",
        "Display name: Tool / One",
        "Platform label: platform/one",
        "Directory: ./exports",
        "Input format: csv",
        "Pattern: *.csv",
        "As of: 2026-06-13T12:00:00+00:00",
        "Config dir: ./configs",
        "Data dir: ./data",
        "Source name: Source / One",
        "Checks:",
        "Check | Status | Command | Resolved Path | Install Hint | Detail",
        "upstream_command | missing | tool-one |  | Install / from upstream docs. | "
        "Command / not found on PATH.",
        "Steps: 1",
        "Order | Step | Suggested Effect | Purpose | Command",
        "1 | lint_export_directory | read_only | Read / local state. | "
        "fashion-radar community-signal-lint-dir ./exports --source-name 'A / B' --strict",
        "Boundaries:",
        "- Does not run / generated commands.",
    ]


def test_readiness_boundaries_include_external_tool_no_scope_terms() -> None:
    boundary_text = " ".join(EXTERNAL_TOOL_READINESS_BOUNDARIES)

    for term in (
        "local read-only",
        "Does not run generated commands.",
        "Does not run adapters or upstream tools.",
        "Does not inspect the supplied directory.",
        "No platform collection",
        "no connectors",
        "no scraping",
        "no browser automation",
        "no platform APIs",
        "no media downloads",
        "no monitoring",
        "no scheduling",
        "no source acquisition",
        "no demand proof",
        "no ranking",
        "no coverage verification",
    ):
        assert term in boundary_text


def test_readiness_model_rejects_extra_fields_and_missing_required_fields() -> None:
    payload = build_external_tool_readiness(
        adapter_id="instaloader",
        directory=Path("./exports"),
        config_dir=Path("./configs"),
        data_dir=Path("./data"),
        as_of="2026-06-13T12:00:00Z",
        which=lambda _command: None,
    ).model_dump(mode="json")

    with pytest.raises(ValidationError, match="Extra inputs are not permitted"):
        ExternalToolReadiness.model_validate({**payload, "unexpected": "value"})

    without_contract_version = {
        key: value for key, value in payload.items() if key != "contract_version"
    }
    with pytest.raises(ValidationError, match="Field required"):
        ExternalToolReadiness.model_validate(without_contract_version)


def test_readiness_command_specs_cover_adapter_registry() -> None:
    registry = build_external_tool_adapter_registry(
        directory=Path("./exports"),
        config_dir=Path("./configs"),
        data_dir=Path("./data"),
        as_of="2026-06-13T12:00:00Z",
    )

    for adapter in registry.adapters:
        readiness = build_external_tool_readiness(
            adapter_id=adapter.id,
            directory=Path("./exports"),
            config_dir=Path("./configs"),
            data_dir=Path("./data"),
            as_of="2026-06-13T12:00:00Z",
            which=lambda _command: None,
        )

        assert readiness.adapter_id == adapter.id
        assert len(readiness.checks) == 1
