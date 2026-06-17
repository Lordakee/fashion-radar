# Stage 70 Adapter Readiness Command Test Hardening Design

## Goal

Make existing tests and first-run smoke validation more explicit about the
`external-tool-readiness` command printed inside external tool adapter
`recommended_commands`.

## Context

Stage 68 added `external-tool-readiness` to every adapter command list. The
implementation and behavior are already covered, but reviews noted two small
explicitness gaps:

- The unit test checks many readiness command flags but does not directly
  assert the `--config-dir` and `--data-dir` values.
- The first-run smoke validator only checks a subset of readiness command
  tokens with substring matching.

Stage 70 hardens those checks without changing runtime behavior.

## Scope

In scope:

- Add explicit unit assertions for `--config-dir` and `--data-dir` in
  `tests/test_external_tool_adapters.py`.
- Upgrade CLI adapter JSON tests in `tests/test_cli.py` from a loose
  substring check to token-level readiness command assertions.
- Parse the first adapter readiness command in
  `scripts/check_first_run_smoke.py` with `shlex.split`.
- Validate stable readiness command structure:
  - command prefix is `fashion-radar external-tool-readiness`
  - required flags are present
  - stable values match for `--adapter`, `--directory`, `--input-format`,
    `--pattern`, `--source-name`, and `--format`
  - `--config-dir`, `--data-dir`, and `--as-of` exist and have non-empty values
- Add negative tests for missing `--format table` and malformed shell quoting.

Out of scope:

- Runtime behavior changes.
- CLI behavior changes.
- Adapter registry content changes.
- Path-specific assertions for user config/data defaults, because those vary
  by environment.
- Platform connectors, source acquisition, scraping, scheduling, browser
  automation, platform APIs, demand proof, ranking, coverage verification, or
  compliance-review product behavior.

## Design

`validate_external_tool_adapters(...)` will keep locating the first readiness
command in the first adapter's `recommended_commands`. Instead of substring
matching all expected tokens, it will parse the command:

```python
try:
    readiness_parts = shlex.split(readiness_command)
except ValueError as exc:
    raise SmokeError(
        f"{command_name} readiness command is not shell-parseable: {exc}"
    ) from exc
```

It will then assert the prefix:

```python
assert_equal(
    f"{command_name} readiness command prefix",
    readiness_parts[:2],
    ["fashion-radar", "external-tool-readiness"],
)
```

A small local helper will fetch flag values:

```python
def required_flag_value(flag: str) -> str:
    if flag not in readiness_parts:
        raise SmokeError(f"{command_name} readiness command missing {flag!r}")
    index = readiness_parts.index(flag)
    if index + 1 >= len(readiness_parts):
        raise SmokeError(f"{command_name} readiness command missing value for {flag!r}")
    value = readiness_parts[index + 1]
    if not value or value.startswith("--"):
        raise SmokeError(f"{command_name} readiness command missing value for {flag!r}")
    return value
```

Stable values will be checked with `assert_equal`; environment-dependent
directory values will only be checked as present and non-empty.

## Test Strategy

- Run focused adapter unit tests before and after the unit assertion change.
- Run focused first-run smoke validator tests before and after validator
  changes.
- Add negative tests for:
  - missing `--format table`
  - non-table `--format` values
  - flag values replaced by the next flag
  - trailing flags with no value
  - malformed shell quoting
- Run the script-level first-run smoke command.
- Run ruff check/format for touched files.
- Run release hygiene, whitespace checks, and the full test suite.

## Acceptance Criteria

- Adapter unit tests explicitly assert readiness `--config-dir` and
  `--data-dir` values.
- First-run smoke validation parses the readiness command with `shlex.split`.
- First-run smoke validation rejects malformed shell quoting.
- First-run smoke validation rejects missing `--format table`.
- First-run smoke validation rejects non-table `--format` values.
- First-run smoke validation rejects required flags whose value is missing,
  including flags followed by another flag or trailing flags with no value.
- CLI JSON tests verify readiness command flag/value mapping with
  `shlex.split`, without hard-coding environment-dependent config/data default
  paths.
- Path-dependent config/data values remain non-empty presence checks, not
  hard-coded local user paths.
- No runtime behavior changes are made.
