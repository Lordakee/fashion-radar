from __future__ import annotations

import importlib.util
import json
import os
import shlex
import subprocess
import sys
from collections.abc import Callable
from pathlib import Path
from typing import cast

import pytest

from fashion_radar.community_handoff_workflow import build_community_handoff_workflow
from fashion_radar.external_tool_adapters import build_external_tool_adapter_registry
from fashion_radar.external_tool_templates import (
    build_external_tool_template,
    render_external_tool_template_json,
)
from fashion_radar.external_tool_workflow import build_external_tool_workflow
from fashion_radar.imported_review_workflow import build_imported_review_workflow

try:
    from fashion_radar.external_tool_readiness import build_external_tool_readiness
except ModuleNotFoundError:  # pragma: no cover - removed once Stage 66 core lands.
    build_external_tool_readiness = None

REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = REPO_ROOT / "scripts" / "check_first_run_smoke.py"


def load_smoke_module():
    spec = importlib.util.spec_from_file_location("check_first_run_smoke", SCRIPT)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


smoke = load_smoke_module()

SAMPLE_CSV_TEXT = (
    "url,title,published_at,summary,source_name,platform,source_weight,collected_at\n"
    "https://example.com/community/the-row-margaux-tote,"
    "The Row Margaux tote interest,"
    "2026-06-12T08:00:00Z,"
    "Sanitized local note about The Row Margaux handbag and tote demand,"
    "Community Tool Export,community,1.3,2026-06-12T08:30:00Z\n"
    "https://example.com/community/ballet-flats-footwear,"
    "Ballet flats footwear mention,"
    "2026-06-12T09:00:00Z,"
    "Short sanitized note about ballet flats shoes and footwear styling,"
    "Community Tool Export,community,1.1,2026-06-12T09:20:00Z\n"
)

EXTERNAL_TOOL_ADAPTER_CASES = (
    (
        "rednote_mcp",
        "rednote",
        "json",
        "*.json",
        "Rednote MCP Export",
        (
            "Metadata target for Rednote/Xiaohongshu MCP exports that already "
            "produce sanitized local observations."
        ),
        ("rednote-mcp",),
    ),
    (
        "xiaohongshu_crawler",
        "xiaohongshu",
        "csv",
        "*.csv",
        "Xiaohongshu Crawler Export",
        (
            "Metadata target for user-controlled Xiaohongshu crawler exports "
            "converted to the community signal row shape."
        ),
        ("xiaohongshu-crawler",),
    ),
    (
        "instaloader",
        "instagram",
        "json",
        "*.json",
        "Instaloader Export",
        (
            "Metadata target for sanitized Instagram post or profile exports "
            "created outside Fashion Radar."
        ),
        ("Instaloader",),
    ),
    (
        "tiktok_api",
        "tiktok",
        "json",
        "*.json",
        "TikTok-Api Export",
        (
            "Metadata target for sanitized TikTok observations exported by a "
            "user-controlled upstream tool."
        ),
        ("TikTok-Api",),
    ),
    (
        "yt_dlp",
        "media",
        "json",
        "*.json",
        "yt-dlp Metadata Export",
        (
            "Metadata target for sanitized media metadata exports, not media "
            "downloads or stored video assets."
        ),
        ("yt-dlp",),
    ),
    (
        "x_search_export",
        "x",
        "csv",
        "*.csv",
        "X Search Export",
        "Metadata target for sanitized X/search exports created outside Fashion Radar.",
        ("AnySearch X export", "snscrape export"),
    ),
    (
        "xpoz_mcp",
        "community",
        "json",
        "*.json",
        "XPOZ MCP Export",
        (
            "Metadata target for sanitized XPOZ MCP / Social Data API exports "
            "created outside Fashion Radar."
        ),
        ("XPOZ MCP", "XPOZ Social Data API"),
    ),
    (
        "generic_community_export",
        "community",
        "csv",
        "*.csv",
        "Generic Community Export",
        (
            "Metadata target for any user-controlled community source already "
            "converted to sanitized local signal rows."
        ),
        ("manual spreadsheet export", "community research export"),
    ),
)

EXTERNAL_TOOL_FIELD_MAPPINGS = [
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

EXTERNAL_TOOL_ADAPTER_BOUNDARIES = [
    "Local producer-discovery metadata only.",
    "Writes should target sanitized CSV/JSON local handoff rows.",
    "Platform label is local provenance only.",
    "No platform collection, connector execution, scraping, browser automation, or API calls.",
]


def external_tool_command(*parts: str) -> str:
    return shlex.join(("fashion-radar", *parts))


def external_tool_adapter_commands(
    *,
    adapter_id: str,
    input_format: str,
    pattern: str,
    source_name: str,
) -> list[str]:
    return [
        external_tool_command("community-signal-profile", "--format", "json"),
        external_tool_command(
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
        external_tool_command(
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
        external_tool_command(
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
        external_tool_command(
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
        external_tool_command(
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
        external_tool_command(
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
        external_tool_command(
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
        external_tool_command(
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


def community_candidates_payload(*, directory: bool = False) -> dict[str, object]:
    payload: dict[str, object] = {
        "input_format": "csv",
        "as_of": "2026-06-13T12:00:00+00:00",
        "current_window_start": "2026-06-06T12:00:00+00:00",
        "baseline_window_start": "2026-05-07T12:00:00+00:00",
        "current_days": 7,
        "baseline_days": 30,
        "source_name": "Community Tool Export",
        "row_count": 2,
        "candidate_count": 0,
        "limit": 50,
        "candidates": [],
    }
    if directory:
        payload["file_count"] = 1
    return payload


def imported_summary_payload() -> dict[str, object]:
    return {
        "database": "/tmp/fashion-radar.sqlite",
        "source_type": "manual_import",
        "platform_counts": {"community": 2},
        "source_count": 1,
        "row_count": 2,
        "matched_count": 2,
        "unmatched_count": 0,
        "first_collected_at": "2026-06-12T08:30:00+00:00",
        "latest_collected_at": "2026-06-12T09:20:00+00:00",
        "sources": [
            {
                "source_name": "Community Tool Export",
                "platform_counts": {"community": 2},
                "row_count": 2,
                "matched_count": 2,
                "unmatched_count": 0,
                "first_collected_at": "2026-06-12T08:30:00+00:00",
                "latest_collected_at": "2026-06-12T09:20:00+00:00",
            }
        ],
    }


def imported_signals_payload() -> dict[str, object]:
    return {
        "database": "/tmp/fashion-radar.sqlite",
        "as_of": "2026-06-13T12:00:00+00:00",
        "window_start": "2026-06-06T12:00:00+00:00",
        "lookback_days": 7,
        "source_name": "Community Tool Export",
        "unmatched_only": False,
        "limit": 50,
        "row_count": 2,
        "total_count": 2,
        "matched_count": 2,
        "unmatched_count": 0,
        "source_name_counts": {"Community Tool Export": 2},
        "platform_counts": {"community": 2},
        "latest_collected_at": "2026-06-12T09:20:00+00:00",
        "items": [
            {
                "id": 2,
                "source_name": "Community Tool Export",
                "platform": "community",
                "url": "https://example.com/community/ballet-flats-footwear",
                "title": "Ballet flats footwear mention",
                "published_at": "2026-06-12T09:00:00+00:00",
                "collected_at": "2026-06-12T09:20:00+00:00",
                "source_weight": 1.1,
                "summary": "Short sanitized note about ballet flats shoes and footwear styling",
                "match_status": "matched",
                "matches": [
                    {
                        "entity_name": "Ballet Flats",
                        "entity_type": "category",
                        "alias": "ballet flats",
                        "confidence": 1.0,
                    }
                ],
            },
            {
                "id": 1,
                "source_name": "Community Tool Export",
                "platform": "community",
                "url": "https://example.com/community/the-row-margaux-tote",
                "title": "The Row Margaux tote interest",
                "published_at": "2026-06-12T08:00:00+00:00",
                "collected_at": "2026-06-12T08:30:00+00:00",
                "source_weight": 1.3,
                "summary": "Sanitized local note about The Row Margaux handbag and tote demand",
                "match_status": "matched",
                "matches": [
                    {
                        "entity_name": "The Row",
                        "entity_type": "brand",
                        "alias": "The Row",
                        "confidence": 1.0,
                    },
                    {
                        "entity_name": "The Row Margaux",
                        "entity_type": "product",
                        "alias": "The Row Margaux",
                        "confidence": 1.0,
                    },
                ],
            },
        ],
    }


def report_payload() -> dict[str, object]:
    return {
        "metadata": {
            "generated_at": "2026-06-13T12:00:00Z",
            "report_date": "2026-06-13T12:00:00Z",
            "item_count": 3,
        },
        "entities": [
            {
                "entity_name": "The Row",
                "entity_type": "brand",
                "label": "new",
                "heat_score": 1.8,
                "current_mentions": 1,
                "baseline_mentions": 0,
                "distinct_sources": 1,
                "growth_ratio": None,
                "weighted_mention_component": 1.3,
                "growth_component": 0.0,
                "source_diversity_component": 0.0,
                "high_weight_component": 0.5,
                "representative_items": [],
            },
            {
                "entity_name": "The Row Margaux",
                "entity_type": "product",
                "label": "new",
                "heat_score": 1.8,
                "current_mentions": 1,
                "baseline_mentions": 0,
                "distinct_sources": 1,
                "growth_ratio": None,
                "weighted_mention_component": 1.3,
                "growth_component": 0.0,
                "source_diversity_component": 0.0,
                "high_weight_component": 0.5,
                "representative_items": [],
            },
            {
                "entity_name": "Ballet Flats",
                "entity_type": "category",
                "label": "new",
                "heat_score": 1.1,
                "current_mentions": 1,
                "baseline_mentions": 0,
                "distinct_sources": 1,
                "growth_ratio": None,
                "weighted_mention_component": 1.1,
                "growth_component": 0.0,
                "source_diversity_component": 0.0,
                "high_weight_component": 0.0,
                "representative_items": [],
            },
        ],
        "candidates": [],
        "source_health": [],
        "recent_runs": [],
    }


def report_markdown() -> str:
    return "\n".join(
        [
            "# Fashion Radar Daily Report",
            "Window ending: 2026-06-13T12:00:00+00:00",
            "Current-window mentions: 3",
            "## Top Signals",
            "### The Row (new)",
            "### The Row Margaux (new)",
            "### Ballet Flats (new)",
            "## Untracked Candidate Signals",
            "No untracked candidate signals in this window.",
            "## Source Health",
            "No source health issues recorded.",
            "## Recent Collector Runs",
            "No recent collector runs recorded.",
        ]
    )


def trends_payload() -> dict[str, object]:
    return {
        "as_of": "2026-06-13T12:00:00Z",
        "baseline_as_of": "2026-06-06T12:00:00Z",
        "deltas": [
            {
                "signal_kind": "entity",
                "comparison_key": "entity:brand:the row",
                "name": "The Row",
                "signal_type": "brand",
                "status": "new",
            },
            {
                "signal_kind": "entity",
                "comparison_key": "entity:product:the row margaux",
                "name": "The Row Margaux",
                "signal_type": "product",
                "status": "new",
            },
            {
                "signal_kind": "entity",
                "comparison_key": "entity:category:ballet flats",
                "name": "Ballet Flats",
                "signal_type": "category",
                "status": "new",
            },
        ],
    }


def imported_review_workflow_payload() -> dict[str, object]:
    return {
        "as_of": "2026-06-13T12:00:00+00:00",
        "config_dir": "configs",
        "data_dir": "data",
        "source_name": "Community Tool Export",
        "lookback_days": 7,
        "current_days": 7,
        "baseline_days": 7,
        "execution_mode": "print_only",
        "step_count": 7,
        "steps": [
            {
                "order": 1,
                "name": "summarize_imported_sources",
                "purpose": "Summarize retained imported source-name labels.",
                "command": "fashion-radar imported-signals-summary --data-dir data",
                "suggested_effect": "read_only",
            },
            {
                "order": 2,
                "name": "refresh_stored_matches",
                "purpose": "Refresh stored local matches using configured entities.",
                "command": "fashion-radar match --config-dir configs --data-dir data",
                "suggested_effect": "updates_local_matches",
            },
            {
                "order": 3,
                "name": "compare_imported_entities",
                "purpose": "Compare stored matched imported entities across collected-at windows.",
                "command": (
                    "fashion-radar imported-entity-deltas --data-dir data "
                    "--as-of 2026-06-13T12:00:00+00:00 "
                    "--current-days 7 --baseline-days 7 "
                    "--source-name 'Community Tool Export'"
                ),
                "suggested_effect": "read_only",
            },
            {
                "order": 4,
                "name": "review_imported_entity_evidence",
                "purpose": "Review retained imported rows behind one selected matched entity.",
                "command": (
                    "fashion-radar imported-entity-evidence --data-dir data "
                    "--as-of 2026-06-13T12:00:00+00:00 --entity-name 'The Row' "
                    "--entity-type brand --current-days 7 --baseline-days 7 "
                    "--source-name 'Community Tool Export'"
                ),
                "suggested_effect": "read_only",
            },
            {
                "order": 5,
                "name": "review_imported_candidate_phrases",
                "purpose": (
                    "Review observed candidate phrases from retained imported rows after stored "
                    "matches are refreshed."
                ),
                "command": (
                    "fashion-radar imported-candidates --config-dir configs "
                    "--data-dir data --as-of 2026-06-13T12:00:00+00:00 "
                    "--source-name 'Community Tool Export'"
                ),
                "suggested_effect": "read_only",
            },
            {
                "order": 6,
                "name": "review_unmatched_imported_rows",
                "purpose": "Review retained imported rows without stored matches.",
                "command": (
                    "fashion-radar imported-signals --data-dir data "
                    "--as-of 2026-06-13T12:00:00+00:00 --lookback-days 7 "
                    "--unmatched-only --source-name 'Community Tool Export'"
                ),
                "suggested_effect": "read_only",
            },
            {
                "order": 7,
                "name": "review_local_heat_movers",
                "purpose": "Review local observed heat movement after imported rows are matched.",
                "command": (
                    "fashion-radar heat-movers --config-dir configs --data-dir data "
                    "--as-of 2026-06-13T12:00:00+00:00"
                ),
                "suggested_effect": "read_only",
            },
        ],
    }


def community_handoff_workflow_payload() -> dict[str, object]:
    return {
        "directory": "/tmp/export",
        "input_format": "csv",
        "pattern": "*.csv",
        "as_of": "2026-06-13T12:00:00+00:00",
        "config_dir": "configs",
        "data_dir": "data",
        "source_name": "Community Tool Export",
        "execution_mode": "print_only",
        "step_count": 6,
        "steps": [
            {
                "order": 1,
                "name": "lint_handoff_directory",
                "purpose": "Lint local community handoff files before import.",
                "command": (
                    "fashion-radar community-signal-lint-dir /tmp/export "
                    "--input-format csv --pattern '*.csv' "
                    "--source-name 'Community Tool Export' --strict"
                ),
                "suggested_effect": "read_only",
            },
            {
                "order": 2,
                "name": "preview_candidate_phrases",
                "purpose": "Preview aggregate candidate phrases before import.",
                "command": (
                    "fashion-radar community-candidates-dir /tmp/export "
                    "--input-format csv --pattern '*.csv' --config-dir configs "
                    "--as-of 2026-06-13T12:00:00+00:00 "
                    "--source-name 'Community Tool Export'"
                ),
                "suggested_effect": "read_only",
            },
            {
                "order": 3,
                "name": "review_handoff_readiness",
                "purpose": "Review local handoff readiness before import.",
                "command": (
                    "fashion-radar community-handoff-check-dir /tmp/export "
                    "--input-format csv --pattern '*.csv' --config-dir configs "
                    "--as-of 2026-06-13T12:00:00+00:00 "
                    "--source-name 'Community Tool Export' --strict"
                ),
                "suggested_effect": "read_only",
            },
            {
                "order": 4,
                "name": "dry_run_directory_import",
                "purpose": (
                    "Validate matched local files through the importer without writing rows."
                ),
                "command": (
                    "fashion-radar import-signals-dir /tmp/export --format csv "
                    "--pattern '*.csv' --data-dir data "
                    "--source-name 'Community Tool Export' "
                    "--imported-at 2026-06-13T12:00:00+00:00 --dry-run"
                ),
                "suggested_effect": "read_only",
            },
            {
                "order": 5,
                "name": "import_directory_signals",
                "purpose": "Import the validated local handoff rows into local SQLite.",
                "command": (
                    "fashion-radar import-signals-dir /tmp/export --format csv "
                    "--pattern '*.csv' --data-dir data "
                    "--source-name 'Community Tool Export' "
                    "--imported-at 2026-06-13T12:00:00+00:00"
                ),
                "suggested_effect": "updates_local_imports",
            },
            {
                "order": 6,
                "name": "print_post_import_review",
                "purpose": "Print the local post-import review checklist.",
                "command": (
                    "fashion-radar imported-review-workflow --config-dir configs "
                    "--data-dir data --as-of 2026-06-13T12:00:00+00:00 "
                    "--source-name 'Community Tool Export'"
                ),
                "suggested_effect": "print_only",
            },
        ],
    }


def replace_workflow_command_fragments(
    payload: dict[str, object],
    replacements: dict[str, str],
) -> None:
    steps = payload["steps"]
    assert isinstance(steps, list)
    for step in steps:
        assert isinstance(step, dict)
        command = step.get("command")
        assert isinstance(command, str)
        for old, new in replacements.items():
            command = command.replace(old, new)
        step["command"] = command


def external_tool_adapters_payload() -> dict[str, object]:
    return {
        "contract_version": "external-tool-adapters/v1",
        "execution_mode": "print_only",
        "adapters": [
            {
                "id": adapter_id,
                "display_name": source_name,
                "platform_label": platform_label,
                "suggested_source_name": source_name,
                "recommended_input_format": input_format,
                "recommended_pattern": pattern,
                "suggested_export_directory": "exports",
                "description": description,
                "upstream_tool_examples": list(upstream_tool_examples),
                "field_mappings": [
                    dict(field_mapping) for field_mapping in EXTERNAL_TOOL_FIELD_MAPPINGS
                ],
                "recommended_commands": external_tool_adapter_commands(
                    adapter_id=adapter_id,
                    input_format=input_format,
                    pattern=pattern,
                    source_name=source_name,
                ),
                "boundaries": list(EXTERNAL_TOOL_ADAPTER_BOUNDARIES),
            }
            for (
                adapter_id,
                platform_label,
                input_format,
                pattern,
                source_name,
                description,
                upstream_tool_examples,
            ) in EXTERNAL_TOOL_ADAPTER_CASES
        ],
        "boundaries": [
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
        ],
    }


def external_tool_adapter_entries(payload: dict[str, object]) -> list[dict[str, object]]:
    adapters = payload["adapters"]
    assert isinstance(adapters, list)
    assert all(isinstance(adapter, dict) for adapter in adapters)
    return cast(list[dict[str, object]], adapters)


def external_tool_adapter_entry(
    payload: dict[str, object],
    adapter_id: str,
) -> dict[str, object]:
    for adapter in external_tool_adapter_entries(payload):
        if adapter.get("id") == adapter_id:
            return adapter
    raise AssertionError(f"missing adapter {adapter_id}")


def assert_external_tool_adapter_contract_drift(
    payload: dict[str, object],
    match: str,
) -> None:
    with pytest.raises(smoke.SmokeError, match=match):
        smoke.validate_external_tool_adapters("external-tool-adapters", payload)


def add_external_tool_registry_extra_key(payload: dict[str, object]) -> None:
    payload["runs_adapters"] = False


def remove_external_tool_registry_boundary(payload: dict[str, object]) -> None:
    boundaries = payload["boundaries"]
    assert isinstance(boundaries, list)
    payload["boundaries"] = boundaries[:-1]


def add_external_tool_adapter_extra_key(payload: dict[str, object]) -> None:
    adapter = external_tool_adapter_entry(payload, "rednote_mcp")
    adapter["runs_adapter"] = False


def remove_external_tool_adapter_key(payload: dict[str, object]) -> None:
    adapter = external_tool_adapter_entry(payload, "rednote_mcp")
    adapter.pop("description")


def drift_external_tool_later_adapter_description(payload: dict[str, object]) -> None:
    adapter = external_tool_adapter_entry(payload, "xiaohongshu_crawler")
    adapter["description"] = "Unexpected crawler description."


def drift_external_tool_upstream_examples(payload: dict[str, object]) -> None:
    adapter = external_tool_adapter_entry(payload, "x_search_export")
    adapter["upstream_tool_examples"] = ["other export"]


def drift_external_tool_field_mapping_required(payload: dict[str, object]) -> None:
    adapter = external_tool_adapter_entry(payload, "rednote_mcp")
    field_mappings = adapter["field_mappings"]
    assert isinstance(field_mappings, list)
    first_mapping = field_mappings[0]
    assert isinstance(first_mapping, dict)
    first_mapping["required"] = False


def drift_external_tool_field_mapping_note(payload: dict[str, object]) -> None:
    adapter = external_tool_adapter_entry(payload, "rednote_mcp")
    field_mappings = adapter["field_mappings"]
    assert isinstance(field_mappings, list)
    second_mapping = field_mappings[1]
    assert isinstance(second_mapping, dict)
    second_mapping["note"] = "Changed note."


def drift_external_tool_adapter_boundaries(payload: dict[str, object]) -> None:
    adapter = external_tool_adapter_entry(payload, "rednote_mcp")
    adapter["boundaries"] = ["Local producer-discovery metadata only."]


def drift_external_tool_later_manifest_command(payload: dict[str, object]) -> None:
    adapter = external_tool_adapter_entry(payload, "xiaohongshu_crawler")
    commands = adapter["recommended_commands"]
    assert isinstance(commands, list)
    commands[2] = external_tool_command(
        "community-handoff-manifest",
        "exports",
        "--input-format",
        "csv",
        "--pattern",
        "*.csv",
        "--config-dir",
        "configs",
        "--data-dir",
        "data",
        "--as-of",
        "2026-06-13T12:00:00+00:00",
        "--source-name",
        "Xiaohongshu Crawler Export",
        "--format",
        "table",
    )


def drift_external_tool_readiness_extra_flag(payload: dict[str, object]) -> None:
    replace_external_tool_readiness_command(
        payload,
        external_tool_command(
            "external-tool-readiness",
            "--adapter",
            "rednote_mcp",
            "--directory",
            "exports",
            "--config-dir",
            "configs",
            "--data-dir",
            "data",
            "--as-of",
            "2026-06-13T12:00:00+00:00",
            "--input-format",
            "json",
            "--pattern",
            "*.json",
            "--source-name",
            "Rednote MCP Export",
            "--format",
            "table",
            "--verbose",
        ),
    )


def replace_external_tool_readiness_command(
    payload: dict[str, object],
    command: str,
    *,
    adapter_index: int = 0,
) -> None:
    adapters = external_tool_adapter_entries(payload)
    commands = adapters[adapter_index]["recommended_commands"]
    assert isinstance(commands, list)
    commands[1] = command


def external_tool_template_payload() -> dict[str, object]:
    return {
        "items": [
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
    }


def external_tool_workflow_payload() -> dict[str, object]:
    return {
        "contract_version": "external-tool-workflow/v1",
        "execution_mode": "print_only",
        "adapter_id": "rednote_mcp",
        "display_name": "Rednote MCP Export",
        "platform_label": "rednote",
        "directory": "exports",
        "input_format": "json",
        "pattern": "*.json",
        "as_of": "2026-06-13T12:00:00+00:00",
        "config_dir": "configs",
        "data_dir": "data",
        "source_name": "Rednote MCP Export",
        "step_count": 12,
        "steps": [
            {
                "order": 1,
                "name": "inspect_adapter_registry",
                "purpose": (
                    "Print adapter defaults and boundaries before preparing local handoff files."
                ),
                "command": (
                    "fashion-radar external-tool-adapters --adapter rednote_mcp "
                    "--directory exports --config-dir configs --data-dir data "
                    "--as-of 2026-06-13T12:00:00+00:00 --format table"
                ),
                "suggested_effect": "print_only",
            },
            {
                "order": 2,
                "name": "check_external_tool_readiness",
                "purpose": (
                    "Print local external tool readiness guidance before preparing sanitized "
                    "handoff rows."
                ),
                "command": (
                    "fashion-radar external-tool-readiness --adapter rednote_mcp "
                    "--directory exports --config-dir configs --data-dir data "
                    "--as-of 2026-06-13T12:00:00+00:00 --input-format json "
                    "--pattern '*.json' --source-name 'Rednote MCP Export' --format table"
                ),
                "suggested_effect": "read_only",
            },
            {
                "order": 3,
                "name": "print_adapter_template_json",
                "purpose": "Print example sanitized local handoff rows for the selected adapter.",
                "command": (
                    "fashion-radar external-tool-template --adapter rednote_mcp "
                    "--directory exports --config-dir configs --data-dir data "
                    "--as-of 2026-06-13T12:00:00+00:00 --format json"
                ),
                "suggested_effect": "print_only",
            },
            {
                "order": 4,
                "name": "print_signal_profile",
                "purpose": "Print the accepted community signal row fields.",
                "command": "fashion-radar community-signal-profile --format json",
                "suggested_effect": "print_only",
            },
            {
                "order": 5,
                "name": "print_handoff_manifest",
                "purpose": "Print a local handoff manifest for the selected export directory.",
                "command": (
                    "fashion-radar community-handoff-manifest exports "
                    "--input-format json --pattern '*.json' --config-dir configs "
                    "--data-dir data --as-of 2026-06-13T12:00:00+00:00 "
                    "--source-name 'Rednote MCP Export' --format json"
                ),
                "suggested_effect": "print_only",
            },
            {
                "order": 6,
                "name": "print_handoff_workflow",
                "purpose": "Print the local community handoff workflow for these adapter settings.",
                "command": (
                    "fashion-radar community-handoff-workflow exports "
                    "--input-format json --pattern '*.json' --config-dir configs "
                    "--data-dir data --as-of 2026-06-13T12:00:00+00:00 "
                    "--source-name 'Rednote MCP Export'"
                ),
                "suggested_effect": "print_only",
            },
            {
                "order": 7,
                "name": "lint_export_directory",
                "purpose": "Lint local external tool handoff files before import.",
                "command": (
                    "fashion-radar community-signal-lint-dir exports "
                    "--input-format json --pattern '*.json' "
                    "--source-name 'Rednote MCP Export' --strict"
                ),
                "suggested_effect": "read_only",
            },
            {
                "order": 8,
                "name": "preview_candidate_phrases",
                "purpose": (
                    "Preview aggregate candidate phrases before importing local handoff rows."
                ),
                "command": (
                    "fashion-radar community-candidates-dir exports "
                    "--input-format json --pattern '*.json' --config-dir configs "
                    "--as-of 2026-06-13T12:00:00+00:00 "
                    "--source-name 'Rednote MCP Export'"
                ),
                "suggested_effect": "read_only",
            },
            {
                "order": 9,
                "name": "review_handoff_readiness",
                "purpose": "Review local handoff readiness before import.",
                "command": (
                    "fashion-radar community-handoff-check-dir exports "
                    "--input-format json --pattern '*.json' --config-dir configs "
                    "--as-of 2026-06-13T12:00:00+00:00 "
                    "--source-name 'Rednote MCP Export' --strict"
                ),
                "suggested_effect": "read_only",
            },
            {
                "order": 10,
                "name": "dry_run_directory_import",
                "purpose": (
                    "Validate matched local files through the importer without writing rows."
                ),
                "command": (
                    "fashion-radar import-signals-dir exports --format json "
                    "--pattern '*.json' --source-name 'Rednote MCP Export' "
                    "--data-dir data --imported-at 2026-06-13T12:00:00+00:00 "
                    "--dry-run"
                ),
                "suggested_effect": "read_only",
            },
            {
                "order": 11,
                "name": "import_directory_signals",
                "purpose": "Import validated local handoff rows into local SQLite.",
                "command": (
                    "fashion-radar import-signals-dir exports --format json "
                    "--pattern '*.json' --source-name 'Rednote MCP Export' "
                    "--data-dir data --imported-at 2026-06-13T12:00:00+00:00"
                ),
                "suggested_effect": "updates_local_imports",
            },
            {
                "order": 12,
                "name": "print_post_import_review",
                "purpose": "Print the local post-import review workflow.",
                "command": (
                    "fashion-radar imported-review-workflow --config-dir configs "
                    "--data-dir data --as-of 2026-06-13T12:00:00+00:00 "
                    "--source-name 'Rednote MCP Export'"
                ),
                "suggested_effect": "print_only",
            },
        ],
        "boundaries": [
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
        ],
    }


def external_tool_readiness_payload() -> dict[str, object]:
    return {
        "contract_version": "external-tool-readiness/v1",
        "execution_mode": "local_read_only",
        "adapter_id": "rednote_mcp",
        "display_name": "Rednote MCP Export",
        "platform_label": "rednote",
        "directory": "exports",
        "input_format": "json",
        "pattern": "*.json",
        "as_of": "2026-06-13T12:00:00+00:00",
        "config_dir": "configs",
        "data_dir": "data",
        "source_name": "Rednote MCP Export",
        "checks": [
            {
                "name": "upstream_command",
                "status": "missing",
                "command": "rednote-mcp",
                "path": None,
                "detail": "Checks whether the Rednote MCP command is discoverable locally.",
                "install_hint": (
                    "npm config set registry https://registry.npmmirror.com && "
                    "npm install -g rednote-mcp"
                ),
            }
        ],
        "step_count": 7,
        "steps": [
            {
                "order": 1,
                "name": "inspect_adapter_registry",
                "purpose": "Print adapter defaults and boundaries before reviewing readiness.",
                "command": (
                    "fashion-radar external-tool-adapters --adapter rednote_mcp "
                    "--directory exports --config-dir configs --data-dir data "
                    "--as-of 2026-06-13T12:00:00+00:00 --format table"
                ),
                "suggested_effect": "print_only",
            },
            {
                "order": 2,
                "name": "print_adapter_template_json",
                "purpose": "Print example sanitized local handoff rows for the selected adapter.",
                "command": (
                    "fashion-radar external-tool-template --adapter rednote_mcp "
                    "--directory exports --config-dir configs --data-dir data "
                    "--as-of 2026-06-13T12:00:00+00:00 --format json"
                ),
                "suggested_effect": "print_only",
            },
            {
                "order": 3,
                "name": "print_external_tool_workflow",
                "purpose": "Print the broader handoff workflow for the selected adapter settings.",
                "command": (
                    "fashion-radar external-tool-workflow --adapter rednote_mcp "
                    "--directory exports --config-dir configs --data-dir data "
                    "--as-of 2026-06-13T12:00:00+00:00 --input-format json "
                    "--pattern '*.json' --source-name 'Rednote MCP Export' --format table"
                ),
                "suggested_effect": "print_only",
            },
            {
                "order": 4,
                "name": "print_signal_profile",
                "purpose": "Print the accepted community signal row fields.",
                "command": "fashion-radar community-signal-profile --format json",
                "suggested_effect": "print_only",
            },
            {
                "order": 5,
                "name": "lint_export_directory",
                "purpose": "Lint local external tool handoff files before import.",
                "command": (
                    "fashion-radar community-signal-lint-dir exports "
                    "--input-format json --pattern '*.json' "
                    "--source-name 'Rednote MCP Export' --strict"
                ),
                "suggested_effect": "read_only",
            },
            {
                "order": 6,
                "name": "review_handoff_readiness",
                "purpose": "Review local handoff readiness before import.",
                "command": (
                    "fashion-radar community-handoff-check-dir exports "
                    "--input-format json --pattern '*.json' --config-dir configs "
                    "--as-of 2026-06-13T12:00:00+00:00 "
                    "--source-name 'Rednote MCP Export' --strict"
                ),
                "suggested_effect": "read_only",
            },
            {
                "order": 7,
                "name": "dry_run_directory_import",
                "purpose": (
                    "Validate matched local files through the importer without writing rows."
                ),
                "command": (
                    "fashion-radar import-signals-dir exports --format json "
                    "--pattern '*.json' --source-name 'Rednote MCP Export' "
                    "--data-dir data --imported-at 2026-06-13T12:00:00+00:00 "
                    "--dry-run"
                ),
                "suggested_effect": "read_only",
            },
        ],
        "boundaries": [
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
        ],
    }


def test_external_tool_adapters_payload_matches_real_registry() -> None:
    expected = json.loads(
        build_external_tool_adapter_registry(
            directory=Path("./exports"),
            config_dir=Path("./configs"),
            data_dir=Path("./data"),
            as_of="2026-06-13T12:00:00Z",
        ).model_dump_json()
    )

    assert external_tool_adapters_payload() == expected


@pytest.mark.parametrize(
    ("adapter_id", "input_format", "pattern", "source_name"),
    (
        ("rednote_mcp", "json", "*.json", "Rednote MCP Export"),
        ("xiaohongshu_crawler", "csv", "*.csv", "Xiaohongshu Crawler Export"),
    ),
)
def test_expected_external_tool_adapter_commands_match_fixture_helper(
    adapter_id: str,
    input_format: str,
    pattern: str,
    source_name: str,
) -> None:
    assert smoke.expected_external_tool_adapter_commands(
        adapter_id=adapter_id,
        input_format=input_format,
        pattern=pattern,
        source_name=source_name,
    ) == external_tool_adapter_commands(
        adapter_id=adapter_id,
        input_format=input_format,
        pattern=pattern,
        source_name=source_name,
    )


def test_external_tool_template_payload_matches_real_rednote_template() -> None:
    expected = json.loads(
        render_external_tool_template_json(
            build_external_tool_template(
                adapter_id="rednote_mcp",
                directory=Path("./exports"),
                config_dir=Path("./configs"),
                data_dir=Path("./data"),
                as_of="2026-06-13T12:00:00Z",
            )
        )
    )

    assert external_tool_template_payload() == expected


def test_external_tool_workflow_payload_matches_real_rednote_workflow() -> None:
    expected = json.loads(
        build_external_tool_workflow(
            adapter_id="rednote_mcp",
            directory=Path("./exports"),
            config_dir=Path("./configs"),
            data_dir=Path("./data"),
            as_of="2026-06-13T12:00:00Z",
        ).model_dump_json()
    )

    assert external_tool_workflow_payload() == expected


@pytest.mark.skipif(
    build_external_tool_readiness is None,
    reason="Stage 66 core external_tool_readiness module is not implemented yet.",
)
def test_external_tool_readiness_payload_matches_real_rednote_readiness() -> None:
    assert build_external_tool_readiness is not None

    assert external_tool_readiness_payload() == json.loads(
        build_external_tool_readiness(
            adapter_id="rednote_mcp",
            directory=Path("./exports"),
            config_dir=Path("./configs"),
            data_dir=Path("./data"),
            as_of="2026-06-13T12:00:00Z",
            which=lambda command: None,
        ).model_dump_json()
    )


def test_imported_review_workflow_payload_matches_real_builder() -> None:
    expected = json.loads(
        build_imported_review_workflow(
            config_dir=Path("configs"),
            data_dir=Path("data"),
            as_of="2026-06-13T12:00:00Z",
            source_name="Community Tool Export",
        ).model_dump_json()
    )

    assert imported_review_workflow_payload() == expected


def test_community_handoff_workflow_payload_matches_real_builder() -> None:
    expected = json.loads(
        build_community_handoff_workflow(
            directory=Path("/tmp/export"),
            config_dir=Path("configs"),
            data_dir=Path("data"),
            input_format="csv",
            pattern="*.csv",
            as_of="2026-06-13T12:00:00Z",
            source_name="Community Tool Export",
        ).model_dump_json()
    )

    assert community_handoff_workflow_payload() == expected


def make_context(tmp_path: Path, *, python: str = "python-test"):
    runtime_dir = tmp_path / "runtime"
    return smoke.SmokeContext(
        repo_root=tmp_path,
        python=python,
        runtime_dir=runtime_dir,
        config_dir=runtime_dir / "config",
        data_dir=runtime_dir / "data",
        reports_dir=runtime_dir / "reports",
        exports_dir=runtime_dir / "exports",
        source_checkout=True,
    )


def test_constants_pin_first_run_sample_inputs() -> None:
    assert smoke.AS_OF == "2026-06-13T12:00:00Z"
    assert smoke.SOURCE_NAME == "Community Tool Export"
    assert smoke.EXAMPLE_CSV == Path("examples/community-signals.example.csv")


def expected_first_run_flow_commands(
    context: smoke.SmokeContext,
    example_csv: Path,
) -> list[tuple[str, ...]]:
    return [
        (
            "init",
            "--config-dir",
            str(context.config_dir),
            "--data-dir",
            str(context.data_dir),
            "--reports-dir",
            str(context.reports_dir),
        ),
        ("migrate-db", "--data-dir", str(context.data_dir)),
        (
            "doctor",
            "--config-dir",
            str(context.config_dir),
            "--data-dir",
            str(context.data_dir),
            "--reports-dir",
            str(context.reports_dir),
        ),
        ("external-tool-adapters", "--format", "json"),
        ("external-tool-template", "--adapter", "rednote_mcp", "--format", "json"),
        (
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
            smoke.AS_OF,
            "--format",
            "json",
        ),
        (
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
            smoke.AS_OF,
            "--format",
            "json",
        ),
        (
            "community-signal-lint",
            str(example_csv),
            "--input-format",
            "csv",
            "--source-name",
            smoke.SOURCE_NAME,
        ),
        (
            "community-candidates",
            str(example_csv),
            "--config-dir",
            str(context.config_dir),
            "--input-format",
            "csv",
            "--as-of",
            smoke.AS_OF,
            "--source-name",
            smoke.SOURCE_NAME,
            "--format",
            "json",
        ),
        (
            "import-signals",
            str(example_csv),
            "--data-dir",
            str(context.data_dir),
            "--format",
            "csv",
            "--source-name",
            smoke.SOURCE_NAME,
            "--dry-run",
        ),
        (
            "import-signals",
            str(example_csv),
            "--data-dir",
            str(context.data_dir),
            "--format",
            "csv",
            "--source-name",
            smoke.SOURCE_NAME,
            "--imported-at",
            smoke.AS_OF,
        ),
        ("match", "--config-dir", str(context.config_dir), "--data-dir", str(context.data_dir)),
        (
            "imported-review-workflow",
            "--config-dir",
            str(context.config_dir),
            "--data-dir",
            str(context.data_dir),
            "--as-of",
            smoke.AS_OF,
            "--source-name",
            smoke.SOURCE_NAME,
            "--format",
            "json",
        ),
        ("imported-signals-summary", "--data-dir", str(context.data_dir), "--format", "json"),
        (
            "imported-signals",
            "--data-dir",
            str(context.data_dir),
            "--as-of",
            smoke.AS_OF,
            "--source-name",
            smoke.SOURCE_NAME,
            "--format",
            "json",
        ),
        (
            "report",
            "--config-dir",
            str(context.config_dir),
            "--data-dir",
            str(context.data_dir),
            "--reports-dir",
            str(context.reports_dir),
            "--as-of",
            smoke.AS_OF,
        ),
        (
            "candidates",
            "--config-dir",
            str(context.config_dir),
            "--data-dir",
            str(context.data_dir),
            "--as-of",
            smoke.AS_OF,
            "--format",
            "json",
        ),
        (
            "trends",
            "--config-dir",
            str(context.config_dir),
            "--data-dir",
            str(context.data_dir),
            "--as-of",
            smoke.AS_OF,
            "--format",
            "json",
        ),
        (
            "community-handoff-workflow",
            str(context.exports_dir),
            "--config-dir",
            str(context.config_dir),
            "--data-dir",
            str(context.data_dir),
            "--input-format",
            "csv",
            "--pattern",
            smoke.DIR_PATTERN,
            "--as-of",
            smoke.AS_OF,
            "--source-name",
            smoke.SOURCE_NAME,
            "--format",
            "json",
        ),
        (
            "community-signal-lint-dir",
            str(context.exports_dir),
            "--input-format",
            "csv",
            "--pattern",
            smoke.DIR_PATTERN,
            "--source-name",
            smoke.SOURCE_NAME,
        ),
        (
            "community-candidates-dir",
            str(context.exports_dir),
            "--config-dir",
            str(context.config_dir),
            "--input-format",
            "csv",
            "--pattern",
            smoke.DIR_PATTERN,
            "--as-of",
            smoke.AS_OF,
            "--source-name",
            smoke.SOURCE_NAME,
            "--format",
            "json",
        ),
        (
            "import-signals-dir",
            str(context.exports_dir),
            "--data-dir",
            str(context.data_dir),
            "--format",
            "csv",
            "--pattern",
            smoke.DIR_PATTERN,
            "--source-name",
            smoke.SOURCE_NAME,
            "--dry-run",
        ),
    ]


def assert_first_run_flow_commands(
    captured: list[tuple[str, ...]],
    context: smoke.SmokeContext,
    example_csv: Path,
) -> None:
    assert captured == expected_first_run_flow_commands(context, example_csv)


def test_cli_command_runs_fashion_radar_module(tmp_path: Path) -> None:
    context = make_context(tmp_path, python="/venv/bin/python")

    command = smoke.cli_command(context, "doctor", "--data-dir", "data")

    assert command == ["/venv/bin/python", "-m", "fashion_radar", "doctor", "--data-dir", "data"]


def test_command_environment_prepends_src_and_preserves_pythonpath(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    context = make_context(tmp_path)
    monkeypatch.setenv("PYTHONPATH", "/already/here")

    env = smoke.command_environment(context)

    assert env["PYTHONPATH"].split(os.pathsep)[:2] == [
        str(tmp_path / "src"),
        "/already/here",
    ]


def test_command_environment_sets_pythonpath_when_absent(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    context = make_context(tmp_path)
    monkeypatch.delenv("PYTHONPATH", raising=False)

    env = smoke.command_environment(context)

    assert env["PYTHONPATH"] == str(tmp_path / "src")


def test_command_environment_does_not_prepend_src_in_installed_mode(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    context = make_context(tmp_path)
    monkeypatch.setenv("PYTHONPATH", "/already/here")

    env = smoke.command_environment(context, source_checkout=False)

    assert env["PYTHONPATH"] == "/already/here"


def test_command_environment_leaves_pythonpath_absent_in_installed_mode(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    context = make_context(tmp_path)
    monkeypatch.delenv("PYTHONPATH", raising=False)

    env = smoke.command_environment(context, source_checkout=False)

    assert "PYTHONPATH" not in env


def test_command_environment_removes_repo_src_from_installed_mode(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    context = make_context(tmp_path)
    repo_src = str(tmp_path / "src")
    monkeypatch.setenv("PYTHONPATH", os.pathsep.join(["/before", repo_src, "/after"]))

    env = smoke.command_environment(context, source_checkout=False)

    assert env["PYTHONPATH"] == os.pathsep.join(["/before", "/after"])


def test_command_environment_removes_pythonpath_when_only_repo_src_in_installed_mode(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    context = make_context(tmp_path)
    monkeypatch.setenv("PYTHONPATH", str(tmp_path / "src"))

    env = smoke.command_environment(context, source_checkout=False)

    assert "PYTHONPATH" not in env


def test_command_environment_removes_relative_repo_src_in_installed_mode(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    repo_root = tmp_path / "repo"
    context = make_context(repo_root)
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("PYTHONPATH", os.pathsep.join(["/before", "src", "/after"]))

    env = smoke.command_environment(context, source_checkout=False)

    assert env["PYTHONPATH"] == os.pathsep.join(["/before", "/after"])


def test_command_environment_sets_deterministic_adapter_registry_dirs(
    tmp_path: Path,
) -> None:
    context = make_context(tmp_path)

    source_env = smoke.command_environment(context)
    installed_env = smoke.command_environment(context, source_checkout=False)

    assert source_env["FASHION_RADAR_CONFIG_DIR"] == "configs"
    assert source_env["FASHION_RADAR_DATA_DIR"] == "data"
    assert installed_env["FASHION_RADAR_CONFIG_DIR"] == "configs"
    assert installed_env["FASHION_RADAR_DATA_DIR"] == "data"


def test_validate_json_output_rejects_invalid_json() -> None:
    with pytest.raises(smoke.SmokeError, match="not valid JSON"):
        smoke.validate_json_output("community-candidates", "not json")


def test_validate_sample_csv_requires_expected_rows(tmp_path: Path) -> None:
    sample = tmp_path / "community.csv"
    sample.write_text(SAMPLE_CSV_TEXT, encoding="utf-8")

    smoke.validate_sample_csv(sample)

    sample.write_text(
        "url,title,published_at\nhttps://example.com/a,Wrong,2026-06-12T08:00:00Z\n",
        encoding="utf-8",
    )
    with pytest.raises(smoke.SmokeError, match="sample CSV row count"):
        smoke.validate_sample_csv(sample)


def test_validate_community_candidates_requires_sample_window_and_rows() -> None:
    smoke.validate_community_candidates("community-candidates", community_candidates_payload())
    smoke.validate_community_candidates(
        "community-candidates-dir",
        community_candidates_payload(directory=True),
        directory=True,
    )

    wrong_source = community_candidates_payload()
    wrong_source["source_name"] = "Other"
    with pytest.raises(smoke.SmokeError, match="source_name"):
        smoke.validate_community_candidates("community-candidates", wrong_source)

    missing_file_count = community_candidates_payload()
    with pytest.raises(smoke.SmokeError, match="file_count"):
        smoke.validate_community_candidates(
            "community-candidates-dir",
            missing_file_count,
            directory=True,
        )


def test_validate_import_outputs_require_two_validated_and_imported_rows() -> None:
    smoke.validate_import_signals_dry_run(
        "Validated 2 manual signal rows\nDry run: no rows imported\n"
    )
    smoke.validate_import_signals_import(
        "Validated 2 manual signal rows\nImported 2 manual signal rows\nItems added: 2\n"
    )
    smoke.validate_import_signals_dir_dry_run(
        "Files: 1 total, 1 valid\n"
        "Rows: 2 import-ready\n"
        "Sources: Community Tool Export=2\n"
        "Platforms: community=2\n"
        "Errors: 0\n"
        "- /tmp/export/community-signals.csv: 2 rows, 0 errors\n"
        "No manual signal directory dry-run errors.\n"
    )

    with pytest.raises(smoke.SmokeError, match="Dry run"):
        smoke.validate_import_signals_dry_run("Validated 2 manual signal rows\n")

    with pytest.raises(smoke.SmokeError, match="Items added"):
        smoke.validate_import_signals_import(
            "Validated 2 manual signal rows\nImported 2 manual signal rows\n"
        )

    with pytest.raises(smoke.SmokeError, match="Rows: 2 import-ready"):
        smoke.validate_import_signals_dir_dry_run("Files: 1 total, 1 valid\n")

    with pytest.raises(smoke.SmokeError, match="Items added: 2"):
        smoke.validate_import_signals_import(
            "Validated 2 manual signal rows\nImported 2 manual signal rows\nItems added: 20\n"
        )


def test_validate_imported_summary_requires_sample_source_platform_counts() -> None:
    smoke.validate_imported_summary("imported-signals-summary", imported_summary_payload())

    unmatched = imported_summary_payload()
    unmatched["matched_count"] = 0
    with pytest.raises(smoke.SmokeError, match="matched_count"):
        smoke.validate_imported_summary("imported-signals-summary", unmatched)

    wrong_platform = imported_summary_payload()
    wrong_platform["platform_counts"] = {"other": 2}
    with pytest.raises(smoke.SmokeError, match="platform_counts"):
        smoke.validate_imported_summary("imported-signals-summary", wrong_platform)


def test_validate_imported_signals_requires_expected_sample_items() -> None:
    smoke.validate_imported_signals("imported-signals", imported_signals_payload())

    missing_item = imported_signals_payload()
    missing_item["items"] = missing_item["items"][:1]  # type: ignore[index]
    with pytest.raises(smoke.SmokeError, match="exactly two sample items"):
        smoke.validate_imported_signals("imported-signals", missing_item)

    missing_match = imported_signals_payload()
    items = missing_match["items"]
    assert isinstance(items, list)
    items[0]["matches"] = []  # type: ignore[index]
    with pytest.raises(smoke.SmokeError, match="Ballet Flats"):
        smoke.validate_imported_signals("imported-signals", missing_match)

    wrong_status = imported_signals_payload()
    items = wrong_status["items"]
    assert isinstance(items, list)
    items[0]["match_status"] = "unmatched"  # type: ignore[index]
    with pytest.raises(smoke.SmokeError, match="marked matched"):
        smoke.validate_imported_signals("imported-signals", wrong_status)


def test_validate_imported_review_workflow_requires_entity_evidence_and_candidate_steps() -> None:
    smoke.validate_imported_review_workflow(
        "imported-review-workflow",
        imported_review_workflow_payload(),
    )


def test_validate_imported_review_workflow_rejects_missing_entity_evidence_step() -> None:
    payload = imported_review_workflow_payload()
    steps = payload["steps"]
    assert isinstance(steps, list)
    del steps[3]

    with pytest.raises(smoke.SmokeError, match="step"):
        smoke.validate_imported_review_workflow("imported-review-workflow", payload)


def test_validate_imported_review_workflow_rejects_missing_candidate_step() -> None:
    payload = imported_review_workflow_payload()
    steps = payload["steps"]
    assert isinstance(steps, list)
    del steps[4]

    with pytest.raises(smoke.SmokeError, match="step"):
        smoke.validate_imported_review_workflow("imported-review-workflow", payload)


def test_validate_imported_review_workflow_rejects_heat_movers_not_final() -> None:
    payload = imported_review_workflow_payload()
    steps = payload["steps"]
    assert isinstance(steps, list)
    steps[-1], steps[-2] = steps[-2], steps[-1]

    with pytest.raises(smoke.SmokeError, match="step names|final step"):
        smoke.validate_imported_review_workflow("imported-review-workflow", payload)


def test_validate_imported_review_workflow_rejects_step_order_drift() -> None:
    payload = imported_review_workflow_payload()
    steps = payload["steps"]
    assert isinstance(steps, list)
    steps[0]["order"] = 99  # type: ignore[index]

    with pytest.raises(smoke.SmokeError, match="step metadata"):
        smoke.validate_imported_review_workflow("imported-review-workflow", payload)


def test_validate_imported_review_workflow_rejects_step_purpose_drift() -> None:
    payload = imported_review_workflow_payload()
    steps = payload["steps"]
    assert isinstance(steps, list)
    steps[3]["purpose"] = "Open a browser and collect fresh platform evidence."  # type: ignore[index]

    with pytest.raises(smoke.SmokeError, match="step metadata"):
        smoke.validate_imported_review_workflow("imported-review-workflow", payload)


def test_validate_imported_review_workflow_rejects_step_effect_drift() -> None:
    payload = imported_review_workflow_payload()
    steps = payload["steps"]
    assert isinstance(steps, list)
    steps[1]["suggested_effect"] = "read_only"  # type: ignore[index]

    with pytest.raises(smoke.SmokeError, match="step metadata"):
        smoke.validate_imported_review_workflow("imported-review-workflow", payload)


@pytest.mark.parametrize(
    ("step_name", "replacement_command", "expected_message"),
    [
        (
            "summarize_imported_sources",
            "fashion-radar imported-signals-summary --data-dir other-data",
            "summary command",
        ),
        (
            "refresh_stored_matches",
            "fashion-radar match --config-dir configs",
            "match refresh command",
        ),
        (
            "compare_imported_entities",
            (
                "fashion-radar imported-entity-deltas --data-dir data "
                "--as-of 2026-06-13T12:00:00+00:00 "
                "--current-days 14 --baseline-days 7 "
                "--source-name 'Community Tool Export'"
            ),
            "entity delta command",
        ),
        (
            "review_imported_entity_evidence",
            (
                "fashion-radar imported-entity-evidence --data-dir data "
                "--as-of 2026-06-13T12:00:00+00:00 --entity-name 'The Row' "
                "--entity-type brand --current-days 14 --baseline-days 7 "
                "--source-name 'Community Tool Export'"
            ),
            "entity evidence command",
        ),
        (
            "review_imported_candidate_phrases",
            (
                "fashion-radar imported-candidates --config-dir configsets "
                "--data-dir data --as-of 2026-06-13T12:00:00+00:00 "
                "--source-name 'Community Tool Export'"
            ),
            "candidate command",
        ),
        (
            "review_unmatched_imported_rows",
            (
                "fashion-radar imported-signals --data-dir data "
                "--as-of 2026-06-13T12:00:00+00:00 --lookback-days 7 "
                "--source-name 'Community Tool Export'"
            ),
            "unmatched rows command",
        ),
        (
            "review_local_heat_movers",
            (
                "fashion-radar heat-movers-extra --config-dir configs --data-dir data "
                "--as-of 2026-06-13T12:00:00+00:00"
            ),
            "final heat command",
        ),
    ],
)
def test_validate_imported_review_workflow_rejects_command_argv_drift(
    step_name: str,
    replacement_command: str,
    expected_message: str,
) -> None:
    payload = imported_review_workflow_payload()
    steps = payload["steps"]
    assert isinstance(steps, list)
    for step in steps:
        assert isinstance(step, dict)
        if step.get("name") == step_name:
            step["command"] = replacement_command
            break
    else:
        pytest.fail(f"missing step {step_name}")

    with pytest.raises(smoke.SmokeError, match=expected_message):
        smoke.validate_imported_review_workflow("imported-review-workflow", payload)


def test_validate_imported_review_workflow_rejects_coordinated_metadata_command_drift() -> None:
    payload = imported_review_workflow_payload()
    payload["source_name"] = "Other Source"
    payload["as_of"] = "2026-06-14T12:00:00+00:00"
    payload["lookback_days"] = 14
    payload["current_days"] = 14
    payload["baseline_days"] = 21
    replace_workflow_command_fragments(
        payload,
        {
            "2026-06-13T12:00:00+00:00": "2026-06-14T12:00:00+00:00",
            "'Community Tool Export'": "'Other Source'",
            "--lookback-days 7": "--lookback-days 14",
            "--current-days 7": "--current-days 14",
            "--baseline-days 7": "--baseline-days 21",
        },
    )

    with pytest.raises(
        smoke.SmokeError,
        match="source_name|as_of|lookback_days|current_days|baseline_days",
    ):
        smoke.validate_imported_review_workflow("imported-review-workflow", payload)


def test_validate_imported_review_workflow_rejects_config_dir_drift() -> None:
    payload = imported_review_workflow_payload()
    payload["config_dir"] = "other-configs"
    replace_workflow_command_fragments(
        payload,
        {"--config-dir configs": "--config-dir other-configs"},
    )

    with pytest.raises(smoke.SmokeError, match="imported-review-workflow config_dir"):
        smoke.validate_imported_review_workflow("imported-review-workflow", payload)


def test_validate_imported_review_workflow_rejects_data_dir_drift() -> None:
    payload = imported_review_workflow_payload()
    payload["data_dir"] = "other-data"
    replace_workflow_command_fragments(
        payload,
        {"--data-dir data": "--data-dir other-data"},
    )

    with pytest.raises(smoke.SmokeError, match="imported-review-workflow data_dir"):
        smoke.validate_imported_review_workflow("imported-review-workflow", payload)


def test_validate_community_handoff_workflow_requires_readiness_step() -> None:
    smoke.validate_community_handoff_workflow(
        "community-handoff-workflow",
        community_handoff_workflow_payload(),
    )


def test_validate_community_handoff_workflow_rejects_missing_readiness_step() -> None:
    payload = community_handoff_workflow_payload()
    steps = payload["steps"]
    assert isinstance(steps, list)
    del steps[2]

    with pytest.raises(smoke.SmokeError, match="step_count|step names"):
        smoke.validate_community_handoff_workflow("community-handoff-workflow", payload)


def test_validate_community_handoff_workflow_rejects_incomplete_readiness_command() -> None:
    payload = community_handoff_workflow_payload()
    steps = payload["steps"]
    assert isinstance(steps, list)
    readiness_step = steps[2]
    assert isinstance(readiness_step, dict)
    readiness_step["command"] = (
        "fashion-radar community-handoff-check-dir /tmp/export "
        "--input-format csv --pattern '*.csv' --config-dir configs "
        "--as-of 2026-06-13T12:00:00+00:00 "
        "--source-name 'Community Tool Export'"
    )

    with pytest.raises(smoke.SmokeError, match="--strict"):
        smoke.validate_community_handoff_workflow("community-handoff-workflow", payload)


def test_validate_community_handoff_workflow_rejects_wrong_readiness_command_argv() -> None:
    payload = community_handoff_workflow_payload()
    steps = payload["steps"]
    assert isinstance(steps, list)
    readiness_step = steps[2]
    assert isinstance(readiness_step, dict)
    readiness_step["command"] = (
        "fashion-radar community-handoff-check-dir-extra /tmp/export "
        "--input-format csv --pattern '*.csv' --config-dir configs "
        "--as-of 2026-06-13T12:00:00+00:00 "
        "--source-name 'Community Tool Export' --strict"
    )

    with pytest.raises(smoke.SmokeError, match="readiness command"):
        smoke.validate_community_handoff_workflow("community-handoff-workflow", payload)


def test_validate_community_handoff_workflow_rejects_extra_command_like_tail_step() -> None:
    payload = community_handoff_workflow_payload()
    steps = payload["steps"]
    assert isinstance(steps, list)
    steps.append("fashion-radar live-collect --platform rednote")

    with pytest.raises(smoke.SmokeError, match="step_count|step 7|JSON object"):
        smoke.validate_community_handoff_workflow("community-handoff-workflow", payload)


def test_validate_community_handoff_workflow_rejects_coordinated_metadata_command_drift() -> None:
    payload = community_handoff_workflow_payload()
    payload["source_name"] = "Other Source"
    payload["as_of"] = "2026-06-14T12:00:00+00:00"
    payload["input_format"] = "json"
    payload["pattern"] = "*.json"
    replace_workflow_command_fragments(
        payload,
        {
            "2026-06-13T12:00:00+00:00": "2026-06-14T12:00:00+00:00",
            "'Community Tool Export'": "'Other Source'",
            "--input-format csv": "--input-format json",
            "--format csv": "--format json",
            "'*.csv'": "'*.json'",
        },
    )

    with pytest.raises(
        smoke.SmokeError,
        match="source_name|as_of|input_format|pattern",
    ):
        smoke.validate_community_handoff_workflow("community-handoff-workflow", payload)


def test_validate_community_handoff_workflow_rejects_directory_drift() -> None:
    payload = community_handoff_workflow_payload()
    payload["directory"] = "/tmp/other-export"
    replace_workflow_command_fragments(
        payload,
        {"/tmp/export": "/tmp/other-export"},
    )

    with pytest.raises(smoke.SmokeError, match="community-handoff-workflow directory"):
        smoke.validate_community_handoff_workflow("community-handoff-workflow", payload)


def test_validate_community_handoff_workflow_rejects_config_dir_drift() -> None:
    payload = community_handoff_workflow_payload()
    payload["config_dir"] = "other-configs"
    replace_workflow_command_fragments(
        payload,
        {"--config-dir configs": "--config-dir other-configs"},
    )

    with pytest.raises(smoke.SmokeError, match="community-handoff-workflow config_dir"):
        smoke.validate_community_handoff_workflow("community-handoff-workflow", payload)


def test_validate_community_handoff_workflow_rejects_data_dir_drift() -> None:
    payload = community_handoff_workflow_payload()
    payload["data_dir"] = "other-data"
    replace_workflow_command_fragments(
        payload,
        {"--data-dir data": "--data-dir other-data"},
    )

    with pytest.raises(smoke.SmokeError, match="community-handoff-workflow data_dir"):
        smoke.validate_community_handoff_workflow("community-handoff-workflow", payload)


@pytest.mark.parametrize(
    ("step_name", "replacement_command", "expected_message"),
    [
        (
            "lint_handoff_directory",
            (
                "fashion-radar community-signal-lint-dir /tmp/export "
                "--input-format csv --pattern '*.csv' "
                "--source-name 'Community Tool Export'"
            ),
            "lint_handoff_directory command",
        ),
        (
            "preview_candidate_phrases",
            (
                "fashion-radar community-candidates-dir-extra /tmp/export "
                "--input-format csv --pattern '*.csv' --config-dir configs "
                "--as-of 2026-06-13T12:00:00+00:00 "
                "--source-name 'Community Tool Export'"
            ),
            "preview_candidate_phrases command",
        ),
        (
            "dry_run_directory_import",
            (
                "fashion-radar import-signals-dir /tmp/export --format csv "
                "--pattern '*.csv' --data-dir data "
                "--source-name 'Community Tool Export' "
                "--imported-at 2026-06-13T12:00:00+00:00"
            ),
            "dry_run_directory_import command",
        ),
        (
            "import_directory_signals",
            (
                "fashion-radar import-signals-dir-extra /tmp/export --format csv "
                "--pattern '*.csv' --data-dir data "
                "--source-name 'Community Tool Export' "
                "--imported-at 2026-06-13T12:00:00+00:00"
            ),
            "import_directory_signals command",
        ),
        (
            "print_post_import_review",
            (
                "fashion-radar imported-review-workflow-extra --config-dir configs "
                "--data-dir data --as-of 2026-06-13T12:00:00+00:00 "
                "--source-name 'Community Tool Export'"
            ),
            "print_post_import_review command",
        ),
    ],
)
def test_validate_community_handoff_workflow_rejects_unpinned_command_drift(
    step_name: str,
    replacement_command: str,
    expected_message: str,
) -> None:
    payload = community_handoff_workflow_payload()
    steps = payload["steps"]
    assert isinstance(steps, list)
    for step in steps:
        assert isinstance(step, dict)
        if step.get("name") == step_name:
            step["command"] = replacement_command
            break
    else:
        pytest.fail(f"missing step {step_name}")

    with pytest.raises(smoke.SmokeError, match=expected_message):
        smoke.validate_community_handoff_workflow("community-handoff-workflow", payload)


def test_validate_community_handoff_workflow_rejects_step_order_drift() -> None:
    payload = community_handoff_workflow_payload()
    steps = payload["steps"]
    assert isinstance(steps, list)
    steps[0]["order"] = 99  # type: ignore[index]

    with pytest.raises(smoke.SmokeError, match="step metadata"):
        smoke.validate_community_handoff_workflow("community-handoff-workflow", payload)


def test_validate_community_handoff_workflow_rejects_step_purpose_drift() -> None:
    payload = community_handoff_workflow_payload()
    steps = payload["steps"]
    assert isinstance(steps, list)
    steps[2]["purpose"] = "Open a browser and collect fresh platform evidence."  # type: ignore[index]

    with pytest.raises(smoke.SmokeError, match="step metadata"):
        smoke.validate_community_handoff_workflow("community-handoff-workflow", payload)


def test_validate_community_handoff_workflow_rejects_step_effect_drift() -> None:
    payload = community_handoff_workflow_payload()
    steps = payload["steps"]
    assert isinstance(steps, list)
    steps[1]["suggested_effect"] = "print_only"  # type: ignore[index]

    with pytest.raises(smoke.SmokeError, match="step metadata"):
        smoke.validate_community_handoff_workflow("community-handoff-workflow", payload)


def test_validate_community_handoff_workflow_requires_import_and_review_effects() -> None:
    payload = community_handoff_workflow_payload()
    steps = payload["steps"]
    assert isinstance(steps, list)
    import_step = steps[4]
    assert isinstance(import_step, dict)
    import_step["suggested_effect"] = "read_only"

    with pytest.raises(smoke.SmokeError, match="import step effect"):
        smoke.validate_community_handoff_workflow("community-handoff-workflow", payload)


def test_validate_external_tool_adapters_requires_print_only_registry_contract() -> None:
    smoke.validate_external_tool_adapters(
        "external-tool-adapters",
        external_tool_adapters_payload(),
    )

    wrong_contract = external_tool_adapters_payload()
    wrong_contract["contract_version"] = "other/v1"
    with pytest.raises(smoke.SmokeError, match="contract_version"):
        smoke.validate_external_tool_adapters("external-tool-adapters", wrong_contract)

    runnable = external_tool_adapters_payload()
    runnable["execution_mode"] = "runs_adapters"
    with pytest.raises(smoke.SmokeError, match="execution_mode"):
        smoke.validate_external_tool_adapters("external-tool-adapters", runnable)

    wrong_adapter = external_tool_adapters_payload()
    adapters = external_tool_adapter_entries(wrong_adapter)
    adapters[1]["id"] = "unexpected_adapter"
    with pytest.raises(smoke.SmokeError, match="adapter ids"):
        smoke.validate_external_tool_adapters("external-tool-adapters", wrong_adapter)

    reordered_adapter = external_tool_adapters_payload()
    adapters = external_tool_adapter_entries(reordered_adapter)
    adapters[0], adapters[1] = adapters[1], adapters[0]
    with pytest.raises(smoke.SmokeError, match="adapter ids"):
        smoke.validate_external_tool_adapters("external-tool-adapters", reordered_adapter)

    metadata_drift = external_tool_adapters_payload()
    adapters = external_tool_adapter_entries(metadata_drift)
    adapters[1]["platform_label"] = "instagram"
    with pytest.raises(smoke.SmokeError, match="xiaohongshu_crawler platform_label"):
        smoke.validate_external_tool_adapters("external-tool-adapters", metadata_drift)

    missing_commands = external_tool_adapters_payload()
    adapters = external_tool_adapter_entries(missing_commands)
    adapters[1].pop("recommended_commands")
    with pytest.raises(smoke.SmokeError, match="recommended_commands must be a list"):
        smoke.validate_external_tool_adapters("external-tool-adapters", missing_commands)

    wrong_command_prefix = external_tool_adapters_payload()
    adapters = external_tool_adapter_entries(wrong_command_prefix)
    commands = adapters[0]["recommended_commands"]
    assert isinstance(commands, list)
    commands[0] = "python community-signal-profile --format json"
    with pytest.raises(smoke.SmokeError, match="command prefixes"):
        smoke.validate_external_tool_adapters("external-tool-adapters", wrong_command_prefix)

    missing_readiness = external_tool_adapters_payload()
    adapters = external_tool_adapter_entries(missing_readiness)
    adapters[0]["recommended_commands"] = [
        external_tool_command("community-signal-profile", "--format", "json")
    ]
    with pytest.raises(smoke.SmokeError, match="missing external-tool-readiness command"):
        smoke.validate_external_tool_adapters("external-tool-adapters", missing_readiness)

    duplicate_readiness = external_tool_adapters_payload()
    adapters = external_tool_adapter_entries(duplicate_readiness)
    commands = adapters[0]["recommended_commands"]
    assert isinstance(commands, list)
    commands[2] = commands[1]
    with pytest.raises(smoke.SmokeError, match="exactly one external-tool-readiness"):
        smoke.validate_external_tool_adapters("external-tool-adapters", duplicate_readiness)

    missing_token = external_tool_adapters_payload()
    replace_external_tool_readiness_command(
        missing_token,
        (
            "fashion-radar external-tool-readiness --adapter rednote_mcp "
            "--directory exports --config-dir configs --data-dir data "
            "--as-of 2026-06-13T12:00:00+00:00 "
            "--pattern '*.json' --source-name 'Rednote MCP Export' --format table"
        ),
    )
    with pytest.raises(smoke.SmokeError, match="readiness command missing '--input-format'"):
        smoke.validate_external_tool_adapters("external-tool-adapters", missing_token)

    missing_format = external_tool_adapters_payload()
    replace_external_tool_readiness_command(
        missing_format,
        (
            "fashion-radar external-tool-readiness --adapter rednote_mcp "
            "--directory exports --config-dir configs --data-dir data "
            "--as-of 2026-06-13T12:00:00+00:00 --input-format json "
            "--pattern '*.json' --source-name 'Rednote MCP Export'"
        ),
    )
    with pytest.raises(smoke.SmokeError, match="readiness command missing '--format'"):
        smoke.validate_external_tool_adapters("external-tool-adapters", missing_format)

    invalid_format = external_tool_adapters_payload()
    replace_external_tool_readiness_command(
        invalid_format,
        (
            "fashion-radar external-tool-readiness --adapter rednote_mcp "
            "--directory exports --config-dir configs --data-dir data "
            "--as-of 2026-06-13T12:00:00+00:00 --input-format json "
            "--pattern '*.json' --source-name 'Rednote MCP Export' --format json"
        ),
    )
    with pytest.raises(smoke.SmokeError, match="readiness output format"):
        smoke.validate_external_tool_adapters("external-tool-adapters", invalid_format)

    later_input_format_drift = external_tool_adapters_payload()
    replace_external_tool_readiness_command(
        later_input_format_drift,
        external_tool_command(
            "external-tool-readiness",
            "--adapter",
            "xiaohongshu_crawler",
            "--directory",
            "exports",
            "--config-dir",
            "configs",
            "--data-dir",
            "data",
            "--as-of",
            "2026-06-13T12:00:00+00:00",
            "--input-format",
            "json",
            "--pattern",
            "*.json",
            "--source-name",
            "Xiaohongshu Crawler Export",
            "--format",
            "table",
        ),
        adapter_index=1,
    )
    with pytest.raises(
        smoke.SmokeError,
        match="xiaohongshu_crawler readiness input_format",
    ):
        smoke.validate_external_tool_adapters(
            "external-tool-adapters",
            later_input_format_drift,
        )

    missing_value = external_tool_adapters_payload()
    replace_external_tool_readiness_command(
        missing_value,
        (
            "fashion-radar external-tool-readiness --adapter rednote_mcp "
            "--directory exports --config-dir configs --data-dir data "
            "--as-of 2026-06-13T12:00:00+00:00 --input-format json "
            "--pattern '*.json' --source-name --format table"
        ),
    )
    with pytest.raises(smoke.SmokeError, match="missing value for '--source-name'"):
        smoke.validate_external_tool_adapters("external-tool-adapters", missing_value)

    trailing_flag = external_tool_adapters_payload()
    replace_external_tool_readiness_command(
        trailing_flag,
        (
            "fashion-radar external-tool-readiness --adapter rednote_mcp "
            "--directory exports --config-dir configs --data-dir data --as-of"
        ),
    )
    with pytest.raises(smoke.SmokeError, match="missing value for '--as-of'"):
        smoke.validate_external_tool_adapters("external-tool-adapters", trailing_flag)

    malformed_readiness = external_tool_adapters_payload()
    replace_external_tool_readiness_command(
        malformed_readiness,
        "fashion-radar external-tool-readiness --adapter rednote_mcp --source-name 'Rednote",
    )
    with pytest.raises(smoke.SmokeError, match="command 2 is not shell-parseable"):
        smoke.validate_external_tool_adapters("external-tool-adapters", malformed_readiness)


@pytest.mark.parametrize(
    ("mutate", "match"),
    (
        (add_external_tool_registry_extra_key, "external-tool-adapters keys"),
        (remove_external_tool_registry_boundary, "external-tool-adapters boundaries"),
        (add_external_tool_adapter_extra_key, "rednote_mcp keys"),
        (remove_external_tool_adapter_key, "rednote_mcp keys"),
        (drift_external_tool_later_adapter_description, "xiaohongshu_crawler description"),
        (drift_external_tool_upstream_examples, "x_search_export upstream_tool_examples"),
        (drift_external_tool_field_mapping_required, "rednote_mcp field_mappings"),
        (drift_external_tool_field_mapping_note, "rednote_mcp field_mappings"),
        (drift_external_tool_adapter_boundaries, "rednote_mcp boundaries"),
        (drift_external_tool_later_manifest_command, "xiaohongshu_crawler recommended_commands"),
        (drift_external_tool_readiness_extra_flag, "rednote_mcp recommended_commands"),
    ),
)
def test_validate_external_tool_adapters_rejects_full_static_contract_drift(
    mutate: Callable[[dict[str, object]], None],
    match: str,
) -> None:
    payload = external_tool_adapters_payload()
    mutate(payload)

    assert_external_tool_adapter_contract_drift(payload, match)


def test_validate_external_tool_template_requires_importable_items() -> None:
    smoke.validate_external_tool_template(
        "external-tool-template",
        external_tool_template_payload(),
    )

    metadata_envelope = {
        "contract_version": "external-tool-template/v1",
        "items": [{"platform": "rednote"}],
    }
    with pytest.raises(smoke.SmokeError, match="keys"):
        smoke.validate_external_tool_template("external-tool-template", metadata_envelope)

    missing_items: dict[str, object] = {"items": []}
    with pytest.raises(smoke.SmokeError, match="exactly 2 rows"):
        smoke.validate_external_tool_template("external-tool-template", missing_items)

    wrong_platform = external_tool_template_payload()
    items = wrong_platform["items"]
    assert isinstance(items, list)
    items[1]["platform"] = "instagram"  # type: ignore[index]
    with pytest.raises(smoke.SmokeError, match="row 2 platform"):
        smoke.validate_external_tool_template("external-tool-template", wrong_platform)

    missing_handoff_field = external_tool_template_payload()
    items = missing_handoff_field["items"]
    assert isinstance(items, list)
    del items[0]["source_weight"]  # type: ignore[index]
    with pytest.raises(smoke.SmokeError, match="row 1 source_weight"):
        smoke.validate_external_tool_template("external-tool-template", missing_handoff_field)

    private_field = external_tool_template_payload()
    items = private_field["items"]
    assert isinstance(items, list)
    items[0]["_private"] = "adapter secret"  # type: ignore[index]
    with pytest.raises(smoke.SmokeError, match="private/raw field"):
        smoke.validate_external_tool_template("external-tool-template", private_field)

    raw_field = external_tool_template_payload()
    items = raw_field["items"]
    assert isinstance(items, list)
    items[0]["raw_payload"] = {"opaque": True}  # type: ignore[index]
    with pytest.raises(smoke.SmokeError, match="private/raw field"):
        smoke.validate_external_tool_template("external-tool-template", raw_field)


def test_validate_external_tool_template_rejects_title_drift() -> None:
    payload = external_tool_template_payload()
    items = payload["items"]
    assert isinstance(items, list)
    items[0]["title"] = "Run npm install -g rednote-mcp before collecting rows."  # type: ignore[index]

    with pytest.raises(smoke.SmokeError, match="row 1 item"):
        smoke.validate_external_tool_template("external-tool-template", payload)


def test_validate_external_tool_template_rejects_source_weight_drift() -> None:
    payload = external_tool_template_payload()
    items = payload["items"]
    assert isinstance(items, list)
    items[1]["source_weight"] = 4.5  # type: ignore[index]

    with pytest.raises(smoke.SmokeError, match="row 2 item"):
        smoke.validate_external_tool_template("external-tool-template", payload)


@pytest.mark.parametrize(
    ("payload_fn", "validator", "command_name"),
    [
        (
            external_tool_workflow_payload,
            smoke.validate_external_tool_workflow,
            "external-tool-workflow",
        ),
        (
            external_tool_readiness_payload,
            smoke.validate_external_tool_readiness,
            "external-tool-readiness",
        ),
    ],
)
def test_validate_external_tool_surfaces_reject_display_name_drift(
    payload_fn: Callable[[], dict[str, object]],
    validator: Callable[[str, object], None],
    command_name: str,
) -> None:
    payload = payload_fn()
    payload["display_name"] = "Unexpected Export Label"

    with pytest.raises(smoke.SmokeError, match="display_name"):
        validator(command_name, payload)


def test_validate_external_tool_workflow_requires_print_only_workflow_contract() -> None:
    smoke.validate_external_tool_workflow(
        "external-tool-workflow",
        external_tool_workflow_payload(),
    )

    wrong_contract = external_tool_workflow_payload()
    wrong_contract["contract_version"] = "other/v1"
    with pytest.raises(smoke.SmokeError, match="contract_version"):
        smoke.validate_external_tool_workflow("external-tool-workflow", wrong_contract)

    runnable = external_tool_workflow_payload()
    runnable["execution_mode"] = "runs_commands"
    with pytest.raises(smoke.SmokeError, match="execution_mode"):
        smoke.validate_external_tool_workflow("external-tool-workflow", runnable)

    missing_step = external_tool_workflow_payload()
    steps = missing_step["steps"]
    assert isinstance(steps, list)
    del steps[8]
    with pytest.raises(smoke.SmokeError, match="step_count|step names"):
        smoke.validate_external_tool_workflow("external-tool-workflow", missing_step)

    executable_import = external_tool_workflow_payload()
    steps = executable_import["steps"]
    assert isinstance(steps, list)
    import_step = steps[10]
    assert isinstance(import_step, dict)
    import_step["suggested_effect"] = "read_only"
    with pytest.raises(smoke.SmokeError, match="import step effect"):
        smoke.validate_external_tool_workflow("external-tool-workflow", executable_import)


def test_validate_external_tool_workflow_rejects_extra_readiness_command_flag() -> None:
    payload = external_tool_workflow_payload()
    steps = payload["steps"]
    assert isinstance(steps, list)
    readiness_step = steps[1]
    assert isinstance(readiness_step, dict)
    readiness_step["command"] = str(readiness_step["command"]) + " --verbose"

    with pytest.raises(smoke.SmokeError, match="readiness command"):
        smoke.validate_external_tool_workflow("external-tool-workflow", payload)


@pytest.mark.parametrize(
    "boundaries",
    [
        [
            *external_tool_workflow_payload()["boundaries"],
            "Runs source acquisition and opens platform APIs.",
        ],
        [
            (
                "Does not run generated commands. No platform collection, no scraping, "
                "no platform APIs. Runs source acquisition and opens platform APIs."
            )
        ],
    ],
)
def test_validate_external_tool_workflow_rejects_boundary_drift(
    boundaries: list[str],
) -> None:
    payload = external_tool_workflow_payload()
    payload["boundaries"] = boundaries

    with pytest.raises(smoke.SmokeError, match="boundaries"):
        smoke.validate_external_tool_workflow("external-tool-workflow", payload)


@pytest.mark.parametrize(
    ("step_name", "replacement_command", "expected_error"),
    [
        (
            "print_signal_profile",
            external_tool_command("community-signal-profile", "--format", "table"),
            "signal profile command",
        ),
        (
            "print_handoff_manifest",
            external_tool_command(
                "community-handoff-manifest",
                "exports",
                "--input-format",
                "json",
                "--pattern",
                "*.json",
                "--config-dir",
                "configs",
                "--data-dir",
                "data",
                "--as-of",
                "2026-06-13T12:00:00+00:00",
                "--source-name",
                "Rednote MCP Export",
                "--format",
                "table",
            ),
            "handoff manifest command",
        ),
        (
            "print_handoff_workflow",
            external_tool_command(
                "community-handoff-workflow",
                "exports",
                "--input-format",
                "json",
                "--pattern",
                "*.json",
                "--config-dir",
                "configs",
                "--data-dir",
                "data",
                "--as-of",
                "2026-06-13T12:00:00+00:00",
                "--source-name",
                "Rednote MCP Export",
                "--format",
                "json",
            ),
            "handoff workflow command",
        ),
        (
            "preview_candidate_phrases",
            external_tool_command(
                "community-candidates-dir",
                "exports",
                "--input-format",
                "json",
                "--pattern",
                "*.json",
                "--config-dir",
                "configs",
                "--as-of",
                "2026-06-13T12:00:00+00:00",
                "--source-name",
                "Wrong Source",
            ),
            "candidate preview command",
        ),
        (
            "review_handoff_readiness",
            external_tool_command(
                "community-handoff-check-dir",
                "exports",
                "--input-format",
                "json",
                "--pattern",
                "*.json",
                "--config-dir",
                "configs",
                "--as-of",
                "2026-06-13T12:00:00+00:00",
                "--source-name",
                "Rednote MCP Export",
            ),
            "handoff readiness command",
        ),
        (
            "dry_run_directory_import",
            external_tool_command(
                "import-signals-dir",
                "exports",
                "--format",
                "json",
                "--pattern",
                "*.json",
                "--source-name",
                "Rednote MCP Export",
                "--data-dir",
                "data",
                "--imported-at",
                "2026-06-13T12:00:00+00:00",
            ),
            "dry-run command",
        ),
        (
            "import_directory_signals",
            external_tool_command(
                "import-signals-dir",
                "exports",
                "--format",
                "json",
                "--pattern",
                "*.json",
                "--source-name",
                "Rednote MCP Export",
                "--data-dir",
                "data",
                "--imported-at",
                "2026-06-13T12:00:00+00:00",
                "--dry-run",
            ),
            "import command",
        ),
        (
            "print_post_import_review",
            external_tool_command(
                "imported-review-workflow",
                "--config-dir",
                "configs",
                "--data-dir",
                "data",
                "--as-of",
                "2026-06-13T12:00:00+00:00",
                "--source-name",
                "Wrong Source",
            ),
            "post-import review command",
        ),
    ],
)
def test_validate_external_tool_workflow_rejects_remaining_step_command_argv_drift(
    step_name: str,
    replacement_command: str,
    expected_error: str,
) -> None:
    payload = external_tool_workflow_payload()
    steps = payload["steps"]
    assert isinstance(steps, list)
    matching_steps = [
        step for step in steps if isinstance(step, dict) and step.get("name") == step_name
    ]
    assert len(matching_steps) == 1
    matching_steps[0]["command"] = replacement_command

    with pytest.raises(smoke.SmokeError, match=expected_error):
        smoke.validate_external_tool_workflow("external-tool-workflow", payload)


def test_validate_external_tool_readiness_rejects_wrong_workflow_output_format() -> None:
    payload = external_tool_readiness_payload()
    steps = payload["steps"]
    assert isinstance(steps, list)
    workflow_step = steps[2]
    assert isinstance(workflow_step, dict)
    workflow_step["command"] = external_tool_command(
        "external-tool-workflow",
        "--adapter",
        "rednote_mcp",
        "--directory",
        "exports",
        "--config-dir",
        "configs",
        "--data-dir",
        "data",
        "--as-of",
        "2026-06-13T12:00:00+00:00",
        "--input-format",
        "json",
        "--pattern",
        "*.json",
        "--source-name",
        "Rednote MCP Export",
        "--format",
        "json",
    )

    with pytest.raises(smoke.SmokeError, match="workflow command"):
        smoke.validate_external_tool_readiness("external-tool-readiness", payload)


def test_validate_external_tool_readiness_rejects_wrong_dry_run_input_format() -> None:
    payload = external_tool_readiness_payload()
    steps = payload["steps"]
    assert isinstance(steps, list)
    dry_run_step = steps[-1]
    assert isinstance(dry_run_step, dict)
    dry_run_step["command"] = external_tool_command(
        "import-signals-dir",
        "exports",
        "--format",
        "csv",
        "--pattern",
        "*.json",
        "--source-name",
        "Rednote MCP Export",
        "--data-dir",
        "data",
        "--imported-at",
        "2026-06-13T12:00:00+00:00",
        "--dry-run",
    )

    with pytest.raises(smoke.SmokeError, match="dry-run command"):
        smoke.validate_external_tool_readiness("external-tool-readiness", payload)


@pytest.mark.parametrize(
    ("step_name", "replacement_command", "expected_error"),
    [
        (
            "inspect_adapter_registry",
            external_tool_command(
                "external-tool-adapters",
                "--adapter",
                "rednote_mcp",
                "--directory",
                "exports",
                "--config-dir",
                "configs",
                "--data-dir",
                "data",
                "--as-of",
                "2026-06-13T12:00:00+00:00",
                "--format",
                "json",
            ),
            "registry command",
        ),
        (
            "print_adapter_template_json",
            external_tool_command(
                "external-tool-template",
                "--adapter",
                "rednote_mcp",
                "--directory",
                "exports",
                "--config-dir",
                "configs",
                "--data-dir",
                "data",
                "--as-of",
                "2026-06-13T12:00:00+00:00",
                "--format",
                "table",
            ),
            "template command",
        ),
        (
            "print_signal_profile",
            external_tool_command("community-signal-profile", "--format", "table"),
            "signal profile command",
        ),
        (
            "lint_export_directory",
            external_tool_command(
                "community-signal-lint-dir",
                "exports",
                "--input-format",
                "json",
                "--pattern",
                "*.json",
                "--source-name",
                "Rednote MCP Export",
            ),
            "lint command",
        ),
        (
            "review_handoff_readiness",
            external_tool_command(
                "community-handoff-check-dir",
                "exports",
                "--input-format",
                "json",
                "--pattern",
                "*.json",
                "--config-dir",
                "configs",
                "--as-of",
                "2026-06-13T12:00:00+00:00",
                "--source-name",
                "Rednote MCP Export",
            ),
            "handoff readiness command",
        ),
    ],
)
def test_validate_external_tool_readiness_rejects_remaining_step_command_argv_drift(
    step_name: str,
    replacement_command: str,
    expected_error: str,
) -> None:
    payload = external_tool_readiness_payload()
    steps = payload["steps"]
    assert isinstance(steps, list)
    matching_steps = [
        step for step in steps if isinstance(step, dict) and step.get("name") == step_name
    ]
    assert len(matching_steps) == 1
    matching_steps[0]["command"] = replacement_command

    with pytest.raises(smoke.SmokeError, match=expected_error):
        smoke.validate_external_tool_readiness("external-tool-readiness", payload)


def test_validate_external_tool_readiness_requires_local_read_only_contract() -> None:
    smoke.validate_external_tool_readiness(
        "external-tool-readiness",
        external_tool_readiness_payload(),
    )

    wrong_contract = external_tool_readiness_payload()
    wrong_contract["contract_version"] = "other/v1"
    with pytest.raises(smoke.SmokeError, match="contract_version"):
        smoke.validate_external_tool_readiness("external-tool-readiness", wrong_contract)

    runnable = external_tool_readiness_payload()
    runnable["execution_mode"] = "print_only"
    with pytest.raises(smoke.SmokeError, match="execution_mode"):
        smoke.validate_external_tool_readiness("external-tool-readiness", runnable)

    wrong_adapter = external_tool_readiness_payload()
    wrong_adapter["adapter_id"] = "instaloader"
    with pytest.raises(smoke.SmokeError, match="adapter_id"):
        smoke.validate_external_tool_readiness("external-tool-readiness", wrong_adapter)

    missing_check = external_tool_readiness_payload()
    missing_check["checks"] = []
    with pytest.raises(smoke.SmokeError, match="checks"):
        smoke.validate_external_tool_readiness("external-tool-readiness", missing_check)

    bad_status = external_tool_readiness_payload()
    checks = bad_status["checks"]
    assert isinstance(checks, list)
    checks[0]["status"] = "ran_command"  # type: ignore[index]
    with pytest.raises(smoke.SmokeError, match="status"):
        smoke.validate_external_tool_readiness("external-tool-readiness", bad_status)

    missing_detail = external_tool_readiness_payload()
    checks = missing_detail["checks"]
    assert isinstance(checks, list)
    checks[0]["detail"] = ""  # type: ignore[index]
    with pytest.raises(smoke.SmokeError, match="detail"):
        smoke.validate_external_tool_readiness("external-tool-readiness", missing_detail)

    missing_hint = external_tool_readiness_payload()
    checks = missing_hint["checks"]
    assert isinstance(checks, list)
    checks[0]["install_hint"] = "npm install rednote-mcp"  # type: ignore[index]
    with pytest.raises(smoke.SmokeError, match="install_hint"):
        smoke.validate_external_tool_readiness("external-tool-readiness", missing_hint)

    missing_step = external_tool_readiness_payload()
    steps = missing_step["steps"]
    assert isinstance(steps, list)
    del steps[2]
    with pytest.raises(smoke.SmokeError, match="step_count|step names"):
        smoke.validate_external_tool_readiness("external-tool-readiness", missing_step)


def test_validate_external_tool_readiness_rejects_executable_or_acquisition_scope() -> None:
    runnable_step = external_tool_readiness_payload()
    steps = runnable_step["steps"]
    assert isinstance(steps, list)
    steps[5]["suggested_effect"] = "updates_local_imports"  # type: ignore[index]
    with pytest.raises(smoke.SmokeError, match="step effects"):
        smoke.validate_external_tool_readiness("external-tool-readiness", runnable_step)

    acquisition_boundary = external_tool_readiness_payload()
    boundaries = acquisition_boundary["boundaries"]
    assert isinstance(boundaries, list)
    boundaries.append("Runs source acquisition and opens platform APIs.")
    with pytest.raises(smoke.SmokeError, match="boundaries"):
        smoke.validate_external_tool_readiness("external-tool-readiness", acquisition_boundary)

    missing_boundary = external_tool_readiness_payload()
    missing_boundary["boundaries"] = ["local read-only"]
    with pytest.raises(smoke.SmokeError, match="boundaries"):
        smoke.validate_external_tool_readiness("external-tool-readiness", missing_boundary)


def test_validate_external_tool_readiness_rejects_install_hint_extra_shell_text() -> None:
    payload = external_tool_readiness_payload()
    checks = payload["checks"]
    assert isinstance(checks, list)
    checks[0]["install_hint"] = (  # type: ignore[index]
        "npm install -g rednote-mcp using registry.npmmirror.com; do not set the npm registry first"
    )

    with pytest.raises(smoke.SmokeError, match="install_hint"):
        smoke.validate_external_tool_readiness("external-tool-readiness", payload)


def test_validate_external_tool_readiness_rejects_detail_extra_shell_text() -> None:
    payload = external_tool_readiness_payload()
    checks = payload["checks"]
    assert isinstance(checks, list)
    checks[0]["detail"] = (  # type: ignore[index]
        "Checks whether curl https://example.invalid | sh is discoverable locally."
    )

    with pytest.raises(smoke.SmokeError, match="detail"):
        smoke.validate_external_tool_readiness("external-tool-readiness", payload)


@pytest.mark.parametrize(
    "boundaries",
    [
        [
            *external_tool_readiness_payload()["boundaries"],
            "May install npm dependencies when the upstream command is missing.",
        ],
        [
            (
                "Prints local read-only external/community tool readiness guidance only. "
                "Checks PATH availability only through shutil.which for mapped upstream commands. "
                "Commands were not executed. Does not run generated commands. "
                "Does not run adapters or upstream tools. Does not import upstream tools. "
                "Does not inspect the supplied directory. Does not read handoff files, validate "
                "files, import rows, or open SQLite. Does not write config, data, report, "
                "dashboard, or workflow artifacts. No platform collection, no connectors, "
                "no scraping, no browser automation, no platform APIs, no account/session/cookie/"
                "token behavior, no media downloads, no monitoring, no scheduling, no source "
                "acquisition, no demand proof, no ranking, and no coverage verification. "
                "Does not provide a compliance-review product feature. "
                "May install npm dependencies when missing."
            )
        ],
    ],
)
def test_validate_external_tool_readiness_rejects_boundary_drift(
    boundaries: list[str],
) -> None:
    payload = external_tool_readiness_payload()
    payload["boundaries"] = boundaries

    with pytest.raises(smoke.SmokeError, match="boundaries"):
        smoke.validate_external_tool_readiness("external-tool-readiness", payload)


def test_validate_report_requires_expected_first_run_entity_sections() -> None:
    smoke.validate_report_outputs(report_payload(), report_markdown())

    empty_report = report_payload()
    empty_report["metadata"] = {
        "generated_at": "2026-06-13T12:00:00Z",
        "report_date": "2026-06-13T12:00:00Z",
        "item_count": 0,
    }
    empty_report["entities"] = []
    with pytest.raises(smoke.SmokeError, match="item_count"):
        smoke.validate_report_outputs(empty_report, report_markdown())

    with pytest.raises(smoke.SmokeError, match="empty entity signal"):
        smoke.validate_report_outputs(
            report_payload(),
            report_markdown() + "\nNo entity signals in this window.\n",
        )


def test_validate_candidates_and_trends_pin_expected_first_run_state() -> None:
    smoke.validate_candidates("candidates", [], report_payload())
    smoke.validate_trends("trends", trends_payload())

    with pytest.raises(smoke.SmokeError, match="candidates"):
        smoke.validate_candidates("candidates", [{"phrase": "unexpected"}], report_payload())

    missing_delta = trends_payload()
    missing_delta["deltas"] = [{"signal_kind": "entity", "name": "The Row"}]
    with pytest.raises(smoke.SmokeError, match="entity delta names"):
        smoke.validate_trends("trends", missing_delta)

    wrong_kind = trends_payload()
    deltas = wrong_kind["deltas"]
    assert isinstance(deltas, list)
    deltas[0]["signal_kind"] = "candidate"  # type: ignore[index]
    with pytest.raises(smoke.SmokeError, match="signal_kind"):
        smoke.validate_trends("trends", wrong_kind)


def test_report_paths_derive_date_from_as_of(tmp_path: Path) -> None:
    context = make_context(tmp_path)

    markdown_path, json_path = smoke.report_paths(context)

    assert markdown_path == context.reports_dir / "fashion-radar-2026-06-13.md"
    assert json_path == context.reports_dir / "fashion-radar-2026-06-13.json"


def test_default_artifact_guard_detects_new_repo_data_and_report_files(
    tmp_path: Path,
) -> None:
    before = smoke.snapshot_default_artifacts(tmp_path)
    data_file = tmp_path / "data" / "fashion-radar.sqlite"
    report_file = tmp_path / "reports" / "fashion-radar-2026-06-13.json"
    data_file.parent.mkdir()
    report_file.parent.mkdir()
    data_file.write_text("sqlite", encoding="utf-8")
    report_file.write_text("{}", encoding="utf-8")

    with pytest.raises(smoke.SmokeError) as exc_info:
        smoke.assert_default_artifacts_unchanged(tmp_path, before)

    message = str(exc_info.value)
    assert "created:" in message
    assert "data/fashion-radar.sqlite" in message
    assert "reports/fashion-radar-2026-06-13.json" in message


def test_default_artifact_guard_detects_changed_repo_data_and_report_files(
    tmp_path: Path,
) -> None:
    data_file = tmp_path / "data" / "fashion-radar.sqlite"
    report_file = tmp_path / "reports" / "fashion-radar-2026-06-13.json"
    data_file.parent.mkdir()
    report_file.parent.mkdir()
    data_file.write_text("before", encoding="utf-8")
    report_file.write_text('{"before": true}', encoding="utf-8")
    before = smoke.snapshot_default_artifacts(tmp_path)

    data_file.write_text("after", encoding="utf-8")
    report_file.write_text('{"after": true}', encoding="utf-8")

    with pytest.raises(smoke.SmokeError) as exc_info:
        smoke.assert_default_artifacts_unchanged(tmp_path, before)

    message = str(exc_info.value)
    assert "changed:" in message
    assert "data/fashion-radar.sqlite" in message
    assert "reports/fashion-radar-2026-06-13.json" in message


def test_default_artifact_guard_detects_deleted_repo_data_or_report_files(
    tmp_path: Path,
) -> None:
    report_file = tmp_path / "reports" / "fashion-radar-2026-06-13.json"
    report_file.parent.mkdir()
    report_file.write_text("{}", encoding="utf-8")
    before = smoke.snapshot_default_artifacts(tmp_path)

    report_file.unlink()

    with pytest.raises(smoke.SmokeError) as exc_info:
        smoke.assert_default_artifacts_unchanged(tmp_path, before)

    message = str(exc_info.value)
    assert "deleted:" in message
    assert "reports/fashion-radar-2026-06-13.json" in message


def test_workspace_artifact_assertion_requires_temp_dirs_and_sqlite(tmp_path: Path) -> None:
    context = make_context(tmp_path)
    context.config_dir.mkdir(parents=True)
    context.data_dir.mkdir(parents=True)
    context.reports_dir.mkdir(parents=True)

    with pytest.raises(smoke.SmokeError, match="Expected SQLite database"):
        smoke.assert_workspace_artifacts(context)

    (context.data_dir / "fashion-radar.sqlite").write_text("sqlite", encoding="utf-8")

    smoke.assert_workspace_artifacts(context)


def test_parse_args_defaults_to_source_checkout() -> None:
    args = smoke.parse_args(["--repo-root", ".", "--python", "python-test"])

    assert args.repo_root == "."
    assert args.python == "python-test"
    assert args.installed is False


def test_parse_args_accepts_installed_mode() -> None:
    args = smoke.parse_args(["--repo-root", ".", "--python", "python-test", "--installed"])

    assert args.installed is True


def test_build_context_records_source_checkout_mode(tmp_path: Path) -> None:
    source_context = smoke.build_context(tmp_path, "python-test", tmp_path / "source")
    installed_context = smoke.build_context(
        tmp_path,
        "python-test",
        tmp_path / "installed",
        source_checkout=False,
    )

    assert source_context.source_checkout is True
    assert installed_context.source_checkout is False


def test_assert_installed_import_origin_rejects_repo_src_path(tmp_path: Path) -> None:
    context = smoke.build_context(
        tmp_path,
        sys.executable,
        tmp_path / "runtime",
        source_checkout=False,
    )
    source_file = tmp_path / "src" / "fashion_radar" / "__init__.py"
    source_file.parent.mkdir(parents=True)
    source_file.write_text("", encoding="utf-8")

    with pytest.raises(smoke.SmokeError, match="source checkout"):
        smoke.assert_installed_import_origin(context, source_file)


def test_assert_installed_import_origin_allows_non_source_path(tmp_path: Path) -> None:
    context = smoke.build_context(
        tmp_path,
        sys.executable,
        tmp_path / "runtime",
        source_checkout=False,
    )
    installed_file = tmp_path / "venv" / "site-packages" / "fashion_radar" / "__init__.py"
    installed_file.parent.mkdir(parents=True)
    installed_file.write_text("", encoding="utf-8")

    smoke.assert_installed_import_origin(context, installed_file)


def test_installed_import_origin_rejects_empty_stdout(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    context = smoke.build_context(
        tmp_path,
        sys.executable,
        tmp_path / "runtime",
        source_checkout=False,
    )

    def fake_run(command, *, cwd, env, text, capture_output, check):
        return subprocess.CompletedProcess(command, 0, stdout="", stderr="")

    monkeypatch.setattr(smoke.subprocess, "run", fake_run)

    with pytest.raises(smoke.SmokeError, match="no module path"):
        smoke.installed_import_origin(context)


def test_installed_import_origin_rejects_extra_stdout_lines(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    context = smoke.build_context(
        tmp_path,
        sys.executable,
        tmp_path / "runtime",
        source_checkout=False,
    )
    source_file = tmp_path / "src" / "fashion_radar" / "__init__.py"

    def fake_run(command, *, cwd, env, text, capture_output, check):
        return subprocess.CompletedProcess(
            command,
            0,
            stdout=f'noise\n{{"module_file": "{source_file}"}}\n',
            stderr="",
        )

    monkeypatch.setattr(smoke.subprocess, "run", fake_run)

    with pytest.raises(smoke.SmokeError, match="no module path"):
        smoke.installed_import_origin(context)


def test_installed_import_origin_rejects_invalid_json(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    context = smoke.build_context(
        tmp_path,
        sys.executable,
        tmp_path / "runtime",
        source_checkout=False,
    )

    def fake_run(command, *, cwd, env, text, capture_output, check):
        return subprocess.CompletedProcess(command, 0, stdout="not-json\n", stderr="")

    monkeypatch.setattr(smoke.subprocess, "run", fake_run)

    with pytest.raises(smoke.SmokeError, match="invalid JSON"):
        smoke.installed_import_origin(context)


def test_installed_import_origin_rejects_command_failure(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    context = smoke.build_context(
        tmp_path,
        sys.executable,
        tmp_path / "runtime",
        source_checkout=False,
    )

    def fake_run(command, *, cwd, env, text, capture_output, check):
        return subprocess.CompletedProcess(command, 1, stdout="", stderr="boom")

    monkeypatch.setattr(smoke.subprocess, "run", fake_run)

    with pytest.raises(smoke.SmokeError, match="Command failed"):
        smoke.installed_import_origin(context)


def test_installed_import_origin_returns_module_file_from_json(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    context = smoke.build_context(
        tmp_path,
        sys.executable,
        tmp_path / "runtime",
        source_checkout=False,
    )
    installed_file = tmp_path / "venv" / "site-packages" / "fashion_radar" / "__init__.py"

    def fake_run(command, *, cwd, env, text, capture_output, check):
        return subprocess.CompletedProcess(
            command,
            0,
            stdout=f'{{"module_file": "{installed_file}"}}\n',
            stderr="",
        )

    monkeypatch.setattr(smoke.subprocess, "run", fake_run)

    assert smoke.installed_import_origin(context) == installed_file


def test_installed_import_origin_uses_scrubbed_installed_environment(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    context = smoke.build_context(
        tmp_path,
        sys.executable,
        tmp_path / "runtime",
        source_checkout=False,
    )
    installed_file = tmp_path / "venv" / "site-packages" / "fashion_radar" / "__init__.py"
    captured_env: dict[str, str] = {}
    monkeypatch.setenv(
        "PYTHONPATH",
        os.pathsep.join(["/already/here", str(tmp_path / "src")]),
    )

    def fake_run(command, *, cwd, env, text, capture_output, check):
        captured_env.update(env)
        return subprocess.CompletedProcess(
            command,
            0,
            stdout=f'{{"module_file": "{installed_file}"}}\n',
            stderr="",
        )

    monkeypatch.setattr(smoke.subprocess, "run", fake_run)

    assert smoke.installed_import_origin(context) == installed_file
    assert captured_env["PYTHONPATH"] == "/already/here"


def test_run_cli_uses_context_source_checkout_flag(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    context = smoke.build_context(
        tmp_path,
        sys.executable,
        tmp_path / "runtime",
        source_checkout=False,
    )
    captured_env: dict[str, str] = {}

    def fake_run(command, *, cwd, env, text, capture_output, check):
        captured_env.clear()
        captured_env.update(env)
        return subprocess.CompletedProcess(command, 0, stdout="", stderr="")

    monkeypatch.setattr(smoke.subprocess, "run", fake_run)
    monkeypatch.setenv(
        "PYTHONPATH",
        os.pathsep.join(["/already/here", str(tmp_path / "src")]),
    )

    smoke.run_cli(context, "--help")

    assert captured_env["PYTHONPATH"] == "/already/here"


def test_main_installed_preflights_before_running_smoke(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    calls: list[tuple[str, bool]] = []
    module_file = tmp_path / "venv" / "site-packages" / "fashion_radar" / "__init__.py"

    def fake_installed_import_origin(context):
        calls.append(("origin", context.source_checkout))
        return module_file

    def fake_assert_installed_import_origin(context, origin):
        assert origin == module_file
        calls.append(("assert", context.source_checkout))

    def fake_run_smoke(context):
        calls.append(("smoke", context.source_checkout))

    monkeypatch.setattr(smoke, "installed_import_origin", fake_installed_import_origin)
    monkeypatch.setattr(
        smoke,
        "assert_installed_import_origin",
        fake_assert_installed_import_origin,
    )
    monkeypatch.setattr(smoke, "run_smoke", fake_run_smoke)

    result = smoke.main(
        [
            "--repo-root",
            str(tmp_path),
            "--python",
            sys.executable,
            "--installed",
        ]
    )

    assert result == 0
    assert calls == [("origin", False), ("assert", False), ("smoke", False)]


def test_assert_first_run_flow_commands_rejects_tail_command_extra_args(
    tmp_path: Path,
) -> None:
    context = make_context(tmp_path)
    example_csv = tmp_path / smoke.EXAMPLE_CSV
    captured = expected_first_run_flow_commands(context, example_csv)
    drifted = list(captured)
    handoff_index = next(
        index for index, command in enumerate(drifted) if command[0] == "community-handoff-workflow"
    )
    drifted[handoff_index] = (*drifted[handoff_index], "--extra")

    with pytest.raises(AssertionError):
        assert_first_run_flow_commands(drifted, context, example_csv)


def test_run_first_run_flow_uses_deterministic_local_command_sequence(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    example_csv = tmp_path / "examples" / "community-signals.example.csv"
    example_csv.parent.mkdir()
    example_csv.write_text(SAMPLE_CSV_TEXT, encoding="utf-8")
    context = make_context(tmp_path, python=sys.executable)
    captured: list[tuple[str, ...]] = []

    def fake_run_cli(fake_context, *args: str):
        assert fake_context is context
        captured.append(args)
        command_name = args[0]
        if command_name == "init":
            context.config_dir.mkdir(parents=True)
            context.data_dir.mkdir(parents=True)
            context.reports_dir.mkdir(parents=True)
        if command_name == "migrate-db":
            context.data_dir.mkdir(parents=True, exist_ok=True)
            (context.data_dir / "fashion-radar.sqlite").write_text(
                "sqlite",
                encoding="utf-8",
            )
        if command_name == "report":
            context.reports_dir.mkdir(parents=True, exist_ok=True)
            markdown_path, json_path = smoke.report_paths(context)
            markdown_path.write_text(report_markdown(), encoding="utf-8")
            json_path.write_text(json.dumps(report_payload()), encoding="utf-8")

        if command_name == "import-signals":
            output = (
                "Validated 2 manual signal rows\nDry run: no rows imported\n"
                if "--dry-run" in args
                else (
                    "Validated 2 manual signal rows\n"
                    "Imported 2 manual signal rows\n"
                    "Items added: 2\n"
                )
            )
            return subprocess.CompletedProcess(
                ["python", "-m", "fashion_radar", *args],
                0,
                stdout=output,
                stderr="",
            )

        if command_name == "import-signals-dir":
            return subprocess.CompletedProcess(
                ["python", "-m", "fashion_radar", *args],
                0,
                stdout=(
                    "Files: 1 total, 1 valid\n"
                    "Rows: 2 import-ready\n"
                    "Sources: Community Tool Export=2\n"
                    "Platforms: community=2\n"
                    "Errors: 0\n"
                    "- /tmp/export/community-signals.csv: 2 rows, 0 errors\n"
                    "No manual signal directory dry-run errors.\n"
                ),
                stderr="",
            )

        stdout_by_command = {
            "community-candidates": json.dumps(community_candidates_payload()),
            "imported-review-workflow": build_imported_review_workflow(
                config_dir=context.config_dir,
                data_dir=context.data_dir,
                as_of=smoke.AS_OF,
                source_name=smoke.SOURCE_NAME,
            ).model_dump_json(),
            "community-handoff-workflow": build_community_handoff_workflow(
                directory=context.exports_dir,
                config_dir=context.config_dir,
                data_dir=context.data_dir,
                input_format="csv",
                pattern=smoke.DIR_PATTERN,
                as_of=smoke.AS_OF,
                source_name=smoke.SOURCE_NAME,
            ).model_dump_json(),
            "external-tool-adapters": json.dumps(external_tool_adapters_payload()),
            "external-tool-template": json.dumps(external_tool_template_payload()),
            "external-tool-workflow": json.dumps(external_tool_workflow_payload()),
            "external-tool-readiness": json.dumps(external_tool_readiness_payload()),
            "imported-signals-summary": json.dumps(imported_summary_payload()),
            "imported-signals": json.dumps(imported_signals_payload()),
            "candidates": json.dumps([]),
            "trends": json.dumps(trends_payload()),
            "community-candidates-dir": json.dumps(community_candidates_payload(directory=True)),
        }
        return subprocess.CompletedProcess(
            ["python", "-m", "fashion_radar", *args],
            0,
            stdout=stdout_by_command.get(command_name, ""),
            stderr="",
        )

    monkeypatch.setattr(smoke, "run_cli", fake_run_cli)

    smoke.run_first_run_flow(context)

    assert_first_run_flow_commands(captured, context, example_csv)
    assert (context.exports_dir / smoke.DIR_EXPORT_CSV).read_text(encoding="utf-8") == (
        example_csv.read_text(encoding="utf-8")
    )
