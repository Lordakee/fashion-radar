# Stage 69 First-Run Smoke Command Lookup Design

## Goal

Reduce brittle positional assertions in the first-run smoke command-capture
test while preserving the exact deterministic command order contract.

## Context

Stage 68 inserted additional external tool command guidance and highlighted that
`tests/test_first_run_smoke.py` is easy to shift accidentally: the test already
asserts the full ordered command-name sequence, but later detailed checks still
reference commands by numeric positions such as `captured[3]`, `captured[18]`,
and `captured[21]`.

Those numeric positions are useful in the ordered command-name assertion, but
they make follow-up assertions noisy when a workflow step is intentionally
inserted. A future insertion should fail the ordered sequence once, then let
command-specific assertions remain readable.

## Scope

In scope:

- Add small local helper functions inside
  `test_run_first_run_flow_uses_deterministic_local_command_sequence`.
- Keep the existing full ordered command-name assertion unchanged.
- Replace later detailed positional assertions with helper-based lookups.
- Preserve special handling for duplicate command names such as
  `import-signals`.
- Keep the node test-only: no production code, CLI code, smoke script behavior,
  docs, schemas, or examples should change.

Out of scope:

- Changing `scripts/check_first_run_smoke.py`.
- Changing the first-run smoke command sequence.
- Adding new commands or changing command flags.
- Weakening the ordered command-name assertion.
- Platform connectors, source acquisition, scraping, scheduling, browser
  automation, platform APIs, demand proof, ranking, coverage verification, or
  compliance-review product behavior.

## Design

The test will keep:

```python
assert [command[0] for command in captured] == [...]
```

Immediately after this assertion, the test will define two local helpers:

```python
def commands_named(command_name: str) -> list[tuple[str, ...]]:
    return [command for command in captured if command[0] == command_name]


def single_command(command_name: str) -> tuple[str, ...]:
    commands = commands_named(command_name)
    assert len(commands) == 1
    return commands[0]
```

Unique commands such as `init`, `migrate-db`, `external-tool-adapters`,
`external-tool-template`, `external-tool-workflow`, `external-tool-readiness`,
`community-handoff-workflow`, `community-signal-lint-dir`,
`community-candidates-dir`, and `import-signals-dir` will use
`single_command(...)`.

Duplicate commands such as `import-signals` will remain covered by the existing
ordered command-name assertion and the existing loop-level flag checks. This
stage will not introduce a helper that hides duplicate command details.

## Test Strategy

- First run the focused test before implementation to confirm the current test
  still passes before the refactor.
- Apply the test-only refactor.
- Run the focused test again.
- Run the first-run smoke test file.
- Run the installed first-run smoke script with the project command.
- Run ruff check/format on the touched test file.
- Run release hygiene, diff whitespace checks, and the full pytest suite before
  commit.

## Acceptance Criteria

- `tests/test_first_run_smoke.py` no longer uses numeric `captured[...]`
  references for unique command detail assertions in the first-run command
  capture test.
- The exact command-name order assertion remains present and unchanged.
- Unique command detail assertions are still exact tuple comparisons where they
  were exact before.
- Directory handoff commands still verify `context.exports_dir`, JSON output
  format, and export file copy behavior.
- The change is test-only and does not modify runtime behavior.
