# Stage 116 Directory Readiness Samples Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add docs and drift tests that connect the checked-in community tool directory examples to the existing external-tool readiness/workflow preflight commands.

**Architecture:** Keep this as a docs/tests-only node. The runtime builders already support `adapter_id`, `directory`, `input_format`, `pattern`, and `source_name` overrides, so the implementation pins those contracts with tests and updates the directory example docs with copyable local commands.

**Tech Stack:** Python 3.11, Typer CLI docs, pytest, shlex command parsing, uv, ruff, local opencode review with `zhipuai-coding-plan/glm-5.2 --variant max`.

---

## Files

- Modify: `tests/test_community_tool_handoff_directory_examples.py`
- Modify: `tests/test_cli_docs.py`
- Modify: `examples/community-tool-handoff-directory.example/README.md`
- Modify: `docs/community-signal-import.md`
- Create: `docs/reviews/opencode-stage-116-plan-review-prompt.md`
- Create later: `docs/reviews/opencode-stage-116-plan-review.md`
- Create later: `docs/reviews/opencode-stage-116-code-review-prompt.md`
- Create later: `docs/reviews/opencode-stage-116-code-review.md`

Do not modify `src/`, `uv.lock`, `pyproject.toml`, schemas, collectors, source
packs, entity packs, dashboard, importers, scoring, reports, CI, or GitHub
workflows.

## Task 0: Plan Review

- [ ] **Step 1: Create the plan review prompt**

Create `docs/reviews/opencode-stage-116-plan-review-prompt.md` with the
current Stage 116 design and plan review request.

- [ ] **Step 2: Run local opencode plan review**

Run:

```bash
opencode run --model zhipuai-coding-plan/glm-5.2 --variant max --dir /home/ubuntu/fashion-radar "$(cat docs/reviews/opencode-stage-116-plan-review-prompt.md)" > docs/reviews/opencode-stage-116-plan-review.md
```

Expected: review completes and explicitly says whether there are Critical or
Important blockers.

- [ ] **Step 3: Resolve Critical/Important plan findings before coding**

If the review identifies Critical or Important findings, update the design,
plan, or scope before Task 1.

## Task 1: Write Failing Tests

- [ ] **Step 1: Import command parsing and builder helpers**

In `tests/test_community_tool_handoff_directory_examples.py`, add:

```python
import shlex
```

and:

```python
from fashion_radar.external_tool_readiness import build_external_tool_readiness
from fashion_radar.external_tool_workflow import build_external_tool_workflow
```

- [ ] **Step 2: Add readiness/workflow override test**

Add this test after
`test_directory_example_signal_files_lint_and_load_cleanly`:

```python
@pytest.mark.parametrize(
    ("directory", "expected_names", "input_format", "pattern"),
    DIRECTORY_EXAMPLES,
    ids=_example_ids(),
)
def test_directory_examples_build_external_tool_readiness_and_workflow_with_overrides(
    directory: Path,
    expected_names: tuple[str, ...],
    input_format: str,
    pattern: str,
) -> None:
    source_name = "External Community Tool"

    def flag_value(tokens: list[str], flag: str) -> str:
        return tokens[tokens.index(flag) + 1]

    assert sorted(path.name for path in directory.glob(pattern)) == sorted(expected_names)

    readiness = build_external_tool_readiness(
        adapter_id="generic_community_export",
        directory=directory,
        input_format=input_format,
        pattern=pattern,
        source_name=source_name,
        which=lambda _command: None,
    )
    workflow = build_external_tool_workflow(
        adapter_id="generic_community_export",
        directory=directory,
        input_format=input_format,
        pattern=pattern,
        source_name=source_name,
    )

    for payload in (readiness, workflow):
        assert payload.adapter_id == "generic_community_export"
        assert payload.display_name == "Generic Community Export"
        assert payload.platform_label == "community"
        assert payload.directory == str(directory)
        assert payload.input_format == input_format
        assert payload.pattern == pattern
        assert payload.source_name == source_name
        assert payload.step_count == len(payload.steps)

    assert readiness.execution_mode == "local_read_only"
    assert readiness.checks[0].status == "not_applicable"
    assert readiness.checks[0].command is None
    assert workflow.execution_mode == "print_only"

    readiness_commands = {step.name: shlex.split(step.command) for step in readiness.steps}
    workflow_commands = {step.name: shlex.split(step.command) for step in workflow.steps}

    readiness_workflow = readiness_commands["print_external_tool_workflow"]
    assert readiness_workflow[:2] == ["fashion-radar", "external-tool-workflow"]
    assert flag_value(readiness_workflow, "--adapter") == "generic_community_export"
    assert flag_value(readiness_workflow, "--directory") == str(directory)
    assert flag_value(readiness_workflow, "--input-format") == input_format
    assert flag_value(readiness_workflow, "--pattern") == pattern
    assert flag_value(readiness_workflow, "--source-name") == source_name

    workflow_readiness = workflow_commands["check_external_tool_readiness"]
    assert workflow_readiness[:2] == ["fashion-radar", "external-tool-readiness"]
    assert flag_value(workflow_readiness, "--adapter") == "generic_community_export"
    assert flag_value(workflow_readiness, "--directory") == str(directory)
    assert flag_value(workflow_readiness, "--input-format") == input_format
    assert flag_value(workflow_readiness, "--pattern") == pattern
    assert flag_value(workflow_readiness, "--source-name") == source_name

    for commands in (readiness_commands, workflow_commands):
        lint_tokens = commands["lint_export_directory"]
        assert lint_tokens[:3] == [
            "fashion-radar",
            "community-signal-lint-dir",
            str(directory),
        ]
        assert flag_value(lint_tokens, "--input-format") == input_format
        assert flag_value(lint_tokens, "--pattern") == pattern
        assert flag_value(lint_tokens, "--source-name") == source_name
```

- [ ] **Step 3: Tighten docs drift test**

In `tests/test_cli_docs.py::test_external_community_tool_directory_example_docs_are_linked_and_bounded`,
append to the existing test body. `import_doc` is already defined near the top
of that test; add an `example_readme` read and assert both that README and
`docs/community-signal-import.md` include the concrete readiness/workflow
commands for the CSV and JSON directories. Parse bash blocks with
`_bash_blocks(...)`, `_shell_commands(...)`, and `shlex.split(...)` so the test
pins command names and flag values without depending on shell quote style. For
`docs/community-signal-import.md`, scope the assertion to
`## External Tool Export Directory Examples`. Assert each required flag appears
exactly once and that the scoped readiness/workflow command set is exactly the
four expected CSV/JSON preflight commands:

```python
example_readme = _read(
    ROOT / "examples" / "community-tool-handoff-directory.example" / "README.md"
)
directory_preflight_cases = (
    ("examples/community-tool-handoff-directory.example/csv", "csv", "*.csv"),
    ("examples/community-tool-handoff-directory.example/json", "json", "*.json"),
)

def _fashion_radar_command_tokens(text: str) -> list[tuple[str, list[str]]]:
    commands: list[tuple[str, list[str]]] = []
    for block in _bash_blocks(text):
        for command in _shell_commands(block):
            match = FASHION_RADAR_COMMAND_RE.search(command)
            if match is not None:
                commands.append((match.group("name"), shlex.split(command)))
    return commands

def _flag_value(tokens: list[str], flag: str) -> str:
    assert tokens.count(flag) == 1, f"Expected exactly one {flag!r} in {tokens!r}"
    return tokens[tokens.index(flag) + 1]

for label, _doc_text, scope_text in (
    (
        "examples/community-tool-handoff-directory.example/README.md",
        example_readme,
        example_readme,
    ),
    (
        "docs/community-signal-import.md",
        import_doc,
        _markdown_section(import_doc, "## External Tool Export Directory Examples"),
    ),
):
    command_tokens = _fashion_radar_command_tokens(scope_text)
    for directory, input_format, pattern in directory_preflight_cases:
        matching = [
            (name, tokens)
            for name, tokens in command_tokens
            if name in {"external-tool-readiness", "external-tool-workflow"}
            and _flag_value(tokens, "--directory") == directory
            and _flag_value(tokens, "--input-format") == input_format
            and _flag_value(tokens, "--pattern") == pattern
        ]
        assert len(matching) == 2, f"{label} missing command pair for {directory}"
```

- [ ] **Step 4: Run RED tests**

Run:

```bash
env -u ALL_PROXY -u all_proxy uv --no-config run --frozen pytest \
  tests/test_community_tool_handoff_directory_examples.py::test_directory_examples_build_external_tool_readiness_and_workflow_with_overrides \
  tests/test_cli_docs.py::test_external_community_tool_directory_example_docs_are_linked_and_bounded \
  -q
```

Expected: the new builder test passes or fails only because of test mistakes;
the docs test fails because the README/import docs do not yet contain the new
preflight snippets.

## Task 2: Update Directory Example Docs

- [ ] **Step 1: Update the checked-in directory example README**

In `examples/community-tool-handoff-directory.example/README.md`, add this
block after the existing CSV/JSON bullets and before the explanatory paragraph
about separate `csv/` and `json/` directories:

````markdown
Optional preflight commands from the repository root:

```bash
uv run fashion-radar external-tool-readiness --adapter generic_community_export --directory examples/community-tool-handoff-directory.example/csv --input-format csv --pattern "*.csv" --source-name "External Community Tool" --format table
uv run fashion-radar external-tool-workflow --adapter generic_community_export --directory examples/community-tool-handoff-directory.example/csv --input-format csv --pattern "*.csv" --source-name "External Community Tool" --format table
uv run fashion-radar external-tool-readiness --adapter generic_community_export --directory examples/community-tool-handoff-directory.example/json --input-format json --pattern "*.json" --source-name "External Community Tool" --format table
uv run fashion-radar external-tool-workflow --adapter generic_community_export --directory examples/community-tool-handoff-directory.example/json --input-format json --pattern "*.json" --source-name "External Community Tool" --format table
```
````

- [ ] **Step 2: Update community signal import docs**

In `docs/community-signal-import.md`, section
`## External Tool Export Directory Examples`, add this sentence before the
command block:

```markdown
Run `external-tool-readiness` and `external-tool-workflow` first when you want
a local preflight for the checked-in CSV or JSON example directory; both
commands remain local guidance and do not run upstream tools.
```

Replace the existing two-command block with:

```bash
uv run fashion-radar external-tool-readiness --adapter generic_community_export --directory examples/community-tool-handoff-directory.example/csv --input-format csv --pattern "*.csv" --source-name "External Community Tool" --format table
uv run fashion-radar external-tool-workflow --adapter generic_community_export --directory examples/community-tool-handoff-directory.example/csv --input-format csv --pattern "*.csv" --source-name "External Community Tool" --format table
uv run fashion-radar community-signal-lint-dir examples/community-tool-handoff-directory.example/csv --input-format csv --pattern "*.csv" --source-name "External Community Tool" --strict
uv run fashion-radar external-tool-readiness --adapter generic_community_export --directory examples/community-tool-handoff-directory.example/json --input-format json --pattern "*.json" --source-name "External Community Tool" --format table
uv run fashion-radar external-tool-workflow --adapter generic_community_export --directory examples/community-tool-handoff-directory.example/json --input-format json --pattern "*.json" --source-name "External Community Tool" --format table
uv run fashion-radar import-signals-dir examples/community-tool-handoff-directory.example/json --format json --pattern "*.json" --source-name "External Community Tool" --data-dir "$PWD/data" --dry-run --output-format json
```

- [ ] **Step 3: Run GREEN focused tests**

Run:

```bash
env -u ALL_PROXY -u all_proxy uv --no-config run --frozen pytest \
  tests/test_community_tool_handoff_directory_examples.py::test_directory_examples_build_external_tool_readiness_and_workflow_with_overrides \
  tests/test_cli_docs.py::test_external_community_tool_directory_example_docs_are_linked_and_bounded \
  -q
```

Expected: all selected tests pass.

## Task 3: Adjacent Verification

- [ ] **Step 1: Run adjacent tests**

Run:

```bash
env -u ALL_PROXY -u all_proxy uv --no-config run --frozen pytest \
  tests/test_external_tool_readiness.py \
  tests/test_external_tool_workflow.py \
  tests/test_community_tool_handoff_directory_examples.py \
  tests/test_cli_docs.py \
  -q
```

Expected: all selected adjacent tests pass.

- [ ] **Step 2: Create code review prompt**

Create `docs/reviews/opencode-stage-116-code-review-prompt.md` summarizing the
Stage 116 code/docs changes, files touched, and verification commands.

- [ ] **Step 3: Run local opencode code review**

Run:

```bash
opencode run --model zhipuai-coding-plan/glm-5.2 --variant max --dir /home/ubuntu/fashion-radar "$(cat docs/reviews/opencode-stage-116-code-review-prompt.md)" > docs/reviews/opencode-stage-116-code-review.md
```

Expected: review completes and explicitly lists no Critical or Important
blockers, or lists findings to fix before release.

- [ ] **Step 4: Fix Critical/Important review findings**

If the review identifies Critical or Important findings, fix them and rerun the
focused and adjacent tests.

## Task 4: Release Gate, Commit, Push

- [ ] **Step 1: Run full release gate**

Run:

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

Expected: every command exits 0, and there is no mirror URL in `uv.lock`.

- [ ] **Step 2: Stage intended files only**

Run:

```bash
git add \
  docs/superpowers/specs/2026-06-19-stage-116-directory-readiness-samples-design.md \
  docs/superpowers/plans/2026-06-19-stage-116-directory-readiness-samples-plan.md \
  docs/reviews/opencode-stage-116-plan-review-prompt.md \
  docs/reviews/opencode-stage-116-plan-review.md \
  docs/reviews/opencode-stage-116-code-review-prompt.md \
  docs/reviews/opencode-stage-116-code-review.md \
  tests/test_community_tool_handoff_directory_examples.py \
  tests/test_cli_docs.py \
  examples/community-tool-handoff-directory.example/README.md \
  docs/community-signal-import.md
git diff --cached --name-only
git diff --cached --check
```

Expected: only intended files are staged, and staged whitespace check exits 0.

- [ ] **Step 3: Commit**

Run:

```bash
git commit -m "Document directory readiness preflight samples"
```

- [ ] **Step 4: Push without persisting credentials**

Use a temporary GitHub auth extraheader for the push only. After push, confirm
there is no persisted extraheader and that `git remote -v` does not expose a
token.

- [ ] **Step 5: Verify CI**

Poll the GitHub Actions run for the pushed commit until it passes or fails.

- [ ] **Step 6: Handoff Summary**

Write a short Handoff Summary with repo status, verified commands, uncommitted
files, and the next recommended stage. Do not include large diffs or logs.
