# Stage 115 XPOZ Adapter Metadata Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add an `xpoz_mcp` external-tool adapter metadata target for sanitized XPOZ MCP / XPOZ Social Data API exports.

**Architecture:** Extend the existing print-only external-tool registry and its downstream readiness/template/workflow contracts. Do not add collection behavior; the new adapter only emits metadata, importable sample rows, and copyable local handoff commands for already-sanitized local JSON exports.

**Tech Stack:** Python 3.11, Pydantic models, Typer CLI, pytest, ruff, uv, local opencode review with `zhipuai-coding-plan/glm-5.2 --variant max`.

---

## Files

- Modify: `src/fashion_radar/external_tool_adapters.py`
- Modify: `src/fashion_radar/external_tool_readiness.py`
- Modify: `tests/test_external_tool_adapters.py`
- Modify: `tests/test_external_tool_readiness.py`
- Modify: `tests/test_external_tool_templates.py`
- Modify: `tests/test_external_tool_contract_parity.py`
- Modify: `tests/test_cli.py`
- Modify: `tests/test_first_run_smoke.py`
- Modify: `scripts/check_first_run_smoke.py`
- Modify: `README.md`
- Modify: `docs/first-run.md`
- Modify: `docs/cli-reference.md`
- Modify: `tests/test_cli_docs.py`
- Create: `docs/reviews/opencode-stage-115-plan-review-prompt.md`
- Create: `docs/reviews/opencode-stage-115-plan-rereview-prompt.md`
- Create: `docs/reviews/opencode-stage-115-plan-rereview.md`
- Create later: `docs/reviews/opencode-stage-115-code-review-prompt.md`
- Create later: `docs/reviews/opencode-stage-115-code-review.md`

Do not modify `uv.lock`, `pyproject.toml`, schemas, collectors, source packs,
entity packs, dashboard, importers, scoring, reports, or CI.

## Task 0: Plan Review

- [ ] **Step 1: Create the plan review prompt**

Create `docs/reviews/opencode-stage-115-plan-review-prompt.md` with the
current Stage 115 design and plan review request.

- [ ] **Step 2: Run local opencode plan review**

Run:

```bash
opencode run --model zhipuai-coding-plan/glm-5.2 --variant max --dir /home/ubuntu/fashion-radar "$(cat docs/reviews/opencode-stage-115-plan-review-prompt.md)" > docs/reviews/opencode-stage-115-plan-review.md
```

Expected: review completes, or lists actionable items. If the broad review
times out before a conclusion, use a focused rereview prompt against the
identified blockers and save it as
`docs/reviews/opencode-stage-115-plan-rereview.md`.

- [ ] **Step 3: Resolve Critical/Important plan findings before coding**

If the review identifies Critical or Important findings, update the design and
plan before Task 1.

- [ ] **Step 4: Run focused plan rereview if needed**

If the initial plan review does not produce a final conclusion, create
`docs/reviews/opencode-stage-115-plan-rereview-prompt.md` and run:

```bash
opencode run --model zhipuai-coding-plan/glm-5.2 --variant max --dir /home/ubuntu/fashion-radar "$(cat docs/reviews/opencode-stage-115-plan-rereview-prompt.md)" > docs/reviews/opencode-stage-115-plan-rereview.md
```

Expected: `docs/reviews/opencode-stage-115-plan-rereview.md` explicitly says
there are no new Critical/Important blockers before implementation.

## Task 1: Write Failing Tests

- [ ] **Step 1: Extend adapter id expectations**

In `tests/test_external_tool_adapters.py`, change `EXPECTED_ADAPTER_IDS` to:

```python
EXPECTED_ADAPTER_IDS = [
    "rednote_mcp",
    "xiaohongshu_crawler",
    "instaloader",
    "tiktok_api",
    "yt_dlp",
    "x_search_export",
    "xpoz_mcp",
    "generic_community_export",
]
```

Change `assert len(registry.adapters) == 7` to `8`.

- [ ] **Step 2: Add a focused XPOZ adapter metadata test**

Add this test near the existing adapter metadata tests in
`tests/test_external_tool_adapters.py`:

```python
def test_xpoz_mcp_adapter_has_expected_mapping_and_commands() -> None:
    registry = build_external_tool_adapter_registry(
        directory=Path("./exports"),
        config_dir=Path("./configs"),
        data_dir=Path("./data"),
        as_of="2026-06-13T12:00:00Z",
    )

    adapter = registry.adapter_by_id("xpoz_mcp")
    commands = [shlex.split(command) for command in adapter.recommended_commands]

    assert adapter.display_name == "XPOZ MCP Export"
    assert adapter.platform_label == "community"
    assert adapter.suggested_source_name == "XPOZ MCP Export"
    assert adapter.recommended_input_format == "json"
    assert adapter.recommended_pattern == "*.json"
    assert adapter.suggested_export_directory == "exports"
    assert adapter.upstream_tool_examples == ["XPOZ MCP", "XPOZ Social Data API"]
    assert "XPOZ MCP / Social Data API" in adapter.description
    assert [command[:2] for command in commands] == [
        ["fashion-radar", "community-signal-profile"],
        ["fashion-radar", "external-tool-readiness"],
        ["fashion-radar", "community-handoff-manifest"],
        ["fashion-radar", "community-handoff-workflow"],
        ["fashion-radar", "community-signal-lint-dir"],
        ["fashion-radar", "community-handoff-check-dir"],
        ["fashion-radar", "import-signals-dir"],
        ["fashion-radar", "import-signals-dir"],
        ["fashion-radar", "imported-review-workflow"],
    ]
    readiness_command = commands[1]
    assert readiness_command[readiness_command.index("--adapter") + 1] == "xpoz_mcp"
    assert readiness_command[readiness_command.index("--input-format") + 1] == "json"
    assert readiness_command[readiness_command.index("--pattern") + 1] == "*.json"
    assert readiness_command[readiness_command.index("--source-name") + 1] == (
        "XPOZ MCP Export"
    )
```

- [ ] **Step 3: Update readiness test expectations**

In `tests/test_external_tool_readiness.py`, add this case to
`test_readiness_upstream_command_mapping`:

```python
("xpoz_mcp", None, "not_applicable", "XPOZ MCP"),
```

- [ ] **Step 4: Update template collection tests**

In `tests/test_external_tool_templates.py`, include `xpoz_mcp` before
`generic_community_export` and change `assert len(collection.items) == 14` to
`16`.

- [ ] **Step 4b: Update template table renderer count and tail adapter assertions**

In `tests/test_external_tool_templates.py`, update
`test_template_collection_table_renderer_includes_each_full_template`:

```python
assert "Templates: 8" in lines
assert "Adapter 8:" in lines
assert "Adapter: generic_community_export" in lines
```

This replaces the current `"Templates: 7"` / `"Adapter 7:"` tail assumptions
so the table-renderer test proves the new adapter count and preserves
`generic_community_export` as the final catch-all adapter.

- [ ] **Step 5: Update cross-contract parity expected ids**

In `tests/test_external_tool_contract_parity.py`, add `xpoz_mcp` before
`generic_community_export`.

- [ ] **Step 6: Update CLI adapter JSON test expected map**

In `tests/test_cli.py::test_external_tool_adapters_command_prints_json`, add:

```python
"xpoz_mcp": ("community", "XPOZ MCP Export", "json", "*.json"),
```

before `generic_community_export`.

- [ ] **Step 6b: Update CLI unfiltered template row count**

In `tests/test_cli.py::test_external_tool_template_command_prints_all_adapters_when_unfiltered`,
change:

```python
assert len(payload["items"]) == 14
```

to:

```python
assert len(payload["items"]) == 16
```

- [ ] **Step 7: Update first-run smoke expected adapter fixtures**

In `scripts/check_first_run_smoke.py`, add:

```python
"xpoz_mcp": ("community", "json", "*.json", "XPOZ MCP Export"),
```

to `EXPECTED_EXTERNAL_TOOL_ADAPTERS` before `generic_community_export`, and add
the corresponding detail block:

```python
"xpoz_mcp": {
    "description": (
        "Metadata target for sanitized XPOZ MCP / Social Data API exports "
        "created outside Fashion Radar."
    ),
    "upstream_tool_examples": ["XPOZ MCP", "XPOZ Social Data API"],
},
```

- [ ] **Step 8: Update first-run unit expected ids and template counts**

In `tests/test_first_run_smoke.py`, update `EXTERNAL_TOOL_ADAPTER_CASES` by
adding this tuple before the `generic_community_export` tuple:

```python
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
    ["XPOZ MCP", "XPOZ Social Data API"],
),
```

Also update any pinned adapter id lists that derive from the adapter tuple list.

- [ ] **Step 9: Update docs tests**

In `tests/test_cli_docs.py`, add expected README / CLI reference matrix lines:

```python
"| `xpoz_mcp` | XPOZ MCP Export | `community` | `json` | `*.json` |"
```

Also update `FIRST_RUN_EXTERNAL_ADAPTER_SMOKE_PHRASE` from "all seven adapters"
to "all eight adapters".

- [ ] **Step 10: Run RED tests**

Run:

```bash
env -u ALL_PROXY -u all_proxy uv --no-config run --frozen pytest \
  tests/test_external_tool_adapters.py \
  tests/test_external_tool_readiness.py \
  tests/test_external_tool_templates.py \
  tests/test_external_tool_contract_parity.py \
  tests/test_cli.py::test_external_tool_adapters_command_prints_json \
  tests/test_cli.py::test_external_tool_template_command_prints_all_adapters_when_unfiltered \
  tests/test_first_run_smoke.py \
  tests/test_cli_docs.py -q
```

Expected: fail because `xpoz_mcp` is not implemented and docs are not updated.

## Task 2: Implement Runtime Metadata

- [ ] **Step 1: Add registry adapter**

In `src/fashion_radar/external_tool_adapters.py`, add an `_adapter(...)` entry
after `x_search_export` and before `generic_community_export`:

```python
_adapter(
    adapter_id="xpoz_mcp",
    display_name="XPOZ MCP Export",
    platform_label="community",
    source_name="XPOZ MCP Export",
    input_format="json",
    pattern="*.json",
    directory_text=directory_text,
    config_text=config_text,
    data_text=data_text,
    as_of_text=as_of_text,
    description=(
        "Metadata target for sanitized XPOZ MCP / Social Data API exports "
        "created outside Fashion Radar."
    ),
    upstream_tool_examples=["XPOZ MCP", "XPOZ Social Data API"],
    field_mappings=field_mappings,
),
```

- [ ] **Step 2: Add readiness upstream command spec**

In `src/fashion_radar/external_tool_readiness.py`, add:

```python
"xpoz_mcp": {
    "command": None,
    "install_hint": (
        "Use XPOZ MCP / Social Data API docs to create a sanitized local JSON export."
    ),
    "detail": "No upstream CLI command is required for sanitized XPOZ handoff rows.",
},
```

before `generic_community_export`.

- [ ] **Step 3: Run focused GREEN tests**

Run:

```bash
env -u ALL_PROXY -u all_proxy uv --no-config run --frozen pytest \
  tests/test_external_tool_adapters.py \
  tests/test_external_tool_readiness.py \
  tests/test_external_tool_templates.py \
  tests/test_external_tool_contract_parity.py \
  tests/test_cli.py::test_external_tool_adapters_command_prints_json \
  tests/test_cli.py::test_external_tool_template_command_prints_all_adapters_when_unfiltered \
  tests/test_first_run_smoke.py \
  tests/test_cli_docs.py -q
```

Expected: remaining failures only in docs/smoke fixture locations that still
need textual updates.

## Task 3: Update Documentation Matrices

- [ ] **Step 1: Update README adapter matrix**

In `README.md`, add this row before `generic_community_export`:

```markdown
| `xpoz_mcp` | XPOZ MCP Export | `community` | `json` | `*.json` |
```

- [ ] **Step 2: Update CLI reference adapter matrix**

In `docs/cli-reference.md`, add the same row before `generic_community_export`.

- [ ] **Step 3: Update first-run adapter-count prose**

In `README.md`, change:

```markdown
external-tool-adapters --format json across all seven adapters.
```

to:

```markdown
external-tool-adapters --format json across all eight adapters.
```

In `docs/first-run.md`, make the same "seven" to "eight" update.

- [ ] **Step 4: Run docs tests**

Run:

```bash
env -u ALL_PROXY -u all_proxy uv --no-config run --frozen pytest tests/test_cli_docs.py -q
```

Expected: pass.

## Task 4: Verify Local CLI Contracts

- [ ] **Step 1: Verify xpoz registry JSON**

Run:

```bash
uv --no-config run --frozen fashion-radar external-tool-adapters --adapter xpoz_mcp --format json
```

Expected: JSON contains one adapter with `id="xpoz_mcp"`,
`platform_label="community"`, `recommended_input_format="json"`, and standard
handoff commands.

- [ ] **Step 2: Verify xpoz template JSON**

Run:

```bash
uv --no-config run --frozen fashion-radar external-tool-template --adapter xpoz_mcp --format json
```

Expected: output is `{"items": [...]}` with two importable rows using
`source_name="XPOZ MCP Export"` and `platform="community"`.

- [ ] **Step 3: Verify xpoz readiness JSON**

Run:

```bash
uv --no-config run --frozen fashion-radar external-tool-readiness --adapter xpoz_mcp --format json
```

Expected: `checks[0].status == "not_applicable"` and `checks[0].command is null`.

- [ ] **Step 4: Verify xpoz workflow JSON**

Run:

```bash
uv --no-config run --frozen fashion-radar external-tool-workflow --adapter xpoz_mcp --format json
```

Expected: workflow prints local handoff steps only.

## Task 5: Code Review

- [ ] **Step 1: Create code review prompt**

Create `docs/reviews/opencode-stage-115-code-review-prompt.md` summarizing the
Stage 115 diff and asking for Critical/Important issues only.

- [ ] **Step 2: Run local opencode code review**

Run:

```bash
opencode run --model zhipuai-coding-plan/glm-5.2 --variant max --dir /home/ubuntu/fashion-radar "$(cat docs/reviews/opencode-stage-115-code-review-prompt.md)" > docs/reviews/opencode-stage-115-code-review.md
```

- [ ] **Step 3: Address Critical/Important findings**

Use `superpowers:receiving-code-review`. Verify each finding against the
codebase before changing anything. Fix Critical/Important findings before
release gate.

## Task 6: Release Gate, Commit, Push, CI

- [ ] **Step 1: Run full release gate**

```bash
uv --no-config run --frozen python scripts/check_release_hygiene.py
env -u ALL_PROXY -u all_proxy uv --no-config run --frozen pytest
uv --no-config run --frozen ruff check .
uv --no-config run --frozen ruff format --check .
UV_NO_CONFIG=1 uv lock --check
if rg -n 'tuna|aliyun|ustc|huaweicloud|mirror|index-url|extra-index-url|find-links' uv.lock; then exit 1; fi
git diff --exit-code -- uv.lock pyproject.toml
git diff --check
```

- [ ] **Step 2: Stage intended files only**

```bash
git add -- \
  src/fashion_radar/external_tool_adapters.py \
  src/fashion_radar/external_tool_readiness.py \
  tests/test_external_tool_adapters.py \
  tests/test_external_tool_readiness.py \
  tests/test_external_tool_templates.py \
  tests/test_external_tool_contract_parity.py \
  tests/test_cli.py \
  tests/test_first_run_smoke.py \
  scripts/check_first_run_smoke.py \
  README.md \
  docs/first-run.md \
  docs/cli-reference.md \
  tests/test_cli_docs.py \
  docs/superpowers/specs/2026-06-19-stage-115-xpoz-adapter-metadata-design.md \
  docs/superpowers/plans/2026-06-19-stage-115-xpoz-adapter-metadata-plan.md \
  docs/reviews/opencode-stage-115-plan-review-prompt.md \
  docs/reviews/opencode-stage-115-plan-rereview-prompt.md \
  docs/reviews/opencode-stage-115-plan-rereview.md \
  docs/reviews/opencode-stage-115-code-review-prompt.md \
  docs/reviews/opencode-stage-115-code-review.md
```

- [ ] **Step 3: Run staged checks**

```bash
git diff --cached --check
if git diff --cached --name-only | rg -x 'uv.lock'; then exit 1; fi
git grep --cached -n -E 'gh[pousr]_[A-Za-z0-9]{36,255}|github_pat_[A-Za-z0-9_]{82,255}|-----BEGIN [A-Z0-9 ]*PRIVATE KEY-----' -- . ':!uv.lock' && exit 1 || true
```

- [ ] **Step 4: Commit**

```bash
git commit -m "Add XPOZ external tool adapter metadata"
```

- [ ] **Step 5: Push with temporary auth only**

Use a one-shot Git HTTP `extraheader`; do not save the GitHub token to remote
URLs or git config. Confirm after push:

```bash
git config --get-all http.https://github.com/.extraheader || true
git remote -v | sed -E 's#(https://)[^/@]+@#\1***@#g'
```

- [ ] **Step 6: Verify CI**

Poll GitHub Actions for the pushed commit and require `completed success`.

## Self-Review

- Spec coverage: The plan adds an XPOZ metadata target, readiness behavior,
  template output, first-run smoke fixtures, docs matrices, local CLI checks,
  review artifacts, and full release gate.
- Placeholder scan: No placeholder implementation steps are left.
- Type consistency: The adapter id, source name, platform label, format,
  pattern, and description are identical across runtime, tests, smoke, and docs.
