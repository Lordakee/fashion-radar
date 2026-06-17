# Stage 69 First-Run Smoke Command Lookup Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace brittle post-order positional assertions in the first-run smoke command-capture test with helper-based command lookups while preserving the exact command order contract.

**Architecture:** This is a test-only maintainability cleanup. The first-run smoke test will keep the full ordered command-name assertion, then use small local helpers to fetch unique commands by name for detailed assertions.

**Tech Stack:** Python 3.11, pytest, ruff, uv.

---

## File Map

- Modify `tests/test_first_run_smoke.py`
  - Add local command lookup helpers inside
    `test_run_first_run_flow_uses_deterministic_local_command_sequence`.
  - Replace unique-command `captured[...]` detailed assertions with helper
    lookups.
  - Preserve duplicate-command behavior and the ordered command-name list.
- Create review artifacts:
  - `docs/reviews/opencode-stage-69-plan-review-prompt.md`
  - `docs/reviews/opencode-stage-69-plan-review.md`
  - `docs/reviews/opencode-stage-69-code-review-prompt.md`
  - `docs/reviews/opencode-stage-69-code-review.md`

## Task 1: Add Lookup Helpers And Refactor Unique Command Assertions

**Files:**
- Modify: `tests/test_first_run_smoke.py`

- [ ] **Step 1: Run the focused test before editing**

Run:

```bash
uv --no-config run --frozen pytest tests/test_first_run_smoke.py::test_run_first_run_flow_uses_deterministic_local_command_sequence -q
```

Expected: pass. This confirms the refactor starts from a green behavioral baseline.

- [ ] **Step 2: Add local lookup helpers after the ordered command-name assertion**

In `test_run_first_run_flow_uses_deterministic_local_command_sequence`, keep the
existing ordered list:

```python
assert [command[0] for command in captured] == [
    "init",
    "migrate-db",
    "doctor",
    "external-tool-adapters",
    "external-tool-template",
    "external-tool-workflow",
    "external-tool-readiness",
    "community-signal-lint",
    "community-candidates",
    "import-signals",
    "import-signals",
    "match",
    "imported-review-workflow",
    "imported-signals-summary",
    "imported-signals",
    "report",
    "candidates",
    "trends",
    "community-handoff-workflow",
    "community-signal-lint-dir",
    "community-candidates-dir",
    "import-signals-dir",
]
```

Immediately after that assertion, add:

```python
def commands_named(command_name: str) -> list[tuple[str, ...]]:
    return [command for command in captured if command[0] == command_name]


def single_command(command_name: str) -> tuple[str, ...]:
    commands = commands_named(command_name)
    assert len(commands) == 1
    return commands[0]
```

- [ ] **Step 3: Replace unique-command positional assertions**

Replace:

```python
assert captured[0] == (
    "init",
    "--config-dir",
    str(context.config_dir),
    "--data-dir",
    str(context.data_dir),
    "--reports-dir",
    str(context.reports_dir),
)
assert captured[1] == ("migrate-db", "--data-dir", str(context.data_dir))
```

with:

```python
assert single_command("init") == (
    "init",
    "--config-dir",
    str(context.config_dir),
    "--data-dir",
    str(context.data_dir),
    "--reports-dir",
    str(context.reports_dir),
)
assert single_command("migrate-db") == ("migrate-db", "--data-dir", str(context.data_dir))
```

Replace:

```python
external_tool_adapters = captured[3]
```

with:

```python
external_tool_adapters = single_command("external-tool-adapters")
```

Replace:

```python
external_tool_template = captured[4]
```

with:

```python
external_tool_template = single_command("external-tool-template")
```

Replace:

```python
external_tool_workflow = captured[5]
```

with:

```python
external_tool_workflow = single_command("external-tool-workflow")
```

Replace:

```python
external_tool_readiness = captured[6]
```

with:

```python
external_tool_readiness = single_command("external-tool-readiness")
```

Replace:

```python
assert captured[18][1] == str(context.exports_dir)
assert "--format" in captured[18]
assert "json" in captured[18]
assert captured[19][1] == str(context.exports_dir)
assert captured[20][1] == str(context.exports_dir)
assert captured[21][1] == str(context.exports_dir)
```

with:

```python
community_handoff_workflow = single_command("community-handoff-workflow")
assert community_handoff_workflow[1] == str(context.exports_dir)
assert "--format" in community_handoff_workflow
assert "json" in community_handoff_workflow
assert single_command("community-signal-lint-dir")[1] == str(context.exports_dir)
assert single_command("community-candidates-dir")[1] == str(context.exports_dir)
assert single_command("import-signals-dir")[1] == str(context.exports_dir)
```

Do not replace or weaken the ordered command-name list. Do not use
`single_command("import-signals")` because `import-signals` intentionally
appears twice.

- [ ] **Step 4: Run the focused test**

Run:

```bash
uv --no-config run --frozen pytest tests/test_first_run_smoke.py::test_run_first_run_flow_uses_deterministic_local_command_sequence -q
```

Expected: pass.

- [ ] **Step 5: Run the first-run smoke test file**

Run:

```bash
uv --no-config run --frozen pytest tests/test_first_run_smoke.py -q
```

Expected: pass.

## Task 2: Review, Verification, And Commit

**Files:**
- Create: `docs/reviews/opencode-stage-69-code-review-prompt.md`
- Create: `docs/reviews/opencode-stage-69-code-review.md`
- Include already-created Stage 69 spec/plan/review artifacts in commit.

- [ ] **Step 1: Run the installed smoke script check**

Run:

```bash
uv --no-config run --frozen python scripts/check_first_run_smoke.py --repo-root .
```

Expected: pass.

- [ ] **Step 2: Run lint and format checks**

Run:

```bash
uv --no-config run --frozen ruff check tests/test_first_run_smoke.py
uv --no-config run --frozen ruff format --check tests/test_first_run_smoke.py
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

Create `docs/reviews/opencode-stage-69-code-review-prompt.md` with the Stage 69
goal, scope, touched files, and verification results. Run:

```bash
opencode run --model zhipuai-coding-plan/glm-5.2 --variant max --dir /home/ubuntu/fashion-radar "$(cat docs/reviews/opencode-stage-69-code-review-prompt.md)" > docs/reviews/opencode-stage-69-code-review.md
```

Fix Critical/Important findings before proceeding.

- [ ] **Step 6: Commit**

Run:

```bash
git add tests/test_first_run_smoke.py docs/superpowers/specs/2026-06-17-stage-69-first-run-smoke-command-lookup-design.md docs/superpowers/plans/2026-06-17-stage-69-first-run-smoke-command-lookup-plan.md docs/reviews/opencode-stage-69-plan-review-prompt.md docs/reviews/opencode-stage-69-plan-review.md docs/reviews/opencode-stage-69-code-review-prompt.md docs/reviews/opencode-stage-69-code-review.md
git commit -m "Refactor first-run smoke command assertions"
```

- [ ] **Step 7: Publish and verify CI**

Prefer regular git push with the ephemeral authorization header. If the local
git HTTPS transport fails with the known GnuTLS issue, publish the equivalent
commit through the GitHub Git API and align local refs to the remote commit
that has the same tree.
