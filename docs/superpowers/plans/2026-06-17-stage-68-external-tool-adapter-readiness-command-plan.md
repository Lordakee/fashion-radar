# Stage 68 External Tool Adapter Readiness Command Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add the existing `external-tool-readiness` command to each `external-tool-adapters` registry entry's `recommended_commands` list.

**Architecture:** Keep `external-tool-adapters` print-only and modify only the printed command list. The adapter builder already has all resolved metadata needed for the readiness command; `_adapter` will pass `adapter_id` into `_recommended_commands`, which will insert one quoted command string without running readiness or touching local paths.

**Tech Stack:** Python 3.11, Typer CLI, Pydantic models, pytest, ruff, uv.

---

## File Map

- Modify `src/fashion_radar/external_tool_adapters.py`
  - Pass `adapter_id` into `_recommended_commands`.
  - Add one `external-tool-readiness` command after `community-signal-profile`.
- Modify `tests/test_external_tool_adapters.py`
  - Update stable command order and command assertions.
- Modify `tests/test_external_tool_templates.py`
  - Assert template command guidance inherits the readiness command while
    JSON/CSV handoff output remains rows-only.
- Modify `tests/test_cli.py`
  - Add JSON assertion that adapter commands include readiness.
- Modify `scripts/check_first_run_smoke.py`
  - Add validator coverage for adapter recommended readiness command if the
    real payload includes commands.
- Modify `tests/test_first_run_smoke.py`
  - Update fixture payload if validator needs representative commands.
- Modify docs:
  - `README.md`
  - `docs/cli-reference.md`
  - `docs/community-signal-import.md`
  - `docs/community-signal-quality.md`
  - `docs/source-boundaries.md`
  - `docs/architecture.md`
  - `docs/github-upload-checklist.md`
  - `AGENTS.md`
  - `CHANGELOG.md`
- Create review artifacts:
  - `docs/reviews/opencode-stage-68-plan-review-prompt.md`
  - `docs/reviews/opencode-stage-68-plan-review.md`
  - `docs/reviews/opencode-stage-68-plan-rereview-prompt.md`
  - `docs/reviews/opencode-stage-68-plan-rereview.md`
  - `docs/reviews/opencode-stage-68-plan-final-rereview-prompt.md`
  - `docs/reviews/opencode-stage-68-plan-final-rereview.md`
  - `docs/reviews/opencode-stage-68-code-review-prompt.md`
  - `docs/reviews/opencode-stage-68-code-review.md`

## Task 1: Adapter Registry Tests

**Files:**
- Modify: `tests/test_external_tool_adapters.py`

- [ ] **Step 1: Update command prefix expectation**

In `test_instaloader_adapter_has_expected_mapping_and_commands`, change:

```python
assert [command[:2] for command in commands] == [
    ["fashion-radar", "community-signal-profile"],
    ["fashion-radar", "community-handoff-manifest"],
    ["fashion-radar", "community-handoff-workflow"],
    ["fashion-radar", "community-signal-lint-dir"],
    ["fashion-radar", "community-handoff-check-dir"],
    ["fashion-radar", "import-signals-dir"],
    ["fashion-radar", "import-signals-dir"],
    ["fashion-radar", "imported-review-workflow"],
]
```

to:

```python
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
```

- [ ] **Step 2: Add readiness command assertions**

After the command prefix assertion, add:

```python
readiness_command = commands[1]
assert readiness_command[readiness_command.index("--adapter") + 1] == "instaloader"
assert readiness_command[readiness_command.index("--directory") + 1] == "exports"
assert readiness_command[readiness_command.index("--input-format") + 1] == "json"
assert readiness_command[readiness_command.index("--pattern") + 1] == "*.json"
assert readiness_command[readiness_command.index("--source-name") + 1] == "Instaloader Export"
assert readiness_command[readiness_command.index("--as-of") + 1] == "2026-06-13T12:00:00+00:00"
assert readiness_command[readiness_command.index("--format") + 1] == "table"
```

Then shift the existing manifest assertions from `commands[1]` to
`commands[2]`, dry-run assertion from `commands[5]` to `commands[6]`, and
non-dry-run assertion from `commands[6]` to `commands[7]`.

- [ ] **Step 3: Update focused path quoting test indexes**

In `test_registry_quotes_paths_pattern_and_source_names`, keep the existing
`adapter.recommended_commands[1]` assertions so they now validate the new
readiness command's quoting, and add the parallel
`adapter.recommended_commands[2]` assertions so the shifted manifest command is
still validated too. The final assertions in that test should include:

```python
assert "'exports ? # & %'" in adapter.recommended_commands[1]
assert "'config ? # & %'" in adapter.recommended_commands[1]
assert "'data ? # & %'" in adapter.recommended_commands[1]
assert "--source-name 'X Search Export'" in adapter.recommended_commands[1]
assert "'exports ? # & %'" in adapter.recommended_commands[2]
assert "'config ? # & %'" in adapter.recommended_commands[2]
assert "'data ? # & %'" in adapter.recommended_commands[2]
assert "--source-name 'X Search Export'" in adapter.recommended_commands[2]
```

- [ ] **Step 4: Run focused test and verify failure**

Run:

```bash
uv --no-config run --frozen pytest tests/test_external_tool_adapters.py -q
```

Expected: fail because the readiness command is not yet in the adapter command
list.

## Task 2: Implement Adapter Readiness Command

**Files:**
- Modify: `src/fashion_radar/external_tool_adapters.py`

- [ ] **Step 1: Pass adapter id into `_recommended_commands`**

In `_adapter(...)`, change the `_recommended_commands(...)` call to include:

```python
adapter_id=adapter_id,
```

Add `adapter_id: str` to `_recommended_commands(...)` parameters.

- [ ] **Step 2: Insert readiness command**

Inside `_recommended_commands`, add this command immediately after
`community-signal-profile`:

```python
        _shell_command(
            "fashion-radar",
            "external-tool-readiness",
            "--adapter",
            adapter_id,
            "--directory",
            directory_text,
            "--config-dir",
            config_text,
            "--data-dir",
            data_text,
            "--as-of",
            as_of_text,
            "--input-format",
            input_format,
            "--pattern",
            pattern,
            "--source-name",
            source_name,
            "--format",
            "table",
        ),
```

- [ ] **Step 3: Run focused test**

Run:

```bash
uv --no-config run --frozen pytest tests/test_external_tool_adapters.py -q
```

Expected: pass.

## Task 3: CLI, Smoke, Docs

**Files:**
- Modify: `tests/test_external_tool_templates.py`
- Modify: `tests/test_cli.py`
- Modify: `scripts/check_first_run_smoke.py`
- Modify: `tests/test_first_run_smoke.py`
- Modify docs listed in the file map.

- [ ] **Step 1: Add template inheritance coverage**

In `tests/test_external_tool_templates.py`, add a focused test:

```python
def test_template_command_guidance_includes_external_tool_readiness() -> None:
    template = build_external_tool_template(
        adapter_id="instaloader",
        directory=Path("./exports"),
        config_dir=Path("./configs"),
        data_dir=Path("./data"),
        as_of="2026-06-13T12:00:00Z",
    )

    assert any(
        "fashion-radar external-tool-readiness" in command
        for command in template.recommended_commands
    )
    json_output = render_external_tool_template_json(template)
    csv_output = render_external_tool_template_csv(template)

    assert "external-tool-readiness" not in json_output
    assert "external-tool-readiness" not in csv_output
```

This documents that template table/model guidance inherits adapter command
guidance, while JSON/CSV handoff-row output remains unchanged.

- [ ] **Step 2: Update CLI JSON assertion**

In `test_external_tool_adapters_command_prints_json`, add:

```python
commands = payload["adapters"][0]["recommended_commands"]
assert any("fashion-radar external-tool-readiness" in command for command in commands)
```

- [ ] **Step 3: Update CLI filtered adapter quoting assertion**

In `test_external_tool_adapters_command_filters_adapter_and_quotes_paths`, do
not leave the test silently checking only the new readiness command at index
`1`. Replace:

```python
command = payload["adapters"][0]["recommended_commands"][1]
assert "'exports ? # & %'" in command
assert "'config ? # & %'" in command
assert "'data ? # & %'" in command
assert "--source-name 'Instaloader Export'" in command
```

with:

```python
commands = payload["adapters"][0]["recommended_commands"]
readiness_command = commands[1]
manifest_command = commands[2]
for command in (readiness_command, manifest_command):
    assert "'exports ? # & %'" in command
    assert "'config ? # & %'" in command
    assert "'data ? # & %'" in command
    assert "--source-name 'Instaloader Export'" in command
assert "fashion-radar external-tool-readiness" in readiness_command
assert "fashion-radar community-handoff-manifest" in manifest_command
```

- [ ] **Step 4: Update smoke adapter fixture and validator**

In `tests/test_first_run_smoke.py::external_tool_adapters_payload`, include a
representative first adapter `recommended_commands` list:

```python
"recommended_commands": [
    "fashion-radar community-signal-profile --format json",
    "fashion-radar external-tool-readiness --adapter rednote_mcp --directory exports --config-dir configs --data-dir data --as-of 2026-06-13T12:00:00+00:00 --input-format json --pattern '*.json' --source-name 'Rednote MCP Export' --format table",
],
```

In `scripts/check_first_run_smoke.py::validate_external_tool_adapters`, add:

```python
recommended_commands = first_adapter.get("recommended_commands")
if not isinstance(recommended_commands, list):
    raise SmokeError(f"{command_name} first adapter recommended_commands must be a list")
readiness_commands = [
    str(command)
    for command in recommended_commands
    if "fashion-radar external-tool-readiness" in str(command)
]
if not readiness_commands:
    raise SmokeError(f"{command_name} first adapter missing external-tool-readiness command")
readiness_command = readiness_commands[0]
for expected in ("--adapter", "rednote_mcp", "--input-format", "json", "--format", "table"):
    if expected not in readiness_command:
        raise SmokeError(f"{command_name} readiness command missing {expected!r}")
```

In `tests/test_first_run_smoke.py::test_validate_external_tool_adapters_requires_print_only_registry_contract`,
add negative coverage for each new validator branch:

```python
missing_commands = external_tool_adapters_payload()
missing_commands["adapters"][0].pop("recommended_commands")
with pytest.raises(SmokeError, match="recommended_commands must be a list"):
    smoke.validate_external_tool_adapters("external-tool-adapters", missing_commands)

missing_readiness = external_tool_adapters_payload()
missing_readiness["adapters"][0]["recommended_commands"] = [
    "fashion-radar community-signal-profile --format json"
]
with pytest.raises(SmokeError, match="missing external-tool-readiness command"):
    smoke.validate_external_tool_adapters("external-tool-adapters", missing_readiness)

missing_token = external_tool_adapters_payload()
missing_token["adapters"][0]["recommended_commands"] = [
    "fashion-radar external-tool-readiness --adapter rednote_mcp --format table"
]
with pytest.raises(SmokeError, match="readiness command missing '--input-format'"):
    smoke.validate_external_tool_adapters("external-tool-adapters", missing_token)
```

- [ ] **Step 5: Update docs**

In external adapter registry docs, add:

```markdown
Each adapter command list includes `external-tool-readiness` as an optional
local read-only preflight command, while `external-tool-adapters` itself remains
print-only and does not run readiness or perform PATH lookup.
```

Also mention where useful that `external-tool-template` JSON/CSV handoff rows
remain importable row output only, while table/model guidance can include the
same adapter recommended command list.

Apply this to:

- `README.md`
- `docs/cli-reference.md`
- `docs/community-signal-import.md`
- `docs/community-signal-quality.md`
- `docs/source-boundaries.md`
- `docs/architecture.md`
- `docs/github-upload-checklist.md`
- `AGENTS.md`
- `CHANGELOG.md`

- [ ] **Step 6: Run integrated tests**

Run:

```bash
uv --no-config run --frozen pytest tests/test_external_tool_adapters.py tests/test_external_tool_templates.py tests/test_cli.py tests/test_first_run_smoke.py tests/test_cli_docs.py -q -k "external_tool_adapters or external_tool_template or run_first_run_flow"
```

Expected: pass.

## Task 4: Verification, Review, Commit, Push

**Files:**
- Create: `docs/reviews/opencode-stage-68-code-review-prompt.md`
- Create: `docs/reviews/opencode-stage-68-code-review.md`

- [ ] **Step 1: Run targeted verification**

Run:

```bash
uv --no-config run --frozen pytest tests/test_external_tool_adapters.py tests/test_external_tool_templates.py tests/test_external_tool_readiness.py tests/test_external_tool_workflow.py tests/test_cli.py tests/test_first_run_smoke.py tests/test_cli_docs.py -q
```

Expected: pass.

- [ ] **Step 2: Run lint/format/release hygiene and full suite**

Run:

```bash
uv --no-config run --frozen ruff check src/fashion_radar/external_tool_adapters.py tests/test_external_tool_adapters.py tests/test_external_tool_templates.py tests/test_cli.py scripts/check_first_run_smoke.py tests/test_first_run_smoke.py tests/test_cli_docs.py
uv --no-config run --frozen ruff format --check src/fashion_radar/external_tool_adapters.py tests/test_external_tool_adapters.py tests/test_external_tool_templates.py tests/test_cli.py scripts/check_first_run_smoke.py tests/test_first_run_smoke.py tests/test_cli_docs.py
uv --no-config run --frozen python scripts/check_release_hygiene.py
git diff --check
uv --no-config run --frozen pytest
```

Expected: pass.

- [ ] **Step 3: Request local opencode code review**

Create `docs/reviews/opencode-stage-68-code-review-prompt.md` with:

```markdown
Review Stage 68 external-tool-adapter readiness command implementation in
/home/ubuntu/fashion-radar.

Scope:
- `external-tool-adapters` recommended_commands should now include one
  `external-tool-readiness` command per adapter.
- `external-tool-adapters` must remain print-only and must not call readiness,
  inspect directories, read handoff files, open SQLite, or execute generated
  commands.
- `external-tool-readiness` and `external-tool-workflow` semantics should remain
  unchanged.
- `external-tool-template` JSON/CSV handoff rows should remain rows-only; its
  table/model recommended command guidance may include the inherited readiness
  command.

Return only Critical or Important findings, plus blocking test gaps.
```

Run:

```bash
opencode run --model zhipuai-coding-plan/glm-5.2 --variant max --dir /home/ubuntu/fashion-radar "$(cat docs/reviews/opencode-stage-68-code-review-prompt.md)" > docs/reviews/opencode-stage-68-code-review.md
```

Expected: no Critical or Important findings. Fix any Critical or Important
findings and rerun relevant verification/review.

- [ ] **Step 4: Commit and push**

Run:

```bash
git status --short
git add src/fashion_radar/external_tool_adapters.py tests/test_external_tool_adapters.py tests/test_external_tool_templates.py tests/test_cli.py scripts/check_first_run_smoke.py tests/test_first_run_smoke.py tests/test_cli_docs.py README.md docs/cli-reference.md docs/community-signal-import.md docs/community-signal-quality.md docs/source-boundaries.md docs/architecture.md docs/github-upload-checklist.md AGENTS.md CHANGELOG.md docs/superpowers/specs/2026-06-17-stage-68-external-tool-adapter-readiness-command-design.md docs/superpowers/plans/2026-06-17-stage-68-external-tool-adapter-readiness-command-plan.md docs/reviews/opencode-stage-68-plan-review-prompt.md docs/reviews/opencode-stage-68-plan-review.md docs/reviews/opencode-stage-68-plan-rereview-prompt.md docs/reviews/opencode-stage-68-plan-rereview.md docs/reviews/opencode-stage-68-plan-final-rereview-prompt.md docs/reviews/opencode-stage-68-plan-final-rereview.md docs/reviews/opencode-stage-68-code-review-prompt.md docs/reviews/opencode-stage-68-code-review.md
git commit -m "Add adapter readiness command guidance"
basic_auth=$(printf 'x-access-token:%s' "$(cat /home/ubuntu/.config/fashion-radar/github-token)" | base64 -w0)
git -c http.version=HTTP/1.1 -c http.extraHeader="AUTHORIZATION: basic $basic_auth" push origin HEAD:main
```

- [ ] **Step 5: Verify remote CI**

Use the GitHub API with the token file to confirm CI succeeds for the pushed
commit.

## Self-Review Checklist

- Scope is narrow: one printed adapter registry command, no new CLI.
- `external-tool-adapters` remains print-only.
- No generated command is executed.
- Tests cover command order, quoting, CLI JSON, and smoke validation.
- Docs preserve boundary language.
