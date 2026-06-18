# Stage 85 Suggested Platform Labels Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add advisory `suggested_platform_labels` to the local producer profile
and directory handoff manifest, with adapter parity and docs drift coverage,
without adding platform collection, schema restrictions, or import/lint changes.

**Architecture:** The producer profile remains the source of truth for local
handoff guidance. The directory manifest copies profile guidance for directory
producers. Adapter parity tests ensure every current adapter `platform_label`
appears in the advisory label list, while importable rows and schema behavior
stay unchanged.

**Tech Stack:** Python/Pydantic models, pytest, Markdown docs, uv, Ruff.

---

## File Map

- Modify `src/fashion_radar/community_signal_profile.py`.
- Modify `src/fashion_radar/community_handoff_manifest.py`.
- Modify `examples/community-signal-profile.example.json`.
- Modify `tests/test_community_signal_profile.py`.
- Modify `tests/test_community_handoff_manifest.py`.
- Modify `tests/test_external_tool_contract_parity.py`.
- Modify `tests/test_cli.py`.
- Modify `tests/test_cli_docs.py`.
- Modify `docs/community-signal-import.md`.
- Modify `docs/community-signal-quality.md`.
- Add Stage 85 review artifacts under `docs/reviews/`.

Do not modify `schemas/community-signals.schema.json`, import/lint behavior,
adapter/template/workflow/readiness command generation, dependency manifests,
`uv.lock`, CI workflows, `AGENTS.md`, or `docs/REVIEW_PROTOCOL.md`.

## Task 1: Plan Review

- [ ] Create `docs/reviews/opencode-stage-85-plan-review-prompt.md`.
- [ ] Run local opencode plan review:

```bash
opencode run --model zhipuai-coding-plan/glm-5.2 --variant max --dir /home/ubuntu/fashion-radar "$(cat docs/reviews/opencode-stage-85-plan-review-prompt.md)" > docs/reviews/opencode-stage-85-plan-review.md
```

- [ ] Fix Critical or Important findings before implementation.

## Task 2: Add Profile Suggested Labels

- [ ] In `src/fashion_radar/community_signal_profile.py`, add this constant
  near the other `COMMUNITY_SIGNAL_*` constants:

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

- [ ] Add `suggested_platform_labels: list[str]` to
  `CommunitySignalProducerProfile` immediately after `json_envelopes`.
- [ ] In `build_community_signal_profile()`, pass
  `suggested_platform_labels=[*COMMUNITY_SIGNAL_SUGGESTED_PLATFORM_LABELS]`
  immediately after `json_envelopes=[*COMMUNITY_SIGNAL_JSON_ENVELOPES]`.
- [ ] In `render_community_signal_profile_table()`, add this line immediately
  after the `JSON envelopes` line:

```python
f"Suggested platform labels: {', '.join(profile.suggested_platform_labels)}",
```

## Task 3: Add Manifest Suggested Labels

- [ ] In `src/fashion_radar/community_handoff_manifest.py`, add
  `suggested_platform_labels: list[str]` to `CommunityHandoffManifest`
  immediately after `supported_input_formats`.
- [ ] In `build_community_handoff_manifest()`, pass
  `suggested_platform_labels=[*profile.suggested_platform_labels]`
  immediately after `supported_input_formats=[*profile.supported_input_formats]`.
- [ ] In `render_community_handoff_manifest_table()`, add this line immediately
  after `Supported input formats`:

```python
f"Suggested platform labels: {', '.join(manifest.suggested_platform_labels)}",
```

## Task 4: Update Profile Tests And Example JSON

- [ ] In `tests/test_community_signal_profile.py`, import
  `COMMUNITY_SIGNAL_SUGGESTED_PLATFORM_LABELS` from
  `fashion_radar.community_signal_profile`.
- [ ] In `test_profile_contract_matches_schema_csv_header_and_constants`, add:

```python
assert profile.suggested_platform_labels == COMMUNITY_SIGNAL_SUGGESTED_PLATFORM_LABELS
assert "suggested_platform_labels" not in profile.allowed_fields
```

- [ ] In `test_profile_has_stable_json_key_order`, insert
  `"suggested_platform_labels"` immediately after `"json_envelopes"`.
- [ ] In `test_profile_table_includes_contract_commands_and_boundaries`, add:

```python
assert (
    "Suggested platform labels: rednote, xiaohongshu, instagram, tiktok, media, x, community"
    in text
)
```

immediately after the existing JSON envelopes assertion.

- [ ] Regenerate `examples/community-signal-profile.example.json`:

```bash
uv --no-config run --frozen python - <<'PY'
from pathlib import Path

from fashion_radar.community_signal_profile import build_community_signal_profile

Path("examples/community-signal-profile.example.json").write_text(
    build_community_signal_profile().model_dump_json(indent=2) + "\n",
    encoding="utf-8",
)
PY
```

## Task 5: Update Manifest Tests

- [ ] In `tests/test_community_handoff_manifest.py`, import
  `build_community_signal_profile`.
- [ ] In `test_build_community_handoff_manifest_has_stable_directory_contract`,
  set `profile = build_community_signal_profile()` before assertions.
- [ ] In the expected key order, insert `"suggested_platform_labels"`
  immediately after `"supported_input_formats"`.
- [ ] Add:

```python
assert manifest.suggested_platform_labels == profile.suggested_platform_labels
```

immediately after the existing supported input formats assertion.

- [ ] In `test_render_community_handoff_manifest_table_sanitizes_cells`, pass
  `suggested_platform_labels=["community", "x"]` when constructing
  `CommunityHandoffManifest`.
- [ ] Add `"Suggested platform labels: community, x"` to the expected rendered
  table immediately after `"Supported input formats: csv, json"`.

## Task 6: Add Adapter Parity Guard

- [ ] In `tests/test_external_tool_contract_parity.py`, update
  `test_every_adapter_field_mapping_matches_community_signal_profile` so each
  adapter also asserts:

```python
assert adapter.platform_label in profile.suggested_platform_labels
```

- [ ] After the adapter loop, add:

```python
assert "suggested_platform_labels" not in profile.allowed_fields
assert "suggested_platform_labels" not in set(profile.csv_header)
```

This verifies labels are advisory metadata, not importable row fields.

## Task 7: Update CLI JSON Key-Order Tests

- [ ] In `tests/test_cli.py`, update
  `test_community_signal_profile_prints_json` so the expected payload key list
  includes `"suggested_platform_labels"` immediately after `"json_envelopes"`.
- [ ] In the same test, add:

```python
assert payload["suggested_platform_labels"] == [
    "rednote",
    "xiaohongshu",
    "instagram",
    "tiktok",
    "media",
    "x",
    "community",
]
```

immediately after the supported input formats assertion.

- [ ] In the `community-handoff-manifest --format json` CLI test, insert
  `"suggested_platform_labels"` immediately after `"supported_input_formats"`
  in the expected payload key list.
- [ ] In that manifest CLI test, add:

```python
assert payload["suggested_platform_labels"] == [
    "rednote",
    "xiaohongshu",
    "instagram",
    "tiktok",
    "media",
    "x",
    "community",
]
```

immediately after the supported input formats assertion.

## Task 8: Update Docs And Docs Drift Tests

- [ ] In `docs/community-signal-import.md`, update the Producer Profile prose to
  mention `suggested_platform_labels` as advisory local provenance label
  guidance for the optional `platform` field.
- [ ] Add this exact advisory sentence to `docs/community-signal-import.md`:

```markdown
`suggested_platform_labels` is advisory local provenance label guidance for
the optional handoff `platform` field. It is not a schema enum, not a linter
restriction, not platform coverage, and not demand proof.
```

- [ ] In the Directory Manifest JSON example in
  `docs/community-signal-import.md`, add:

```json
"suggested_platform_labels": ["rednote", "xiaohongshu", "instagram", "tiktok", "media", "x", "community"],
```

immediately after `"supported_input_formats": ["csv", "json"],`.

- [ ] In the manifest prose, mention that the manifest includes advisory
  `suggested_platform_labels`.
- [ ] In the optional `platform` field bullet, add that the labels can help
  producers choose the local value but do not make `platform` required.
- [ ] In `docs/community-signal-quality.md`, add one paragraph near the producer
  contract guidance:

```markdown
`suggested_platform_labels` is advisory local provenance label guidance for
the optional handoff `platform` field. It is not a schema enum, not a linter
restriction, not platform coverage, and not demand proof.
```

- [ ] In `tests/test_cli_docs.py`, extend
  `test_community_signal_profile_docs_are_linked` to assert
  `community-signal-import.md` and `community-signal-quality.md` include:

```python
for term in (
    "suggested_platform_labels",
    "advisory local provenance label guidance",
    "optional handoff `platform` field",
    "not a schema enum",
    "not a linter restriction",
    "not platform coverage",
    "not demand proof",
):
    assert term in import_doc
    assert term in quality_doc
```

## Task 9: Focused Verification

Run:

```bash
uv --no-config run --frozen pytest tests/test_community_signal_profile.py -q
uv --no-config run --frozen pytest tests/test_community_handoff_manifest.py -q
uv --no-config run --frozen pytest tests/test_external_tool_contract_parity.py -q
uv --no-config run --frozen pytest tests/test_cli.py::test_community_signal_profile_prints_json -q
uv --no-config run --frozen pytest tests/test_cli.py::test_community_handoff_manifest_command_prints_json_with_stable_keys -q
uv --no-config run --frozen pytest tests/test_cli_docs.py::test_community_signal_profile_docs_are_linked -q
uv --no-config run --frozen pytest tests/test_cli.py -q
uv --no-config run --frozen pytest tests/test_cli_docs.py -q
uv --no-config run --frozen ruff check src/fashion_radar/community_signal_profile.py src/fashion_radar/community_handoff_manifest.py tests/test_community_signal_profile.py tests/test_community_handoff_manifest.py tests/test_external_tool_contract_parity.py tests/test_cli.py tests/test_cli_docs.py
uv --no-config run --frozen ruff format --check src/fashion_radar/community_signal_profile.py src/fashion_radar/community_handoff_manifest.py tests/test_community_signal_profile.py tests/test_community_handoff_manifest.py tests/test_external_tool_contract_parity.py tests/test_cli.py tests/test_cli_docs.py
git diff --check -- src/fashion_radar/community_signal_profile.py src/fashion_radar/community_handoff_manifest.py examples/community-signal-profile.example.json tests/test_community_signal_profile.py tests/test_community_handoff_manifest.py tests/test_external_tool_contract_parity.py tests/test_cli.py tests/test_cli_docs.py docs/community-signal-import.md docs/community-signal-quality.md
```

## Task 10: Code Review And Full Verification

- [ ] Create `docs/reviews/opencode-stage-85-code-review-prompt.md`.
- [ ] Run local opencode code review:

```bash
opencode run --model zhipuai-coding-plan/glm-5.2 --variant max --dir /home/ubuntu/fashion-radar "$(cat docs/reviews/opencode-stage-85-code-review-prompt.md)" > docs/reviews/opencode-stage-85-code-review.md
```

- [ ] Fix Critical or Important findings.
- [ ] Run full verification:

```bash
uv --no-config run --frozen python scripts/check_release_hygiene.py
env -u ALL_PROXY -u all_proxy uv --no-config run --frozen pytest
uv --no-config run --frozen ruff check .
uv --no-config run --frozen ruff format --check .
UV_NO_CONFIG=1 uv lock --check
! rg -n 'tuna|aliyun|ustc|huaweicloud|mirror|index-url|extra-index-url|find-links' uv.lock
git diff --exit-code -- uv.lock pyproject.toml
git diff --check
```

`env -u ALL_PROXY -u all_proxy` avoids the current local SOCKS proxy inherited
by `httpx` tests; it does not change project dependencies or behavior.

## Task 11: Commit And Publish

- [ ] Stage only Stage 85 files:

```bash
git add -- \
  src/fashion_radar/community_signal_profile.py \
  src/fashion_radar/community_handoff_manifest.py \
  examples/community-signal-profile.example.json \
  tests/test_community_signal_profile.py \
  tests/test_community_handoff_manifest.py \
  tests/test_external_tool_contract_parity.py \
  tests/test_cli.py \
  tests/test_cli_docs.py \
  docs/community-signal-import.md \
  docs/community-signal-quality.md \
  docs/superpowers/specs/2026-06-18-stage-85-suggested-platform-labels-design.md \
  docs/superpowers/plans/2026-06-18-stage-85-suggested-platform-labels-plan.md \
  docs/reviews/opencode-stage-85-plan-review-prompt.md \
  docs/reviews/opencode-stage-85-plan-review.md \
  docs/reviews/opencode-stage-85-code-review-prompt.md \
  docs/reviews/opencode-stage-85-code-review.md
```

- [ ] Confirm `uv.lock` is not staged.
- [ ] Run staged release hygiene, whitespace check, and secret scan.
- [ ] Commit with message `Add suggested platform label guidance`.
- [ ] Push safely without persisting credentials.
- [ ] Verify local/remote `main` alignment, GitHub Actions success, clean
  worktree, mirror-free `uv.lock`, and no token/extraheader in git config.
