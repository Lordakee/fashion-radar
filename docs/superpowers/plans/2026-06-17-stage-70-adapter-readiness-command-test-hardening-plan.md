# Stage 70 Adapter Readiness Command Test Hardening Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Harden tests and first-run smoke validation for the readiness command printed in external tool adapter recommended commands.

**Architecture:** This is a test/smoke-validation cleanup. The adapter registry runtime behavior stays unchanged; the smoke validator parses the already-printed command with `shlex.split` and checks stable structure.

**Tech Stack:** Python 3.11, pytest, ruff, uv, standard-library `shlex`.

---

## File Map

- Modify `tests/test_external_tool_adapters.py`
  - Add explicit readiness `--config-dir` and `--data-dir` value assertions.
- Modify `tests/test_cli.py`
  - Parse readiness recommended commands in CLI JSON tests.
  - Assert stable readiness flag/value pairs and non-empty path values.
- Modify `scripts/check_first_run_smoke.py`
  - Parse readiness recommended command with `shlex.split`.
  - Add structured flag/value validation.
- Modify `tests/test_first_run_smoke.py`
  - Add negative cases for missing `--format table`.
  - Add negative case for malformed shell quoting.
- Create review artifacts:
  - `docs/reviews/opencode-stage-70-plan-review-prompt.md`
  - `docs/reviews/opencode-stage-70-plan-review.md`
  - `docs/reviews/opencode-stage-70-code-review-prompt.md`
  - `docs/reviews/opencode-stage-70-code-review.md`

## Task 1: Adapter Unit Test Explicitness

**Files:**
- Modify: `tests/test_external_tool_adapters.py`

- [ ] **Step 1: Run the current focused adapter test**

Run:

```bash
uv --no-config run --frozen pytest tests/test_external_tool_adapters.py::test_instaloader_adapter_has_expected_mapping_and_commands -q
```

Expected: pass.

- [ ] **Step 2: Add explicit config/data readiness assertions**

In `test_instaloader_adapter_has_expected_mapping_and_commands`, after:

```python
assert readiness_command[readiness_command.index("--directory") + 1] == "exports"
```

add:

```python
assert readiness_command[readiness_command.index("--config-dir") + 1] == "configs"
assert readiness_command[readiness_command.index("--data-dir") + 1] == "data"
```

- [ ] **Step 3: Run the focused adapter test**

Run:

```bash
uv --no-config run --frozen pytest tests/test_external_tool_adapters.py::test_instaloader_adapter_has_expected_mapping_and_commands -q
```

Expected: pass.

## Task 2: First-Run Smoke Readiness Command Parser

**Files:**
- Modify: `tests/test_cli.py`

- [ ] **Step 1: Run the current CLI adapter tests**

Run:

```bash
uv --no-config run --frozen pytest tests/test_cli.py::test_external_tool_adapters_command_prints_json tests/test_cli.py::test_external_tool_adapters_command_filters_adapter_and_quotes_paths -q
```

Expected: pass.

- [ ] **Step 2: Add token-level assertions to the default CLI JSON test**

In `test_external_tool_adapters_command_prints_json`, replace:

```python
commands = payload["adapters"][0]["recommended_commands"]
assert any("fashion-radar external-tool-readiness" in command for command in commands)
```

with:

```python
commands = payload["adapters"][0]["recommended_commands"]
readiness_command = next(
    command for command in commands if "fashion-radar external-tool-readiness" in command
)
readiness_parts = shlex.split(readiness_command)

def flag_value(flag: str) -> str:
    value = readiness_parts[readiness_parts.index(flag) + 1]
    assert value
    return value

assert readiness_parts[:2] == ["fashion-radar", "external-tool-readiness"]
assert flag_value("--adapter") == "rednote_mcp"
assert flag_value("--directory") == "exports"
assert flag_value("--config-dir")
assert flag_value("--data-dir")
assert flag_value("--as-of") == "2026-06-13T12:00:00+00:00"
assert flag_value("--input-format") == "json"
assert flag_value("--pattern") == "*.json"
assert flag_value("--source-name") == "Rednote MCP Export"
assert flag_value("--format") == "table"
```

This deliberately does not hard-code `--config-dir` or `--data-dir` default
values because the CLI resolves them from user/environment defaults.

- [ ] **Step 3: Parse the readiness command in the quoted-path CLI test**

In `test_external_tool_adapters_command_filters_adapter_and_quotes_paths`,
after:

```python
assert "fashion-radar external-tool-readiness" in readiness_command
```

add:

```python
readiness_parts = shlex.split(readiness_command)
assert readiness_parts[readiness_parts.index("--directory") + 1] == "exports ? # & %"
assert readiness_parts[readiness_parts.index("--config-dir") + 1] == "config ? # & %"
assert readiness_parts[readiness_parts.index("--data-dir") + 1] == "data ? # & %"
```

- [ ] **Step 4: Run the CLI adapter tests**

Run:

```bash
uv --no-config run --frozen pytest tests/test_cli.py::test_external_tool_adapters_command_prints_json tests/test_cli.py::test_external_tool_adapters_command_filters_adapter_and_quotes_paths -q
```

Expected: pass.

## Task 3: First-Run Smoke Readiness Command Parser

**Files:**
- Modify: `scripts/check_first_run_smoke.py`
- Modify: `tests/test_first_run_smoke.py`

- [ ] **Step 1: Run the current focused smoke validator test**

Run:

```bash
uv --no-config run --frozen pytest tests/test_first_run_smoke.py::test_validate_external_tool_adapters_requires_print_only_registry_contract -q
```

Expected: pass.

- [ ] **Step 2: Add negative tests for malformed readiness command structure**

In `test_validate_external_tool_adapters_requires_print_only_registry_contract`,
replace the existing `missing_token` command:

```python
adapters[0]["recommended_commands"] = [  # type: ignore[index]
    "fashion-radar external-tool-readiness --adapter rednote_mcp --format table"
]
```

with a command that keeps the earlier required flags and omits only
`--input-format`:

```python
adapters[0]["recommended_commands"] = [  # type: ignore[index]
    (
        "fashion-radar external-tool-readiness --adapter rednote_mcp "
        "--directory exports --config-dir configs --data-dir data "
        "--as-of 2026-06-13T12:00:00+00:00 "
        "--pattern '*.json' --source-name 'Rednote MCP Export' --format table"
    )
]
```

Then add:

```python
missing_format = external_tool_adapters_payload()
adapters = missing_format["adapters"]
assert isinstance(adapters, list)
adapters[0]["recommended_commands"] = [  # type: ignore[index]
    (
        "fashion-radar external-tool-readiness --adapter rednote_mcp "
        "--directory exports --config-dir configs --data-dir data "
        "--as-of 2026-06-13T12:00:00+00:00 --input-format json "
        "--pattern '*.json' --source-name 'Rednote MCP Export'"
    )
]
with pytest.raises(smoke.SmokeError, match="readiness command missing '--format'"):
    smoke.validate_external_tool_adapters("external-tool-adapters", missing_format)

invalid_format = external_tool_adapters_payload()
adapters = invalid_format["adapters"]
assert isinstance(adapters, list)
adapters[0]["recommended_commands"] = [  # type: ignore[index]
    (
        "fashion-radar external-tool-readiness --adapter rednote_mcp "
        "--directory exports --config-dir configs --data-dir data "
        "--as-of 2026-06-13T12:00:00+00:00 --input-format json "
        "--pattern '*.json' --source-name 'Rednote MCP Export' --format json"
    )
]
with pytest.raises(smoke.SmokeError, match="readiness output format"):
    smoke.validate_external_tool_adapters("external-tool-adapters", invalid_format)

missing_value = external_tool_adapters_payload()
adapters = missing_value["adapters"]
assert isinstance(adapters, list)
adapters[0]["recommended_commands"] = [  # type: ignore[index]
    (
        "fashion-radar external-tool-readiness --adapter rednote_mcp "
        "--directory exports --config-dir configs --data-dir data "
        "--as-of 2026-06-13T12:00:00+00:00 --input-format json "
        "--pattern '*.json' --source-name --format table"
    )
]
with pytest.raises(smoke.SmokeError, match="missing value for '--source-name'"):
    smoke.validate_external_tool_adapters("external-tool-adapters", missing_value)

trailing_flag = external_tool_adapters_payload()
adapters = trailing_flag["adapters"]
assert isinstance(adapters, list)
adapters[0]["recommended_commands"] = [  # type: ignore[index]
    (
        "fashion-radar external-tool-readiness --adapter rednote_mcp "
        "--directory exports --config-dir configs --data-dir data "
        "--as-of"
    )
]
with pytest.raises(smoke.SmokeError, match="missing value for '--as-of'"):
    smoke.validate_external_tool_adapters("external-tool-adapters", trailing_flag)

malformed_readiness = external_tool_adapters_payload()
adapters = malformed_readiness["adapters"]
assert isinstance(adapters, list)
adapters[0]["recommended_commands"] = [  # type: ignore[index]
    "fashion-radar external-tool-readiness --adapter rednote_mcp --source-name 'Rednote"
]
with pytest.raises(smoke.SmokeError, match="readiness command is not shell-parseable"):
    smoke.validate_external_tool_adapters("external-tool-adapters", malformed_readiness)
```

- [ ] **Step 3: Run the focused validator test and verify failure**

Run:

```bash
uv --no-config run --frozen pytest tests/test_first_run_smoke.py::test_validate_external_tool_adapters_requires_print_only_registry_contract -q
```

Expected: fail before the validator is hardened because the existing substring
checks do not produce the new shell-parseable error for malformed quoting.

- [ ] **Step 4: Replace substring token checks with parsed command checks**

In `validate_external_tool_adapters`, replace:

```python
readiness_command = readiness_commands[0]
for expected in ("--adapter", "rednote_mcp", "--input-format", "json", "--format", "table"):
    if expected not in readiness_command:
        raise SmokeError(f"{command_name} readiness command missing {expected!r}")
```

with:

```python
readiness_command = readiness_commands[0]
try:
    readiness_parts = shlex.split(readiness_command)
except ValueError as exc:
    raise SmokeError(
        f"{command_name} readiness command is not shell-parseable: {exc}"
    ) from exc
assert_equal(
    f"{command_name} readiness command prefix",
    readiness_parts[:2],
    ["fashion-radar", "external-tool-readiness"],
)

def required_readiness_value(flag: str) -> str:
    if flag not in readiness_parts:
        raise SmokeError(f"{command_name} readiness command missing {flag!r}")
    index = readiness_parts.index(flag)
    if index + 1 >= len(readiness_parts):
        raise SmokeError(f"{command_name} readiness command missing value for {flag!r}")
    value = readiness_parts[index + 1]
    if not value or value.startswith("--"):
        raise SmokeError(f"{command_name} readiness command missing value for {flag!r}")
    return value

assert_equal(
    f"{command_name} readiness adapter",
    required_readiness_value("--adapter"),
    "rednote_mcp",
)
assert_equal(
    f"{command_name} readiness directory",
    required_readiness_value("--directory"),
    "exports",
)
required_readiness_value("--config-dir")
required_readiness_value("--data-dir")
required_readiness_value("--as-of")
assert_equal(
    f"{command_name} readiness input_format",
    required_readiness_value("--input-format"),
    "json",
)
assert_equal(
    f"{command_name} readiness pattern",
    required_readiness_value("--pattern"),
    "*.json",
)
assert_equal(
    f"{command_name} readiness source_name",
    required_readiness_value("--source-name"),
    "Rednote MCP Export",
)
assert_equal(
    f"{command_name} readiness output format",
    required_readiness_value("--format"),
    "table",
)
```

- [ ] **Step 5: Run focused validator and smoke tests**

Run:

```bash
uv --no-config run --frozen pytest tests/test_first_run_smoke.py::test_validate_external_tool_adapters_requires_print_only_registry_contract -q
uv --no-config run --frozen pytest tests/test_first_run_smoke.py -q
```

Expected: both pass.

## Task 4: Review, Verification, And Commit

**Files:**
- Create: `docs/reviews/opencode-stage-70-code-review-prompt.md`
- Create: `docs/reviews/opencode-stage-70-code-review.md`
- Include Stage 70 spec/plan/review artifacts in commit.

- [ ] **Step 1: Run script-level first-run smoke**

Run:

```bash
uv --no-config run --frozen python scripts/check_first_run_smoke.py --repo-root .
```

Expected: pass.

- [ ] **Step 2: Run lint and format checks**

Run:

```bash
uv --no-config run --frozen ruff check tests/test_external_tool_adapters.py tests/test_cli.py scripts/check_first_run_smoke.py tests/test_first_run_smoke.py
uv --no-config run --frozen ruff format --check tests/test_external_tool_adapters.py tests/test_cli.py scripts/check_first_run_smoke.py tests/test_first_run_smoke.py
```

Expected: both pass.

- [ ] **Step 3: Run release and whitespace checks**

Run:

```bash
uv --no-config run --frozen python scripts/check_release_hygiene.py
git diff --check
```

Expected: both pass.

- [ ] **Step 4: Run the full test suite**

Run:

```bash
uv --no-config run --frozen pytest
```

Expected: pass.

- [ ] **Step 5: Request implementation code review**

Create `docs/reviews/opencode-stage-70-code-review-prompt.md` with the Stage 70
goal, scope, touched files, and verification results. Run:

```bash
opencode run --model zhipuai-coding-plan/glm-5.2 --variant max --dir /home/ubuntu/fashion-radar "$(cat docs/reviews/opencode-stage-70-code-review-prompt.md)" > docs/reviews/opencode-stage-70-code-review.md
```

Fix Critical/Important findings before proceeding.

- [ ] **Step 6: Commit**

Run:

```bash
git add tests/test_external_tool_adapters.py tests/test_cli.py scripts/check_first_run_smoke.py tests/test_first_run_smoke.py docs/superpowers/specs/2026-06-17-stage-70-adapter-readiness-command-test-hardening-design.md docs/superpowers/plans/2026-06-17-stage-70-adapter-readiness-command-test-hardening-plan.md docs/reviews/opencode-stage-70-plan-review-prompt.md docs/reviews/opencode-stage-70-plan-review.md docs/reviews/opencode-stage-70-plan-rereview-prompt.md docs/reviews/opencode-stage-70-plan-rereview.md docs/reviews/opencode-stage-70-code-review-prompt.md docs/reviews/opencode-stage-70-code-review.md
git commit -m "Harden adapter readiness command tests"
```

- [ ] **Step 7: Publish and verify CI**

Prefer regular git push with the ephemeral authorization header. If local git
HTTPS transport fails with the known GnuTLS issue, publish the equivalent
commit through the GitHub Git API and align local refs to the remote commit
that has the same tree.
