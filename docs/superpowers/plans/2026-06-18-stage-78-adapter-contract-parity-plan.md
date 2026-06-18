# Stage 78 Adapter Contract Parity Gate Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a test/docs-only parity gate proving external/community adapter metadata, template models, workflow commands, and readiness guidance stay aligned with the community signal handoff contract.

**Architecture:** Add one focused pytest module that uses public builders and rendered template outputs to compare adapter surfaces across all known adapters. Add a short docs subsection and docs drift test so the guarantee remains visible without changing runtime behavior.

**Tech Stack:** Python 3.11, pytest, pathlib, shlex, json, uv, ruff, Markdown.

**Review Protocol Note:** The current stage-local review instruction is to use
local opencode with `opencode run --model zhipuai-coding-plan/glm-5.2 --variant
max`. Public `uv.lock` must remain free of mirror-bound URLs per `AGENTS.md`;
the pre-existing local `uv.lock` mirror rewrite is not part of this stage and
must not be staged.

---

## File Map

- Add `tests/test_external_tool_contract_parity.py`
  - Cross-surface parity tests using public builders only.
- Modify `tests/test_cli_docs.py`
  - Add docs drift coverage for the adapter parity subsection.
- Modify `docs/community-signal-import.md`
  - Document the local adapter parity guarantee.
- Modify `CHANGELOG.md`
  - Add Stage 78 entry.
- Create review artifacts:
  - `docs/reviews/opencode-stage-78-plan-review-prompt.md`
  - `docs/reviews/opencode-stage-78-plan-review.md`
  - `docs/reviews/opencode-stage-78-plan-rereview-prompt.md`
  - `docs/reviews/opencode-stage-78-plan-rereview.md`
  - `docs/reviews/opencode-stage-78-code-review-prompt.md`
  - `docs/reviews/opencode-stage-78-code-review.md`

## Task 1: Add Failing Adapter Contract Parity Tests

**Files:**
- Create: `tests/test_external_tool_contract_parity.py`

- [ ] **Step 1: Create the test module with shared fixtures and constants**

Create `tests/test_external_tool_contract_parity.py` with:

```python
from __future__ import annotations

import json
import shlex
from pathlib import Path

import pytest

from fashion_radar.community_signal_profile import build_community_signal_profile
from fashion_radar.community_signals import lint_community_signal_file
from fashion_radar.external_tool_adapters import (
    build_external_tool_adapter_registry,
)
from fashion_radar.external_tool_readiness import build_external_tool_readiness
from fashion_radar.external_tool_templates import (
    build_external_tool_template,
    render_external_tool_template_csv,
    render_external_tool_template_json,
)
from fashion_radar.external_tool_workflow import build_external_tool_workflow

DIRECTORY = Path("./exports")
CONFIG_DIR = Path("./configs")
DATA_DIR = Path("./data")
AS_OF = "2026-06-13T12:00:00Z"

EXPECTED_ADAPTER_IDS = [
    "rednote_mcp",
    "xiaohongshu_crawler",
    "instaloader",
    "tiktok_api",
    "yt_dlp",
    "x_search_export",
    "generic_community_export",
]

WORKFLOW_RECOMMENDED_COMMAND_STEPS = {
    "check_external_tool_readiness": 1,
    "print_signal_profile": 0,
    "print_handoff_manifest": 2,
    "print_handoff_workflow": 3,
    "lint_export_directory": 4,
    "review_handoff_readiness": 5,
    "dry_run_directory_import": 6,
    "import_directory_signals": 7,
    "print_post_import_review": 8,
}

READINESS_RECOMMENDED_COMMAND_STEPS = {
    "print_signal_profile": 0,
    "lint_export_directory": 4,
    "review_handoff_readiness": 5,
    "dry_run_directory_import": 6,
}

BANNED_COMMAND_TOKENS = {
    "api",
    "browser",
    "cookie",
    "crawl",
    "download",
    "login",
    "monitor",
    "playwright",
    "proxy",
    "schedule",
    "scrape",
    "session",
    "token",
    "watch",
}


@pytest.fixture(scope="module")
def registry():
    return build_external_tool_adapter_registry(
        directory=DIRECTORY,
        config_dir=CONFIG_DIR,
        data_dir=DATA_DIR,
        as_of=AS_OF,
    )
```

- [ ] **Step 2: Add field-mapping parity test**

Add:

```python
def test_every_adapter_field_mapping_matches_community_signal_profile(registry) -> None:
    profile = build_community_signal_profile()

    assert [adapter.id for adapter in registry.adapters] == EXPECTED_ADAPTER_IDS

    for adapter in registry.adapters:
        mappings = [mapping.model_dump(mode="json") for mapping in adapter.field_mappings]

        assert [mapping["field"] for mapping in mappings] == profile.allowed_fields
        assert {mapping["field"] for mapping in mappings if mapping["required"]} == set(
            profile.required_fields
        )
        assert all(mapping["note"].strip() for mapping in mappings)
```

- [ ] **Step 3: Add template metadata and command parity test**

Add:

```python
def test_every_template_model_mirrors_adapter_contract(registry) -> None:
    for adapter in registry.adapters:
        template = build_external_tool_template(
            adapter_id=adapter.id,
            directory=DIRECTORY,
            config_dir=CONFIG_DIR,
            data_dir=DATA_DIR,
            as_of=AS_OF,
        )

        assert template.adapter_id == adapter.id
        assert template.display_name == adapter.display_name
        assert template.platform_label == adapter.platform_label
        assert template.source_name == adapter.suggested_source_name
        assert template.recommended_input_format == adapter.recommended_input_format
        assert template.recommended_pattern == adapter.recommended_pattern
        assert template.suggested_export_directory == adapter.suggested_export_directory
        assert [mapping.field for mapping in template.field_mappings] == [
            mapping.field for mapping in adapter.field_mappings
        ]
        assert [mapping.model_dump(mode="json") for mapping in template.field_mappings] == [
            mapping.model_dump(mode="json") for mapping in adapter.field_mappings
        ]
        assert template.csv_header == [mapping.field for mapping in adapter.field_mappings]
        assert template.recommended_commands == adapter.recommended_commands
```

- [ ] **Step 4: Add all-adapter template lint test**

Add:

```python
def test_every_template_json_and_csv_output_lints_cleanly(registry, tmp_path: Path) -> None:
    profile_fields = set(build_community_signal_profile().allowed_fields)

    for adapter in registry.adapters:
        template = build_external_tool_template(
            adapter_id=adapter.id,
            directory=DIRECTORY,
            config_dir=CONFIG_DIR,
            data_dir=DATA_DIR,
            as_of=AS_OF,
        )

        payload = json.loads(render_external_tool_template_json(template))
        assert list(payload) == ["items"]
        assert len(payload["items"]) == 2
        assert all(set(item) == profile_fields for item in payload["items"])

        json_path = tmp_path / f"{adapter.id}.json"
        json_path.write_text(render_external_tool_template_json(template), encoding="utf-8")
        json_result = lint_community_signal_file(json_path, input_format="json")
        assert json_result.ok is True
        assert json_result.valid_row_count == 2

        csv_path = tmp_path / f"{adapter.id}.csv"
        csv_path.write_text(render_external_tool_template_csv(template), encoding="utf-8")
        csv_result = lint_community_signal_file(csv_path, input_format="csv")
        assert csv_result.ok is True
        assert csv_result.valid_row_count == 2
```

- [ ] **Step 5: Add workflow/readiness command parity tests**

Add:

```python
def test_every_workflow_reuses_adapter_commands_for_shared_steps(registry) -> None:
    for adapter in registry.adapters:
        workflow = build_external_tool_workflow(
            adapter_id=adapter.id,
            directory=DIRECTORY,
            config_dir=CONFIG_DIR,
            data_dir=DATA_DIR,
            as_of=AS_OF,
        )
        workflow_commands = {step.name: step.command for step in workflow.steps}

        for step_name, command_index in WORKFLOW_RECOMMENDED_COMMAND_STEPS.items():
            assert workflow_commands[step_name] == adapter.recommended_commands[command_index]

        assert "--dry-run" in shlex.split(workflow_commands["dry_run_directory_import"])
        assert "--dry-run" not in shlex.split(workflow_commands["import_directory_signals"])


def test_every_readiness_reuses_adapter_commands_for_shared_steps(registry) -> None:
    for adapter in registry.adapters:
        readiness = build_external_tool_readiness(
            adapter_id=adapter.id,
            directory=DIRECTORY,
            config_dir=CONFIG_DIR,
            data_dir=DATA_DIR,
            as_of=AS_OF,
            which=lambda _command: None,
        )
        readiness_commands = {step.name: step.command for step in readiness.steps}

        for step_name, command_index in READINESS_RECOMMENDED_COMMAND_STEPS.items():
            assert readiness_commands[step_name] == adapter.recommended_commands[command_index]

        assert "--dry-run" in shlex.split(readiness_commands["dry_run_directory_import"])
```

- [ ] **Step 6: Add banned generated-command token test**

Add:

```python
def test_generated_fashion_radar_guidance_excludes_platform_acquisition_tokens(
    registry,
) -> None:
    commands: list[str] = []
    for adapter in registry.adapters:
        commands.extend(adapter.recommended_commands)
        commands.extend(
            step.command
            for step in build_external_tool_workflow(
                adapter_id=adapter.id,
                directory=DIRECTORY,
                config_dir=CONFIG_DIR,
                data_dir=DATA_DIR,
                as_of=AS_OF,
            ).steps
        )
        commands.extend(
            step.command
            for step in build_external_tool_readiness(
                adapter_id=adapter.id,
                directory=DIRECTORY,
                config_dir=CONFIG_DIR,
                data_dir=DATA_DIR,
                as_of=AS_OF,
                which=lambda _command: None,
            ).steps
        )

    for command in commands:
        tokens = {token.lower() for token in shlex.split(command)}
        assert tokens.isdisjoint(BANNED_COMMAND_TOKENS), command
```

- [ ] **Step 7: Run the new test module**

Run:

```bash
uv --no-config run --frozen pytest tests/test_external_tool_contract_parity.py -q
```

Expected after the file is created: tests pass without production-code changes.

## Task 2: Document The Adapter Parity Gate

**Files:**
- Modify: `docs/community-signal-import.md`
- Modify: `tests/test_cli_docs.py`
- Modify: `CHANGELOG.md`

- [ ] **Step 1: Add a docs drift test first**

In `tests/test_cli_docs.py`, add a test near the existing community signal import
docs tests. First add this module constant near the other `ROOT / "docs" / ...`
constants:

```python
COMMUNITY_SIGNAL_IMPORT_DOC = ROOT / "docs" / "community-signal-import.md"
```

Then add:

```python
def test_community_signal_import_docs_describe_external_tool_contract_parity() -> None:
    text = _read(COMMUNITY_SIGNAL_IMPORT_DOC)
    normalized = _normalized_doc_text(COMMUNITY_SIGNAL_IMPORT_DOC).casefold()

    for term in (
        "External Tool Contract Parity",
        "community-signal-profile",
        "external-tool-adapters",
        "external-tool-template",
        "external-tool-workflow",
        "external-tool-readiness",
        "field mappings",
    ):
        assert term in text

    for term in (
        "dry-run import guidance remains separate from real import guidance",
        "json/csv template output remains importable rows only",
        "local handoff guidance",
        "not platform collection",
        "does not add connectors",
        "does not prove demand",
        "does not rank sources",
        "does not verify platform coverage",
    ):
        assert term in normalized
```

- [ ] **Step 2: Verify the docs test fails before docs are updated**

Run:

```bash
uv --no-config run --frozen pytest tests/test_cli_docs.py::test_community_signal_import_docs_describe_external_tool_contract_parity -q
```

Expected before docs update: the test fails because the new subsection is
missing.

- [ ] **Step 3: Add the docs subsection**

In `docs/community-signal-import.md`, add this subsection after the
`External Tool Adapter Registry` section and before `External Tool Template
Rows`:

```markdown
## External Tool Contract Parity

The external tool adapter surfaces are guarded as one local contract:
`community-signal-profile` defines the accepted row fields,
`external-tool-adapters` exposes adapter field mappings and local command
guidance, `external-tool-template` mirrors those mappings for sanitized example
rows, and `external-tool-workflow` plus `external-tool-readiness` reuse the same
handoff commands for shared steps.

The parity gate checks every built-in adapter so field mappings, template model
metadata, workflow commands, readiness commands, and dry-run import guidance
remain aligned. JSON/CSV template output remains importable rows only; table and
model output can include local handoff guidance. Dry-run import guidance remains
separate from real import guidance.

This is local handoff guidance, not platform collection. It does not add
connectors, fetch URLs, search platforms, run adapters, or call platform APIs.
It does not prove demand. It does not rank sources. It does not verify platform
coverage.
```

- [ ] **Step 4: Add the changelog entry**

In `CHANGELOG.md`, under `### Added`, add:

```markdown
- Stage 78 external/community adapter contract parity tests so adapter field
  mappings, template model metadata, workflow commands, readiness commands, and
  dry-run guidance stay aligned with the local community signal profile. This
  is test/docs-only and adds no scraping, platform APIs, connectors, source
  acquisition, demand proof, ranking, or platform coverage verification.
```

- [ ] **Step 5: Run focused docs and parity checks**

Run:

```bash
uv --no-config run --frozen pytest tests/test_external_tool_contract_parity.py tests/test_cli_docs.py::test_community_signal_import_docs_describe_external_tool_contract_parity -q
uv --no-config run --frozen ruff check tests/test_external_tool_contract_parity.py tests/test_cli_docs.py
uv --no-config run --frozen ruff format --check tests/test_external_tool_contract_parity.py tests/test_cli_docs.py
```

Expected: all pass.

## Task 3: Stage Review, Verification, Commit, And Publish

**Files:**
- Add: `docs/reviews/opencode-stage-78-plan-review-prompt.md`
- Add: `docs/reviews/opencode-stage-78-plan-review.md`
- Add: `docs/reviews/opencode-stage-78-plan-rereview-prompt.md`
- Add: `docs/reviews/opencode-stage-78-plan-rereview.md`
- Add: `docs/reviews/opencode-stage-78-code-review-prompt.md`
- Add: `docs/reviews/opencode-stage-78-code-review.md`

- [ ] **Step 1: Run opencode plan review before implementation**

Create `docs/reviews/opencode-stage-78-plan-review-prompt.md` summarizing this
plan, the design spec, current boundaries, and the unchanged dirty `uv.lock`
risk. Then run:

```bash
opencode run --model zhipuai-coding-plan/glm-5.2 --variant max --dir /home/ubuntu/fashion-radar "$(cat docs/reviews/opencode-stage-78-plan-review-prompt.md)" > docs/reviews/opencode-stage-78-plan-review.md
```

Fix any Critical or Important findings before implementation.

- [ ] **Step 2: Run opencode code review after implementation**

Create `docs/reviews/opencode-stage-78-code-review-prompt.md` and run:

```bash
opencode run --model zhipuai-coding-plan/glm-5.2 --variant max --dir /home/ubuntu/fashion-radar "$(cat docs/reviews/opencode-stage-78-code-review-prompt.md)" > docs/reviews/opencode-stage-78-code-review.md
```

Fix any Critical or Important findings before release verification.

- [ ] **Step 3: Run full verification**

Run:

```bash
uv --no-config run --frozen python scripts/check_release_hygiene.py
uv --no-config run --frozen pytest
uv --no-config run --frozen ruff check .
uv --no-config run --frozen ruff format --check .
UV_NO_CONFIG=1 uv lock --check
tmp_public_lock="$(mktemp)"
git show HEAD:uv.lock > "$tmp_public_lock"
! rg -n 'tuna|aliyun|ustc|huaweicloud|mirror|index-url|extra-index-url|find-links' "$tmp_public_lock"
rm -f "$tmp_public_lock"
! git diff --cached --name-only | rg -x 'uv.lock'
git diff --check
```

- [ ] **Step 4: Stage only Stage 78 files**

Run:

```bash
git add tests/test_external_tool_contract_parity.py \
  tests/test_cli_docs.py \
  docs/community-signal-import.md \
  CHANGELOG.md \
  docs/superpowers/specs/2026-06-18-stage-78-adapter-contract-parity-design.md \
  docs/superpowers/plans/2026-06-18-stage-78-adapter-contract-parity-plan.md \
  docs/reviews/opencode-stage-78-plan-review-prompt.md \
  docs/reviews/opencode-stage-78-plan-review.md \
  docs/reviews/opencode-stage-78-plan-rereview-prompt.md \
  docs/reviews/opencode-stage-78-plan-rereview.md \
  docs/reviews/opencode-stage-78-code-review-prompt.md \
  docs/reviews/opencode-stage-78-code-review.md
```

Then run:

```bash
! git diff --cached --name-only | rg -x 'uv.lock'
uv --no-config run --frozen python scripts/check_release_hygiene.py --repo-root .
git diff --cached --check
git grep --cached -n -E 'gh[pousr]_[A-Za-z0-9]{36,255}|github_pat_[A-Za-z0-9_]{82,255}|-----BEGIN [A-Z0-9 ]*PRIVATE KEY-----' -- . ':!uv.lock' && exit 1 || true
```

- [ ] **Step 5: Commit and publish through GitHub Git Data API**

Commit:

```bash
git commit -m "Add adapter contract parity gate"
```

Publish using the existing GitHub Git Data API flow with token read only from
`/home/ubuntu/.config/fashion-radar/github-token`, `force:false`, no token in
remote URLs, and no persistent `http.*.extraheader`.

- [ ] **Step 6: Verify remote and CI**

Run:

```bash
git fetch origin main
test "$(git rev-parse HEAD^{tree})" = "$(git rev-parse origin/main^{tree})"
test "$(git remote get-url origin)" = "https://github.com/Lordakee/fashion-radar.git"
git config --show-origin --get-regexp '^http\..*\.extraheader$' && exit 1 || true
git config --show-origin --list | rg -i 'gh[pousr]_|github_pat_|x-access-token|authorization' && exit 1 || true
! git diff --cached --name-only | rg -x 'uv.lock'
```

Poll the latest `main` GitHub Actions run and require `completed success`.
