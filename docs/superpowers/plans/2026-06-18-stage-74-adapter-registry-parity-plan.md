# Stage 74 Adapter Registry Parity Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a direct parity test proving the first-run smoke
`external_tool_adapters_payload()` fixture matches the real adapter registry
JSON for deterministic local inputs.

**Architecture:** Test-only fixture fidelity hardening. Runtime CLI and adapter
registry code remain unchanged.

**Tech Stack:** Python 3.11, pytest, uv, ruff.

**Review Protocol Note:** Per the current user instruction for this stage,
local review is performed with `opencode run --model
zhipuai-coding-plan/glm-5.2 --variant max`. This stage-local review path does
not change the repository's broader review protocol documents.

---

## File Map

- Modify `tests/test_first_run_smoke.py`
  - Import `build_external_tool_adapter_registry`.
  - Make the `external_tool_adapters_payload()` helper full-fidelity with the
    runtime registry JSON.
  - Add `test_external_tool_adapters_payload_matches_real_registry`.
- Create review artifacts:
  - `docs/reviews/opencode-stage-74-plan-review-prompt.md`
  - `docs/reviews/opencode-stage-74-plan-review.md`
  - `docs/reviews/opencode-stage-74-code-review-prompt.md`
  - `docs/reviews/opencode-stage-74-code-review.md`

## Task 1: Add Adapter Registry Fixture Parity

**Files:**
- Modify: `tests/test_first_run_smoke.py`

- [x] **Step 1: Import runtime registry builder**

Add this import near the existing external-tool imports:

```python
from fashion_radar.external_tool_adapters import build_external_tool_adapter_registry
```

- [x] **Step 2: Add the parity test red state**

Add the new test near the existing external-tool payload parity tests:

```python
def test_external_tool_adapters_payload_matches_real_registry() -> None:
    expected = json.loads(
        build_external_tool_adapter_registry(
            directory=Path("./exports"),
            config_dir=Path("./configs"),
            data_dir=Path("./data"),
            as_of="2026-06-13T12:00:00Z",
        ).model_dump_json()
    )

    assert external_tool_adapters_payload() == expected
```

Run:

```bash
uv --no-config run --frozen pytest tests/test_first_run_smoke.py::test_external_tool_adapters_payload_matches_real_registry -q
```

Expected before fixture updates: fail, because the Stage 73 helper still uses
generic descriptions, upstream examples, field mapping notes, and boundaries.

- [x] **Step 3: Make fixture metadata full-fidelity**

Update helper data in `tests/test_first_run_smoke.py` so
`external_tool_adapters_payload()` matches the runtime registry exactly for:

- `description`
- `upstream_tool_examples`
- `field_mappings`
- adapter-level `boundaries`
- registry-level `boundaries`

Keep the Stage 73 `shlex.join` command helper or equivalent deterministic
command generation, as long as the resulting JSON exactly matches runtime.

- [x] **Step 4: Preserve Stage 73 contract negatives**

Run:

```bash
uv --no-config run --frozen pytest tests/test_first_run_smoke.py::test_validate_external_tool_adapters_requires_print_only_registry_contract -q
```

Expected: pass. If it fails, fix only the fixture/test helper drift needed to
keep the Stage 73 contract intact.

- [x] **Step 5: Preserve first-run flow sequence**

Run:

```bash
uv --no-config run --frozen pytest tests/test_first_run_smoke.py::test_run_first_run_flow_uses_deterministic_local_command_sequence -q
```

Expected: pass. Do not add extra first-run CLI calls for later adapters.

## Task 2: Review, Verification, Commit, Publish

**Files:**
- Create: `docs/reviews/opencode-stage-74-code-review-prompt.md`
- Create: `docs/reviews/opencode-stage-74-code-review.md`
- Include Stage 74 spec/plan/review artifacts in commit.

- [x] **Step 1: Run targeted and broad local verification**

Run:

```bash
uv --no-config run --frozen pytest tests/test_first_run_smoke.py::test_external_tool_adapters_payload_matches_real_registry -q
uv --no-config run --frozen pytest tests/test_first_run_smoke.py::test_validate_external_tool_adapters_requires_print_only_registry_contract tests/test_first_run_smoke.py::test_run_first_run_flow_uses_deterministic_local_command_sequence -q
uv --no-config run --frozen pytest tests/test_first_run_smoke.py -q
uv --no-config run --frozen ruff check tests/test_first_run_smoke.py
uv --no-config run --frozen ruff format --check tests/test_first_run_smoke.py
uv --no-config run --frozen python scripts/check_release_hygiene.py
git diff --check
uv --no-config run --frozen pytest
```

Expected: pass.

- [x] **Step 2: Request opencode code review**

Create `docs/reviews/opencode-stage-74-code-review-prompt.md` with the Stage 74
goal, touched files, implementation summary, and verification results. Run:

```bash
opencode run --model zhipuai-coding-plan/glm-5.2 --variant max --dir /home/ubuntu/fashion-radar "$(cat docs/reviews/opencode-stage-74-code-review-prompt.md)" > docs/reviews/opencode-stage-74-code-review.md
```

Fix Critical/Important findings before proceeding.

- [x] **Step 3: Commit**

Run:

```bash
git add tests/test_first_run_smoke.py docs/superpowers/specs/2026-06-18-stage-74-adapter-registry-parity-design.md docs/superpowers/plans/2026-06-18-stage-74-adapter-registry-parity-plan.md docs/reviews/opencode-stage-74-plan-review-prompt.md docs/reviews/opencode-stage-74-plan-review.md docs/reviews/opencode-stage-74-code-review-prompt.md docs/reviews/opencode-stage-74-code-review.md
git commit -m "Add adapter registry smoke parity test"
```

- [ ] **Step 4: Publish and verify CI**

Use the GitHub Git Data API path if normal git HTTPS push remains unreliable.
Verify remote `main`, local `origin/main`, release hygiene, credential-free git
config, and GitHub Actions CI success.
