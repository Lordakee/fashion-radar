# Stage 88 Suggested Platform Label Boundary Tests Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Harden tests proving `suggested_platform_labels` remains advisory
producer metadata, not row data, schema validation, or template output.

**Architecture:** This is a test-only boundary hardening. Existing source,
schema, docs, template, import, and lint behavior already have the intended
shape; Stage 88 adds focused assertions around that behavior without changing
runtime code.

**Tech Stack:** pytest, JSON Schema fixture inspection, structured CSV parsing,
Markdown docs tests, uv, Ruff.

---

## File Map

- Modify `tests/test_community_signal_profile.py`.
- Modify `tests/test_external_tool_contract_parity.py`.
- Modify `tests/test_cli_docs.py`.
- Add Stage 88 review artifacts under `docs/reviews/`.

Do not modify `src/`, schemas, docs content, lint/import behavior, adapter
command behavior, dependency manifests, `uv.lock`, CI workflows, `AGENTS.md`,
or `docs/REVIEW_PROTOCOL.md`.

## Task 1: Plan Review

- [ ] Create `docs/reviews/opencode-stage-88-plan-review-prompt.md`.
- [ ] Run local opencode plan review:

```bash
opencode run --model zhipuai-coding-plan/glm-5.2 --variant max --dir /home/ubuntu/fashion-radar "$(cat docs/reviews/opencode-stage-88-plan-review-prompt.md)" > docs/reviews/opencode-stage-88-plan-review.md
```

- [ ] Fix Critical or Important findings before implementation.

## Task 2: Harden Profile And Schema Boundary Assertions

- [ ] In `tests/test_community_signal_profile.py`,
  `test_profile_contract_matches_schema_csv_header_and_constants`, immediately
  after:

```python
assert profile.suggested_platform_labels == COMMUNITY_SIGNAL_SUGGESTED_PLATFORM_LABELS
assert "suggested_platform_labels" not in profile.allowed_fields
```

add:

```python
assert "suggested_platform_labels" not in profile.required_fields
assert "suggested_platform_labels" not in profile.optional_fields
assert "suggested_platform_labels" not in profile.prohibited_fields
assert "suggested_platform_labels" not in signal["properties"]

platform_schema = signal["properties"]["platform"]
assert platform_schema["type"] == "string"
assert "enum" not in platform_schema
assert "const" not in platform_schema
```

## Task 3: Harden Template Output Boundary Assertions

- [ ] In `tests/test_external_tool_contract_parity.py`, add imports:

```python
import csv
import io
```

above the existing `import json`.

- [ ] In `test_every_template_json_and_csv_output_lints_cleanly`, immediately
  after:

```python
assert all(set(item) == profile_fields for item in payload["items"])
```

add:

```python
assert all("suggested_platform_labels" not in item for item in payload["items"])
```

- [ ] Before writing the CSV file, replace:

```python
csv_path.write_text(render_external_tool_template_csv(template), encoding="utf-8")
```

with:

```python
csv_text = render_external_tool_template_csv(template)
csv_header = next(csv.reader(io.StringIO(csv_text)))
assert "suggested_platform_labels" not in csv_header
csv_path.write_text(csv_text, encoding="utf-8")
```

## Task 4: Add Optional Platform Field Docs Boundary Test

- [ ] In `tests/test_cli_docs.py`, add this focused test immediately after
  `test_community_signal_profile_docs_are_linked`:

```python
def test_community_signal_import_platform_field_keeps_suggested_labels_advisory() -> None:
    section = _markdown_section_exact_heading(
        _read(COMMUNITY_SIGNAL_IMPORT_DOC),
        "Optional Fields",
    )
    normalized = _normalized_text(section).casefold()

    for term in (
        "`platform`: short local provenance label",
        "not platform coverage",
        "source acquisition",
        "demand proof",
        "claim of complete platform/community visibility",
        "suggested_platform_labels",
        "advisory metadata only",
        "do not make `platform` required",
    ):
        assert term.casefold() in normalized
```

## Task 5: Focused Verification And Review

- [ ] Run:

```bash
uv --no-config run --frozen pytest \
  tests/test_community_signal_profile.py::test_profile_contract_matches_schema_csv_header_and_constants \
  tests/test_external_tool_contract_parity.py::test_every_template_json_and_csv_output_lints_cleanly \
  tests/test_cli_docs.py::test_community_signal_import_platform_field_keeps_suggested_labels_advisory \
  -q
uv --no-config run --frozen pytest \
  tests/test_community_signal_profile.py \
  tests/test_external_tool_contract_parity.py \
  tests/test_cli_docs.py \
  -q
uv --no-config run --frozen ruff check \
  tests/test_community_signal_profile.py \
  tests/test_external_tool_contract_parity.py \
  tests/test_cli_docs.py
```

- [ ] Create `docs/reviews/opencode-stage-88-code-review-prompt.md`.
- [ ] Run local opencode code review:

```bash
opencode run --model zhipuai-coding-plan/glm-5.2 --variant max --dir /home/ubuntu/fashion-radar "$(cat docs/reviews/opencode-stage-88-code-review-prompt.md)" > docs/reviews/opencode-stage-88-code-review.md
```

- [ ] Fix Critical or Important findings before final verification.

## Task 6: Full Verification, Commit, Push

- [ ] Run:

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

- [ ] Stage only Stage 88 files and run staged hygiene checks:

```bash
! git diff --cached --name-only | rg -x 'uv.lock'
uv --no-config run --frozen python scripts/check_release_hygiene.py --repo-root .
git diff --cached --check
git grep --cached -n -E 'gh[pousr]_[A-Za-z0-9]{36,255}|github_pat_[A-Za-z0-9_]{82,255}|-----BEGIN [A-Z0-9 ]*PRIVATE KEY-----' -- . ':!uv.lock' && exit 1 || true
```

- [ ] Commit with:

```bash
git commit -m "Harden suggested platform label boundaries"
```

- [ ] Push with the stored token via temporary git extraheader only.
- [ ] Verify GitHub Actions completes successfully.
