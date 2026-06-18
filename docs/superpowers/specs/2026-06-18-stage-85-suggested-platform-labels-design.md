# Stage 85 Suggested Platform Labels Design

## Goal

Expose advisory `suggested_platform_labels` in the local producer profile and
directory handoff manifest so future user-controlled external/community tools
can choose stable local provenance labels for Xiaohongshu/Instagram/TikTok/X
style handoff rows without adding scraping, connectors, platform APIs, or
stricter validation.

## Scope

Modify:

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
- Stage 85 spec/plan/review artifacts

Do not modify:

- `schemas/community-signals.schema.json`
- community signal lint/import behavior
- external adapter/template/workflow/readiness command generation
- dependency manifests or `uv.lock`
- CI workflows
- `AGENTS.md`
- `docs/REVIEW_PROTOCOL.md`

## Labels

The advisory list is:

```python
["rednote", "xiaohongshu", "instagram", "tiktok", "media", "x", "community"]
```

The list intentionally covers every current adapter `platform_label`, including
both `rednote` and `xiaohongshu`.

## Design

Add a profile constant in `community_signal_profile.py`:

```python
COMMUNITY_SIGNAL_SUGGESTED_PLATFORM_LABELS = [
    "rednote",
    "xiaohongshu",
    "instagram",
    "tiktok",
    "media",
    "x",
    "community",
]
```

Add `suggested_platform_labels: list[str]` to
`CommunitySignalProducerProfile` immediately after `json_envelopes`. Populate
it from the constant in `build_community_signal_profile()` and render it in the
table immediately after `JSON envelopes`.

Add `suggested_platform_labels: list[str]` to `CommunityHandoffManifest`
immediately after `supported_input_formats`, copy it from the profile, and
render it in the manifest table after `Supported input formats`.

Update `examples/community-signal-profile.example.json` by regenerating it from
`build_community_signal_profile().model_dump_json(indent=2) + "\n"`.

## Tests

Profile tests should assert:

- Stable key order includes `suggested_platform_labels` after
  `json_envelopes`.
- Profile labels equal the exact list above.
- The table renderer includes the exact label list.
- The deterministic example JSON matches the generated profile.

Manifest tests should assert:

- Stable key order includes `suggested_platform_labels` after
  `supported_input_formats`.
- Manifest labels equal `build_community_signal_profile().suggested_platform_labels`.
- The table renderer includes the exact label list.

CLI JSON tests should update the parallel profile and manifest key-order
assertions so installed CLI output reflects the new field order.

External adapter parity should assert every adapter `platform_label` is present
in the profile `suggested_platform_labels` list. It should also assert
`suggested_platform_labels` is not an importable community signal row field.

Docs tests should pin that `community-signal-import.md` and
`community-signal-quality.md` describe:

- `suggested_platform_labels`
- advisory local provenance label guidance
- optional handoff `platform` field
- not a schema enum
- not a linter restriction
- no schema enum or linter restriction
- not platform coverage
- not demand proof

## Boundaries

`suggested_platform_labels` is advisory producer guidance only.

It is not:

- a JSON schema enum
- an allowed CSV/JSON row field
- an import or lint restriction
- a platform support guarantee
- source acquisition
- platform coverage verification
- demand proof
- source ranking
- a compliance-review product feature

The optional `platform` row field remains local provenance metadata only.
