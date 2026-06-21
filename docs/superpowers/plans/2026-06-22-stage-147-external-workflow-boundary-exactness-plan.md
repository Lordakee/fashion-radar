# Stage 147 External Workflow Boundary Exactness Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make `external-tool-workflow` first-run smoke validation reject appended or contradictory boundary text.

**Architecture:** Keep runtime external workflow output unchanged. Add RED tests that mutate `boundaries`, then pin the expected workflow boundary list in the smoke checker and replace substring checks with exact list equality.

**Tech Stack:** Python 3.12, pytest, uv, ruff, existing first-run smoke checker.

---

### Task 1: Plan Review

**Files:**
- Create: `docs/reviews/opencode-stage-147-plan-review-prompt.md`
- Create: `docs/reviews/opencode-stage-147-plan-review.md`

- [ ] **Step 1: Write opencode plan review prompt**

Create `docs/reviews/opencode-stage-147-plan-review-prompt.md`:

```markdown
# Stage 147 Plan Review Prompt

You are reviewing the Stage 147 implementation plan for `/home/ubuntu/fashion-radar`.

Goal: Harden `external-tool-workflow` first-run smoke validation so workflow `boundaries` must match the canonical boundary list exactly.

Relevant files:
- `docs/superpowers/specs/2026-06-22-stage-147-external-workflow-boundary-exactness-design.md`
- `docs/superpowers/plans/2026-06-22-stage-147-external-workflow-boundary-exactness-plan.md`
- `scripts/check_first_run_smoke.py`
- `tests/test_first_run_smoke.py`
- `src/fashion_radar/external_tool_workflow.py`

Please review:
- Whether the RED tests would fail before implementation and pass after exact boundary equality.
- Whether the expected boundary list matches the runtime builder and first-run fixture.
- Whether runtime behavior remains unchanged.
- Whether focused verification is sufficient.

Return findings first with severity and file/line references. If there are no blocking issues, say that explicitly.
```

- [ ] **Step 2: Run opencode plan review**

Run:

```bash
opencode run --model zhipuai-coding-plan/glm-5.2 --variant max --dir /home/ubuntu/fashion-radar "$(cat docs/reviews/opencode-stage-147-plan-review-prompt.md)" > /tmp/opencode-stage-147-plan-review.md
```

Expected: exit code 0 and review output in `/tmp/opencode-stage-147-plan-review.md`.

- [ ] **Step 3: Save sanitized review artifact**

Inspect `/tmp/opencode-stage-147-plan-review.md`. Strip live narration before the review heading if present. Save the body to `docs/reviews/opencode-stage-147-plan-review.md`.

### Task 2: RED Tests

**Files:**
- Modify: `tests/test_first_run_smoke.py`

- [ ] **Step 1: Add boundary drift test**

Add this test after `test_validate_external_tool_workflow_rejects_extra_readiness_command_flag()`:

```python
@pytest.mark.parametrize(
    "boundaries",
    [
        [
            *external_tool_workflow_payload()["boundaries"],
            "Runs source acquisition and opens platform APIs.",
        ],
        [
            (
                "Does not run generated commands. No platform collection, no scraping, "
                "no platform APIs. Runs source acquisition and opens platform APIs."
            )
        ],
    ],
)
def test_validate_external_tool_workflow_rejects_boundary_drift(
    boundaries: list[str],
) -> None:
    payload = external_tool_workflow_payload()
    payload["boundaries"] = boundaries

    with pytest.raises(smoke.SmokeError, match="boundaries"):
        smoke.validate_external_tool_workflow("external-tool-workflow", payload)
```

- [ ] **Step 2: Run RED test**

Run:

```bash
uv --no-config run --frozen pytest tests/test_first_run_smoke.py -q -k "boundary_drift"
```

Expected: both cases fail with `DID NOT RAISE` because the current validator accepts appended and substring-preserving contradictory boundary text.

### Task 3: Exact Boundary Validation

**Files:**
- Modify: `scripts/check_first_run_smoke.py`

- [ ] **Step 1: Add expected workflow boundaries constant**

Near the existing external tool boundary constants, preferably adjacent to `EXPECTED_EXTERNAL_TOOL_REGISTRY_BOUNDARIES`, add:

```python
EXPECTED_EXTERNAL_TOOL_WORKFLOW_BOUNDARIES = (
    "Prints local external/community tool handoff workflow commands only.",
    "Does not run generated commands.",
    "Does not run adapters or upstream tools.",
    "Does not inspect the supplied directory.",
    "Does not read handoff files, validate files, import rows, or open SQLite.",
    "Does not write config, data, report, dashboard, or workflow artifacts.",
    (
        "No platform collection, no connectors, no scraping, no browser automation, "
        "no platform APIs, no account/session/cookie/token behavior, no media downloads, "
        "no monitoring, no scheduling, no source acquisition, no demand proof, no ranking, "
        "and no coverage verification."
    ),
    "Does not provide a compliance-review workflow.",
)
```

- [ ] **Step 2: Replace substring boundary scan**

In `validate_external_tool_workflow()`, replace:

```python
    boundary_text = " ".join(str(boundary) for boundary in boundaries)
    for expected in ("Does not run", "No platform collection", "no scraping", "no platform APIs"):
        if expected not in boundary_text:
            raise SmokeError(f"{command_name} boundaries missing {expected!r}")
```

with:

```python
    assert_equal(
        f"{command_name} boundaries",
        boundaries,
        list(EXPECTED_EXTERNAL_TOOL_WORKFLOW_BOUNDARIES),
    )
```

- [ ] **Step 3: Run GREEN test**

Run:

```bash
uv --no-config run --frozen pytest tests/test_first_run_smoke.py -q -k "boundary_drift"
```

Expected: both cases pass.

- [ ] **Step 4: Run focused workflow tests**

Run:

```bash
uv --no-config run --frozen pytest tests/test_first_run_smoke.py -q -k "external_tool_workflow"
```

Expected: all selected external workflow tests pass.

### Task 4: Review And Release Gate

**Files:**
- Create: `docs/reviews/opencode-stage-147-code-review-prompt.md`
- Create: `docs/reviews/opencode-stage-147-code-review.md`

- [ ] **Step 1: Run focused verification**

Run:

```bash
uv --no-config run --frozen pytest tests/test_first_run_smoke.py -q
uv --no-config run --frozen ruff check scripts/check_first_run_smoke.py tests/test_first_run_smoke.py
uv --no-config run --frozen ruff format --check scripts/check_first_run_smoke.py tests/test_first_run_smoke.py
git diff --check
```

Expected: all commands exit 0.

- [ ] **Step 2: Write opencode code review prompt**

Create `docs/reviews/opencode-stage-147-code-review-prompt.md`:

```markdown
# Stage 147 Code Review Prompt

You are reviewing Stage 147 changes in `/home/ubuntu/fashion-radar`.

Goal: Harden `external-tool-workflow` first-run smoke validation so workflow `boundaries` must match the canonical boundary list exactly.

Review range:
- Base: `d814214e517cd2ee1714690983521f511840e470`
- Head: current working tree

Expected changed files:
- `docs/superpowers/specs/2026-06-22-stage-147-external-workflow-boundary-exactness-design.md`
- `docs/superpowers/plans/2026-06-22-stage-147-external-workflow-boundary-exactness-plan.md`
- `docs/reviews/opencode-stage-147-plan-review-prompt.md`
- `docs/reviews/opencode-stage-147-plan-review.md`
- `docs/reviews/opencode-stage-147-code-review-prompt.md`
- `scripts/check_first_run_smoke.py`
- `tests/test_first_run_smoke.py`

Please review:
- Whether the new tests prove the prior gap with true RED cases.
- Whether `validate_external_tool_workflow()` now checks exact boundary equality.
- Whether runtime behavior remains unchanged.
- Whether verification coverage is sufficient.

Return findings first with severity and file/line references. If there are no blocking issues, say that explicitly.
```

- [ ] **Step 3: Run opencode code review**

Run:

```bash
opencode run --model zhipuai-coding-plan/glm-5.2 --variant max --dir /home/ubuntu/fashion-radar "$(cat docs/reviews/opencode-stage-147-code-review-prompt.md)" > /tmp/opencode-stage-147-code-review.md
```

Expected: exit code 0 and review output in `/tmp/opencode-stage-147-code-review.md`.

- [ ] **Step 4: Save sanitized review artifact**

Inspect `/tmp/opencode-stage-147-code-review.md`. Strip live narration before the review heading if present. Save the body to `docs/reviews/opencode-stage-147-code-review.md`.

- [ ] **Step 5: Run release gate**

Run:

```bash
uv --no-config run --frozen python scripts/check_release_hygiene.py
env -u all_proxy -u ALL_PROXY -u http_proxy -u HTTP_PROXY -u https_proxy -u HTTPS_PROXY -u no_proxy -u NO_PROXY uv --no-config run --frozen pytest -q
uv --no-config run --frozen ruff check .
uv --no-config run --frozen ruff format --check .
env -u UV_DEFAULT_INDEX -u UV_INDEX_URL -u UV_EXTRA_INDEX_URL UV_NO_CONFIG=1 uv lock --check
git diff --check
if rg -n 'ghp_[A-Za-z0-9]+' .; then echo 'GitHub token pattern found in worktree' >&2; exit 1; fi
if git config --get-all http.https://github.com/.extraheader; then echo 'Persistent GitHub auth header configured' >&2; exit 1; fi
```

Expected: all commands exit 0 and token/auth checks print no secret findings.

- [ ] **Step 6: Commit and push**

Run:

```bash
git status --short
git add docs/superpowers/specs/2026-06-22-stage-147-external-workflow-boundary-exactness-design.md docs/superpowers/plans/2026-06-22-stage-147-external-workflow-boundary-exactness-plan.md docs/reviews/opencode-stage-147-plan-review-prompt.md docs/reviews/opencode-stage-147-plan-review.md docs/reviews/opencode-stage-147-code-review-prompt.md docs/reviews/opencode-stage-147-code-review.md scripts/check_first_run_smoke.py tests/test_first_run_smoke.py
git commit -m "Pin external workflow boundary validation"
```

Push with the existing ephemeral auth-header pattern only; do not persist credentials in git config or files.

- [ ] **Step 7: Poll CI**

Poll the GitHub Actions run for the pushed commit until it completes.

Expected: workflow conclusion is `success`.
