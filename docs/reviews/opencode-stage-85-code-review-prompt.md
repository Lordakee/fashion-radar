# Stage 85 Code Review Prompt

Review the Stage 85 implementation in `/home/ubuntu/fashion-radar`.

Use model `zhipuai-coding-plan/glm-5.2` with variant `max`.

## Goal

Stage 85 adds advisory `suggested_platform_labels` to the local producer
profile and directory handoff manifest so future user-controlled
external/community tools can choose stable local provenance labels for
sanitized handoff rows.

## Intended Scope

Allowed changed files:

- `src/fashion_radar/community_signal_profile.py`
- `src/fashion_radar/community_handoff_manifest.py`
- `examples/community-signal-profile.example.json`
- `tests/test_community_signal_profile.py`
- `tests/test_community_handoff_manifest.py`
- `tests/test_external_tool_contract_parity.py`
- `tests/test_cli.py`
- `tests/test_cli_docs.py`
- `docs/community-signal-import.md`
- `docs/community-signal-quality.md`
- Stage 85 spec/plan/review artifacts under `docs/superpowers/` and
  `docs/reviews/`

Out of scope:

- `schemas/community-signals.schema.json`
- community signal lint/import behavior
- external adapter/template/workflow/readiness command generation
- dependency manifests
- `uv.lock`
- CI workflows
- `AGENTS.md`
- `docs/REVIEW_PROTOCOL.md`

## Requirements

- `CommunitySignalProducerProfile` exposes
  `suggested_platform_labels` immediately after `json_envelopes`.
- `CommunityHandoffManifest` exposes `suggested_platform_labels` immediately
  after `supported_input_formats` and copies it from the profile.
- The exact advisory label list is:
  `rednote`, `xiaohongshu`, `instagram`, `tiktok`, `media`, `x`,
  `community`.
- The deterministic profile example JSON is regenerated from
  `build_community_signal_profile().model_dump_json(indent=2) + "\n"`.
- Tests cover model key order, CLI JSON key order, manifest/profile table
  output, adapter `platform_label` parity, and docs drift.
- `suggested_platform_labels` must remain advisory metadata only:
  it must not be added to schema fields, CSV header, allowed row fields, lint
  behavior, import behavior, or template JSON/CSV handoff rows.
- Docs must avoid wording that implies supported platforms, official platform
  integrations, coverage verification, demand proof, scraping, connectors,
  platform APIs, login/session/token handling, monitoring, or compliance-review
  product behavior.

## Review Instructions

Return findings first, ordered by severity. Classify each finding as Critical,
Important, or Minor. Include file and line references. If there are no
Critical or Important findings, say that explicitly.
