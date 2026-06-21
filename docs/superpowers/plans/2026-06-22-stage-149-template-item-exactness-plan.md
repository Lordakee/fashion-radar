# Stage 149 Template Item Exactness Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make `external-tool-template` first-run smoke validation reject populated but drifted Rednote template example rows.

**Architecture:** Keep runtime template output unchanged. Add RED tests for title and `source_weight` drift that current schema-only validation accepts, then pin the exact two Rednote example rows inside the smoke checker after the existing structural checks.

**Tech Stack:** Python 3.12, pytest, uv, ruff, existing first-run smoke checker.

---

### Task 1: Plan Review

**Files:**
- Create: `docs/reviews/opencode-stage-149-plan-review-prompt.md`
- Create: `docs/reviews/opencode-stage-149-plan-review.md`

- [ ] **Step 1: Write opencode plan review prompt**

Create `docs/reviews/opencode-stage-149-plan-review-prompt.md`:

```markdown
# Stage 149 Plan Review Prompt

You are reviewing the Stage 149 implementation plan for `/home/ubuntu/fashion-radar`.

Goal: Harden `external-tool-template` first-run smoke validation so the two Rednote example rows must match the pinned first-run contract exactly.

Relevant files:
- `docs/superpowers/specs/2026-06-22-stage-149-template-item-exactness-design.md`
- `docs/superpowers/plans/2026-06-22-stage-149-template-item-exactness-plan.md`
- `scripts/check_first_run_smoke.py`
- `tests/test_first_run_smoke.py`
- `src/fashion_radar/external_tool_templates.py`

Please review:
- Whether the RED tests would fail before implementation and pass after exact item equality.
- Whether the pinned item values match the runtime builder and first-run fixture.
- Whether existing targeted errors for missing fields, private/raw fields, extra fields, and wrong platform remain intact.
- Whether runtime behavior remains unchanged.
- Whether focused verification is sufficient.

Return findings first with severity and file/line references. If there are no blocking issues, say that explicitly.
```

- [ ] **Step 2: Run opencode plan review**

Run:

```bash
opencode run --model zhipuai-coding-plan/glm-5.2 --variant max --dir /home/ubuntu/fashion-radar "$(cat docs/reviews/opencode-stage-149-plan-review-prompt.md)" > /tmp/opencode-stage-149-plan-review.md
```

Expected: exit code 0 and review output in `/tmp/opencode-stage-149-plan-review.md`.

- [ ] **Step 3: Save sanitized review artifact**

Inspect `/tmp/opencode-stage-149-plan-review.md`. Strip live narration before the review heading if present. Save the body to `docs/reviews/opencode-stage-149-plan-review.md`.

### Task 2: RED Tests

**Files:**
- Modify: `tests/test_first_run_smoke.py`

- [ ] **Step 1: Add title drift test**

Add this test immediately after `test_validate_external_tool_template_requires_importable_items()`:

```python
def test_validate_external_tool_template_rejects_title_drift() -> None:
    payload = external_tool_template_payload()
    items = payload["items"]
    assert isinstance(items, list)
    items[0]["title"] = "Run npm install -g rednote-mcp before collecting rows."

    with pytest.raises(smoke.SmokeError, match="row 1 item"):
        smoke.validate_external_tool_template("external-tool-template", payload)
```

- [ ] **Step 2: Run title RED test**

Run:

```bash
uv --no-config run --frozen pytest tests/test_first_run_smoke.py -q -k "template_rejects_title_drift"
```

Expected: fail with `DID NOT RAISE` because the current validator accepts any populated title.

- [ ] **Step 3: Add source weight drift test**

Add this test immediately after the title drift test:

```python
def test_validate_external_tool_template_rejects_source_weight_drift() -> None:
    payload = external_tool_template_payload()
    items = payload["items"]
    assert isinstance(items, list)
    items[1]["source_weight"] = 4.5

    with pytest.raises(smoke.SmokeError, match="row 2 item"):
        smoke.validate_external_tool_template("external-tool-template", payload)
```

- [ ] **Step 4: Run source weight RED test**

Run:

```bash
uv --no-config run --frozen pytest tests/test_first_run_smoke.py -q -k "template_rejects_source_weight_drift"
```

Expected: fail with `DID NOT RAISE` because the current validator accepts any populated source weight.

### Task 3: Exact Template Item Validation

**Files:**
- Modify: `scripts/check_first_run_smoke.py`

- [ ] **Step 1: Add expected item constant**

After `EXPECTED_EXTERNAL_TOOL_TEMPLATE_FIELDS`, add:

```python
EXPECTED_EXTERNAL_TOOL_TEMPLATE_ITEMS = [
    {
        "url": "https://example.com/external-tool-template/rednote_mcp/the-row-bag",
        "title": "Rednote MCP Export The Row bag observed signal",
        "published_at": "2026-06-13T12:00:00+00:00",
        "summary": (
            "Synthetic sanitized observation about The Row bag interest from a "
            "user-controlled external/community tool."
        ),
        "source_name": "Rednote MCP Export",
        "platform": "rednote",
        "source_weight": 1.2,
        "collected_at": "2026-06-13T12:15:00+00:00",
    },
    {
        "url": "https://example.com/external-tool-template/rednote_mcp/silver-flat-shoe",
        "title": "Rednote MCP Export silver flat shoe observed signal",
        "published_at": "2026-06-13T13:00:00+00:00",
        "summary": (
            "Synthetic sanitized observation about silver flat shoes and styling "
            "from a user-controlled external/community tool."
        ),
        "source_name": "Rednote MCP Export",
        "platform": "rednote",
        "source_weight": 1.1,
        "collected_at": "2026-06-13T13:15:00+00:00",
    },
]
```

- [ ] **Step 2: Assert exact row items after existing platform assertion**

In `validate_external_tool_template()`, after:

```python
        assert_equal(f"{command_name} row {index} platform", item.get("platform"), "rednote")
```

add:

```python
        assert_equal(
            f"{command_name} row {index} item",
            item,
            EXPECTED_EXTERNAL_TOOL_TEMPLATE_ITEMS[index - 1],
        )
```

This keeps the existing `row N platform` error label for platform drift and adds exact equality only after all structural checks pass.

- [ ] **Step 3: Run focused GREEN tests**

Run:

```bash
uv --no-config run --frozen pytest tests/test_first_run_smoke.py -q -k "template_rejects_title_drift or template_rejects_source_weight_drift"
```

Expected: both tests pass.

- [ ] **Step 4: Run the full external template test slice**

Run:

```bash
uv --no-config run --frozen pytest tests/test_first_run_smoke.py -q -k "external_tool_template"
```

Expected: all selected external template tests pass, including existing wrong-platform, missing-field, private-field, and raw-field checks.

### Task 4: Review And Release Gate

**Files:**
- Create: `docs/reviews/opencode-stage-149-code-review-prompt.md`
- Create: `docs/reviews/opencode-stage-149-code-review.md`

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

Create `docs/reviews/opencode-stage-149-code-review-prompt.md`:

```markdown
# Stage 149 Code Review Prompt

You are reviewing Stage 149 changes in `/home/ubuntu/fashion-radar`.

Goal: Harden `external-tool-template` first-run smoke validation so the two Rednote example rows must match the pinned first-run contract exactly.

Review range:
- Base: `46f646bdf1499bb50395e7b88c928ff88aa6d470`
- Head: current working tree

Expected changed files:
- `docs/superpowers/specs/2026-06-22-stage-149-template-item-exactness-design.md`
- `docs/superpowers/plans/2026-06-22-stage-149-template-item-exactness-plan.md`
- `docs/reviews/opencode-stage-149-plan-review-prompt.md`
- `docs/reviews/opencode-stage-149-plan-review.md`
- `docs/reviews/opencode-stage-149-code-review-prompt.md`
- `scripts/check_first_run_smoke.py`
- `tests/test_first_run_smoke.py`

Please review:
- Whether the new tests prove the prior gaps with true RED cases.
- Whether `validate_external_tool_template()` now checks exact template row equality after existing structural checks.
- Whether existing targeted structural error messages remain intact.
- Whether runtime behavior remains unchanged.
- Whether verification coverage is sufficient.

Return findings first with severity and file/line references. If there are no blocking issues, say that explicitly.
```

- [ ] **Step 3: Run opencode code review**

Run:

```bash
opencode run --model zhipuai-coding-plan/glm-5.2 --variant max --dir /home/ubuntu/fashion-radar "$(cat docs/reviews/opencode-stage-149-code-review-prompt.md)" > /tmp/opencode-stage-149-code-review.md
```

Expected: exit code 0 and review output in `/tmp/opencode-stage-149-code-review.md`.

- [ ] **Step 4: Save sanitized review artifact**

Inspect `/tmp/opencode-stage-149-code-review.md`. Strip live narration before the review heading if present. Save the body to `docs/reviews/opencode-stage-149-code-review.md`.

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
git add docs/superpowers/specs/2026-06-22-stage-149-template-item-exactness-design.md docs/superpowers/plans/2026-06-22-stage-149-template-item-exactness-plan.md docs/reviews/opencode-stage-149-plan-review-prompt.md docs/reviews/opencode-stage-149-plan-review.md docs/reviews/opencode-stage-149-code-review-prompt.md docs/reviews/opencode-stage-149-code-review.md scripts/check_first_run_smoke.py tests/test_first_run_smoke.py
git commit -m "Pin external tool template items"
```

Push with the existing ephemeral auth-header pattern only; do not persist credentials in git config or files.

- [ ] **Step 7: Poll CI**

Poll the GitHub Actions run for the pushed commit until it completes.

Expected: workflow conclusion is `success`.
