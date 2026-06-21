# Stage 141 Workflow Fixture Parity Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make imported-review and community-handoff workflow smoke fixtures exactly match their real runtime builders.

**Architecture:** Add builder parity tests in `tests/test_first_run_smoke.py`, then enrich the hand-maintained fixture step dictionaries with the same `order`, `purpose`, and `suggested_effect` metadata emitted by the builders.

**Tech Stack:** Python 3.12, pytest, Pydantic `model_dump_json()`, uv, ruff.

---

### Task 1: Plan Review

**Files:**
- Create: `docs/reviews/opencode-stage-141-plan-review-prompt.md`
- Create: `docs/reviews/opencode-stage-141-plan-review.md`

- [ ] **Step 1: Write opencode plan review prompt**

Create `docs/reviews/opencode-stage-141-plan-review-prompt.md`:

```markdown
# Stage 141 Plan Review Prompt

You are reviewing the Stage 141 implementation plan for `/home/ubuntu/fashion-radar`.

Goal: Add exact builder parity tests for imported-review and community-handoff workflow smoke fixtures, then update fixture step metadata to match runtime builder JSON.

Relevant files:
- `docs/superpowers/specs/2026-06-21-stage-141-workflow-fixture-parity-design.md`
- `docs/superpowers/plans/2026-06-21-stage-141-workflow-fixture-parity-plan.md`
- `tests/test_first_run_smoke.py`
- `src/fashion_radar/imported_review_workflow.py`
- `src/fashion_radar/community_handoff_workflow.py`

Please review:
- Whether the parity tests use the correct builder args and JSON mode.
- Whether the fixture metadata values match builder output exactly.
- Whether runtime behavior remains unchanged.
- Whether the RED/GREEN strategy is valid.

Return findings first with severity and file/line references. If there are no blocking issues, say that explicitly.
```

- [ ] **Step 2: Run opencode plan review**

Run:

```bash
opencode run --model zhipuai-coding-plan/glm-5.2 --variant max --dir /home/ubuntu/fashion-radar "$(cat docs/reviews/opencode-stage-141-plan-review-prompt.md)" > /tmp/opencode-stage-141-plan-review.md
```

Expected: exit code 0 and review output in `/tmp/opencode-stage-141-plan-review.md`.

- [ ] **Step 3: Save sanitized review artifact**

Inspect `/tmp/opencode-stage-141-plan-review.md`. Strip live narration before the review heading if present. Save the body to `docs/reviews/opencode-stage-141-plan-review.md`.

### Task 2: RED Parity Tests

**Files:**
- Modify: `tests/test_first_run_smoke.py`

- [ ] **Step 1: Add builder imports**

Add imports near existing builder imports:

```python
from fashion_radar.community_handoff_workflow import build_community_handoff_workflow
from fashion_radar.imported_review_workflow import build_imported_review_workflow
```

- [ ] **Step 2: Add imported-review parity test**

Add after `test_external_tool_readiness_payload_matches_real_rednote_readiness()`:

```python
def test_imported_review_workflow_payload_matches_real_builder() -> None:
    expected = json.loads(
        build_imported_review_workflow(
            config_dir=Path("configs"),
            data_dir=Path("data"),
            as_of="2026-06-13T12:00:00Z",
            source_name="Community Tool Export",
        ).model_dump_json()
    )

    assert imported_review_workflow_payload() == expected
```

- [ ] **Step 3: Add community-handoff parity test**

Add below the imported-review parity test:

```python
def test_community_handoff_workflow_payload_matches_real_builder() -> None:
    expected = json.loads(
        build_community_handoff_workflow(
            directory=Path("/tmp/export"),
            config_dir=Path("configs"),
            data_dir=Path("data"),
            input_format="csv",
            pattern="*.csv",
            as_of="2026-06-13T12:00:00Z",
            source_name="Community Tool Export",
        ).model_dump_json()
    )

    assert community_handoff_workflow_payload() == expected
```

- [ ] **Step 4: Run RED tests**

Run:

```bash
uv --no-config run --frozen pytest tests/test_first_run_smoke.py -q -k "workflow_payload_matches_real_builder"
```

Expected: both tests fail because nested step metadata is missing from fixtures.

### Task 3: Update Fixtures

**Files:**
- Modify: `tests/test_first_run_smoke.py`

- [ ] **Step 1: Update imported-review fixture steps**

For each step in `imported_review_workflow_payload()["steps"]`, add:

```python
"order": N,
"purpose": "<builder purpose>",
"suggested_effect": "<builder suggested_effect>",
```

Use exact values from `src/fashion_radar/imported_review_workflow.py`.

- [ ] **Step 2: Update community-handoff fixture steps**

For each step in `community_handoff_workflow_payload()["steps"]`, add:

```python
"order": N,
"purpose": "<builder purpose>",
```

Keep the existing `suggested_effect` values.

- [ ] **Step 3: Run GREEN tests**

Run:

```bash
uv --no-config run --frozen pytest tests/test_first_run_smoke.py -q -k "workflow_payload_matches_real_builder"
```

Expected: both parity tests pass.

### Task 4: Focused Verification and Code Review

**Files:**
- Create: `docs/reviews/opencode-stage-141-code-review-prompt.md`
- Create: `docs/reviews/opencode-stage-141-code-review.md`

- [ ] **Step 1: Run focused verification**

Run:

```bash
uv --no-config run --frozen pytest tests/test_first_run_smoke.py -q -k "workflow_payload_matches_real_builder or imported_review_workflow or community_handoff_workflow"
uv --no-config run --frozen pytest tests/test_first_run_smoke.py -q
uv --no-config run --frozen ruff check tests/test_first_run_smoke.py
uv --no-config run --frozen ruff format --check tests/test_first_run_smoke.py
git diff --check
```

Expected: all commands exit 0.

- [ ] **Step 2: Write code review prompt**

Create `docs/reviews/opencode-stage-141-code-review-prompt.md`:

```markdown
# Stage 141 Code Review Prompt

You are reviewing Stage 141 changes in `/home/ubuntu/fashion-radar`.

Base commit: `91cc24f7ea6690916c1a4f2e1ed05eddc477df54`

Review scope:
- `tests/test_first_run_smoke.py`
- Stage 141 plan and review docs

Requirements:
- Imported-review and community-handoff workflow payload fixtures must exactly match real builder JSON.
- Runtime code must not change.
- RED/GREEN should prove fixture drift was present and then fixed.

Please report findings first with severity and file/line references. If there are no blocking findings, say that explicitly.
```

- [ ] **Step 3: Run opencode code review**

Run:

```bash
opencode run --model zhipuai-coding-plan/glm-5.2 --variant max --dir /home/ubuntu/fashion-radar "$(cat docs/reviews/opencode-stage-141-code-review-prompt.md)" > /tmp/opencode-stage-141-code-review.md
```

Expected: exit code 0 and review output in `/tmp/opencode-stage-141-code-review.md`.

- [ ] **Step 4: Save sanitized code review artifact**

Inspect `/tmp/opencode-stage-141-code-review.md`. Strip live narration before the review heading if present. Save the body to `docs/reviews/opencode-stage-141-code-review.md`.

### Task 5: Release Gate, Commit, Push, CI

**Files:**
- Commit all Stage 141 files after verification and review.

- [ ] **Step 1: Run release gate**

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

Expected: all commands exit 0.

- [ ] **Step 2: Commit Stage 141**

Run:

```bash
git status --short
git add docs/superpowers/specs/2026-06-21-stage-141-workflow-fixture-parity-design.md docs/superpowers/plans/2026-06-21-stage-141-workflow-fixture-parity-plan.md docs/reviews/opencode-stage-141-plan-review-prompt.md docs/reviews/opencode-stage-141-plan-review.md docs/reviews/opencode-stage-141-code-review-prompt.md docs/reviews/opencode-stage-141-code-review.md tests/test_first_run_smoke.py
git commit -m "Align workflow smoke fixtures with builders"
```

Expected: commit succeeds.

- [ ] **Step 3: Push with ephemeral auth**

Use an ephemeral HTTP extraheader only for this push.

Run:

```bash
git -c http.https://github.com/.extraheader="$AUTH_HEADER" push origin main
git config --get-all http.https://github.com/.extraheader || true
```

Expected: push succeeds and no persistent auth header is printed.

- [ ] **Step 4: Poll CI**

Use GitHub Actions API to poll the new run until completion.

- [ ] **Step 5: Handoff Summary**

Write:

```markdown
**Handoff Summary**

- Repo status:
- Verified commands:
- CI:
- Uncommitted files:
- Next step:
```
