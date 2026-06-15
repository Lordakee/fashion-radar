from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field

from fashion_radar.community_signals import (
    ALLOWED_COMMUNITY_SIGNAL_FIELDS,
    PROHIBITED_COMMUNITY_SIGNAL_FIELDS,
)

COMMUNITY_SIGNAL_CONTRACT_VERSION = "community-signals/v1"
COMMUNITY_SIGNAL_EXECUTION_MODE = "print_only"
COMMUNITY_SIGNAL_SCHEMA_PATH = "schemas/community-signals.schema.json"
COMMUNITY_SIGNAL_EXAMPLE_PATHS = [
    "examples/community-signals.example.csv",
    "examples/community-signals.example.json",
]
COMMUNITY_SIGNAL_CSV_HEADER = [
    "url",
    "title",
    "published_at",
    "summary",
    "source_name",
    "platform",
    "source_weight",
    "collected_at",
]
COMMUNITY_SIGNAL_REQUIRED_FIELDS = ["url", "title", "published_at"]
COMMUNITY_SIGNAL_JSON_ENVELOPES = ["top_level_array", "object_with_items_only"]
COMMUNITY_SIGNAL_UNSUPPORTED_CAPABILITIES = [
    "scraping",
    "browser_automation",
    "account_login",
    "cookies_sessions",
    "platform_api",
    "compliance_review",
    "source_acquisition",
    "media_download",
    "watching_monitoring",
    "scheduling",
]


class CommunitySignalProducerProfile(BaseModel):
    model_config = ConfigDict(extra="forbid")

    contract_version: str
    execution_mode: str
    schema_path: str
    example_paths: list[str]
    supported_input_formats: list[str]
    csv_header: list[str]
    required_fields: list[str]
    optional_fields: list[str]
    allowed_fields: list[str]
    prohibited_fields: list[str]
    json_envelopes: list[str]
    field_notes: dict[str, str] = Field(default_factory=dict)
    field_rules: dict[str, dict[str, int | float]] = Field(default_factory=dict)
    unsupported_capabilities: list[str]
    recommended_commands: list[str]
    boundaries: list[str]


def build_community_signal_profile() -> CommunitySignalProducerProfile:
    allowed_fields = _ordered_allowed_fields()
    return CommunitySignalProducerProfile(
        contract_version=COMMUNITY_SIGNAL_CONTRACT_VERSION,
        execution_mode=COMMUNITY_SIGNAL_EXECUTION_MODE,
        schema_path=COMMUNITY_SIGNAL_SCHEMA_PATH,
        example_paths=[*COMMUNITY_SIGNAL_EXAMPLE_PATHS],
        supported_input_formats=["csv", "json"],
        csv_header=[*COMMUNITY_SIGNAL_CSV_HEADER],
        required_fields=[*COMMUNITY_SIGNAL_REQUIRED_FIELDS],
        optional_fields=[
            field for field in allowed_fields if field not in COMMUNITY_SIGNAL_REQUIRED_FIELDS
        ],
        allowed_fields=allowed_fields,
        prohibited_fields=sorted(PROHIBITED_COMMUNITY_SIGNAL_FIELDS),
        json_envelopes=[*COMMUNITY_SIGNAL_JSON_ENVELOPES],
        field_notes={
            "url": "Source URL or stable reference URL for the observed item.",
            "title": "Short observed text, headline, or normalized signal phrase.",
            "published_at": "ISO 8601-compatible publication or observation timestamp.",
            "summary": "Short sanitized note for local review.",
            "source_name": (
                "Display name for the external tool or local export; import commands can "
                "supply a fallback when omitted."
            ),
            "platform": (
                "Short local provenance label; not platform coverage, source acquisition, "
                "demand proof, or source ranking."
            ),
            "source_weight": (
                "Local score weight accepted in the range (0, 5]; importer default is 1.0 "
                "when omitted or blank."
            ),
            "collected_at": (
                "Timestamp for when the external tool produced the row; importer may use "
                "the import timestamp when omitted."
            ),
        },
        field_rules={
            "source_weight": {
                "exclusive_minimum": 0,
                "maximum": 5,
                "default": 1.0,
            }
        },
        unsupported_capabilities=[*COMMUNITY_SIGNAL_UNSUPPORTED_CAPABILITIES],
        recommended_commands=[
            (
                "fashion-radar community-signal-lint-dir ./exports --input-format csv "
                '--pattern "*.csv" --source-name "Community Tool Export" --strict'
            ),
            (
                "fashion-radar community-candidates-dir ./exports --input-format csv "
                '--pattern "*.csv" --config-dir "$PWD/configs" --as-of "$AS_OF" '
                '--source-name "Community Tool Export"'
            ),
            (
                "fashion-radar import-signals-dir ./exports --format csv --pattern "
                '"*.csv" --source-name "Community Tool Export" --data-dir "$PWD/data" '
                "--dry-run"
            ),
            (
                "fashion-radar import-signals-dir ./exports --format csv --pattern "
                '"*.csv" --source-name "Community Tool Export" --imported-at "$AS_OF" '
                '--data-dir "$PWD/data"'
            ),
            (
                'fashion-radar imported-review-workflow --data-dir "$PWD/data" '
                '--config-dir "$PWD/configs" --as-of "$AS_OF" '
                '--source-name "Community Tool Export"'
            ),
        ],
        boundaries=[
            "Prints the local handoff contract only.",
            "Does not read handoff files or directories.",
            "Does not create config, data, report, dashboard, or SQLite artifacts.",
            (
                "Does not fetch URLs, search platforms, log in, store cookies, automate "
                "browsers, call platform APIs, monitor communities, rank sources, or verify "
                "platform coverage."
            ),
            "Does not provide a compliance-review workflow.",
        ],
    )


def render_community_signal_profile_table(
    profile: CommunitySignalProducerProfile,
) -> list[str]:
    source_weight_rules = profile.field_rules["source_weight"]
    lines = [
        "Community signal producer profile",
        f"Contract version: {profile.contract_version}",
        f"Execution mode: {profile.execution_mode}",
        f"Schema path: {profile.schema_path}",
        f"Example paths: {', '.join(profile.example_paths)}",
        f"Supported input formats: {', '.join(profile.supported_input_formats)}",
        f"CSV header: {', '.join(profile.csv_header)}",
        f"Required fields: {', '.join(profile.required_fields)}",
        f"Optional fields: {', '.join(profile.optional_fields)}",
        f"Allowed fields: {', '.join(profile.allowed_fields)}",
        f"Prohibited fields: {', '.join(profile.prohibited_fields)}",
        f"JSON envelopes: {', '.join(profile.json_envelopes)}",
        (
            f"Source weight: >{source_weight_rules['exclusive_minimum']:g} and "
            f"<={source_weight_rules['maximum']:g}, default "
            f"{source_weight_rules['default']:g}"
        ),
        f"Unsupported capabilities: {', '.join(profile.unsupported_capabilities)}",
        "Field notes:",
    ]
    for field, note in profile.field_notes.items():
        lines.append(f"- {field}: {note}")
    lines.append("Recommended commands:")
    for command in profile.recommended_commands:
        lines.append(f"- {command}")
    lines.append("Boundaries:")
    for boundary in profile.boundaries:
        lines.append(f"- {boundary}")
    return lines


def _ordered_allowed_fields() -> list[str]:
    header_fields = set(COMMUNITY_SIGNAL_CSV_HEADER)
    missing = header_fields - ALLOWED_COMMUNITY_SIGNAL_FIELDS
    extra = ALLOWED_COMMUNITY_SIGNAL_FIELDS - header_fields
    if missing or extra:
        raise ValueError("Community signal profile fields differ from lint contract.")
    return [*COMMUNITY_SIGNAL_CSV_HEADER]
