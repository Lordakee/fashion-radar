#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import hashlib
import http.client
import json
import os
import shlex
import shutil
import socket
import subprocess
import sys
import tempfile
import time
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
SMOKE_COMMAND_TIMEOUT_SECONDS = 120
EXPECTED_SAMPLE_ENTITIES = ("The Row", "The Row Margaux", "Ballet Flats")
EXPECTED_ENTITY_MATCH_EVIDENCE_KEYS = (
    "matched_items",
    "accepted_without_context_items",
    "context_supported_items",
    "parent_brand_supported_items",
    "safe_alias_supported_items",
    "other_supported_items",
    "min_confidence",
    "avg_confidence",
    "max_confidence",
)
EXPECTED_ENTITY_MATCH_EVIDENCE_COUNT_KEYS = EXPECTED_ENTITY_MATCH_EVIDENCE_KEYS[:6]
FORBIDDEN_REPORT_ENTITY_MATCHER_FIELDS = (
    "alias",
    "context_terms",
    "item_id",
    "normalized_url",
    "reason",
)
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
EXPECTED_IMPORTED_REVIEW_WORKFLOW_STEP_METADATA = [
    {
        "order": 1,
        "name": "summarize_imported_sources",
        "purpose": "Summarize retained imported source-name labels.",
        "suggested_effect": "read_only",
    },
    {
        "order": 2,
        "name": "refresh_stored_matches",
        "purpose": "Refresh stored local matches using configured entities.",
        "suggested_effect": "updates_local_matches",
    },
    {
        "order": 3,
        "name": "compare_imported_entities",
        "purpose": "Compare stored matched imported entities across collected-at windows.",
        "suggested_effect": "read_only",
    },
    {
        "order": 4,
        "name": "review_imported_entity_evidence",
        "purpose": "Review retained imported rows behind one selected matched entity.",
        "suggested_effect": "read_only",
    },
    {
        "order": 5,
        "name": "review_imported_candidate_phrases",
        "purpose": (
            "Review observed candidate phrases from retained imported rows after stored "
            "matches are refreshed."
        ),
        "suggested_effect": "read_only",
    },
    {
        "order": 6,
        "name": "review_unmatched_imported_rows",
        "purpose": "Review retained imported rows without stored matches.",
        "suggested_effect": "read_only",
    },
    {
        "order": 7,
        "name": "review_local_heat_movers",
        "purpose": "Review local observed heat movement after imported rows are matched.",
        "suggested_effect": "read_only",
    },
]
EXPECTED_COMMUNITY_HANDOFF_WORKFLOW_STEPS = (
    "lint_handoff_directory",
    "preview_candidate_phrases",
    "review_handoff_readiness",
    "dry_run_directory_import",
    "import_directory_signals",
    "print_post_import_review",
)
EXPECTED_COMMUNITY_HANDOFF_WORKFLOW_STEP_METADATA = [
    {
        "order": 1,
        "name": "lint_handoff_directory",
        "purpose": "Lint local community handoff files before import.",
        "suggested_effect": "read_only",
    },
    {
        "order": 2,
        "name": "preview_candidate_phrases",
        "purpose": "Preview aggregate candidate phrases before import.",
        "suggested_effect": "read_only",
    },
    {
        "order": 3,
        "name": "review_handoff_readiness",
        "purpose": "Review local handoff readiness before import.",
        "suggested_effect": "read_only",
    },
    {
        "order": 4,
        "name": "dry_run_directory_import",
        "purpose": "Validate matched local files through the importer without writing rows.",
        "suggested_effect": "read_only",
    },
    {
        "order": 5,
        "name": "import_directory_signals",
        "purpose": "Import the validated local handoff rows into local SQLite.",
        "suggested_effect": "updates_local_imports",
    },
    {
        "order": 6,
        "name": "print_post_import_review",
        "purpose": "Print the local post-import review checklist.",
        "suggested_effect": "print_only",
    },
]
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
EXPECTED_EXTERNAL_TOOL_DISPLAY_NAME = "Rednote MCP Export"
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


def validate_community_handoff_check_dir(
    command_name: str,
    payload: Any,
    *,
    expected_directory: str = "/tmp/export",
    expected_config_dir: str = "configs",
) -> None:
    if not isinstance(payload, dict):
        raise SmokeError(f"{command_name} output must be a JSON object")
    assert_equal(f"{command_name} execution_mode", payload.get("execution_mode"), "local_read_only")
    assert_equal(f"{command_name} directory", payload.get("directory"), expected_directory)
    assert_equal(f"{command_name} config_dir", payload.get("config_dir"), expected_config_dir)
    assert_equal(f"{command_name} input_format", payload.get("input_format"), "csv")
    assert_equal(f"{command_name} pattern", payload.get("pattern"), DIR_PATTERN)
    assert_equal(f"{command_name} as_of", payload.get("as_of"), "2026-06-13T12:00:00+00:00")
    assert_equal(f"{command_name} source_name", payload.get("source_name"), SOURCE_NAME)
    assert_equal(f"{command_name} strict", payload.get("strict"), True)
    assert_equal(f"{command_name} limit", payload.get("limit"), 50)
    assert_equal(f"{command_name} ok", payload.get("ok"), True)
    assert_equal(f"{command_name} failed_check_count", payload.get("failed_check_count"), 0)
    assert_equal(f"{command_name} warning_count", payload.get("warning_count"), 0)
    assert_equal(f"{command_name} findings", payload.get("findings"), [])

    lint = payload.get("community_signal_lint")
    if not isinstance(lint, dict):
        raise SmokeError(f"{command_name} community_signal_lint must be a JSON object")
    assert_equal(f"{command_name} lint file_count", lint.get("file_count"), 1)
    assert_equal(f"{command_name} lint row_count", lint.get("row_count"), 2)
    assert_equal(f"{command_name} lint valid_row_count", lint.get("valid_row_count"), 2)
    assert_equal(f"{command_name} lint error_count", lint.get("error_count"), 0)
    assert_equal(f"{command_name} lint warning_count", lint.get("warning_count"), 0)
    assert_equal(f"{command_name} lint directory", lint.get("directory"), expected_directory)
    assert_equal(f"{command_name} lint input_format", lint.get("input_format"), "csv")
    assert_equal(f"{command_name} lint pattern", lint.get("pattern"), DIR_PATTERN)
    assert_equal(f"{command_name} lint info_count", lint.get("info_count"), 0)
    assert_equal(
        f"{command_name} lint field_counts",
        lint.get("field_counts"),
        {field: len(EXPECTED_SAMPLE_ROWS) for field in EXPECTED_EXTERNAL_TOOL_TEMPLATE_FIELDS},
    )
    assert_equal(
        f"{command_name} lint source_name_counts",
        lint.get("source_name_counts"),
        EXPECTED_SOURCE_COUNTS,
    )
    assert_equal(
        f"{command_name} lint platform_counts",
        lint.get("platform_counts"),
        EXPECTED_PLATFORM_COUNTS,
    )

    candidate_preview = payload.get("candidate_preview")
    if not isinstance(candidate_preview, dict):
        raise SmokeError(f"{command_name} candidate_preview must be a JSON object")
    assert_equal(
        f"{command_name} candidate_preview candidate_count",
        candidate_preview.get("candidate_count"),
        0,
    )
    assert_equal(
        f"{command_name} candidate_preview row_count",
        candidate_preview.get("row_count"),
        2,
    )
    assert_equal(
        f"{command_name} candidate_preview input_format",
        candidate_preview.get("input_format"),
        "csv",
    )
    assert_equal(
        f"{command_name} candidate_preview as_of",
        candidate_preview.get("as_of"),
        "2026-06-13T12:00:00+00:00",
    )
    assert_equal(
        f"{command_name} candidate_preview current_window_start",
        candidate_preview.get("current_window_start"),
        "2026-06-06T12:00:00+00:00",
    )
    assert_equal(
        f"{command_name} candidate_preview baseline_window_start",
        candidate_preview.get("baseline_window_start"),
        "2026-05-07T12:00:00+00:00",
    )
    assert_equal(
        f"{command_name} candidate_preview current_days",
        candidate_preview.get("current_days"),
        7,
    )
    assert_equal(
        f"{command_name} candidate_preview baseline_days",
        candidate_preview.get("baseline_days"),
        30,
    )
    assert_equal(
        f"{command_name} candidate_preview source_name",
        candidate_preview.get("source_name"),
        SOURCE_NAME,
    )
    assert_equal(
        f"{command_name} candidate_preview file_count",
        candidate_preview.get("file_count"),
        1,
    )
    assert_equal(
        f"{command_name} candidate_preview limit",
        candidate_preview.get("limit"),
        50,
    )
    assert_equal(
        f"{command_name} candidate_preview candidates",
        candidate_preview.get("candidates"),
        [],
    )

    import_dry_run = payload.get("import_dry_run")
    if not isinstance(import_dry_run, dict):
        raise SmokeError(f"{command_name} import_dry_run must be a JSON object")
    assert_equal(f"{command_name} import dry-run file_count", import_dry_run.get("file_count"), 1)
    assert_equal(
        f"{command_name} import dry-run valid_file_count",
        import_dry_run.get("valid_file_count"),
        1,
    )
    assert_equal(f"{command_name} import dry-run row_count", import_dry_run.get("row_count"), 2)
    assert_equal(f"{command_name} import dry-run error_count", import_dry_run.get("error_count"), 0)
    assert_equal(
        f"{command_name} import dry-run directory",
        import_dry_run.get("directory"),
        expected_directory,
    )
    assert_equal(
        f"{command_name} import dry-run input_format",
        import_dry_run.get("input_format"),
        "csv",
    )
    assert_equal(
        f"{command_name} import dry-run pattern",
        import_dry_run.get("pattern"),
        DIR_PATTERN,
    )
    assert_equal(
        f"{command_name} import dry-run source_name_counts",
        import_dry_run.get("source_name_counts"),
        EXPECTED_SOURCE_COUNTS,
    )
    assert_equal(
        f"{command_name} import dry-run platform_counts",
        import_dry_run.get("platform_counts"),
        EXPECTED_PLATFORM_COUNTS,
    )


def assert_output_contains(command_name: str, output: str, expected_lines: Sequence[str]) -> None:
    output_lines = {line.strip() for line in output.splitlines() if line.strip()}
    for expected in expected_lines:
        if expected not in output_lines:
            raise SmokeError(f"{command_name} output missing expected text: {expected}")


def assert_output_contains_text(
    command_name: str,
    output: str,
    expected_text: Sequence[str],
) -> None:
    for expected in expected_text:
        if expected not in output:
            raise SmokeError(f"{command_name} output missing expected text: {expected}")


def assert_output_not_contains_text(
    command_name: str,
    output: str,
    forbidden_text: Sequence[str],
) -> None:
    for forbidden in forbidden_text:
        if forbidden in output:
            raise SmokeError(f"{command_name} output includes forbidden text: {forbidden}")


def validate_row_one_schedule_output(output: str) -> None:
    assert_output_contains_text(
        "row-one schedule",
        output,
        (
            "ROW ONE scheduled refresh runs the single refresh command.",
            "fashion-radar row-one refresh",
            "--output-dir",
            "04:00",
        ),
    )
    assert_output_not_contains_text(
        "row-one schedule",
        output,
        (
            "fashion-radar run",
            "fashion-radar row-one build",
            "fashion-radar row-one refresh --latest-only",
        ),
    )


def validate_row_one_manifest(
    manifest_payload: Any,
    edition_payload: Any,
) -> None:
    if not isinstance(manifest_payload, dict):
        raise SmokeError("row-one manifest must be a JSON object")
    if not isinstance(edition_payload, dict):
        raise SmokeError("row-one edition must be a JSON object")

    assert_equal(
        "row-one manifest contract_version",
        manifest_payload.get("contract_version"),
        "row-one-manifest/v1",
    )
    assert_equal("row-one manifest brand", manifest_payload.get("brand"), "ROW ONE")
    assert_equal(
        "row-one manifest app_contract path",
        (manifest_payload.get("app_contract") or {}).get("path")
        if isinstance(manifest_payload.get("app_contract"), dict)
        else None,
        "data/edition.json",
    )
    app_contract = manifest_payload.get("app_contract")
    if not isinstance(app_contract, dict):
        raise SmokeError("row-one manifest app_contract must be a JSON object")
    assert_equal(
        "row-one manifest app_contract version",
        app_contract.get("version"),
        "row-one-app/v7",
    )
    assert_equal(
        "row-one manifest app_contract schema_path",
        app_contract.get("schema_path"),
        "schemas/row-one-app.schema.json",
    )
    site = manifest_payload.get("site")
    if not isinstance(site, dict):
        raise SmokeError("row-one manifest site must be a JSON object")
    assert_equal("row-one manifest index path", site.get("index_path"), "index.html")
    assert_equal("row-one manifest manifest path", site.get("manifest_path"), "data/manifest.json")
    assert_equal(
        "row-one manifest generated_at",
        manifest_payload.get("generated_at"),
        edition_payload.get("generated_at"),
    )
    assert_equal(
        "row-one manifest edition_date",
        manifest_payload.get("edition_date"),
        edition_payload.get("edition_date"),
    )

    counts = manifest_payload.get("counts")
    if not isinstance(counts, dict):
        raise SmokeError("row-one manifest counts must be a JSON object")
    sections = edition_payload.get("sections")
    if not isinstance(sections, list):
        raise SmokeError("row-one edition sections must be a JSON array")
    assert_equal(
        "row-one manifest story_count",
        counts.get("story_count"),
        edition_payload.get("story_count"),
    )
    assert_equal("row-one manifest section_count", counts.get("section_count"), len(sections))
    assert_equal(
        "row-one manifest evidence_count",
        counts.get("evidence_count"),
        edition_payload.get("evidence_count"),
    )

    readiness = manifest_payload.get("readiness")
    if not isinstance(readiness, dict):
        raise SmokeError("row-one manifest readiness must be a JSON object")
    expected_status = "ready" if counts.get("story_count") else "empty"
    assert_equal("row-one manifest readiness status", readiness.get("status"), expected_status)


def validate_row_one_story_directory(edition_payload: Any) -> None:
    if not isinstance(edition_payload, dict):
        raise SmokeError("row-one edition must be a JSON object")
    assert_equal(
        "row-one edition contract_version",
        edition_payload.get("contract_version"),
        "row-one-app/v7",
    )
    stories = edition_payload.get("stories")
    if not isinstance(stories, list):
        raise SmokeError("row-one edition stories must be a JSON array")
    story_directory = edition_payload.get("story_directory")
    if not isinstance(story_directory, dict):
        raise SmokeError("row-one edition story_directory must be a JSON object")

    assert_equal(
        "row-one story_directory story_count",
        story_directory.get("story_count"),
        len(stories),
    )
    expected_story_ids = []
    story_by_id: dict[Any, dict[str, Any]] = {}
    for index, story in enumerate(stories):
        if not isinstance(story, dict):
            raise SmokeError(f"row-one edition stories[{index}] must be a JSON object")
        story_id = story.get("id")
        expected_story_ids.append(story_id)
        story_by_id[story_id] = story
    assert_equal(
        "row-one story_directory story_ids",
        story_directory.get("story_ids"),
        expected_story_ids,
    )

    routes = story_directory.get("routes")
    if not isinstance(routes, list):
        raise SmokeError("row-one story_directory routes must be a JSON array")
    assert_equal("row-one story_directory routes length", len(routes), len(stories))
    for index, route in enumerate(routes):
        if not isinstance(route, dict):
            raise SmokeError(f"row-one story_directory routes[{index}] must be a JSON object")
        story_id = route.get("story_id")
        story = story_by_id.get(story_id)
        if story is None:
            raise SmokeError(f"row-one story_directory routes[{index}] story_id is unknown")
        section = story.get("section")
        if not isinstance(section, dict):
            raise SmokeError(f"row-one edition stories[{index}] section must be a JSON object")
        for key, expected in (
            ("detail_href", story.get("detail_href")),
            ("section_key", story.get("section_key")),
            ("section_href", section.get("href")),
            ("published_date", story.get("published_date")),
        ):
            assert_equal(
                f"row-one story_directory routes[{index}] {key}",
                route.get(key),
                expected,
            )


def validate_row_one_edition_brief(edition_payload: Any) -> None:
    if not isinstance(edition_payload, dict):
        raise SmokeError("row-one edition must be a JSON object")
    brief = edition_payload.get("edition_brief")
    if not isinstance(brief, dict):
        raise SmokeError("row-one edition edition_brief must be a JSON object")
    story_directory = edition_payload.get("story_directory")
    if not isinstance(story_directory, dict):
        raise SmokeError("row-one edition story_directory must be a JSON object")
    assert_equal(
        "row-one edition_brief story_directory_story_count",
        brief.get("story_directory_story_count"),
        story_directory.get("story_count"),
    )
    metrics = brief.get("metrics")
    if not isinstance(metrics, list) or len(metrics) != 4:
        raise SmokeError("row-one edition_brief metrics must contain four metrics")
    content_sections = edition_payload.get("content_sections")
    if not isinstance(content_sections, list):
        content_sections = []
    daily_digest = edition_payload.get("daily_digest")
    briefing_topics = daily_digest.get("briefing_topics") if isinstance(daily_digest, dict) else []
    if not isinstance(briefing_topics, list):
        briefing_topics = []
    expected_metrics = (
        ("stories", edition_payload.get("story_count")),
        (
            "sections",
            len(
                [
                    section
                    for section in content_sections
                    if isinstance(section, dict) and int(section.get("story_count", 0)) > 0
                ]
            ),
        ),
        ("topics", len([topic for topic in briefing_topics if isinstance(topic, dict)])),
        ("evidence", edition_payload.get("evidence_count")),
    )
    for index, (expected_key, expected_value) in enumerate(expected_metrics):
        metric = metrics[index]
        if not isinstance(metric, dict):
            raise SmokeError(f"row-one edition_brief metrics[{index}] must be a JSON object")
        assert_equal(
            f"row-one edition_brief metrics[{index}] key",
            metric.get("key"),
            expected_key,
        )
        assert_equal(
            f"row-one edition_brief metrics[{index}] value",
            metric.get("value"),
            expected_value,
        )


def validate_row_one_signal_synthesis(edition_payload: Any) -> None:
    if not isinstance(edition_payload, dict):
        raise SmokeError("row-one edition must be a JSON object")
    synthesis = edition_payload.get("signal_synthesis")
    if not isinstance(synthesis, dict):
        raise SmokeError("row-one edition signal_synthesis must be a JSON object")
    boundaries = synthesis.get("boundaries")
    if not isinstance(boundaries, dict):
        raise SmokeError("row-one edition signal_synthesis boundaries must be a JSON object")
    assert_equal(
        "row-one signal_synthesis boundaries en",
        boundaries.get("en"),
        "Local observed signals; review required.",
    )
    assert_equal(
        "row-one signal_synthesis boundaries zh",
        boundaries.get("zh"),
        "本地观察，需人工复核。",
    )
    stories = edition_payload.get("stories")
    if not isinstance(stories, list):
        raise SmokeError("row-one edition stories must be a JSON array")
    story_by_id = {
        story.get("id"): story for story in stories if isinstance(story, dict) and story.get("id")
    }
    groups = synthesis.get("groups")
    if not isinstance(groups, list):
        raise SmokeError("row-one edition signal_synthesis groups must be a JSON array")
    assert_equal("row-one signal_synthesis group_count", synthesis.get("group_count"), len(groups))
    signal_count = 0
    for group_index, group in enumerate(groups):
        if not isinstance(group, dict):
            raise SmokeError(f"row-one signal_synthesis groups[{group_index}] must be an object")
        signals = group.get("signals")
        if not isinstance(signals, list):
            raise SmokeError(
                f"row-one signal_synthesis groups[{group_index}] signals must be a JSON array"
            )
        assert_equal(
            f"row-one signal_synthesis groups[{group_index}] signal_count",
            group.get("signal_count"),
            len(signals),
        )
        signal_count += len(signals)
        for signal_index, signal in enumerate(signals):
            if not isinstance(signal, dict):
                raise SmokeError(
                    f"row-one signal_synthesis groups[{group_index}] signals[{signal_index}] "
                    "must be an object"
                )
            lead_story_id = signal.get("lead_story_id")
            story = story_by_id.get(lead_story_id)
            if story is None:
                raise SmokeError(
                    f"row-one signal_synthesis groups[{group_index}] signals[{signal_index}] "
                    "lead_story_id is unknown"
                )
            assert_equal(
                f"row-one signal_synthesis groups[{group_index}] signals[{signal_index}] "
                "lead_story_href",
                signal.get("lead_story_href"),
                story.get("detail_href"),
            )
            story_ids = signal.get("story_ids")
            if not isinstance(story_ids, list) or lead_story_id not in story_ids:
                raise SmokeError(
                    f"row-one signal_synthesis groups[{group_index}] signals[{signal_index}] "
                    "story_ids must include lead_story_id"
                )
            story_refs = signal.get("story_refs")
            if not isinstance(story_refs, list) or not story_refs:
                raise SmokeError(
                    f"row-one signal_synthesis groups[{group_index}] signals[{signal_index}] "
                    "story_refs must be a non-empty JSON array"
                )
            for ref_index, ref in enumerate(story_refs):
                if not isinstance(ref, dict):
                    raise SmokeError(
                        f"row-one signal_synthesis groups[{group_index}] signals[{signal_index}] "
                        f"story_refs[{ref_index}] must be an object"
                    )
                if "story_id" not in ref:
                    raise SmokeError(
                        f"row-one signal_synthesis groups[{group_index}] "
                        f"signals[{signal_index}] story_refs[{ref_index}] story_id is required"
                    )
            story_ref_ids = [ref.get("story_id") for ref in story_refs]
            assert_equal(
                f"row-one signal_synthesis groups[{group_index}] signals[{signal_index}] "
                "story_refs ids",
                story_ref_ids,
                story_ids,
            )
            for ref_index, ref in enumerate(story_refs):
                ref_story = story_by_id.get(ref.get("story_id"))
                if ref_story is None:
                    raise SmokeError(
                        f"row-one signal_synthesis groups[{group_index}] signals[{signal_index}] "
                        f"story_refs[{ref_index}] story_id is unknown"
                    )
                section = ref_story.get("section")
                if not isinstance(section, dict):
                    raise SmokeError(
                        f"row-one signal_synthesis groups[{group_index}] signals[{signal_index}] "
                        f"story_refs[{ref_index}] story section must be an object"
                    )
                for key, expected in (
                    ("headline", ref_story.get("headline")),
                    ("section_key", ref_story.get("section_key")),
                    ("section_title", section.get("title")),
                    ("detail_href", ref_story.get("detail_href")),
                    ("source_name", ref_story.get("source_name")),
                    ("published_date", ref_story.get("published_date")),
                    ("evidence_count", ref_story.get("evidence_count")),
                    ("heat_delta", ref_story.get("heat_delta")),
                ):
                    if key not in ref:
                        raise SmokeError(
                            f"row-one signal_synthesis groups[{group_index}] "
                            f"signals[{signal_index}] story_refs[{ref_index}] {key} is required"
                        )
                    assert_equal(
                        f"row-one signal_synthesis groups[{group_index}] "
                        f"signals[{signal_index}] story_refs[{ref_index}] {key}",
                        ref.get(key),
                        expected,
                    )
    assert_equal(
        "row-one signal_synthesis signal_count",
        synthesis.get("signal_count"),
        signal_count,
    )


def validate_row_one_runtime(
    runtime_payload: Any,
    manifest_payload: Any,
    edition_payload: Any,
) -> None:
    if not isinstance(runtime_payload, dict):
        raise SmokeError("row-one runtime must be a JSON object")

    assert_equal(
        "row-one runtime contract_version",
        runtime_payload.get("contract_version"),
        "row-one-runtime/v1",
    )
    assert_equal("row-one runtime brand", runtime_payload.get("brand"), "ROW ONE")
    assert_equal(
        "row-one runtime schema path",
        runtime_payload.get("runtime_schema_path"),
        "schemas/row-one-runtime.schema.json",
    )

    site = runtime_payload.get("site")
    if not isinstance(site, dict):
        raise SmokeError("row-one runtime site must be a JSON object")
    for key, expected in (
        ("index_path", "index.html"),
        ("edition_path", "data/edition.json"),
        ("manifest_path", "data/manifest.json"),
        ("runtime_path", "data/runtime.json"),
    ):
        assert_equal(f"row-one runtime site {key}", site.get(key), expected)

    refresh = runtime_payload.get("refresh")
    if not isinstance(refresh, dict):
        raise SmokeError("row-one runtime refresh must be a JSON object")
    assert_equal("row-one runtime refresh time", refresh.get("recommended_time"), "04:00")
    assert_equal(
        "row-one runtime cleanup mode",
        refresh.get("latest_only_cleanup"),
        True,
    )
    command = refresh.get("command")
    if not isinstance(command, str) or "fashion-radar row-one refresh" not in command:
        raise SmokeError("row-one runtime refresh command must run row-one refresh")

    serve = runtime_payload.get("serve")
    if not isinstance(serve, dict):
        raise SmokeError("row-one runtime serve must be a JSON object")
    assert_equal("row-one runtime host", serve.get("default_host"), "127.0.0.1")
    assert_equal("row-one runtime port", serve.get("default_port"), 8787)
    assert_equal("row-one runtime local_url", serve.get("local_url"), "http://127.0.0.1:8787")
    assert_equal(
        "row-one runtime lan_url_hint",
        serve.get("lan_url_hint"),
        "http://<LAN-IP>:8787",
    )
    assert_equal(
        "row-one runtime generated_at",
        runtime_payload.get("generated_at"),
        edition_payload.get("generated_at"),
    )
    assert_equal(
        "row-one runtime edition_date",
        runtime_payload.get("edition_date"),
        edition_payload.get("edition_date"),
    )

    counts = runtime_payload.get("counts")
    if not isinstance(counts, dict):
        raise SmokeError("row-one runtime counts must be a JSON object")
    manifest_counts = manifest_payload.get("counts")
    if not isinstance(manifest_counts, dict):
        raise SmokeError("row-one manifest counts must be a JSON object")
    assert_equal("row-one runtime counts", counts, manifest_counts)

    readiness = runtime_payload.get("readiness")
    if not isinstance(readiness, dict):
        raise SmokeError("row-one runtime readiness must be a JSON object")
    manifest_readiness = manifest_payload.get("readiness")
    if not isinstance(manifest_readiness, dict):
        raise SmokeError("row-one manifest readiness must be a JSON object")
    assert_equal(
        "row-one runtime readiness status",
        readiness.get("status"),
        manifest_readiness.get("status"),
    )
    assert_equal("row-one runtime readiness en", readiness.get("en"), readiness.get("status"))
    if not isinstance(readiness.get("zh"), str) or not readiness.get("zh"):
        raise SmokeError("row-one runtime readiness zh must be a non-empty string")
    validate_row_one_story_directory(edition_payload)
    validate_row_one_edition_brief(edition_payload)
    validate_row_one_signal_synthesis(edition_payload)


def validate_row_one_status_payload(
    status_payload: Any,
    *,
    runtime_payload: Mapping[str, Any],
    manifest_payload: Mapping[str, Any],
) -> None:
    if not isinstance(status_payload, dict):
        raise SmokeError("row-one status --json output must be a JSON object")
    assert_equal("row-one status ok", status_payload.get("ok"), True)
    assert_equal(
        "row-one status paths",
        status_payload.get("paths"),
        {
            "manifest": "data/manifest.json",
            "edition": "data/edition.json",
            "runtime": "data/runtime.json",
        },
    )
    assert_equal(
        "row-one status contracts",
        status_payload.get("contracts"),
        {
            "app": "row-one-app/v7",
            "manifest": "row-one-manifest/v1",
            "runtime": "row-one-runtime/v1",
        },
    )
    assert_equal("row-one status runtime payload", status_payload.get("runtime"), runtime_payload)
    assert_equal(
        "row-one status manifest payload", status_payload.get("manifest"), manifest_payload
    )
    assert_equal(
        "row-one status counts", status_payload.get("counts"), runtime_payload.get("counts")
    )
    assert_equal(
        "row-one status readiness",
        status_payload.get("readiness"),
        runtime_payload.get("readiness"),
    )
    assert_equal("row-one status site", status_payload.get("site"), runtime_payload.get("site"))
    assert_equal("row-one status serve", status_payload.get("serve"), runtime_payload.get("serve"))
    assert_equal(
        "row-one status refresh",
        status_payload.get("refresh"),
        runtime_payload.get("refresh"),
    )


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


def validate_imported_review_workflow(
    command_name: str,
    payload: Any,
    *,
    expected_config_dir: str = "configs",
    expected_data_dir: str = "data",
) -> None:
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
    for index, step in enumerate(steps, start=1):
        if not isinstance(step, dict):
            raise SmokeError(f"{command_name} step {index} must be a JSON object")
    step_metadata = [
        {
            "order": step.get("order"),
            "name": step.get("name"),
            "purpose": step.get("purpose"),
            "suggested_effect": step.get("suggested_effect"),
        }
        for step in steps
    ]
    assert_equal(
        f"{command_name} step metadata",
        step_metadata,
        EXPECTED_IMPORTED_REVIEW_WORKFLOW_STEP_METADATA,
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
    assert_equal(f"{command_name} config_dir", payload.get("config_dir"), expected_config_dir)
    assert_equal(f"{command_name} data_dir", payload.get("data_dir"), expected_data_dir)
    as_of = EXPECTED_WORKFLOW_AS_OF
    source_name = SOURCE_NAME
    lookback_days = str(EXPECTED_IMPORTED_REVIEW_LOOKBACK_DAYS)
    current_days = str(EXPECTED_IMPORTED_REVIEW_CURRENT_DAYS)
    baseline_days = str(EXPECTED_IMPORTED_REVIEW_BASELINE_DAYS)

    expected_commands = expected_imported_review_workflow_command_parts(
        config_dir=expected_config_dir,
        data_dir=expected_data_dir,
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


def validate_community_handoff_workflow(
    command_name: str,
    payload: Any,
    *,
    expected_directory: str = "/tmp/export",
    expected_config_dir: str = "configs",
    expected_data_dir: str = "data",
) -> None:
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
    assert_equal(f"{command_name} directory", payload.get("directory"), expected_directory)
    assert_equal(f"{command_name} config_dir", payload.get("config_dir"), expected_config_dir)
    assert_equal(f"{command_name} data_dir", payload.get("data_dir"), expected_data_dir)
    input_format = EXPECTED_COMMUNITY_HANDOFF_INPUT_FORMAT
    pattern = DIR_PATTERN
    as_of = EXPECTED_WORKFLOW_AS_OF
    source_name = SOURCE_NAME

    expected_commands = expected_community_handoff_workflow_command_parts(
        directory=expected_directory,
        input_format=input_format,
        pattern=pattern,
        config_dir=expected_config_dir,
        data_dir=expected_data_dir,
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
    for index, step in enumerate(steps, start=1):
        if not isinstance(step, dict):
            raise SmokeError(f"{command_name} step {index} must be a JSON object")
    step_metadata = [
        {
            "order": step.get("order"),
            "name": step.get("name"),
            "purpose": step.get("purpose"),
            "suggested_effect": step.get("suggested_effect"),
        }
        for step in steps
    ]
    assert_equal(
        f"{command_name} step metadata",
        step_metadata,
        EXPECTED_COMMUNITY_HANDOFF_WORKFLOW_STEP_METADATA,
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


def validate_external_tool_workflow(
    command_name: str,
    payload: Any,
    *,
    expected_directory: str = "exports",
    expected_config_dir: str = "configs",
    expected_data_dir: str = "data",
) -> None:
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
    assert_equal(
        f"{command_name} display_name",
        payload.get("display_name"),
        EXPECTED_EXTERNAL_TOOL_DISPLAY_NAME,
    )
    assert_equal(f"{command_name} input_format", payload.get("input_format"), "json")
    assert_equal(f"{command_name} pattern", payload.get("pattern"), "*.json")
    assert_equal(f"{command_name} as_of", payload.get("as_of"), "2026-06-13T12:00:00+00:00")
    assert_equal(f"{command_name} source_name", payload.get("source_name"), "Rednote MCP Export")
    assert_equal(f"{command_name} step_count", payload.get("step_count"), 12)
    assert_equal(f"{command_name} directory", payload.get("directory"), expected_directory)
    assert_equal(f"{command_name} config_dir", payload.get("config_dir"), expected_config_dir)
    assert_equal(f"{command_name} data_dir", payload.get("data_dir"), expected_data_dir)
    adapter_id = str(payload["adapter_id"])
    directory = expected_directory
    config_dir = expected_config_dir
    data_dir = expected_data_dir
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


def validate_external_tool_readiness(
    command_name: str,
    payload: Any,
    *,
    expected_directory: str = "exports",
    expected_config_dir: str = "configs",
    expected_data_dir: str = "data",
) -> None:
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
    assert_equal(
        f"{command_name} display_name",
        payload.get("display_name"),
        EXPECTED_EXTERNAL_TOOL_DISPLAY_NAME,
    )
    assert_equal(f"{command_name} input_format", payload.get("input_format"), "json")
    assert_equal(f"{command_name} pattern", payload.get("pattern"), "*.json")
    assert_equal(f"{command_name} as_of", payload.get("as_of"), "2026-06-13T12:00:00+00:00")
    assert_equal(f"{command_name} source_name", payload.get("source_name"), "Rednote MCP Export")
    assert_equal(f"{command_name} step_count", payload.get("step_count"), 7)
    assert_equal(f"{command_name} directory", payload.get("directory"), expected_directory)
    assert_equal(f"{command_name} config_dir", payload.get("config_dir"), expected_config_dir)
    assert_equal(f"{command_name} data_dir", payload.get("data_dir"), expected_data_dir)
    adapter_id = str(payload["adapter_id"])
    directory = expected_directory
    config_dir = expected_config_dir
    data_dir = expected_data_dir
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
    brief = json_payload.get("brief")
    if not isinstance(brief, dict):
        raise SmokeError("report JSON brief must be an object")
    assert_equal("report brief contract_version", brief.get("contract_version"), "daily-brief/v1")
    if not report_brief_mentions(brief, "The Row"):
        raise SmokeError("report brief missing sample item mentioning The Row")
    if "## Daily Brief" not in markdown_text:
        raise SmokeError("report Markdown missing Daily Brief section")
    entities = json_payload.get("entities")
    if not isinstance(entities, list):
        raise SmokeError("report JSON entities must be a list")
    entity_names = [entity.get("entity_name") for entity in entities if isinstance(entity, dict)]
    assert_equal("report entity names", entity_names, list(EXPECTED_SAMPLE_ENTITIES))
    for index, entity in enumerate(entities, start=1):
        validate_report_entity_json(entity, index=index)
    for expected in EXPECTED_SAMPLE_ENTITIES:
        if f"### {expected} (new)" not in markdown_text:
            raise SmokeError(f"report Markdown missing sample entity section: {expected}")
    if "No entity signals in this window." in markdown_text:
        raise SmokeError("report Markdown should not contain the empty entity signal message")


def validate_report_entity_json(entity: Any, *, index: int) -> None:
    if not isinstance(entity, dict):
        raise SmokeError(f"report JSON entity {index} must be an object")

    entity_name = str(entity.get("entity_name", f"entity {index}"))
    forbidden_field = find_forbidden_report_entity_matcher_text(entity)
    if forbidden_field is not None:
        raise SmokeError(
            f"report JSON entity {entity_name} contains raw matcher field: {forbidden_field}"
        )

    match_evidence = entity.get("match_evidence")
    if not isinstance(match_evidence, dict):
        raise SmokeError(f"report JSON entity {entity_name} match_evidence must be an object")
    assert_equal(
        f"report JSON entity {entity_name} match_evidence keys",
        list(match_evidence),
        list(EXPECTED_ENTITY_MATCH_EVIDENCE_KEYS),
    )

    for field in EXPECTED_ENTITY_MATCH_EVIDENCE_COUNT_KEYS:
        value = match_evidence.get(field)
        if not isinstance(value, int) or isinstance(value, bool) or value < 0:
            raise SmokeError(
                f"report JSON entity {entity_name} match_evidence {field} "
                "must be a non-negative integer"
            )

    matched_items = match_evidence["matched_items"]
    if entity.get("entity_name") == "The Row":
        if matched_items < 1:
            raise SmokeError("report JSON entity The Row match_evidence matched_items must be >= 1")


def find_forbidden_report_entity_matcher_text(value: Any) -> str | None:
    if isinstance(value, dict):
        for key, child in value.items():
            if key in FORBIDDEN_REPORT_ENTITY_MATCHER_FIELDS:
                return str(key)
            found = find_forbidden_report_entity_matcher_text(child)
            if found is not None:
                return found
    elif isinstance(value, list):
        for child in value:
            found = find_forbidden_report_entity_matcher_text(child)
            if found is not None:
                return found
    return None


def report_brief_mentions(brief: Mapping[str, Any], expected_text: str) -> bool:
    sections = brief.get("sections")
    if not isinstance(sections, list):
        raise SmokeError("report JSON brief sections must be a list")
    for section_index, section in enumerate(sections, start=1):
        if not isinstance(section, dict):
            raise SmokeError(f"report JSON brief section {section_index} must be an object")
        items = section.get("items")
        if not isinstance(items, list):
            raise SmokeError(f"report JSON brief section {section_index} items must be a list")
        for item_index, item in enumerate(items, start=1):
            if not isinstance(item, dict):
                raise SmokeError(
                    f"report JSON brief section {section_index} item {item_index} must be an object"
                )
            if item.get("title") == expected_text:
                return True
    return False


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
    checked_deltas: list[dict[str, Any]] = []
    for index, delta in enumerate(deltas, start=1):
        if not isinstance(delta, dict):
            raise SmokeError(f"{command_name} delta {index} must be a JSON object")
        checked_deltas.append(delta)
    deltas_by_name = {str(delta.get("name")): delta for delta in checked_deltas}
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


def report_paths(context: SmokeContext) -> tuple[Path, Path, Path]:
    report_date = AS_OF.split("T", 1)[0]
    return (
        context.reports_dir / f"fashion-radar-{report_date}.md",
        context.reports_dir / f"fashion-radar-{report_date}.json",
        context.reports_dir / f"fashion-radar-{report_date}.html",
    )


def file_digest(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


DEFAULT_GENERATED_CONFIG_ARTIFACT_PATHS = (
    Path("configs/sources.yaml"),
    Path("configs/entities.yaml"),
    Path("configs/scoring.yaml"),
)


def snapshot_default_artifacts(repo_root: Path) -> dict[Path, str]:
    artifacts: dict[Path, str] = {}
    for directory_name in ("data", "reports"):
        directory = repo_root / directory_name
        if not directory.exists():
            continue
        for path in directory.rglob("*"):
            if path.is_file():
                artifacts[path.relative_to(repo_root)] = file_digest(path)

    for relative_path in DEFAULT_GENERATED_CONFIG_ARTIFACT_PATHS:
        path = repo_root / relative_path
        if path.is_file():
            artifacts[relative_path] = file_digest(path)
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
    raise SmokeError(
        "Smoke changed files under default data/reports or generated configs "
        f"({'; '.join(changes)})"
    )


def format_paths(paths: Sequence[Path]) -> str:
    return ", ".join(path.as_posix() for path in paths)


def run_cli(context: SmokeContext, *args: str) -> subprocess.CompletedProcess[str]:
    command = cli_command(context, *args)
    try:
        completed = subprocess.run(
            command,
            cwd=context.repo_root,
            env=command_environment(context, source_checkout=context.source_checkout),
            text=True,
            capture_output=True,
            check=False,
            timeout=SMOKE_COMMAND_TIMEOUT_SECONDS,
        )
    except subprocess.TimeoutExpired as exc:
        raise SmokeError(format_command_timeout(command, exc)) from exc
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


def format_command_timeout(command: Sequence[str], exc: subprocess.TimeoutExpired) -> str:
    command_text = " ".join(shlex.quote(part) for part in command)
    return (
        f"Command timed out after {exc.timeout} seconds: {command_text}\n"
        f"stdout:\n{_format_timeout_output(exc.stdout)}\n"
        f"stderr:\n{_format_timeout_output(exc.stderr)}"
    )


def _format_timeout_output(output: object) -> str:
    if output is None:
        return "<empty>"
    if isinstance(output, bytes):
        text = output.decode("utf-8", errors="replace")
    else:
        text = str(output)
    stripped = text.strip()
    if not stripped:
        return "<empty>"
    if len(stripped) <= 1000:
        return stripped
    return f"{stripped[:1000]}..."


def _reserve_local_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(("127.0.0.1", 0))
        return int(sock.getsockname()[1])


def _fetch_local_http_path(port: int, path: str) -> str:
    connection = http.client.HTTPConnection("127.0.0.1", port, timeout=0.75)
    try:
        connection.request("GET", path)
        response = connection.getresponse()
        body = response.read().decode("utf-8")
    finally:
        connection.close()
    if response.status != 200:
        raise OSError(f"{path} returned HTTP {response.status}")
    return body


def _fetch_local_http_path_with_retry(port: int, path: str) -> str:
    last_error: OSError | None = None
    for _attempt in range(3):
        try:
            return _fetch_local_http_path(port, path)
        except OSError as exc:
            last_error = exc
            time.sleep(0.1)
    if last_error is not None:
        raise last_error
    raise OSError(f"{path} was not fetched")


def _process_output_snippet(output: str, *, limit: int = 1000) -> str:
    stripped = output.strip()
    if not stripped:
        return "<empty>"
    if len(stripped) <= limit:
        return stripped
    return f"{stripped[:limit]}..."


def _raise_row_one_serve_exited(
    command: Sequence[str],
    process: subprocess.Popen[str],
    *,
    port: int,
    returncode: int | None = None,
) -> None:
    stdout, stderr = process.communicate()
    command_text = " ".join(shlex.quote(part) for part in command)
    if returncode is None:
        returncode = process.returncode
    raise SmokeError(
        "row-one serve exited before HTTP readiness "
        f"on port {port} with exit code {returncode}: {command_text}\n"
        f"stdout:\n{_process_output_snippet(stdout)}\n"
        f"stderr:\n{_process_output_snippet(stderr)}"
    )


def _is_retryable_row_one_serve_startup_error(exc: SmokeError) -> bool:
    message = str(exc).lower()
    return "address already in use" in message or "errno 98" in message or "eaddrinuse" in message


def _wait_for_row_one_http_ready(
    command: Sequence[str],
    process: subprocess.Popen[str],
    *,
    port: int,
) -> str:
    deadline = time.monotonic() + 10.0
    last_error: OSError | None = None
    while time.monotonic() < deadline:
        returncode = process.poll()
        if returncode is not None:
            _raise_row_one_serve_exited(command, process, port=port, returncode=returncode)
        try:
            return _fetch_local_http_path(port, "/")
        except OSError as exc:
            last_error = exc
            time.sleep(0.1)
    returncode = process.poll()
    if returncode is not None:
        _raise_row_one_serve_exited(command, process, port=port, returncode=returncode)
    detail = f": {last_error}" if last_error is not None else ""
    raise OSError(f"row-one serve did not become ready on port {port}{detail}")


def _stop_row_one_serve_process(process: subprocess.Popen[str]) -> None:
    if process.poll() is not None:
        return
    process.terminate()
    try:
        process.communicate(timeout=5)
    except subprocess.TimeoutExpired:
        process.kill()
        process.communicate(timeout=5)


def _validate_row_one_contract_payload(
    path: str,
    payload: Any,
    *,
    expected_contract_version: str,
) -> dict[str, Any]:
    if not isinstance(payload, dict):
        raise SmokeError(f"row-one serve {path} returned non-object JSON")
    assert_equal(
        f"row-one serve {path} contract_version",
        payload.get("contract_version"),
        expected_contract_version,
    )
    return payload


def _fetch_row_one_contract_payload(
    port: int,
    path: str,
    *,
    expected_contract_version: str,
) -> dict[str, Any]:
    payload = validate_json_output(
        f"row-one serve {path}",
        _fetch_local_http_path_with_retry(port, path),
    )
    return _validate_row_one_contract_payload(
        path,
        payload,
        expected_contract_version=expected_contract_version,
    )


def _first_row_one_detail_path(edition_payload: Mapping[str, Any]) -> str | None:
    story_directory = edition_payload.get("story_directory")
    if not isinstance(story_directory, Mapping):
        return None
    routes = story_directory.get("routes")
    if not isinstance(routes, list) or not routes:
        return None
    first_route = routes[0]
    if not isinstance(first_route, Mapping):
        return None
    detail_href = first_route.get("detail_href")
    if not isinstance(detail_href, str) or not detail_href:
        return None
    detail_path = detail_href.split("#", 1)[0]
    if not detail_path:
        return None
    return detail_path if detail_path.startswith("/") else f"/{detail_path}"


def _validate_row_one_local_http_paths(port: int, root_body: str) -> None:
    if "ROW ONE" not in root_body:
        raise SmokeError("row-one serve / output missing expected text: ROW ONE")

    _fetch_row_one_contract_payload(
        port,
        "/data/manifest.json",
        expected_contract_version="row-one-manifest/v1",
    )
    edition_payload = _fetch_row_one_contract_payload(
        port,
        "/data/edition.json",
        expected_contract_version="row-one-app/v7",
    )
    _fetch_row_one_contract_payload(
        port,
        "/data/runtime.json",
        expected_contract_version="row-one-runtime/v1",
    )
    for asset_path in ("/assets/row-one.css", "/assets/row-one.js"):
        if not _fetch_local_http_path_with_retry(port, asset_path).strip():
            raise SmokeError(f"row-one serve {asset_path} returned an empty body")

    detail_path = _first_row_one_detail_path(edition_payload)
    if detail_path is not None:
        _fetch_local_http_path_with_retry(port, detail_path)


def run_row_one_local_http_serve_smoke(context: SmokeContext, site_dir: Path) -> None:
    startup_errors: list[str] = []
    for _attempt in range(3):
        port = _reserve_local_port()
        command = cli_command(
            context,
            "row-one",
            "serve",
            "--site-dir",
            str(site_dir),
            "--host",
            "127.0.0.1",
            "--port",
            str(port),
        )
        process = subprocess.Popen(
            command,
            cwd=context.repo_root,
            env=command_environment(context, source_checkout=context.source_checkout),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        try:
            try:
                root_body = _wait_for_row_one_http_ready(command, process, port=port)
            except OSError as exc:
                startup_errors.append(f"port {port}: {exc}")
                continue
            except SmokeError as exc:
                if _is_retryable_row_one_serve_startup_error(exc):
                    startup_errors.append(f"port {port}: {exc}")
                    continue
                raise
            try:
                _validate_row_one_local_http_paths(port, root_body)
            except OSError as exc:
                returncode = process.poll()
                if returncode is not None:
                    _raise_row_one_serve_exited(
                        command,
                        process,
                        port=port,
                        returncode=returncode,
                    )
                raise SmokeError(f"ROW ONE local HTTP serve smoke failed: {exc}") from exc
            return
        finally:
            _stop_row_one_serve_process(process)

    raise SmokeError(
        "ROW ONE local HTTP serve smoke failed after 3 startup attempts: "
        + "; ".join(startup_errors)
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


def assert_not_exists(path: Path) -> None:
    if path.exists():
        raise SmokeError(f"Unexpected path exists: {path}")


def write_first_run_sample_sources_config(config_dir: Path) -> None:
    """Keep the sample smoke deterministic by avoiding live source collection."""
    (config_dir / "sources.yaml").write_text("version: 1\nsources: []\n", encoding="utf-8")


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
    write_first_run_sample_sources_config(context.config_dir)
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
    validate_external_tool_workflow(
        "external-tool-workflow",
        external_tool_workflow,
        expected_directory=str(context.exports_dir),
        expected_config_dir=str(context.config_dir),
        expected_data_dir=str(context.data_dir),
    )
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
    validate_external_tool_readiness(
        "external-tool-readiness",
        external_tool_readiness,
        expected_directory=str(context.exports_dir),
        expected_config_dir=str(context.config_dir),
        expected_data_dir=str(context.data_dir),
    )
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
    validate_imported_review_workflow(
        "imported-review-workflow",
        imported_review_workflow,
        expected_config_dir=str(context.config_dir),
        expected_data_dir=str(context.data_dir),
    )
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
    markdown_path, json_path, html_path = report_paths(context)
    assert_non_empty_file(markdown_path)
    assert_non_empty_file(json_path)
    assert_non_empty_file(html_path)
    report_payload = validate_json_output("report JSON", json_path.read_text(encoding="utf-8"))
    validate_report_outputs(report_payload, markdown_path.read_text(encoding="utf-8"))
    for command_parts in (
        ("row-one", "--help"),
        ("row-one", "build", "--help"),
        ("row-one", "refresh", "--help"),
        ("row-one", "serve", "--help"),
        ("row-one", "schedule", "--help"),
        ("row-one", "preview", "--help"),
        ("row-one", "status", "--help"),
        ("row-one", "local-ops", "--help"),
        ("row-one", "install-local", "--help"),
    ):
        run_cli(context, *command_parts)
    validate_row_one_schedule_output(
        run_cli(context, "row-one", "schedule", "--time", "04:00").stdout
    )
    row_one_output_dir = context.reports_dir / "row-one" / "site"
    stale_report_artifact_names = (
        "fashion-radar-2026-06-12.md",
        "fashion-radar-2026-06-12.json",
        "fashion-radar-2026-06-12.html",
    )
    for name in stale_report_artifact_names:
        (context.reports_dir / name).write_text("stale", encoding="utf-8")
    untouched_report_note = context.reports_dir / "notes.txt"
    untouched_report_note.write_text("keep me", encoding="utf-8")
    run_cli(
        context,
        "row-one",
        "refresh",
        "--config-dir",
        str(context.config_dir),
        "--data-dir",
        str(context.data_dir),
        "--reports-dir",
        str(context.reports_dir),
        "--output-dir",
        str(row_one_output_dir),
        "--as-of",
        AS_OF,
        "--skip-data-retention",
    )
    for name in stale_report_artifact_names:
        assert_not_exists(context.reports_dir / name)
    assert_non_empty_file(context.reports_dir / "fashion-radar-2026-06-13.md")
    assert_non_empty_file(context.reports_dir / "fashion-radar-2026-06-13.json")
    assert_non_empty_file(context.reports_dir / "fashion-radar-2026-06-13.html")
    assert_non_empty_file(untouched_report_note)
    row_one_preview = run_cli(
        context,
        "row-one",
        "preview",
        "--config-dir",
        str(context.config_dir),
        "--data-dir",
        str(context.data_dir),
        "--reports-dir",
        str(context.reports_dir),
        "--output-dir",
        str(row_one_output_dir),
        "--as-of",
        AS_OF,
        "--latest-only",
        "--dry-run-serve-url",
    ).stdout
    assert_output_contains_text(
        "row-one preview",
        row_one_preview,
        (
            "ROW ONE preview",
            f"Site: {row_one_output_dir / 'index.html'}",
            f"JSON: {row_one_output_dir / 'data' / 'edition.json'}",
            f"Manifest: {row_one_output_dir / 'data' / 'manifest.json'}",
            f"Runtime: {row_one_output_dir / 'data' / 'runtime.json'}",
            "Stories:",
            "Sections:",
            "Evidence links:",
            "Empty sections:",
            "Generated at:",
            "Readiness:",
            "Open:",
        ),
    )
    assert_non_empty_file(row_one_output_dir / "index.html")
    row_one_edition_path = row_one_output_dir / "data" / "edition.json"
    row_one_manifest_path = row_one_output_dir / "data" / "manifest.json"
    row_one_runtime_path = row_one_output_dir / "data" / "runtime.json"
    assert_non_empty_file(row_one_edition_path)
    assert_non_empty_file(row_one_manifest_path)
    assert_non_empty_file(row_one_runtime_path)
    row_one_edition_payload = validate_json_output(
        "row-one edition",
        row_one_edition_path.read_text(encoding="utf-8"),
    )
    row_one_manifest_payload = validate_json_output(
        "row-one manifest",
        row_one_manifest_path.read_text(encoding="utf-8"),
    )
    row_one_runtime_payload = validate_json_output(
        "row-one runtime",
        row_one_runtime_path.read_text(encoding="utf-8"),
    )
    validate_row_one_manifest(row_one_manifest_payload, row_one_edition_payload)
    validate_row_one_runtime(
        row_one_runtime_payload,
        row_one_manifest_payload,
        row_one_edition_payload,
    )
    row_one_status = run_cli(
        context,
        "row-one",
        "status",
        "--site-dir",
        str(row_one_output_dir),
        "--json",
    ).stdout
    row_one_status_payload = validate_json_output("row-one status --json", row_one_status)
    validate_row_one_status_payload(
        row_one_status_payload,
        runtime_payload=row_one_runtime_payload,
        manifest_payload=row_one_manifest_payload,
    )
    row_one_serve = run_cli(
        context,
        "row-one",
        "serve",
        "--site-dir",
        str(row_one_output_dir),
        "--host",
        "127.0.0.1",
        "--port",
        "8787",
        "--dry-run",
    ).stdout
    assert_output_contains(
        "row-one serve --dry-run",
        row_one_serve,
        ("Open: http://127.0.0.1:8787",),
    )
    run_row_one_local_http_serve_smoke(context, row_one_output_dir)
    row_one_local_ops = run_cli(
        context,
        "row-one",
        "local-ops",
        "--config-dir",
        str(context.config_dir),
        "--data-dir",
        str(context.data_dir),
        "--reports-dir",
        str(context.reports_dir),
        "--output-dir",
        str(row_one_output_dir),
        "--time",
        "04:00",
        "--host",
        "0.0.0.0",
        "--port",
        "8787",
    ).stdout
    assert_output_contains_text(
        "row-one local-ops",
        row_one_local_ops,
        (
            "ROW ONE local daily ops",
            "fashion-radar row-one refresh",
            "fashion-radar row-one preview",
            "fashion-radar row-one status",
            "fashion-radar row-one serve",
            "Source checkout commands:",
            'AS_OF="$(date -u +%Y-%m-%dT%H:%M:%SZ)"',
            "uv run fashion-radar row-one refresh",
            "uv run fashion-radar row-one preview",
            "--config-dir",
            "--data-dir",
            "--reports-dir",
            "--output-dir",
            '--as-of "$AS_OF"',
            "--latest-only",
            "--host 0.0.0.0",
            "--port 8787",
            "uv run fashion-radar row-one status",
            "--site-dir",
            "uv run fashion-radar row-one serve",
            "--json",
            str(context.config_dir),
            str(context.data_dir),
            str(context.reports_dir),
            str(row_one_output_dir),
            "Open from LAN: http://<LAN-IP>:8787",
            "LAN",
            "cron",
        ),
    )
    assert_output_not_contains_text(
        "row-one local-ops",
        row_one_local_ops,
        ("fashion-radar run", "fashion-radar row-one build"),
    )
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
        expected_directory=str(context.exports_dir),
        expected_config_dir=str(context.config_dir),
        expected_data_dir=str(context.data_dir),
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
        "--strict",
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
    community_handoff_check_dir = validate_json_output(
        "community-handoff-check-dir",
        run_cli(
            context,
            "community-handoff-check-dir",
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
            "--strict",
            "--format",
            "json",
        ).stdout,
    )
    validate_community_handoff_check_dir(
        "community-handoff-check-dir",
        community_handoff_check_dir,
        expected_directory=str(context.exports_dir),
        expected_config_dir=str(context.config_dir),
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
            "--imported-at",
            AS_OF,
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
    try:
        completed = subprocess.run(
            command,
            cwd=context.repo_root,
            env=command_environment(context, source_checkout=False),
            text=True,
            capture_output=True,
            check=False,
            timeout=SMOKE_COMMAND_TIMEOUT_SECONDS,
        )
    except subprocess.TimeoutExpired as exc:
        raise SmokeError(format_command_timeout(command, exc)) from exc
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
