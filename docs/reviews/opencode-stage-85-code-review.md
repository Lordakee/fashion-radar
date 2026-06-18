I'll review the Stage 85 implementation. Let me start by examining the changed files and verifying the requirements.
Now let me verify the boundary constraints — that `suggested_platform_labels` does NOT leak into schema, CSV header, lint, import, or template rows.
Let me verify the example JSON is genuinely regenerated from the model, and run the test suite.
Let me check the full profile/manifest table test details and verify the adapter parity test context.
Let me verify the adapter `platform_label` values exactly match the 7 suggested labels (to confirm parity test isn't trivially passing).
Let me read the full doc sections to check for forbidden wording (supported platforms, official integration, coverage, scraping, connectors, etc.).
Let me run the broader test suite to confirm no regressions beyond the directly changed test files.
## Stage 85 Code Review Findings

The 4 failures in the full-suite run (`test_collectors_runner.py`, `test_workflows.py`) are pre-existing environment issues (`ImportError: socksio not installed` for a SOCKS proxy) in collector/HTTP code that Stage 85 does not touch. All **378 Stage-85-relevant tests pass**.

### No Critical findings
### No Important findings

### Minor

1. **Parity check is subset, not equality** — `tests/test_external_tool_contract_parity.py:97` asserts `adapter.platform_label in profile.suggested_platform_labels` (per-adapter membership). A future advisory label added to the profile that no adapter references would pass silently. Today all 7 adapters match the 7 labels exactly (verified at runtime), so this is acceptable as an intentional "advisory superset" design, but worth noting if exact drift detection is desired later.

2. **Boundary assertion is partial** — `tests/test_community_signal_profile.py:77` and `test_external_tool_contract_parity.py:99-100` assert `suggested_platform_labels` is absent from `allowed_fields` and `csv_header`. They do not assert absence from `prohibited_fields` or schema `properties`. The schema file is unchanged and out of scope (verified `schemas/community-signals.schema.json` has no `enum` and no such key via grep), so the boundary holds; the test coverage is just narrower than the prose boundary.

### Verification performed

- **Field placement**: `CommunitySignalProducerProfile.suggested_platform_labels` is immediately after `json_envelopes` (`community_signal_profile.py:76-77`); `CommunityHandoffManifest.suggested_platform_labels` is immediately after `supported_input_formats` (`community_handoff_manifest.py:59-60`).
- **Manifest sourcing**: copied via `[*profile.suggested_platform_labels]` (`community_handoff_manifest.py:112`); test asserts equality against profile (`test_community_handoff_manifest.py:80`).
- **Exact label list** matches `rednote, xiaohongshu, instagram, tiktok, media, x, community` (`community_signal_profile.py:39-47`).
- **Example JSON regeneration**: byte-identical to `build_community_signal_profile().model_dump_json(indent=2) + "\n"` (verified `MATCH: True`).
- **Advisory-only boundary**: grep confirms `suggested_platform_labels` appears only in profile/manifest source, the two docs, the example JSON, tests, and review artifacts — *not* in the schema, `community_signals.py` (lint/import), templates, CSV header, or row fields.
- **Adapter parity**: all 7 `adapter.platform_label` values exactly equal the 7 suggested labels.
- **Key-order tests**: profile model keys (`test_community_signal_profile.py:117-136`), CLI JSON keys (`test_cli.py:505-517`, `5124-5145`), and manifest model/CLI keys (`test_community_handoff_manifest.py`, `test_cli.py:5128-5150`) all place the new key in the required position.
- **Table output**: profile and manifest renderers emit `Suggested platform labels: ...` lines (`community_signal_profile.py:191`, `community_handoff_manifest.py:153`), with sanitization preserved in the manifest table test.
- **Docs drift**: `test_cli_docs.py:1245-1255` asserts all seven required phrases appear in both docs; verified present with correct advisory framing and no forbidden wording (no "supported platforms", "official integration", "coverage", "scraping", "connectors", "platform APIs", "login/session/token", "monitoring", or "compliance-review product" language introduced).
- **Scope**: exactly the 10 allowed files are modified; untracked spec/plan/review artifacts live under `docs/superpowers/` and `docs/reviews/`. No out-of-scope file touched.

Implementation is clean, correctly scoped, and meets all stated requirements.
