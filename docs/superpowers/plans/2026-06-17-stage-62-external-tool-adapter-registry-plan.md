# Stage 62 External Tool Adapter Registry Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a local, print-only external social/community tool adapter registry that helps user-controlled upstream tools target the existing sanitized CSV/JSON community handoff contract.

**Architecture:** Implement one focused registry module with deterministic Pydantic models, wire it to a new Typer command, document it as producer-discovery metadata, and smoke the installed CLI JSON output. The registry reuses existing community signal field names and existing handoff commands; it never runs upstream tools or changes import/storage behavior.

**Tech Stack:** Python 3.11+, Typer, Pydantic v2, pytest, ruff, existing `uv` workflow.

---

## File Structure

- Create `src/fashion_radar/external_tool_adapters.py`: deterministic registry models, builder, filtering, command rendering, and table rendering.
- Modify `src/fashion_radar/cli.py`: add output format alias, import registry functions, and register `external-tool-adapters`.
- Create `tests/test_external_tool_adapters.py`: unit tests for model shape, adapter list, field mapping boundaries, filtering, quoting, and rendering.
- Modify `tests/test_cli.py`: CLI smoke tests for JSON/table output and invalid adapter errors.
- Modify `scripts/check_first_run_smoke.py`: installed/source smoke validation for print-only registry JSON.
- Modify `tests/test_first_run_smoke.py`: fake command sequence and validator coverage for the new smoke command.
- Modify `tests/test_cli_docs.py`: docs-drift tests for registry docs and installed-wheel help loop.
- Modify docs: `README.md`, `docs/community-signal-import.md`, `docs/community-signal-quality.md`, `docs/source-boundaries.md`, `docs/architecture.md`, `docs/cli-reference.md`, `docs/github-upload-checklist.md`, and `CHANGELOG.md`.
- Add review artifacts under `docs/reviews/`.

## Task 1: Registry Module

**Files:**
- Create: `src/fashion_radar/external_tool_adapters.py`
- Create: `tests/test_external_tool_adapters.py`

- [ ] **Step 1: Write failing registry shape tests**

Add tests that call `build_external_tool_adapter_registry()` and assert:

```python
def test_registry_has_stable_contract_and_adapter_ids() -> None:
    registry = build_external_tool_adapter_registry(
        directory=Path("./exports"),
        config_dir=Path("./configs"),
        data_dir=Path("./data"),
        as_of="2026-06-13T12:00:00Z",
    )
    payload = registry.model_dump(mode="json")
    assert list(payload) == ["contract_version", "execution_mode", "adapters", "boundaries"]
    assert registry.contract_version == "external-tool-adapters/v1"
    assert registry.execution_mode == "print_only"
    assert [adapter.id for adapter in registry.adapters] == [
        "rednote_mcp",
        "xiaohongshu_crawler",
        "instaloader",
        "tiktok_api",
        "yt_dlp",
        "x_search_export",
        "generic_community_export",
    ]
```

Also assert one representative adapter:

```python
instaloader = registry.adapter_by_id("instaloader")
assert instaloader.platform_label == "instagram"
assert instaloader.suggested_source_name == "Instaloader Export"
assert instaloader.recommended_input_format == "json"
assert instaloader.recommended_pattern == "*.json"
assert "fashion-radar community-handoff-manifest" in instaloader.recommended_commands[1]
```

- [ ] **Step 2: Run tests to verify failure**

Run:

```bash
uv run pytest tests/test_external_tool_adapters.py -q
```

Expected: fail because the module does not exist.

- [ ] **Step 3: Implement registry models and builder**

Create `src/fashion_radar/external_tool_adapters.py` with:

```python
from __future__ import annotations

import shlex
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from fashion_radar.community_signal_profile import (
    build_community_signal_profile,
)
from fashion_radar.importers.manual_signals import ManualSignalFormat
from fashion_radar.utils.dates import parse_datetime_utc

EXTERNAL_TOOL_ADAPTERS_CONTRACT_VERSION = "external-tool-adapters/v1"
EXTERNAL_TOOL_ADAPTERS_EXECUTION_MODE = "print_only"
DEFAULT_ADAPTER_AS_OF = "2026-06-13T12:00:00Z"
DEFAULT_EXPORT_DIRECTORY = "./exports"


class ExternalToolAdapterFieldMapping(BaseModel):
    model_config = ConfigDict(extra="forbid")

    field: str
    required: bool
    note: str


class ExternalToolAdapter(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str
    display_name: str
    platform_label: str
    suggested_source_name: str
    recommended_input_format: ManualSignalFormat
    recommended_pattern: str
    suggested_export_directory: str
    description: str
    upstream_tool_examples: list[str]
    field_mappings: list[ExternalToolAdapterFieldMapping]
    recommended_commands: list[str]
    boundaries: list[str]


class ExternalToolAdapterRegistry(BaseModel):
    model_config = ConfigDict(extra="forbid")

    contract_version: str
    execution_mode: Literal["print_only"]
    adapters: list[ExternalToolAdapter] = Field(default_factory=list)
    boundaries: list[str] = Field(default_factory=list)

    def adapter_by_id(self, adapter_id: str) -> ExternalToolAdapter:
        for adapter in self.adapters:
            if adapter.id == adapter_id:
                return adapter
        raise KeyError(adapter_id)
```

Implement `build_external_tool_adapter_registry(...)` to create the seven
adapter records listed in the design. Use `build_community_signal_profile()`
for required, optional, and allowed field names. Mark each `field_mappings`
entry as required when the field appears in `profile.required_fields`, and
raise `ValueError("External tool adapter field mappings differ from community signal contract.")`
if any mapping field is outside `profile.allowed_fields`. Normalize `as_of`
with `parse_datetime_utc(as_of).isoformat()` before generating command strings.
Generate the same eight command forms:

```text
fashion-radar community-signal-profile --format json
fashion-radar community-handoff-manifest <dir> --input-format <format> --pattern <pattern> --config-dir <config_dir> --data-dir <data_dir> --as-of <as_of> --source-name <source_name> --format json
fashion-radar community-handoff-workflow <dir> --input-format <format> --pattern <pattern> --config-dir <config_dir> --data-dir <data_dir> --as-of <as_of> --source-name <source_name>
fashion-radar community-signal-lint-dir <dir> --input-format <format> --pattern <pattern> --source-name <source_name> --strict
fashion-radar community-handoff-check-dir <dir> --input-format <format> --pattern <pattern> --config-dir <config_dir> --as-of <as_of> --source-name <source_name> --strict
fashion-radar import-signals-dir <dir> --format <format> --pattern <pattern> --source-name <source_name> --data-dir <data_dir> --imported-at <as_of> --dry-run
fashion-radar import-signals-dir <dir> --format <format> --pattern <pattern> --source-name <source_name> --data-dir <data_dir> --imported-at <as_of>
fashion-radar imported-review-workflow --config-dir <config_dir> --data-dir <data_dir> --as-of <as_of> --source-name <source_name>
```

Use `shlex.join(str(part) for part in parts)` for every generated command.

- [ ] **Step 4: Add filtering and rendering**

Add:

```python
def filter_external_tool_adapter_registry(
    registry: ExternalToolAdapterRegistry,
    *,
    adapter_id: str | None,
) -> ExternalToolAdapterRegistry:
    if adapter_id is None:
        return registry
    try:
        adapter = registry.adapter_by_id(adapter_id)
    except KeyError as exc:
        raise ValueError(f"Unknown external tool adapter: {adapter_id}") from exc
    return registry.model_copy(update={"adapters": [adapter]})
```

Add `render_external_tool_adapter_registry_table()` that prints:

```text
External tool adapter registry.
Contract version: external-tool-adapters/v1
Execution mode: print_only
Adapters: 7
Adapter | Platform | Source name | Format | Pattern | Directory
...
Commands for <id>:
- <command>
Boundaries:
- ...
```

Use a local `_table_cell()` sanitizer matching existing modules.

- [ ] **Step 5: Run focused tests**

Run:

```bash
uv run pytest tests/test_external_tool_adapters.py -q
```

Expected: pass.

## Task 2: CLI Command

**Files:**
- Modify: `src/fashion_radar/cli.py`
- Modify: `tests/test_cli.py`

- [ ] **Step 1: Write failing CLI tests**

Add tests using the existing Typer runner style:

```python
def test_external_tool_adapters_command_prints_json() -> None:
    result = runner.invoke(app, ["external-tool-adapters", "--format", "json"])
    assert result.exit_code == 0
    payload = json.loads(result.stdout)
    assert payload["contract_version"] == "external-tool-adapters/v1"
    assert payload["execution_mode"] == "print_only"
    assert [adapter["id"] for adapter in payload["adapters"]][:2] == [
        "rednote_mcp",
        "xiaohongshu_crawler",
    ]
```

Add adapter filtering and invalid adapter tests.

- [ ] **Step 2: Run tests to verify failure**

Run:

```bash
uv run pytest tests/test_cli.py -q
```

Expected: fail because the command does not exist.

- [ ] **Step 3: Wire CLI command**

In `src/fashion_radar/cli.py`, import:

```python
from fashion_radar.external_tool_adapters import (
    DEFAULT_ADAPTER_AS_OF,
    DEFAULT_EXPORT_DIRECTORY,
    build_external_tool_adapter_registry,
    filter_external_tool_adapter_registry,
    render_external_tool_adapter_registry_table,
)
```

Add:

```python
ExternalToolAdaptersOutputFormat = Literal["table", "json"]
EXTERNAL_TOOL_ADAPTERS_FORMAT_OPTION = typer.Option("table", "--format", help="Output format.")
```

Add command near the community handoff commands:

```python
@app.command(name="external-tool-adapters")
def external_tool_adapters_command(
    adapter: str | None = typer.Option(None, "--adapter", help="Adapter id to print."),
    directory: str = typer.Option(DEFAULT_EXPORT_DIRECTORY, "--directory", help="Suggested local export directory used in printed commands only."),
    config_dir: str = CONFIG_DIR_OPTION,
    data_dir: str = DATA_DIR_OPTION,
    as_of: str = typer.Option(DEFAULT_ADAPTER_AS_OF, "--as-of", help="UTC timestamp used in printed commands only."),
    output_format: ExternalToolAdaptersOutputFormat = EXTERNAL_TOOL_ADAPTERS_FORMAT_OPTION,
) -> None:
    """Print local external tool adapter handoff guidance without running tools."""
    try:
        registry = build_external_tool_adapter_registry(
            directory=Path(directory),
            config_dir=Path(config_dir),
            data_dir=Path(data_dir),
            as_of=as_of,
        )
        registry = filter_external_tool_adapter_registry(registry, adapter_id=adapter)
    except ValueError as exc:
        typer.echo(f"Could not build external tool adapter registry: {exc}", err=True)
        raise typer.Exit(1) from exc

    if output_format == "json":
        typer.echo(registry.model_dump_json(indent=2))
        return
    for line in render_external_tool_adapter_registry_table(registry):
        typer.echo(line)
```

- [ ] **Step 4: Run focused CLI tests**

Run:

```bash
uv run pytest tests/test_cli.py tests/test_external_tool_adapters.py -q
```

Expected: pass.

## Task 3: Smoke And Docs-Drift Tests

**Files:**
- Modify: `scripts/check_first_run_smoke.py`
- Modify: `tests/test_first_run_smoke.py`
- Modify: `tests/test_cli_docs.py`

- [ ] **Step 1: Extend first-run smoke validator**

In `scripts/check_first_run_smoke.py`, add a small validator function that checks:

```python
payload["contract_version"] == "external-tool-adapters/v1"
payload["execution_mode"] == "print_only"
payload["adapters"][0]["id"] == "rednote_mcp"
```

Run the CLI command first, then pass stdout through the existing
`validate_json_output(...)` helper:

```text
fashion-radar external-tool-adapters --format json
```

Do not add external commands, network calls, writes, or collection.

- [ ] **Step 2: Update first-run smoke tests**

Update fake stdout and sequence expectations in `tests/test_first_run_smoke.py`
so the new print-only command is included and validated.

- [ ] **Step 3: Add docs-drift assertions**

Add one docs-drift test in `tests/test_cli_docs.py`:

```python
def test_external_tool_adapter_registry_docs_are_linked_and_bounded() -> None:
    readme = _read(README)
    import_doc = _read(ROOT / "docs" / "community-signal-import.md")
    quality_doc = _read(ROOT / "docs" / "community-signal-quality.md")
    cli_reference = _read(CLI_REFERENCE)
    checklist = _read(UPLOAD_CHECKLIST)
    boundaries = _read(ROOT / "docs" / "source-boundaries.md")
    architecture = _read(ROOT / "docs" / "architecture.md")
    agents = _read(ROOT / "AGENTS.md")
    changelog = _read(ROOT / "CHANGELOG.md")

    for text in (readme, import_doc, quality_doc, cli_reference, checklist, boundaries, architecture, changelog):
        assert "external-tool-adapters" in text

    for doc_text in (readme, import_doc, quality_doc, boundaries, architecture, agents):
        normalized = _normalized_text(doc_text).casefold()
        for term in (
            "external social/community tool adapter registry",
            "local producer-discovery registry",
            "sanitized csv/json local file handoff",
            "user-controlled external/community tools",
            "not platform collection",
            "connectors",
            "scraping",
            "browser automation",
            "platform apis",
            "monitoring",
            "scheduling",
            "source acquisition",
            "demand proof",
            "ranking",
            "coverage verification",
        ):
            assert term in normalized
```

Ensure `test_cli_reference_lists_every_public_command` and the upload checklist
help loop tests pass by documenting the new command.

- [ ] **Step 4: Run focused tests**

Run:

```bash
uv run pytest tests/test_first_run_smoke.py tests/test_cli_docs.py -q
```

Expected: pass after docs are updated in Task 4.

## Task 4: Public Documentation

**Files:**
- Modify: `README.md`
- Modify: `docs/community-signal-import.md`
- Modify: `docs/community-signal-quality.md`
- Modify: `docs/source-boundaries.md`
- Modify: `docs/architecture.md`
- Modify: `docs/cli-reference.md`
- Modify: `docs/github-upload-checklist.md`
- Modify: `AGENTS.md`
- Modify: `CHANGELOG.md`

- [ ] **Step 1: Update README**

Add a bullet under "What It Does":

```markdown
- Prints a local external social/community tool adapter registry that maps
  user-controlled upstream tools to the sanitized CSV/JSON handoff contract
  without running those tools.
```

Add a bounded paragraph near external tool handoff text:

```markdown
`external-tool-adapters` is a local producer-discovery registry for
user-controlled external/community tools that write sanitized CSV/JSON local
file handoff rows. It includes examples for Rednote/Xiaohongshu, Instagram,
TikTok, yt-dlp media metadata exports, X/search exports, and generic community
exports. It does not run adapters, fetch URLs, log in, call platform APIs,
monitor communities, schedule work, add source/platform connectors, acquire
sources, prove demand, rank sources, or verify platform coverage.
```

- [ ] **Step 2: Update community import and quality docs**

Add an "Adapter Registry" section that shows:

```bash
uv run fashion-radar external-tool-adapters --format json
uv run fashion-radar external-tool-adapters --adapter instaloader --directory "$tmp_run/exports" --config-dir "$PWD/configs" --data-dir "$PWD/data" --as-of "$AS_OF"
```

Explain that the registry is guidance for writing the same existing fields:
`url`, `title`, `published_at`, `summary`, `source_name`, `platform`,
`source_weight`, and `collected_at`.

- [ ] **Step 3: Update source boundaries and architecture**

Add the registry to the existing external tool handoff boundary paragraphs.
Use both exact phrases "external social/community tool adapter registry" and
"local producer-discovery registry" in `docs/community-signal-import.md`,
`docs/community-signal-quality.md`, `docs/source-boundaries.md`, and
`docs/architecture.md`, together with the negative boundary vocabulary from the
design.

- [ ] **Step 4: Update CLI reference and upload checklist**

Add `external-tool-adapters` command docs in `docs/cli-reference.md`, including
options and print-only execution mode.

Add installed-wheel help loop entries in `docs/github-upload-checklist.md`:

```bash
"$tmp_env/venv/bin/fashion-radar" external-tool-adapters --help
"$tmp_env/venv/bin/fashion-radar" external-tool-adapters --format json
```

- [ ] **Step 5: Update AGENTS.md**

Append a Stage 62 boundary rule under "Scope Boundaries":

```markdown
- Future external social/community tool adapter registry work must stay a local
  producer-discovery registry for user-controlled external/community tools that
  write sanitized CSV/JSON local file handoff rows. It is not platform
  collection and does not add connectors, scraping, browser automation,
  platform APIs, monitoring, scheduling, source acquisition, demand proof,
  ranking, or coverage verification.
```

- [ ] **Step 6: Update changelog**

Add an Unreleased bullet:

```markdown
- Added `external-tool-adapters`, a print-only local producer-discovery
  registry for mapping user-controlled external/community tools to the
  sanitized CSV/JSON community handoff contract.
```

- [ ] **Step 7: Run docs tests**

Run:

```bash
uv run pytest tests/test_cli_docs.py -q
```

Expected: pass.

## Task 5: Review, Verification, Commit, Push

**Files:**
- Add: `docs/reviews/opencode-stage-62-plan-review-prompt.md`
- Add: `docs/reviews/opencode-stage-62-plan-review.md`
- Add: `docs/reviews/opencode-stage-62-plan-rereview-prompt.md`
- Add: `docs/reviews/opencode-stage-62-plan-rereview.md`
- Add: `docs/reviews/opencode-stage-62-release-review-prompt.md`
- Add: `docs/reviews/opencode-stage-62-release-review.md`

- [ ] **Step 1: Request plan review before implementation**

Run local opencode:

```bash
opencode run -m zhipuai-coding-plan/glm-5.2 "$(cat docs/reviews/opencode-stage-62-plan-review-prompt.md)" > docs/reviews/opencode-stage-62-plan-review.md
```

Expected: `APPROVED FOR STAGE 62 PLAN`. Fix Critical/Important findings before
implementation.

- [ ] **Step 2: Run focused verification**

Run:

```bash
uv run pytest tests/test_external_tool_adapters.py tests/test_cli.py tests/test_first_run_smoke.py tests/test_cli_docs.py -q
ruff check .
ruff format --check .
git diff --check
UV_NO_CONFIG=1 uv lock --check
UV_NO_CONFIG=1 uv sync --locked --dev --check
```

Expected: all exit 0.

- [ ] **Step 3: Run release verification**

Run:

```bash
uv run pytest -q
UV_NO_CONFIG=1 uv run python scripts/check_release_hygiene.py
UV_NO_CONFIG=1 uv run python scripts/check_first_run_smoke.py --repo-root .
tmp_build="$(mktemp -d)"
UV_NO_CONFIG=1 uv build --out-dir "$tmp_build"
UV_NO_CONFIG=1 uv run python scripts/check_package_archives.py "$tmp_build"/*
tmp_env="$(mktemp -d)"
uv venv "$tmp_env/venv"
uv pip install --python "$tmp_env/venv/bin/python" "$tmp_build"/*.whl
"$tmp_env/venv/bin/python" scripts/check_first_run_smoke.py --repo-root . --python "$tmp_env/venv/bin/python" --installed
"$tmp_env/venv/bin/fashion-radar" external-tool-adapters --format json
```

Expected: all exit 0.

- [ ] **Step 4: Request release review**

Create `docs/reviews/opencode-stage-62-release-review-prompt.md` with changed
files, objective, boundaries, and verification commands. Run:

```bash
opencode run -m zhipuai-coding-plan/glm-5.2 "$(cat docs/reviews/opencode-stage-62-release-review-prompt.md)" > docs/reviews/opencode-stage-62-release-review.md
```

Expected: approval or only Minor findings. Fix Critical/Important findings.

- [ ] **Step 5: Commit and push**

Run:

```bash
git status --short
git add src/fashion_radar/external_tool_adapters.py src/fashion_radar/cli.py tests/test_external_tool_adapters.py tests/test_cli.py tests/test_first_run_smoke.py tests/test_cli_docs.py scripts/check_first_run_smoke.py README.md docs/community-signal-import.md docs/community-signal-quality.md docs/source-boundaries.md docs/architecture.md docs/cli-reference.md docs/github-upload-checklist.md AGENTS.md CHANGELOG.md docs/superpowers/specs/2026-06-17-stage-62-external-tool-adapter-registry-design.md docs/superpowers/plans/2026-06-17-stage-62-external-tool-adapter-registry-plan.md docs/reviews/opencode-stage-62-plan-review-prompt.md docs/reviews/opencode-stage-62-plan-review.md docs/reviews/opencode-stage-62-plan-rereview-prompt.md docs/reviews/opencode-stage-62-plan-rereview.md docs/reviews/opencode-stage-62-release-review-prompt.md docs/reviews/opencode-stage-62-release-review.md
git commit -m "Add external tool adapter registry"
TOKEN="$(cat /home/ubuntu/.config/fashion-radar/github-token)"
git -c http.https://github.com/.extraheader="AUTHORIZATION: bearer $TOKEN" push origin main
```

Expected: push succeeds without storing the token in git config or remote URL.

- [ ] **Step 6: Confirm CI**

Use the GitHub API with the saved token to poll the pushed commit's Actions run.
Expected: CI conclusion `success`.

## Self-Review

- Spec coverage: all Stage 62 design requirements map to tasks.
- Placeholder scan: no TBD/TODO placeholders remain.
- Type consistency: model and function names are consistent across tasks.
- Boundary check: no dependency, schema, collector, scheduler, scraping, browser,
  platform API, account, media download, report, dashboard, or storage change is
  planned.
