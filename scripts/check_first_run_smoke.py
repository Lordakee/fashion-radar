#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import shlex
import shutil
import subprocess
import sys
import tempfile
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any

AS_OF = "2026-06-13T12:00:00Z"
SOURCE_NAME = "Community Tool Export"
EXAMPLE_CSV = Path("examples/community-signals.example.csv")
DIR_EXPORT_CSV = "community-signals.csv"
DIR_PATTERN = "*.csv"
EXPECTED_WORKFLOW_AS_OF = "2026-06-13T12:00:00+00:00"
EXPECTED_COMMUNITY_HANDOFF_INPUT_FORMAT = "csv"
EXPECTED_IMPORTED_REVIEW_LOOKBACK_DAYS = 7
EXPECTED_IMPORTED_REVIEW_CURRENT_DAYS = 7
EXPECTED_IMPORTED_REVIEW_BASELINE_DAYS = 7
EXPECTED_SAMPLE_ROWS = (
    {
        "url": "https://example.com/community/the-row-margaux-tote",
        "title": "The Row Margaux tote interest",
        "published_at": "2026-06-12T08:00:00Z",
        "summary": "Sanitized local note about The Row Margaux handbag and tote demand",
        "source_name": SOURCE_NAME,
        "platform": "community",
        "source_weight": "1.3",
        "collected_at": "2026-06-12T08:30:00Z",
    },
    {
        "url": "https://example.com/community/ballet-flats-footwear",
        "title": "Ballet flats footwear mention",
        "published_at": "2026-06-12T09:00:00Z",
        "summary": "Short sanitized note about ballet flats shoes and footwear styling",
        "source_name": SOURCE_NAME,
        "platform": "community",
        "source_weight": "1.1",
        "collected_at": "2026-06-12T09:20:00Z",
    },
)
EXPECTED_SAMPLE_TITLES = tuple(row["title"] for row in EXPECTED_SAMPLE_ROWS)
EXPECTED_SAMPLE_ENTITIES = ("The Row", "The Row Margaux", "Ballet Flats")
EXPECTED_PLATFORM_COUNTS = {"community": 2}
EXPECTED_SOURCE_COUNTS = {SOURCE_NAME: 2}
EXPECTED_EXTERNAL_TOOL_TEMPLATE_FIELDS = (
    "url",
    "title",
    "published_at",
    "summary",
    "source_name",
    "platform",
    "source_weight",
    "collected_at",
)
EXPECTED_EXTERNAL_TOOL_TEMPLATE_ITEMS = [
    {
        "url": "https://example.com/external-tool-template/rednote_mcp/the-row-bag",
        "title": "Rednote MCP Export The Row bag observed signal",
        "published_at": "2026-06-13T12:00:00+00:00",
        "summary": (
            "Synthetic sanitized observation about The Row bag interest from a "
            "user-controlled external/community tool."
        ),
        "source_name": "Rednote MCP Export",
        "platform": "rednote",
        "source_weight": 1.2,
        "collected_at": "2026-06-13T12:15:00+00:00",
    },
    {
        "url": "https://example.com/external-tool-template/rednote_mcp/silver-flat-shoe",
        "title": "Rednote MCP Export silver flat shoe observed signal",
        "published_at": "2026-06-13T13:00:00+00:00",
        "summary": (
            "Synthetic sanitized observation about silver flat shoes and styling "
            "from a user-controlled external/community tool."
        ),
        "source_name": "Rednote MCP Export",
        "platform": "rednote",
        "source_weight": 1.1,
        "collected_at": "2026-06-13T13:15:00+00:00",
    },
]
EXPECTED_IMPORTED_REVIEW_WORKFLOW_STEPS = (
    "summarize_imported_sources",
    "refresh_stored_matches",
    "compare_imported_entities",
    "review_imported_entity_evidence",
    "review_imported_candidate_phrases",
    "review_unmatched_imported_rows",
    "review_local_heat_movers",
)
EXPECTED_COMMUNITY_HANDOFF_WORKFLOW_STEPS = (
    "lint_handoff_directory",
    "preview_candidate_phrases",
    "review_handoff_readiness",
    "dry_run_directory_import",
    "import_directory_signals",
    "print_post_import_review",
)
EXPECTED_EXTERNAL_TOOL_WORKFLOW_STEPS = (
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
EXPECTED_EXTERNAL_TOOL_READINESS_STEPS = (
    "inspect_adapter_registry",
    "print_adapter_template_json",
    "print_external_tool_workflow",
    "print_signal_profile",
    "lint_export_directory",
    "review_handoff_readiness",
    "dry_run_directory_import",
)
EXPECTED_EXTERNAL_TOOL_READINESS_INSTALL_HINT = (
    "npm config set registry https://registry.npmmirror.com && npm install -g rednote-mcp"
)
EXPECTED_EXTERNAL_TOOL_READINESS_DETAIL = (
    "Checks whether the Rednote MCP command is discoverable locally."
)
# Pinned independently from the runtime registry so first-run smoke catches
# adapter registry drift instead of importing the code under test.
EXPECTED_EXTERNAL_TOOL_ADAPTERS = {
    "rednote_mcp": ("rednote", "json", "*.json", "Rednote MCP Export"),
    "xiaohongshu_crawler": (
        "xiaohongshu",
        "csv",
        "*.csv",
        "Xiaohongshu Crawler Export",
    ),
    "instaloader": ("instagram", "json", "*.json", "Instaloader Export"),
    "tiktok_api": ("tiktok", "json", "*.json", "TikTok-Api Export"),
    "yt_dlp": ("media", "json", "*.json", "yt-dlp Metadata Export"),
    "x_search_export": ("x", "csv", "*.csv", "X Search Export"),
    "xpoz_mcp": ("community", "json", "*.json", "XPOZ MCP Export"),
    "generic_community_export": ("community", "csv", "*.csv", "Generic Community Export"),
}
EXPECTED_EXTERNAL_TOOL_COMMAND_NAMES = (
    "community-signal-profile",
    "external-tool-readiness",
    "community-handoff-manifest",
    "community-handoff-workflow",
    "community-signal-lint-dir",
    "community-handoff-check-dir",
    "import-signals-dir",
    "import-signals-dir",
    "imported-review-workflow",
)
EXPECTED_EXTERNAL_TOOL_REGISTRY_KEYS = (
    "contract_version",
    "execution_mode",
    "adapters",
    "boundaries",
)
EXPECTED_EXTERNAL_TOOL_WORKFLOW_BOUNDARIES = (
    "Prints local external/community tool handoff workflow commands only.",
    "Does not run generated commands.",
    "Does not run adapters or upstream tools.",
    "Does not inspect the supplied directory.",
    "Does not read handoff files, validate files, import rows, or open SQLite.",
    "Does not write config, data, report, dashboard, or workflow artifacts.",
    (
        "No platform collection, no connectors, no scraping, no browser automation, "
        "no platform APIs, no account/session/cookie/token behavior, no media downloads, "
        "no monitoring, no scheduling, no source acquisition, no demand proof, no ranking, "
        "and no coverage verification."
    ),
    "Does not provide a compliance-review workflow.",
)
EXPECTED_EXTERNAL_TOOL_ADAPTER_KEYS = (
    "id",
    "display_name",
    "platform_label",
    "suggested_source_name",
    "recommended_input_format",
    "recommended_pattern",
    "suggested_export_directory",
    "description",
    "upstream_tool_examples",
    "field_mappings",
    "recommended_commands",
    "boundaries",
)
EXPECTED_EXTERNAL_TOOL_ADAPTER_DETAILS = {
    "rednote_mcp": {
        "description": (
            "Metadata target for Rednote/Xiaohongshu MCP exports that already "
            "produce sanitized local observations."
        ),
        "upstream_tool_examples": ["rednote-mcp"],
    },
    "xiaohongshu_crawler": {
        "description": (
            "Metadata target for user-controlled Xiaohongshu crawler exports "
            "converted to the community signal row shape."
        ),
        "upstream_tool_examples": ["xiaohongshu-crawler"],
    },
    "instaloader": {
        "description": (
            "Metadata target for sanitized Instagram post or profile exports "
            "created outside Fashion Radar."
        ),
        "upstream_tool_examples": ["Instaloader"],
    },
    "tiktok_api": {
        "description": (
            "Metadata target for sanitized TikTok observations exported by a "
            "user-controlled upstream tool."
        ),
        "upstream_tool_examples": ["TikTok-Api"],
    },
    "yt_dlp": {
        "description": (
            "Metadata target for sanitized media metadata exports, not media "
            "downloads or stored video assets."
        ),
        "upstream_tool_examples": ["yt-dlp"],
    },
    "x_search_export": {
        "description": (
            "Metadata target for sanitized X/search exports created outside Fashion Radar."
        ),
        "upstream_tool_examples": ["AnySearch X export", "snscrape export"],
    },
    "xpoz_mcp": {
        "description": (
            "Metadata target for sanitized XPOZ MCP / Social Data API exports "
            "created outside Fashion Radar."
        ),
        "upstream_tool_examples": ["XPOZ MCP", "XPOZ Social Data API"],
    },
    "generic_community_export": {
        "description": (
            "Metadata target for any user-controlled community source already "
            "converted to sanitized local signal rows."
        ),
        "upstream_tool_examples": ["manual spreadsheet export", "community research export"],
    },
}
EXPECTED_EXTERNAL_TOOL_FIELD_MAPPINGS = [
    {
        "field": "url",
        "required": True,
        "note": "Stable source URL or local reference URL for the observed item.",
    },
    {
        "field": "title",
        "required": True,
        "note": "Short observed text, headline, caption summary, or normalized signal phrase.",
    },
    {
        "field": "published_at",
        "required": True,
        "note": "ISO 8601-compatible publication or observation timestamp.",
    },
    {
        "field": "summary",
        "required": False,
        "note": "Short sanitized local review note without raw comments or full post bodies.",
    },
    {
        "field": "source_name",
        "required": False,
        "note": "Producer/export display name for the local handoff rows.",
    },
    {
        "field": "platform",
        "required": False,
        "note": "Short local provenance label for review summaries.",
    },
    {
        "field": "source_weight",
        "required": False,
        "note": "Optional local weight in the existing community signal range (0, 5].",
    },
    {
        "field": "collected_at",
        "required": False,
        "note": "Timestamp for when the upstream tool produced the sanitized row.",
    },
]
EXPECTED_EXTERNAL_TOOL_ADAPTER_BOUNDARIES = [
    "Local producer-discovery metadata only.",
    "Writes should target sanitized CSV/JSON local handoff rows.",
    "Platform label is local provenance only.",
    "No platform collection, connector execution, scraping, browser automation, or API calls.",
]
EXPECTED_EXTERNAL_TOOL_REGISTRY_BOUNDARIES = [
    "Does not run adapters.",
    "Does not inspect the supplied directory.",
    "Does not read handoff files, validate files, import rows, or open SQLite.",
    "Does not create config, data, report, dashboard, or workflow artifacts.",
    (
        "Does not fetch URLs, search platforms, log in, store cookies, automate "
        "browsers, call platform APIs, monitor communities, schedule work, add "
        "source/platform connectors, acquire sources, prove demand, rank sources, "
        "or verify platform coverage."
    ),
    "Does not provide a compliance-review workflow.",
]
EXPECTED_EXTERNAL_TOOL_READINESS_BOUNDARIES = (
    "Prints local read-only external/community tool readiness guidance only.",
    "Checks PATH availability only through shutil.which for mapped upstream commands.",
    "Commands were not executed.",
    "Does not run generated commands.",
    "Does not run adapters or upstream tools.",
    "Does not import upstream tools.",
    "Does not inspect the supplied directory.",
    "Does not read handoff files, validate files, import rows, or open SQLite.",
    "Does not write config, data, report, dashboard, or workflow artifacts.",
    (
        "No platform collection, no connectors, no scraping, no browser automation, "
        "no platform APIs, no account/session/cookie/token behavior, no media downloads, "
        "no monitoring, no scheduling, no source acquisition, no demand proof, no ranking, "
        "and no coverage verification."
    ),
    "Does not provide a compliance-review product feature.",
)


class SmokeError(Exception):
    """Raised when the first-run smoke check fails."""


@dataclass(frozen=True)
class SmokeContext:
    repo_root: Path
    python: str
    runtime_dir: Path
    config_dir: Path
    data_dir: Path
    reports_dir: Path
    exports_dir: Path
    source_checkout: bool = True


def cli_command(context: SmokeContext, *args: str) -> list[str]:
    return [context.python, "-m", "fashion_radar", *args]


def command_environment(
    context: SmokeContext,
    base_env: Mapping[str, str] | None = None,
    *,
    source_checkout: bool = True,
) -> dict[str, str]:
    env = dict(os.environ if base_env is None else base_env)
    # Keep print-only adapter registry commands deterministic in source and wheel smokes.
    env["FASHION_RADAR_CONFIG_DIR"] = "configs"
    env["FASHION_RADAR_DATA_DIR"] = "data"
    if not source_checkout:
        remove_pythonpath_entry(env, context.repo_root / "src", relative_to=context.repo_root)
        return env

    src_path = str(context.repo_root / "src")
    existing_pythonpath = env.get("PYTHONPATH")
    env["PYTHONPATH"] = (
        src_path if not existing_pythonpath else os.pathsep.join([src_path, existing_pythonpath])
    )
    return env


def remove_pythonpath_entry(env: dict[str, str], entry: Path, *, relative_to: Path) -> None:
    pythonpath = env.get("PYTHONPATH")
    if not pythonpath:
        return

    target = entry.resolve()
    kept = [
        value
        for value in pythonpath.split(os.pathsep)
        if value and resolve_pythonpath_entry(value, relative_to=relative_to) != target
    ]
    if kept:
        env["PYTHONPATH"] = os.pathsep.join(kept)
    else:
        env.pop("PYTHONPATH", None)


def resolve_pythonpath_entry(value: str, *, relative_to: Path) -> Path:
    path = Path(value)
    if not path.is_absolute():
        path = relative_to / path
    return path.resolve()


def validate_json_output(command_name: str, output: str) -> Any:
    try:
        return json.loads(output)
    except json.JSONDecodeError as exc:
        raise SmokeError(f"{command_name} output is not valid JSON: {exc}") from exc


def assert_equal(label: str, actual: Any, expected: Any) -> None:
    if actual != expected:
        raise SmokeError(f"{label} expected {expected!r}, got {actual!r}")


def expected_external_tool_command(*parts: str) -> str:
    return shlex.join(("fashion-radar", *parts))


def validate_expected_external_tool_command(
    command_name: str,
    label: str,
    command: object,
    *parts: str,
) -> None:
    try:
        actual_parts = shlex.split(str(command))
    except ValueError as exc:
        raise SmokeError(f"{command_name} {label} command is not shell-parseable: {exc}") from exc
    assert_equal(
        f"{command_name} {label} command",
        actual_parts,
        ["fashion-radar", *parts],
    )


def expected_imported_review_workflow_command_parts(
    *,
    config_dir: str,
    data_dir: str,
    as_of: str,
    source_name: str,
    lookback_days: str,
    current_days: str,
    baseline_days: str,
) -> tuple[tuple[str, tuple[str, ...]], ...]:
    source_args = ("--source-name", source_name) if source_name else ()
    return (
        ("summary", ("imported-signals-summary", "--data-dir", data_dir)),
        ("match refresh", ("match", "--config-dir", config_dir, "--data-dir", data_dir)),
        (
            "entity delta",
            (
                "imported-entity-deltas",
                "--data-dir",
                data_dir,
                "--as-of",
                as_of,
                "--current-days",
                current_days,
                "--baseline-days",
                baseline_days,
                *source_args,
            ),
        ),
        (
            "entity evidence",
            (
                "imported-entity-evidence",
                "--data-dir",
                data_dir,
                "--as-of",
                as_of,
                "--entity-name",
                "The Row",
                "--entity-type",
                "brand",
                "--current-days",
                current_days,
                "--baseline-days",
                baseline_days,
                *source_args,
            ),
        ),
        (
            "candidate",
            (
                "imported-candidates",
                "--config-dir",
                config_dir,
                "--data-dir",
                data_dir,
                "--as-of",
                as_of,
                *source_args,
            ),
        ),
        (
            "unmatched rows",
            (
                "imported-signals",
                "--data-dir",
                data_dir,
                "--as-of",
                as_of,
                "--lookback-days",
                lookback_days,
                "--unmatched-only",
                *source_args,
            ),
        ),
        (
            "final heat",
            ("heat-movers", "--config-dir", config_dir, "--data-dir", data_dir, "--as-of", as_of),
        ),
    )


def expected_community_handoff_workflow_command_parts(
    *,
    directory: str,
    input_format: str,
    pattern: str,
    config_dir: str,
    data_dir: str,
    as_of: str,
    source_name: str,
) -> tuple[tuple[str, tuple[str, ...]], ...]:
    return (
        (
            "lint_handoff_directory",
            (
                "community-signal-lint-dir",
                directory,
                "--input-format",
                input_format,
                "--pattern",
                pattern,
                "--source-name",
                source_name,
                "--strict",
            ),
        ),
        (
            "preview_candidate_phrases",
            (
                "community-candidates-dir",
                directory,
                "--input-format",
                input_format,
                "--pattern",
                pattern,
                "--config-dir",
                config_dir,
                "--as-of",
                as_of,
                "--source-name",
                source_name,
            ),
        ),
        (
            "review_handoff_readiness",
            (
                "community-handoff-check-dir",
                directory,
                "--input-format",
                input_format,
                "--pattern",
                pattern,
                "--config-dir",
                config_dir,
                "--as-of",
                as_of,
                "--source-name",
                source_name,
                "--strict",
            ),
        ),
        (
            "dry_run_directory_import",
            (
                "import-signals-dir",
                directory,
                "--format",
                input_format,
                "--pattern",
                pattern,
                "--data-dir",
                data_dir,
                "--source-name",
                source_name,
                "--imported-at",
                as_of,
                "--dry-run",
            ),
        ),
        (
            "import_directory_signals",
            (
                "import-signals-dir",
                directory,
                "--format",
                input_format,
                "--pattern",
                pattern,
                "--data-dir",
                data_dir,
                "--source-name",
                source_name,
                "--imported-at",
                as_of,
            ),
        ),
        (
            "print_post_import_review",
            (
                "imported-review-workflow",
                "--config-dir",
                config_dir,
                "--data-dir",
                data_dir,
                "--as-of",
                as_of,
                "--source-name",
                source_name,
            ),
        ),
    )


def expected_external_tool_adapter_commands(
    *,
    adapter_id: str,
    input_format: str,
    pattern: str,
    source_name: str,
) -> list[str]:
    return [
        expected_external_tool_command("community-signal-profile", "--format", "json"),
        expected_external_tool_command(
            "external-tool-readiness",
            "--adapter",
            adapter_id,
            "--directory",
            "exports",
            "--config-dir",
            "configs",
            "--data-dir",
            "data",
            "--as-of",
            "2026-06-13T12:00:00+00:00",
            "--input-format",
            input_format,
            "--pattern",
            pattern,
            "--source-name",
            source_name,
            "--format",
            "table",
        ),
        expected_external_tool_command(
            "community-handoff-manifest",
            "exports",
            "--input-format",
            input_format,
            "--pattern",
            pattern,
            "--config-dir",
            "configs",
            "--data-dir",
            "data",
            "--as-of",
            "2026-06-13T12:00:00+00:00",
            "--source-name",
            source_name,
            "--format",
            "json",
        ),
        expected_external_tool_command(
            "community-handoff-workflow",
            "exports",
            "--input-format",
            input_format,
            "--pattern",
            pattern,
            "--config-dir",
            "configs",
            "--data-dir",
            "data",
            "--as-of",
            "2026-06-13T12:00:00+00:00",
            "--source-name",
            source_name,
        ),
        expected_external_tool_command(
            "community-signal-lint-dir",
            "exports",
            "--input-format",
            input_format,
            "--pattern",
            pattern,
            "--source-name",
            source_name,
            "--strict",
        ),
        expected_external_tool_command(
            "community-handoff-check-dir",
            "exports",
            "--input-format",
            input_format,
            "--pattern",
            pattern,
            "--config-dir",
            "configs",
            "--as-of",
            "2026-06-13T12:00:00+00:00",
            "--source-name",
            source_name,
            "--strict",
        ),
        expected_external_tool_command(
            "import-signals-dir",
            "exports",
            "--format",
            input_format,
            "--pattern",
            pattern,
            "--source-name",
            source_name,
            "--data-dir",
            "data",
            "--imported-at",
            "2026-06-13T12:00:00+00:00",
            "--dry-run",
        ),
        expected_external_tool_command(
            "import-signals-dir",
            "exports",
            "--format",
            input_format,
            "--pattern",
            pattern,
            "--source-name",
            source_name,
            "--data-dir",
            "data",
            "--imported-at",
            "2026-06-13T12:00:00+00:00",
        ),
        expected_external_tool_command(
            "imported-review-workflow",
            "--config-dir",
            "configs",
            "--data-dir",
            "data",
            "--as-of",
            "2026-06-13T12:00:00+00:00",
            "--source-name",
            source_name,
        ),
    ]


def validate_sample_csv(path: Path) -> None:
    with path.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))

    assert_equal("sample CSV row count", len(rows), len(EXPECTED_SAMPLE_ROWS))
    for index, expected in enumerate(EXPECTED_SAMPLE_ROWS):
        row = rows[index]
        for key, expected_value in expected.items():
            assert_equal(
                f"sample CSV row {index + 1} {key}",
                row.get(key),
                expected_value,
            )


def validate_community_candidates(
    command_name: str,
    payload: Any,
    *,
    directory: bool = False,
) -> None:
    if not isinstance(payload, dict):
        raise SmokeError(f"{command_name} output must be a JSON object")
    assert_equal(f"{command_name} input_format", payload.get("input_format"), "csv")
    assert_equal(f"{command_name} source_name", payload.get("source_name"), SOURCE_NAME)
    assert_equal(f"{command_name} row_count", payload.get("row_count"), 2)
    assert_equal(f"{command_name} candidate_count", payload.get("candidate_count"), 0)
    assert_equal(f"{command_name} candidates", payload.get("candidates"), [])
    assert_equal(f"{command_name} as_of", payload.get("as_of"), "2026-06-13T12:00:00+00:00")
    if directory:
        assert_equal(f"{command_name} file_count", payload.get("file_count"), 1)


def assert_output_contains(command_name: str, output: str, expected_lines: Sequence[str]) -> None:
    output_lines = {line.strip() for line in output.splitlines() if line.strip()}
    for expected in expected_lines:
        if expected not in output_lines:
            raise SmokeError(f"{command_name} output missing expected text: {expected}")


def validate_import_signals_dry_run(output: str) -> None:
    assert_output_contains(
        "import-signals --dry-run",
        output,
        ("Validated 2 manual signal rows", "Dry run: no rows imported"),
    )


def validate_import_signals_import(output: str) -> None:
    assert_output_contains(
        "import-signals",
        output,
        ("Validated 2 manual signal rows", "Imported 2 manual signal rows", "Items added: 2"),
    )


def validate_import_signals_dir_dry_run(output: str) -> None:
    output_lines = {line.strip() for line in output.splitlines() if line.strip()}
    assert_output_contains(
        "import-signals-dir --dry-run",
        output,
        (
            "Files: 1 total, 1 valid",
            "Rows: 2 import-ready",
            "Sources: Community Tool Export=2",
            "Platforms: community=2",
            "Errors: 0",
            "No manual signal directory dry-run errors.",
        ),
    )
    expected_file_suffix = f"{DIR_EXPORT_CSV}: 2 rows, 0 errors"
    if not any(line.endswith(expected_file_suffix) for line in output_lines):
        raise SmokeError(
            f"import-signals-dir --dry-run output missing expected text: {expected_file_suffix}"
        )


def validate_imported_summary(command_name: str, payload: Any) -> None:
    if not isinstance(payload, dict):
        raise SmokeError(f"{command_name} output must be a JSON object")

    assert_equal(f"{command_name} row_count", payload.get("row_count"), 2)
    assert_equal(f"{command_name} source_count", payload.get("source_count"), 1)
    assert_equal(f"{command_name} matched_count", payload.get("matched_count"), 2)
    assert_equal(f"{command_name} unmatched_count", payload.get("unmatched_count"), 0)
    assert_equal(
        f"{command_name} platform_counts",
        payload.get("platform_counts"),
        EXPECTED_PLATFORM_COUNTS,
    )
    sources = payload.get("sources")
    if not isinstance(sources, list) or len(sources) != 1:
        raise SmokeError(f"{command_name} must report exactly one source")
    source = sources[0]
    if not isinstance(source, dict):
        raise SmokeError(f"{command_name} source summary must be a JSON object")
    assert_equal(f"{command_name} source name", source.get("source_name"), SOURCE_NAME)
    assert_equal(f"{command_name} source row_count", source.get("row_count"), 2)
    assert_equal(f"{command_name} source matched_count", source.get("matched_count"), 2)


def validate_imported_signals(command_name: str, payload: Any) -> None:
    if not isinstance(payload, dict):
        raise SmokeError(f"{command_name} output must be a JSON object")
    assert_equal(f"{command_name} row_count", payload.get("row_count"), 2)
    assert_equal(f"{command_name} total_count", payload.get("total_count"), 2)
    assert_equal(f"{command_name} matched_count", payload.get("matched_count"), 2)
    assert_equal(f"{command_name} unmatched_count", payload.get("unmatched_count"), 0)
    assert_equal(
        f"{command_name} source_name_counts",
        payload.get("source_name_counts"),
        EXPECTED_SOURCE_COUNTS,
    )
    assert_equal(
        f"{command_name} platform_counts",
        payload.get("platform_counts"),
        EXPECTED_PLATFORM_COUNTS,
    )
    items = payload.get("items")
    if not isinstance(items, list) or len(items) != 2:
        raise SmokeError(f"{command_name} must contain exactly two sample items")

    titles = [item.get("title") for item in items if isinstance(item, dict)]
    assert_equal(
        f"{command_name} item titles",
        titles,
        ["Ballet flats footwear mention", "The Row Margaux tote interest"],
    )

    matches_by_title: dict[str, set[str]] = {}
    for item in items:
        if not isinstance(item, dict):
            continue
        if item.get("match_status") != "matched":
            raise SmokeError(f"{command_name} item must be marked matched: {item.get('title')}")
        matches = item.get("matches")
        if not isinstance(matches, list):
            matches = []
        matches_by_title[str(item.get("title"))] = {
            str(match.get("entity_name"))
            for match in matches
            if isinstance(match, dict) and match.get("entity_name") is not None
        }

    for title in EXPECTED_SAMPLE_TITLES:
        if title not in matches_by_title:
            raise SmokeError(f"{command_name} missing sample title: {title}")
    if "Ballet Flats" not in matches_by_title["Ballet flats footwear mention"]:
        raise SmokeError(f"{command_name} missing Ballet Flats match")
    row_matches = matches_by_title["The Row Margaux tote interest"]
    for expected_entity in ("The Row", "The Row Margaux"):
        if expected_entity not in row_matches:
            raise SmokeError(f"{command_name} missing {expected_entity} match")


def validate_imported_review_workflow(command_name: str, payload: Any) -> None:
    if not isinstance(payload, dict):
        raise SmokeError(f"{command_name} output must be a JSON object")
    assert_equal(f"{command_name} execution_mode", payload.get("execution_mode"), "print_only")
    assert_equal(f"{command_name} step_count", payload.get("step_count"), 7)
    steps = payload.get("steps")
    if not isinstance(steps, list):
        raise SmokeError(f"{command_name} steps must be a list")
    names = [step.get("name") for step in steps if isinstance(step, dict)]
    assert_equal(
        f"{command_name} step names",
        names,
        list(EXPECTED_IMPORTED_REVIEW_WORKFLOW_STEPS),
    )
    assert_equal(f"{command_name} as_of", payload.get("as_of"), EXPECTED_WORKFLOW_AS_OF)
    assert_equal(f"{command_name} source_name", payload.get("source_name"), SOURCE_NAME)
    assert_equal(
        f"{command_name} lookback_days",
        payload.get("lookback_days"),
        EXPECTED_IMPORTED_REVIEW_LOOKBACK_DAYS,
    )
    assert_equal(
        f"{command_name} current_days",
        payload.get("current_days"),
        EXPECTED_IMPORTED_REVIEW_CURRENT_DAYS,
    )
    assert_equal(
        f"{command_name} baseline_days",
        payload.get("baseline_days"),
        EXPECTED_IMPORTED_REVIEW_BASELINE_DAYS,
    )
    config_dir = str(payload.get("config_dir", ""))
    data_dir = str(payload.get("data_dir", ""))
    as_of = EXPECTED_WORKFLOW_AS_OF
    source_name = SOURCE_NAME
    lookback_days = str(EXPECTED_IMPORTED_REVIEW_LOOKBACK_DAYS)
    current_days = str(EXPECTED_IMPORTED_REVIEW_CURRENT_DAYS)
    baseline_days = str(EXPECTED_IMPORTED_REVIEW_BASELINE_DAYS)

    expected_commands = expected_imported_review_workflow_command_parts(
        config_dir=config_dir,
        data_dir=data_dir,
        as_of=as_of,
        source_name=source_name,
        lookback_days=lookback_days,
        current_days=current_days,
        baseline_days=baseline_days,
    )
    for index, (label, expected_parts) in enumerate(expected_commands):
        step = steps[index]
        if not isinstance(step, dict):
            raise SmokeError(f"{command_name} {label} step must be a JSON object")
        validate_expected_external_tool_command(
            command_name,
            label,
            step.get("command", ""),
            *expected_parts,
        )

    heat_step = steps[-1]
    if not isinstance(heat_step, dict):
        raise SmokeError(f"{command_name} heat step must be a JSON object")
    assert_equal(f"{command_name} final step", heat_step.get("name"), "review_local_heat_movers")


def validate_community_handoff_workflow(command_name: str, payload: Any) -> None:
    if not isinstance(payload, dict):
        raise SmokeError(f"{command_name} output must be a JSON object")
    assert_equal(f"{command_name} execution_mode", payload.get("execution_mode"), "print_only")
    assert_equal(f"{command_name} step_count", payload.get("step_count"), 6)
    steps = payload.get("steps")
    if not isinstance(steps, list):
        raise SmokeError(f"{command_name} steps must be a list")
    if len(steps) != len(EXPECTED_COMMUNITY_HANDOFF_WORKFLOW_STEPS):
        raise SmokeError(
            f"{command_name} step_count expected "
            f"{len(EXPECTED_COMMUNITY_HANDOFF_WORKFLOW_STEPS)!r}, got {len(steps)!r}"
        )
    for index, step in enumerate(steps, start=1):
        if not isinstance(step, dict):
            raise SmokeError(f"{command_name} step {index} must be a JSON object")
    names = [step.get("name") for step in steps]
    assert_equal(
        f"{command_name} step names",
        names,
        list(EXPECTED_COMMUNITY_HANDOFF_WORKFLOW_STEPS),
    )
    assert_equal(
        f"{command_name} input_format",
        payload.get("input_format"),
        EXPECTED_COMMUNITY_HANDOFF_INPUT_FORMAT,
    )
    assert_equal(f"{command_name} pattern", payload.get("pattern"), DIR_PATTERN)
    assert_equal(f"{command_name} as_of", payload.get("as_of"), EXPECTED_WORKFLOW_AS_OF)
    assert_equal(f"{command_name} source_name", payload.get("source_name"), SOURCE_NAME)
    directory = str(payload.get("directory", ""))
    input_format = EXPECTED_COMMUNITY_HANDOFF_INPUT_FORMAT
    pattern = DIR_PATTERN
    config_dir = str(payload.get("config_dir", ""))
    data_dir = str(payload.get("data_dir", ""))
    as_of = EXPECTED_WORKFLOW_AS_OF
    source_name = SOURCE_NAME

    expected_commands = expected_community_handoff_workflow_command_parts(
        directory=directory,
        input_format=input_format,
        pattern=pattern,
        config_dir=config_dir,
        data_dir=data_dir,
        as_of=as_of,
        source_name=source_name,
    )
    for index, (label, expected_parts) in enumerate(expected_commands):
        step = steps[index]
        if not isinstance(step, dict):
            raise SmokeError(f"{command_name} {label} step must be a JSON object")
        validate_expected_external_tool_command(
            command_name,
            label,
            step.get("command", ""),
            *expected_parts,
        )

    import_step = steps[4]
    if not isinstance(import_step, dict):
        raise SmokeError(f"{command_name} import step must be a JSON object")
    assert_equal(
        f"{command_name} import step effect",
        import_step.get("suggested_effect"),
        "updates_local_imports",
    )

    post_review_step = steps[5]
    if not isinstance(post_review_step, dict):
        raise SmokeError(f"{command_name} post-review step must be a JSON object")
    assert_equal(
        f"{command_name} post-review step effect",
        post_review_step.get("suggested_effect"),
        "print_only",
    )


def validate_external_tool_adapters(command_name: str, payload: Any) -> None:
    if not isinstance(payload, dict):
        raise SmokeError(f"{command_name} output must be a JSON object")
    assert_equal(
        f"{command_name} contract_version",
        payload.get("contract_version"),
        "external-tool-adapters/v1",
    )
    assert_equal(f"{command_name} execution_mode", payload.get("execution_mode"), "print_only")
    adapters = payload.get("adapters")
    if not isinstance(adapters, list) or not adapters:
        raise SmokeError(f"{command_name} adapters must be a non-empty list")
    adapter_ids: list[str] = []
    for index, adapter in enumerate(adapters, start=1):
        if not isinstance(adapter, dict):
            raise SmokeError(f"{command_name} adapter {index} must be a JSON object")
        adapter_id = str(adapter.get("id", ""))
        adapter_ids.append(adapter_id)

    assert_equal(
        f"{command_name} adapter ids",
        adapter_ids,
        list(EXPECTED_EXTERNAL_TOOL_ADAPTERS),
    )

    def required_readiness_value(parts: list[str], adapter_id: str, flag: str) -> str:
        if flag not in parts:
            raise SmokeError(f"{command_name} {adapter_id} readiness command missing {flag!r}")
        index = parts.index(flag)
        if index + 1 >= len(parts):
            raise SmokeError(
                f"{command_name} {adapter_id} readiness command missing value for {flag!r}"
            )
        value = parts[index + 1]
        if not value or value.startswith("--"):
            raise SmokeError(
                f"{command_name} {adapter_id} readiness command missing value for {flag!r}"
            )
        return value

    for adapter in adapters:
        adapter_id = str(adapter["id"])
        platform_label, input_format, pattern, source_name = EXPECTED_EXTERNAL_TOOL_ADAPTERS[
            adapter_id
        ]
        assert_equal(
            f"{command_name} {adapter_id} display_name",
            adapter.get("display_name"),
            source_name,
        )
        assert_equal(
            f"{command_name} {adapter_id} platform_label",
            adapter.get("platform_label"),
            platform_label,
        )
        assert_equal(
            f"{command_name} {adapter_id} suggested_source_name",
            adapter.get("suggested_source_name"),
            source_name,
        )
        assert_equal(
            f"{command_name} {adapter_id} recommended_input_format",
            adapter.get("recommended_input_format"),
            input_format,
        )
        assert_equal(
            f"{command_name} {adapter_id} recommended_pattern",
            adapter.get("recommended_pattern"),
            pattern,
        )
        assert_equal(
            f"{command_name} {adapter_id} suggested_export_directory",
            adapter.get("suggested_export_directory"),
            "exports",
        )
        recommended_commands = adapter.get("recommended_commands")
        if not isinstance(recommended_commands, list):
            raise SmokeError(f"{command_name} {adapter_id} recommended_commands must be a list")
        command_parts: list[list[str]] = []
        for command_index, command in enumerate(recommended_commands, start=1):
            try:
                parts = shlex.split(str(command))
            except ValueError as exc:
                raise SmokeError(
                    f"{command_name} {adapter_id} command {command_index} is not "
                    f"shell-parseable: {exc}"
                ) from exc
            command_parts.append(parts)

        readiness_commands = [
            parts
            for parts in command_parts
            if parts[:2] == ["fashion-radar", "external-tool-readiness"]
        ]
        if not readiness_commands:
            raise SmokeError(f"{command_name} {adapter_id} missing external-tool-readiness command")
        if len(readiness_commands) != 1:
            raise SmokeError(
                f"{command_name} {adapter_id} must contain exactly one "
                "external-tool-readiness command"
            )
        assert_equal(
            f"{command_name} {adapter_id} command prefixes",
            [parts[:2] for parts in command_parts],
            [
                ["fashion-radar", expected_name]
                for expected_name in EXPECTED_EXTERNAL_TOOL_COMMAND_NAMES
            ],
        )
        readiness_parts = readiness_commands[0]
        assert_equal(
            f"{command_name} {adapter_id} readiness command prefix",
            readiness_parts[:2],
            ["fashion-radar", "external-tool-readiness"],
        )
        assert_equal(
            f"{command_name} {adapter_id} readiness adapter",
            required_readiness_value(readiness_parts, adapter_id, "--adapter"),
            adapter_id,
        )
        assert_equal(
            f"{command_name} {adapter_id} readiness directory",
            required_readiness_value(readiness_parts, adapter_id, "--directory"),
            "exports",
        )
        required_readiness_value(readiness_parts, adapter_id, "--config-dir")
        required_readiness_value(readiness_parts, adapter_id, "--data-dir")
        required_readiness_value(readiness_parts, adapter_id, "--as-of")
        assert_equal(
            f"{command_name} {adapter_id} readiness input_format",
            required_readiness_value(readiness_parts, adapter_id, "--input-format"),
            input_format,
        )
        assert_equal(
            f"{command_name} {adapter_id} readiness pattern",
            required_readiness_value(readiness_parts, adapter_id, "--pattern"),
            pattern,
        )
        assert_equal(
            f"{command_name} {adapter_id} readiness source_name",
            required_readiness_value(readiness_parts, adapter_id, "--source-name"),
            source_name,
        )
        assert_equal(
            f"{command_name} {adapter_id} readiness output format",
            required_readiness_value(readiness_parts, adapter_id, "--format"),
            "table",
        )
        assert_equal(
            f"{command_name} {adapter_id} keys",
            list(adapter),
            list(EXPECTED_EXTERNAL_TOOL_ADAPTER_KEYS),
        )
        adapter_details = EXPECTED_EXTERNAL_TOOL_ADAPTER_DETAILS[adapter_id]
        assert_equal(
            f"{command_name} {adapter_id} description",
            adapter.get("description"),
            adapter_details["description"],
        )
        assert_equal(
            f"{command_name} {adapter_id} upstream_tool_examples",
            adapter.get("upstream_tool_examples"),
            adapter_details["upstream_tool_examples"],
        )
        assert_equal(
            f"{command_name} {adapter_id} field_mappings",
            adapter.get("field_mappings"),
            EXPECTED_EXTERNAL_TOOL_FIELD_MAPPINGS,
        )
        assert_equal(
            f"{command_name} {adapter_id} recommended_commands",
            adapter.get("recommended_commands"),
            expected_external_tool_adapter_commands(
                adapter_id=adapter_id,
                input_format=input_format,
                pattern=pattern,
                source_name=source_name,
            ),
        )
        assert_equal(
            f"{command_name} {adapter_id} boundaries",
            adapter.get("boundaries"),
            EXPECTED_EXTERNAL_TOOL_ADAPTER_BOUNDARIES,
        )

    assert_equal(
        f"{command_name} keys",
        list(payload),
        list(EXPECTED_EXTERNAL_TOOL_REGISTRY_KEYS),
    )
    assert_equal(
        f"{command_name} boundaries",
        payload.get("boundaries"),
        EXPECTED_EXTERNAL_TOOL_REGISTRY_BOUNDARIES,
    )


def validate_external_tool_template(command_name: str, payload: Any) -> None:
    if not isinstance(payload, dict):
        raise SmokeError(f"{command_name} output must be a JSON object")
    assert_equal(f"{command_name} keys", list(payload), ["items"])
    items = payload.get("items")
    if not isinstance(items, list):
        raise SmokeError(f"{command_name} items must be a list")
    if len(items) != 2:
        raise SmokeError(f"{command_name} items must contain exactly 2 rows")
    for index, item in enumerate(items, start=1):
        if not isinstance(item, dict):
            raise SmokeError(f"{command_name} row {index} must be a JSON object")
        forbidden_fields = [
            key for key in item if key == "metadata" or key.startswith("_") or key.startswith("raw")
        ]
        if forbidden_fields:
            raise SmokeError(
                f"{command_name} row {index} contains private/raw field: {forbidden_fields[0]}"
            )
        for field in EXPECTED_EXTERNAL_TOOL_TEMPLATE_FIELDS:
            if field not in item:
                raise SmokeError(f"{command_name} row {index} {field} is required")
        extra_fields = set(item) - set(EXPECTED_EXTERNAL_TOOL_TEMPLATE_FIELDS)
        if extra_fields:
            raise SmokeError(
                f"{command_name} row {index} has unexpected field: {sorted(extra_fields)[0]}"
            )
        for field in EXPECTED_EXTERNAL_TOOL_TEMPLATE_FIELDS:
            if item.get(field) in (None, ""):
                raise SmokeError(f"{command_name} row {index} {field} must be populated")
        assert_equal(f"{command_name} row {index} platform", item.get("platform"), "rednote")
        assert_equal(
            f"{command_name} row {index} item",
            item,
            EXPECTED_EXTERNAL_TOOL_TEMPLATE_ITEMS[index - 1],
        )


def validate_external_tool_workflow(command_name: str, payload: Any) -> None:
    if not isinstance(payload, dict):
        raise SmokeError(f"{command_name} output must be a JSON object")
    assert_equal(
        f"{command_name} keys",
        list(payload),
        [
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
            "step_count",
            "steps",
            "boundaries",
        ],
    )
    assert_equal(
        f"{command_name} contract_version",
        payload.get("contract_version"),
        "external-tool-workflow/v1",
    )
    assert_equal(f"{command_name} execution_mode", payload.get("execution_mode"), "print_only")
    assert_equal(f"{command_name} adapter_id", payload.get("adapter_id"), "rednote_mcp")
    assert_equal(f"{command_name} platform_label", payload.get("platform_label"), "rednote")
    assert_equal(f"{command_name} input_format", payload.get("input_format"), "json")
    assert_equal(f"{command_name} pattern", payload.get("pattern"), "*.json")
    assert_equal(f"{command_name} as_of", payload.get("as_of"), "2026-06-13T12:00:00+00:00")
    assert_equal(f"{command_name} source_name", payload.get("source_name"), "Rednote MCP Export")
    assert_equal(f"{command_name} step_count", payload.get("step_count"), 12)
    for field in ("directory", "config_dir", "data_dir"):
        value = payload.get(field)
        if not isinstance(value, str) or not value:
            raise SmokeError(f"{command_name} {field} must be populated")
    adapter_id = str(payload["adapter_id"])
    directory = str(payload["directory"])
    config_dir = str(payload["config_dir"])
    data_dir = str(payload["data_dir"])
    as_of = str(payload["as_of"])
    input_format = str(payload["input_format"])
    pattern = str(payload["pattern"])
    source_name = str(payload["source_name"])

    steps = payload.get("steps")
    if not isinstance(steps, list):
        raise SmokeError(f"{command_name} steps must be a list")
    if len(steps) != len(EXPECTED_EXTERNAL_TOOL_WORKFLOW_STEPS):
        raise SmokeError(
            f"{command_name} step_count expected {len(EXPECTED_EXTERNAL_TOOL_WORKFLOW_STEPS)!r}, "
            f"got {len(steps)!r}"
        )
    names = [step.get("name") for step in steps if isinstance(step, dict)]
    assert_equal(
        f"{command_name} step names",
        names,
        list(EXPECTED_EXTERNAL_TOOL_WORKFLOW_STEPS),
    )

    import_step = steps[10]
    if not isinstance(import_step, dict):
        raise SmokeError(f"{command_name} import step must be a JSON object")
    assert_equal(
        f"{command_name} import step effect",
        import_step.get("suggested_effect"),
        "updates_local_imports",
    )

    effects = [step.get("suggested_effect") for step in steps if isinstance(step, dict)]
    assert_equal(
        f"{command_name} step effects",
        effects,
        [
            "print_only",
            "read_only",
            "print_only",
            "print_only",
            "print_only",
            "print_only",
            "read_only",
            "read_only",
            "read_only",
            "read_only",
            "updates_local_imports",
            "print_only",
        ],
    )

    registry_step = steps[0]
    if not isinstance(registry_step, dict):
        raise SmokeError(f"{command_name} registry step must be a JSON object")
    validate_expected_external_tool_command(
        command_name,
        "registry",
        registry_step.get("command", ""),
        "external-tool-adapters",
        "--adapter",
        adapter_id,
        "--directory",
        directory,
        "--config-dir",
        config_dir,
        "--data-dir",
        data_dir,
        "--as-of",
        as_of,
        "--format",
        "table",
    )

    readiness_step = steps[1]
    if not isinstance(readiness_step, dict):
        raise SmokeError(f"{command_name} readiness step must be a JSON object")
    validate_expected_external_tool_command(
        command_name,
        "readiness",
        readiness_step.get("command", ""),
        "external-tool-readiness",
        "--adapter",
        adapter_id,
        "--directory",
        directory,
        "--config-dir",
        config_dir,
        "--data-dir",
        data_dir,
        "--as-of",
        as_of,
        "--input-format",
        input_format,
        "--pattern",
        pattern,
        "--source-name",
        source_name,
        "--format",
        "table",
    )

    template_step = steps[2]
    if not isinstance(template_step, dict):
        raise SmokeError(f"{command_name} template step must be a JSON object")
    validate_expected_external_tool_command(
        command_name,
        "template",
        template_step.get("command", ""),
        "external-tool-template",
        "--adapter",
        adapter_id,
        "--directory",
        directory,
        "--config-dir",
        config_dir,
        "--data-dir",
        data_dir,
        "--as-of",
        as_of,
        "--format",
        "json",
    )

    signal_profile_step = steps[3]
    if not isinstance(signal_profile_step, dict):
        raise SmokeError(f"{command_name} signal profile step must be a JSON object")
    validate_expected_external_tool_command(
        command_name,
        "signal profile",
        signal_profile_step.get("command", ""),
        "community-signal-profile",
        "--format",
        "json",
    )

    handoff_manifest_step = steps[4]
    if not isinstance(handoff_manifest_step, dict):
        raise SmokeError(f"{command_name} handoff manifest step must be a JSON object")
    validate_expected_external_tool_command(
        command_name,
        "handoff manifest",
        handoff_manifest_step.get("command", ""),
        "community-handoff-manifest",
        directory,
        "--input-format",
        input_format,
        "--pattern",
        pattern,
        "--config-dir",
        config_dir,
        "--data-dir",
        data_dir,
        "--as-of",
        as_of,
        "--source-name",
        source_name,
        "--format",
        "json",
    )

    handoff_workflow_step = steps[5]
    if not isinstance(handoff_workflow_step, dict):
        raise SmokeError(f"{command_name} handoff workflow step must be a JSON object")
    validate_expected_external_tool_command(
        command_name,
        "handoff workflow",
        handoff_workflow_step.get("command", ""),
        "community-handoff-workflow",
        directory,
        "--input-format",
        input_format,
        "--pattern",
        pattern,
        "--config-dir",
        config_dir,
        "--data-dir",
        data_dir,
        "--as-of",
        as_of,
        "--source-name",
        source_name,
    )

    lint_step = steps[6]
    if not isinstance(lint_step, dict):
        raise SmokeError(f"{command_name} lint step must be a JSON object")
    validate_expected_external_tool_command(
        command_name,
        "lint",
        lint_step.get("command", ""),
        "community-signal-lint-dir",
        directory,
        "--input-format",
        input_format,
        "--pattern",
        pattern,
        "--source-name",
        source_name,
        "--strict",
    )

    candidate_preview_step = steps[7]
    if not isinstance(candidate_preview_step, dict):
        raise SmokeError(f"{command_name} candidate preview step must be a JSON object")
    validate_expected_external_tool_command(
        command_name,
        "candidate preview",
        candidate_preview_step.get("command", ""),
        "community-candidates-dir",
        directory,
        "--input-format",
        input_format,
        "--pattern",
        pattern,
        "--config-dir",
        config_dir,
        "--as-of",
        as_of,
        "--source-name",
        source_name,
    )

    handoff_readiness_step = steps[8]
    if not isinstance(handoff_readiness_step, dict):
        raise SmokeError(f"{command_name} handoff readiness step must be a JSON object")
    validate_expected_external_tool_command(
        command_name,
        "handoff readiness",
        handoff_readiness_step.get("command", ""),
        "community-handoff-check-dir",
        directory,
        "--input-format",
        input_format,
        "--pattern",
        pattern,
        "--config-dir",
        config_dir,
        "--as-of",
        as_of,
        "--source-name",
        source_name,
        "--strict",
    )

    dry_run_import_step = steps[9]
    if not isinstance(dry_run_import_step, dict):
        raise SmokeError(f"{command_name} dry-run step must be a JSON object")
    validate_expected_external_tool_command(
        command_name,
        "dry-run",
        dry_run_import_step.get("command", ""),
        "import-signals-dir",
        directory,
        "--format",
        input_format,
        "--pattern",
        pattern,
        "--source-name",
        source_name,
        "--data-dir",
        data_dir,
        "--imported-at",
        as_of,
        "--dry-run",
    )

    validate_expected_external_tool_command(
        command_name,
        "import",
        import_step.get("command", ""),
        "import-signals-dir",
        directory,
        "--format",
        input_format,
        "--pattern",
        pattern,
        "--source-name",
        source_name,
        "--data-dir",
        data_dir,
        "--imported-at",
        as_of,
    )

    post_import_review_step = steps[11]
    if not isinstance(post_import_review_step, dict):
        raise SmokeError(f"{command_name} post-import review step must be a JSON object")
    validate_expected_external_tool_command(
        command_name,
        "post-import review",
        post_import_review_step.get("command", ""),
        "imported-review-workflow",
        "--config-dir",
        config_dir,
        "--data-dir",
        data_dir,
        "--as-of",
        as_of,
        "--source-name",
        source_name,
    )

    boundaries = payload.get("boundaries")
    if not isinstance(boundaries, list) or not boundaries:
        raise SmokeError(f"{command_name} boundaries must be a non-empty list")
    assert_equal(
        f"{command_name} boundaries",
        boundaries,
        list(EXPECTED_EXTERNAL_TOOL_WORKFLOW_BOUNDARIES),
    )


def validate_external_tool_readiness(command_name: str, payload: Any) -> None:
    if not isinstance(payload, dict):
        raise SmokeError(f"{command_name} output must be a JSON object")
    assert_equal(
        f"{command_name} keys",
        list(payload),
        [
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
        ],
    )
    assert_equal(
        f"{command_name} contract_version",
        payload.get("contract_version"),
        "external-tool-readiness/v1",
    )
    assert_equal(f"{command_name} execution_mode", payload.get("execution_mode"), "local_read_only")
    assert_equal(f"{command_name} adapter_id", payload.get("adapter_id"), "rednote_mcp")
    assert_equal(f"{command_name} platform_label", payload.get("platform_label"), "rednote")
    assert_equal(f"{command_name} input_format", payload.get("input_format"), "json")
    assert_equal(f"{command_name} pattern", payload.get("pattern"), "*.json")
    assert_equal(f"{command_name} as_of", payload.get("as_of"), "2026-06-13T12:00:00+00:00")
    assert_equal(f"{command_name} source_name", payload.get("source_name"), "Rednote MCP Export")
    assert_equal(f"{command_name} step_count", payload.get("step_count"), 7)
    for field in ("directory", "config_dir", "data_dir"):
        value = payload.get(field)
        if not isinstance(value, str) or not value:
            raise SmokeError(f"{command_name} {field} must be populated")
    adapter_id = str(payload["adapter_id"])
    directory = str(payload["directory"])
    config_dir = str(payload["config_dir"])
    data_dir = str(payload["data_dir"])
    as_of = str(payload["as_of"])
    input_format = str(payload["input_format"])
    pattern = str(payload["pattern"])
    source_name = str(payload["source_name"])

    checks = payload.get("checks")
    if not isinstance(checks, list) or len(checks) != 1:
        raise SmokeError(f"{command_name} checks must contain exactly one readiness check")
    check = checks[0]
    if not isinstance(check, dict):
        raise SmokeError(f"{command_name} readiness check must be a JSON object")
    assert_equal(
        f"{command_name} check keys",
        list(check),
        ["name", "status", "command", "path", "detail", "install_hint"],
    )
    assert_equal(f"{command_name} check name", check.get("name"), "upstream_command")
    assert_equal(f"{command_name} check command", check.get("command"), "rednote-mcp")
    detail = check.get("detail")
    if not isinstance(detail, str) or not detail:
        raise SmokeError(f"{command_name} check detail must be populated")
    assert_equal(
        f"{command_name} check detail",
        detail,
        EXPECTED_EXTERNAL_TOOL_READINESS_DETAIL,
    )
    install_hint = check.get("install_hint")
    if not isinstance(install_hint, str) or not install_hint:
        raise SmokeError(f"{command_name} check install_hint must be populated")
    assert_equal(
        f"{command_name} check install_hint",
        install_hint,
        EXPECTED_EXTERNAL_TOOL_READINESS_INSTALL_HINT,
    )
    status = check.get("status")
    if status not in {"found", "missing"}:
        raise SmokeError(f"{command_name} check status must be found or missing, got {status!r}")
    path = check.get("path")
    if status == "found":
        if not isinstance(path, str) or not path:
            raise SmokeError(f"{command_name} found check must include a path")
    if status == "missing" and path is not None:
        raise SmokeError(f"{command_name} missing check must not include a path")

    steps = payload.get("steps")
    if not isinstance(steps, list):
        raise SmokeError(f"{command_name} steps must be a list")
    if len(steps) != len(EXPECTED_EXTERNAL_TOOL_READINESS_STEPS):
        raise SmokeError(
            f"{command_name} step_count expected "
            f"{len(EXPECTED_EXTERNAL_TOOL_READINESS_STEPS)!r}, got {len(steps)!r}"
        )
    names = [step.get("name") for step in steps if isinstance(step, dict)]
    assert_equal(
        f"{command_name} step names",
        names,
        list(EXPECTED_EXTERNAL_TOOL_READINESS_STEPS),
    )
    effects = [step.get("suggested_effect") for step in steps if isinstance(step, dict)]
    assert_equal(
        f"{command_name} step effects",
        effects,
        [
            "print_only",
            "print_only",
            "print_only",
            "print_only",
            "read_only",
            "read_only",
            "read_only",
        ],
    )

    registry_step = steps[0]
    if not isinstance(registry_step, dict):
        raise SmokeError(f"{command_name} registry step must be a JSON object")
    validate_expected_external_tool_command(
        command_name,
        "registry",
        registry_step.get("command", ""),
        "external-tool-adapters",
        "--adapter",
        adapter_id,
        "--directory",
        directory,
        "--config-dir",
        config_dir,
        "--data-dir",
        data_dir,
        "--as-of",
        as_of,
        "--format",
        "table",
    )

    template_step = steps[1]
    if not isinstance(template_step, dict):
        raise SmokeError(f"{command_name} template step must be a JSON object")
    validate_expected_external_tool_command(
        command_name,
        "template",
        template_step.get("command", ""),
        "external-tool-template",
        "--adapter",
        adapter_id,
        "--directory",
        directory,
        "--config-dir",
        config_dir,
        "--data-dir",
        data_dir,
        "--as-of",
        as_of,
        "--format",
        "json",
    )

    workflow_step = steps[2]
    if not isinstance(workflow_step, dict):
        raise SmokeError(f"{command_name} workflow step must be a JSON object")
    validate_expected_external_tool_command(
        command_name,
        "workflow",
        workflow_step.get("command", ""),
        "external-tool-workflow",
        "--adapter",
        adapter_id,
        "--directory",
        directory,
        "--config-dir",
        config_dir,
        "--data-dir",
        data_dir,
        "--as-of",
        as_of,
        "--input-format",
        input_format,
        "--pattern",
        pattern,
        "--source-name",
        source_name,
        "--format",
        "table",
    )

    signal_profile_step = steps[3]
    if not isinstance(signal_profile_step, dict):
        raise SmokeError(f"{command_name} signal profile step must be a JSON object")
    validate_expected_external_tool_command(
        command_name,
        "signal profile",
        signal_profile_step.get("command", ""),
        "community-signal-profile",
        "--format",
        "json",
    )

    lint_step = steps[4]
    if not isinstance(lint_step, dict):
        raise SmokeError(f"{command_name} lint step must be a JSON object")
    validate_expected_external_tool_command(
        command_name,
        "lint",
        lint_step.get("command", ""),
        "community-signal-lint-dir",
        directory,
        "--input-format",
        input_format,
        "--pattern",
        pattern,
        "--source-name",
        source_name,
        "--strict",
    )

    handoff_readiness_step = steps[5]
    if not isinstance(handoff_readiness_step, dict):
        raise SmokeError(f"{command_name} handoff readiness step must be a JSON object")
    validate_expected_external_tool_command(
        command_name,
        "handoff readiness",
        handoff_readiness_step.get("command", ""),
        "community-handoff-check-dir",
        directory,
        "--input-format",
        input_format,
        "--pattern",
        pattern,
        "--config-dir",
        config_dir,
        "--as-of",
        as_of,
        "--source-name",
        source_name,
        "--strict",
    )

    dry_run_step = steps[-1]
    if not isinstance(dry_run_step, dict):
        raise SmokeError(f"{command_name} dry-run step must be a JSON object")
    validate_expected_external_tool_command(
        command_name,
        "dry-run",
        dry_run_step.get("command", ""),
        "import-signals-dir",
        directory,
        "--format",
        input_format,
        "--pattern",
        pattern,
        "--source-name",
        source_name,
        "--data-dir",
        data_dir,
        "--imported-at",
        as_of,
        "--dry-run",
    )

    boundaries = payload.get("boundaries")
    if not isinstance(boundaries, list) or not boundaries:
        raise SmokeError(f"{command_name} boundaries must be a non-empty list")
    assert_equal(
        f"{command_name} boundaries",
        boundaries,
        list(EXPECTED_EXTERNAL_TOOL_READINESS_BOUNDARIES),
    )


def validate_report_outputs(json_payload: Any, markdown_text: str) -> None:
    if not isinstance(json_payload, dict):
        raise SmokeError("report JSON output must be a JSON object")
    metadata = json_payload.get("metadata")
    if not isinstance(metadata, dict):
        raise SmokeError("report JSON missing metadata")
    assert_equal("report metadata item_count", metadata.get("item_count"), 3)
    entities = json_payload.get("entities")
    if not isinstance(entities, list):
        raise SmokeError("report JSON entities must be a list")
    entity_names = [entity.get("entity_name") for entity in entities if isinstance(entity, dict)]
    assert_equal("report entity names", entity_names, list(EXPECTED_SAMPLE_ENTITIES))
    for expected in EXPECTED_SAMPLE_ENTITIES:
        if f"### {expected} (new)" not in markdown_text:
            raise SmokeError(f"report Markdown missing sample entity section: {expected}")
    if "No entity signals in this window." in markdown_text:
        raise SmokeError("report Markdown should not contain the empty entity signal message")


def validate_candidates(command_name: str, payload: Any, report_payload: Any) -> None:
    assert_equal(f"{command_name} candidates", payload, [])
    if isinstance(report_payload, dict):
        assert_equal("report candidates", report_payload.get("candidates"), payload)


def validate_trends(command_name: str, payload: Any) -> None:
    if not isinstance(payload, dict):
        raise SmokeError(f"{command_name} output must be a JSON object")
    assert_equal(f"{command_name} as_of", payload.get("as_of"), "2026-06-13T12:00:00Z")
    deltas = payload.get("deltas")
    if not isinstance(deltas, list):
        raise SmokeError(f"{command_name} deltas must be a list")
    expected_types = {
        "The Row": "brand",
        "The Row Margaux": "product",
        "Ballet Flats": "category",
    }
    deltas_by_name = {str(delta.get("name")): delta for delta in deltas if isinstance(delta, dict)}
    assert_equal(
        f"{command_name} entity delta names",
        list(deltas_by_name),
        list(EXPECTED_SAMPLE_ENTITIES),
    )
    for name, signal_type in expected_types.items():
        delta = deltas_by_name[name]
        assert_equal(f"{command_name} {name} signal_kind", delta.get("signal_kind"), "entity")
        assert_equal(f"{command_name} {name} signal_type", delta.get("signal_type"), signal_type)
        assert_equal(f"{command_name} {name} status", delta.get("status"), "new")


def report_paths(context: SmokeContext) -> tuple[Path, Path]:
    report_date = AS_OF.split("T", 1)[0]
    return (
        context.reports_dir / f"fashion-radar-{report_date}.md",
        context.reports_dir / f"fashion-radar-{report_date}.json",
    )


def file_digest(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def snapshot_default_artifacts(repo_root: Path) -> dict[Path, str]:
    artifacts: dict[Path, str] = {}
    for directory_name in ("data", "reports"):
        directory = repo_root / directory_name
        if not directory.exists():
            continue
        for path in directory.rglob("*"):
            if path.is_file():
                artifacts[path.relative_to(repo_root)] = file_digest(path)
    return artifacts


def assert_default_artifacts_unchanged(repo_root: Path, before: dict[Path, str]) -> None:
    after = snapshot_default_artifacts(repo_root)
    before_paths = set(before)
    after_paths = set(after)
    created = sorted(after_paths - before_paths)
    deleted = sorted(before_paths - after_paths)
    changed = sorted(path for path in before_paths & after_paths if before[path] != after[path])
    if not (created or deleted or changed):
        return

    changes: list[str] = []
    if created:
        changes.append(f"created: {format_paths(created)}")
    if changed:
        changes.append(f"changed: {format_paths(changed)}")
    if deleted:
        changes.append(f"deleted: {format_paths(deleted)}")
    raise SmokeError(f"Smoke changed files under default data/reports ({'; '.join(changes)})")


def format_paths(paths: Sequence[Path]) -> str:
    return ", ".join(path.as_posix() for path in paths)


def run_cli(context: SmokeContext, *args: str) -> subprocess.CompletedProcess[str]:
    command = cli_command(context, *args)
    completed = subprocess.run(
        command,
        cwd=context.repo_root,
        env=command_environment(context, source_checkout=context.source_checkout),
        text=True,
        capture_output=True,
        check=False,
    )
    if completed.returncode != 0:
        raise SmokeError(format_command_failure(command, completed))
    return completed


def format_command_failure(
    command: Sequence[str],
    completed: subprocess.CompletedProcess[str],
) -> str:
    command_text = " ".join(shlex.quote(part) for part in command)
    stdout = completed.stdout.strip() or "<empty>"
    stderr = completed.stderr.strip() or "<empty>"
    return (
        f"Command failed with exit code {completed.returncode}: {command_text}\n"
        f"stdout:\n{stdout}\n"
        f"stderr:\n{stderr}"
    )


def prepare_directory_export(context: SmokeContext) -> Path:
    source = context.repo_root / EXAMPLE_CSV
    if not source.is_file():
        raise SmokeError(f"Missing example CSV: {source}")
    context.exports_dir.mkdir(parents=True, exist_ok=True)
    destination = context.exports_dir / DIR_EXPORT_CSV
    shutil.copyfile(source, destination)
    return destination


def assert_non_empty_file(path: Path) -> None:
    if not path.is_file():
        raise SmokeError(f"Expected file was not created: {path}")
    if path.stat().st_size <= 0:
        raise SmokeError(f"Expected file is empty: {path}")


def run_smoke(context: SmokeContext) -> None:
    before_default_artifacts = snapshot_default_artifacts(context.repo_root)
    flow_error: SmokeError | None = None

    try:
        run_first_run_flow(context)
    except SmokeError as exc:
        flow_error = exc

    try:
        assert_default_artifacts_unchanged(context.repo_root, before_default_artifacts)
    except SmokeError as artifact_error:
        if flow_error is not None:
            raise SmokeError(f"{flow_error}\n{artifact_error}") from flow_error
        raise

    if flow_error is not None:
        raise flow_error


def run_first_run_flow(context: SmokeContext) -> None:
    example_csv = context.repo_root / EXAMPLE_CSV
    if not example_csv.is_file():
        raise SmokeError(f"Missing example CSV: {example_csv}")
    validate_sample_csv(example_csv)

    run_cli(
        context,
        "init",
        "--config-dir",
        str(context.config_dir),
        "--data-dir",
        str(context.data_dir),
        "--reports-dir",
        str(context.reports_dir),
    )
    run_cli(context, "migrate-db", "--data-dir", str(context.data_dir))
    assert_workspace_artifacts(context)
    run_cli(
        context,
        "doctor",
        "--config-dir",
        str(context.config_dir),
        "--data-dir",
        str(context.data_dir),
        "--reports-dir",
        str(context.reports_dir),
    )
    external_tool_adapters = validate_json_output(
        "external-tool-adapters",
        run_cli(context, "external-tool-adapters", "--format", "json").stdout,
    )
    validate_external_tool_adapters("external-tool-adapters", external_tool_adapters)
    external_tool_template = validate_json_output(
        "external-tool-template",
        run_cli(
            context,
            "external-tool-template",
            "--adapter",
            "rednote_mcp",
            "--format",
            "json",
        ).stdout,
    )
    validate_external_tool_template("external-tool-template", external_tool_template)
    external_tool_workflow = validate_json_output(
        "external-tool-workflow",
        run_cli(
            context,
            "external-tool-workflow",
            "--adapter",
            "rednote_mcp",
            "--directory",
            str(context.exports_dir),
            "--config-dir",
            str(context.config_dir),
            "--data-dir",
            str(context.data_dir),
            "--as-of",
            AS_OF,
            "--format",
            "json",
        ).stdout,
    )
    validate_external_tool_workflow("external-tool-workflow", external_tool_workflow)
    external_tool_readiness = validate_json_output(
        "external-tool-readiness",
        run_cli(
            context,
            "external-tool-readiness",
            "--adapter",
            "rednote_mcp",
            "--directory",
            str(context.exports_dir),
            "--config-dir",
            str(context.config_dir),
            "--data-dir",
            str(context.data_dir),
            "--as-of",
            AS_OF,
            "--format",
            "json",
        ).stdout,
    )
    validate_external_tool_readiness("external-tool-readiness", external_tool_readiness)
    run_cli(
        context,
        "community-signal-lint",
        str(example_csv),
        "--input-format",
        "csv",
        "--source-name",
        SOURCE_NAME,
    )
    community_candidates = validate_json_output(
        "community-candidates",
        run_cli(
            context,
            "community-candidates",
            str(example_csv),
            "--config-dir",
            str(context.config_dir),
            "--input-format",
            "csv",
            "--as-of",
            AS_OF,
            "--source-name",
            SOURCE_NAME,
            "--format",
            "json",
        ).stdout,
    )
    validate_community_candidates("community-candidates", community_candidates)
    validate_import_signals_dry_run(
        run_cli(
            context,
            "import-signals",
            str(example_csv),
            "--data-dir",
            str(context.data_dir),
            "--format",
            "csv",
            "--source-name",
            SOURCE_NAME,
            "--dry-run",
        ).stdout
    )
    validate_import_signals_import(
        run_cli(
            context,
            "import-signals",
            str(example_csv),
            "--data-dir",
            str(context.data_dir),
            "--format",
            "csv",
            "--source-name",
            SOURCE_NAME,
            "--imported-at",
            AS_OF,
        ).stdout
    )
    run_cli(
        context,
        "match",
        "--config-dir",
        str(context.config_dir),
        "--data-dir",
        str(context.data_dir),
    )
    imported_review_workflow = validate_json_output(
        "imported-review-workflow",
        run_cli(
            context,
            "imported-review-workflow",
            "--config-dir",
            str(context.config_dir),
            "--data-dir",
            str(context.data_dir),
            "--as-of",
            AS_OF,
            "--source-name",
            SOURCE_NAME,
            "--format",
            "json",
        ).stdout,
    )
    validate_imported_review_workflow("imported-review-workflow", imported_review_workflow)
    imported_summary = validate_json_output(
        "imported-signals-summary",
        run_cli(
            context,
            "imported-signals-summary",
            "--data-dir",
            str(context.data_dir),
            "--format",
            "json",
        ).stdout,
    )
    validate_imported_summary("imported-signals-summary", imported_summary)
    imported_signals = validate_json_output(
        "imported-signals",
        run_cli(
            context,
            "imported-signals",
            "--data-dir",
            str(context.data_dir),
            "--as-of",
            AS_OF,
            "--source-name",
            SOURCE_NAME,
            "--format",
            "json",
        ).stdout,
    )
    validate_imported_signals("imported-signals", imported_signals)
    run_cli(
        context,
        "report",
        "--config-dir",
        str(context.config_dir),
        "--data-dir",
        str(context.data_dir),
        "--reports-dir",
        str(context.reports_dir),
        "--as-of",
        AS_OF,
    )
    markdown_path, json_path = report_paths(context)
    assert_non_empty_file(markdown_path)
    assert_non_empty_file(json_path)
    report_payload = validate_json_output("report JSON", json_path.read_text(encoding="utf-8"))
    validate_report_outputs(report_payload, markdown_path.read_text(encoding="utf-8"))
    candidates_payload = validate_json_output(
        "candidates",
        run_cli(
            context,
            "candidates",
            "--config-dir",
            str(context.config_dir),
            "--data-dir",
            str(context.data_dir),
            "--as-of",
            AS_OF,
            "--format",
            "json",
        ).stdout,
    )
    validate_candidates("candidates", candidates_payload, report_payload)
    trends_payload = validate_json_output(
        "trends",
        run_cli(
            context,
            "trends",
            "--config-dir",
            str(context.config_dir),
            "--data-dir",
            str(context.data_dir),
            "--as-of",
            AS_OF,
            "--format",
            "json",
        ).stdout,
    )
    validate_trends("trends", trends_payload)

    prepare_directory_export(context)
    community_handoff_workflow = validate_json_output(
        "community-handoff-workflow",
        run_cli(
            context,
            "community-handoff-workflow",
            str(context.exports_dir),
            "--config-dir",
            str(context.config_dir),
            "--data-dir",
            str(context.data_dir),
            "--input-format",
            "csv",
            "--pattern",
            DIR_PATTERN,
            "--as-of",
            AS_OF,
            "--source-name",
            SOURCE_NAME,
            "--format",
            "json",
        ).stdout,
    )
    validate_community_handoff_workflow(
        "community-handoff-workflow",
        community_handoff_workflow,
    )
    run_cli(
        context,
        "community-signal-lint-dir",
        str(context.exports_dir),
        "--input-format",
        "csv",
        "--pattern",
        DIR_PATTERN,
        "--source-name",
        SOURCE_NAME,
    )
    community_candidates_dir = validate_json_output(
        "community-candidates-dir",
        run_cli(
            context,
            "community-candidates-dir",
            str(context.exports_dir),
            "--config-dir",
            str(context.config_dir),
            "--input-format",
            "csv",
            "--pattern",
            DIR_PATTERN,
            "--as-of",
            AS_OF,
            "--source-name",
            SOURCE_NAME,
            "--format",
            "json",
        ).stdout,
    )
    validate_community_candidates(
        "community-candidates-dir",
        community_candidates_dir,
        directory=True,
    )
    validate_import_signals_dir_dry_run(
        run_cli(
            context,
            "import-signals-dir",
            str(context.exports_dir),
            "--data-dir",
            str(context.data_dir),
            "--format",
            "csv",
            "--pattern",
            DIR_PATTERN,
            "--source-name",
            SOURCE_NAME,
            "--dry-run",
        ).stdout
    )


def assert_workspace_artifacts(context: SmokeContext) -> None:
    for directory in (context.config_dir, context.data_dir, context.reports_dir):
        if not directory.is_dir():
            raise SmokeError(f"Expected directory was not created: {directory}")

    database_path = context.data_dir / "fashion-radar.sqlite"
    if not database_path.is_file():
        raise SmokeError(f"Expected SQLite database was not created: {database_path}")


def assert_installed_import_origin(context: SmokeContext, module_file: Path) -> None:
    source_root = (context.repo_root / "src").resolve()
    resolved_file = module_file.resolve()
    if resolved_file == source_root or source_root in resolved_file.parents:
        raise SmokeError(
            f"Installed smoke imported fashion_radar from source checkout: {resolved_file}"
        )


def installed_import_origin(context: SmokeContext) -> Path:
    command = [
        context.python,
        "-c",
        (
            "import fashion_radar, json, pathlib; "
            "print(json.dumps({'module_file': "
            "str(pathlib.Path(fashion_radar.__file__).resolve())}))"
        ),
    ]
    completed = subprocess.run(
        command,
        cwd=context.repo_root,
        env=command_environment(context, source_checkout=False),
        text=True,
        capture_output=True,
        check=False,
    )
    if completed.returncode != 0:
        raise SmokeError(format_command_failure(command, completed))

    output_lines = [line for line in completed.stdout.splitlines() if line.strip()]
    if len(output_lines) != 1:
        raise SmokeError("Installed smoke import-origin preflight returned no module path")
    try:
        payload = json.loads(output_lines[0])
    except json.JSONDecodeError as exc:
        raise SmokeError(
            f"Installed smoke import-origin preflight returned invalid JSON: {exc}"
        ) from exc
    if not isinstance(payload, dict):
        raise SmokeError("Installed smoke import-origin preflight returned invalid payload")
    module_file = payload.get("module_file")
    if not isinstance(module_file, str) or not module_file:
        raise SmokeError("Installed smoke import-origin preflight returned no module path")
    return Path(module_file)


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run the local first-run sample smoke flow.",
    )
    parser.add_argument(
        "--repo-root",
        default=".",
        help="Repository root to run the smoke check against.",
    )
    parser.add_argument(
        "--python",
        default=sys.executable,
        help="Python executable used to run `-m fashion_radar`.",
    )
    parser.add_argument(
        "--installed",
        action="store_true",
        help=(
            "Run against the supplied installed Python environment without "
            "prepending repo_root/src to PYTHONPATH."
        ),
    )
    return parser.parse_args(argv)


def build_context(
    repo_root: Path,
    python: str,
    runtime_dir: Path,
    *,
    source_checkout: bool = True,
) -> SmokeContext:
    return SmokeContext(
        repo_root=repo_root,
        python=python,
        runtime_dir=runtime_dir,
        config_dir=runtime_dir / "config",
        data_dir=runtime_dir / "data",
        reports_dir=runtime_dir / "reports",
        exports_dir=runtime_dir / "exports",
        source_checkout=source_checkout,
    )


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    repo_root = Path(args.repo_root).resolve()

    try:
        with tempfile.TemporaryDirectory(prefix="fashion-radar-first-run-") as temp_dir:
            context = build_context(
                repo_root,
                args.python,
                Path(temp_dir),
                source_checkout=not args.installed,
            )
            if args.installed:
                assert_installed_import_origin(context, installed_import_origin(context))
            run_smoke(context)
    except SmokeError as exc:
        print(str(exc), file=sys.stderr)
        return 1
    except Exception as exc:
        print(f"First-run sample smoke failed: {exc}", file=sys.stderr)
        return 1

    print("First-run sample smoke passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
