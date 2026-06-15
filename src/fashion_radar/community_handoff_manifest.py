from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from fashion_radar.community_handoff_workflow import (
    CommunityHandoffWorkflow,
    build_community_handoff_workflow,
)
from fashion_radar.community_signal_profile import build_community_signal_profile
from fashion_radar.importers.manual_signals import ManualSignalFormat

COMMUNITY_HANDOFF_MANIFEST_CONTRACT_VERSION = "community-handoff-manifest/v1"
COMMUNITY_HANDOFF_MANIFEST_EXECUTION_MODE = "print_only"
COMMUNITY_HANDOFF_MANIFEST_PROFILE_COMMAND = "fashion-radar community-signal-profile --format json"
COMMUNITY_HANDOFF_MANIFEST_MATCHED_FILE_RULE = (
    "Downstream lint, preview, and import commands treat matching regular files "
    "directly under the supplied directory as handoff files; they do not recurse "
    "into subdirectories."
)
COMMUNITY_HANDOFF_MANIFEST_STORAGE_NOTE = (
    "Do not save this manifest as a matched handoff file. For example, when "
    'using --pattern "*.json", do not save the manifest as a .json file inside '
    "the handoff directory; save it outside the directory or use an excluded "
    "filename/pattern."
)
COMMUNITY_HANDOFF_MANIFEST_BOUNDARIES = [
    "Prints the local directory handoff manifest only.",
    "Does not inspect the supplied directory.",
    "Does not read handoff files, validate files, import rows, or open SQLite.",
    "Does not create config, data, report, dashboard, or workflow artifacts.",
    (
        "Does not fetch URLs, search platforms, log in, store cookies, automate "
        "browsers, call platform APIs, monitor communities, schedule work, add "
        "source/platform connectors, prove demand, verify platform coverage, or "
        "rank sources."
    ),
    "Does not provide a compliance-review workflow.",
]


class CommunityHandoffManifest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    contract_version: str
    execution_mode: Literal["print_only"]
    directory: str
    input_format: ManualSignalFormat
    pattern: str
    as_of: str
    config_dir: str
    data_dir: str
    source_name: str
    producer_profile_command: str
    producer_contract_version: str
    supported_input_formats: list[str]
    suggested_filename: str
    matched_file_rule: str
    manifest_storage_note: str
    schema_path: str
    example_paths: list[str]
    csv_header: list[str]
    required_fields: list[str]
    optional_fields: list[str]
    prohibited_fields: list[str]
    json_envelopes: list[str]
    field_notes: dict[str, str] = Field(default_factory=dict)
    field_rules: dict[str, dict[str, int | float]] = Field(default_factory=dict)
    unsupported_capabilities: list[str]
    workflow: CommunityHandoffWorkflow
    boundaries: list[str] = Field(default_factory=list)


def build_community_handoff_manifest(
    *,
    directory: Path,
    config_dir: Path,
    data_dir: Path,
    input_format: ManualSignalFormat,
    pattern: str,
    as_of: str | datetime,
    source_name: str,
) -> CommunityHandoffManifest:
    profile = build_community_signal_profile()
    workflow = build_community_handoff_workflow(
        directory=directory,
        config_dir=config_dir,
        data_dir=data_dir,
        input_format=input_format,
        pattern=pattern,
        as_of=as_of,
        source_name=source_name,
    )
    return CommunityHandoffManifest(
        contract_version=COMMUNITY_HANDOFF_MANIFEST_CONTRACT_VERSION,
        execution_mode=COMMUNITY_HANDOFF_MANIFEST_EXECUTION_MODE,
        directory=workflow.directory,
        input_format=workflow.input_format,
        pattern=workflow.pattern,
        as_of=workflow.as_of,
        config_dir=workflow.config_dir,
        data_dir=workflow.data_dir,
        source_name=workflow.source_name,
        producer_profile_command=COMMUNITY_HANDOFF_MANIFEST_PROFILE_COMMAND,
        producer_contract_version=profile.contract_version,
        supported_input_formats=[*profile.supported_input_formats],
        suggested_filename=_suggested_filename(input_format),
        matched_file_rule=COMMUNITY_HANDOFF_MANIFEST_MATCHED_FILE_RULE,
        manifest_storage_note=COMMUNITY_HANDOFF_MANIFEST_STORAGE_NOTE,
        schema_path=profile.schema_path,
        example_paths=[*profile.example_paths],
        csv_header=[*profile.csv_header],
        required_fields=[*profile.required_fields],
        optional_fields=[*profile.optional_fields],
        prohibited_fields=[*profile.prohibited_fields],
        json_envelopes=[*profile.json_envelopes],
        field_notes=dict(profile.field_notes),
        field_rules={key: dict(value) for key, value in profile.field_rules.items()},
        unsupported_capabilities=[*profile.unsupported_capabilities],
        workflow=workflow,
        boundaries=[*COMMUNITY_HANDOFF_MANIFEST_BOUNDARIES],
    )


def render_community_handoff_manifest_table(
    manifest: CommunityHandoffManifest,
) -> list[str]:
    lines = [
        "Community handoff manifest.",
        f"Contract version: {manifest.contract_version}",
        f"Execution mode: {manifest.execution_mode}",
        "Workflow commands were not executed.",
        f"Directory: {_table_cell(manifest.directory)}",
        f"Input format: {manifest.input_format}",
        f"Pattern: {_table_cell(manifest.pattern)}",
        f"As of: {manifest.as_of}",
        f"Config dir: {_table_cell(manifest.config_dir)}",
        f"Data dir: {_table_cell(manifest.data_dir)}",
        f"Source name: {_table_cell(manifest.source_name)}",
        f"Suggested filename: {_table_cell(manifest.suggested_filename)}",
        f"Matched file rule: {_table_cell(manifest.matched_file_rule)}",
        f"Manifest storage note: {_table_cell(manifest.manifest_storage_note)}",
        f"Producer profile command: {_table_cell(manifest.producer_profile_command)}",
        f"Producer contract version: {manifest.producer_contract_version}",
        f"Supported input formats: {', '.join(manifest.supported_input_formats)}",
        f"Schema path: {manifest.schema_path}",
        f"Example paths: {', '.join(manifest.example_paths)}",
        f"CSV header: {', '.join(manifest.csv_header)}",
        f"Required fields: {', '.join(manifest.required_fields)}",
        f"Optional fields: {', '.join(manifest.optional_fields)}",
        f"Prohibited fields: {', '.join(manifest.prohibited_fields)}",
        f"JSON envelopes: {', '.join(manifest.json_envelopes)}",
        (
            f"Source weight: >"
            f"{manifest.field_rules['source_weight']['exclusive_minimum']:g} "
            f"and <={manifest.field_rules['source_weight']['maximum']:g}, default "
            f"{manifest.field_rules['source_weight']['default']:g}"
        ),
        f"Unsupported capabilities: {', '.join(manifest.unsupported_capabilities)}",
        f"Workflow steps: {manifest.workflow.step_count}",
        "Order | Step | Suggested Effect | Purpose | Command",
    ]
    for step in manifest.workflow.steps:
        lines.append(
            f"{step.order} | {_table_cell(step.name)} | {step.suggested_effect} | "
            f"{_table_cell(step.purpose)} | {_table_cell(step.command)}"
        )
    lines.append("Boundaries:")
    for boundary in manifest.boundaries:
        lines.append(f"- {_table_cell(boundary)}")
    return lines


def _suggested_filename(input_format: ManualSignalFormat) -> str:
    return f"community-signals.{input_format}"


def _table_cell(value: str) -> str:
    sanitized = value.replace("|", "/").replace("\r", " ").replace("\n", " ")
    return " ".join(sanitized.split())
