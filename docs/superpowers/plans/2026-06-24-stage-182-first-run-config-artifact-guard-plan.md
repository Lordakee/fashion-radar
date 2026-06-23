# Stage 182 First-Run Config Artifact Guard Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make first-run smoke fail if it creates repo-local generated runtime config files under `configs/`.

**Architecture:** Small smoke-check hardening. Extend the existing default-artifact snapshot to include exactly `configs/sources.yaml`, `configs/entities.yaml`, and `configs/scoring.yaml` when present, reusing the current created/changed/deleted diff logic and avoiding a broad `configs/` tree scan.

**Tech Stack:** Python, pytest, existing `scripts/check_first_run_smoke.py` helper tests, `uv --no-config run --frozen`, local opencode review with `zhipuai-coding-plan/glm-5.2 --variant max`.

---

## Files

- Modify: `scripts/check_first_run_smoke.py`
  - Add `DEFAULT_GENERATED_CONFIG_ARTIFACT_PATHS`.
  - Extend `snapshot_default_artifacts(...)`.
  - Update default-artifact error wording.
- Modify: `tests/test_first_run_smoke.py`
  - Add `test_default_artifact_guard_detects_new_repo_config_files`.
- Add: `docs/superpowers/specs/2026-06-24-stage-182-first-run-config-artifact-guard-design.md`
- Add: `docs/superpowers/plans/2026-06-24-stage-182-first-run-config-artifact-guard-plan.md`
- Add: `docs/reviews/opencode-stage-182-plan-review-prompt.md`
- Add after plan review: `docs/reviews/opencode-stage-182-plan-review.md`
- Add after implementation: `docs/reviews/opencode-stage-182-code-review-prompt.md`
- Add after implementation: `docs/reviews/opencode-stage-182-code-review.md`
- Add before commit: `docs/reviews/opencode-stage-182-release-review-prompt.md`
- Add before commit: `docs/reviews/opencode-stage-182-release-review.md`

## Task 1: Add Failing Generated Config Artifact Test

**Files:**

- Modify: `tests/test_first_run_smoke.py`

- [ ] **Step 1: Confirm the new test does not already exist**

Run:

```bash
uv --no-config run --frozen pytest \
  tests/test_first_run_smoke.py::test_default_artifact_guard_detects_new_repo_config_files -q
```

Expected before adding the test: pytest reports the test name is not found or no
matching test is collected.

- [ ] **Step 2: Add the failing test**

Add this test immediately after
`test_default_artifact_guard_detects_deleted_repo_data_or_report_files`:

```python
def test_default_artifact_guard_detects_new_repo_config_files(
    tmp_path: Path,
) -> None:
    before = smoke.snapshot_default_artifacts(tmp_path)
    generated_config_paths = [
        tmp_path / "configs" / "sources.yaml",
        tmp_path / "configs" / "entities.yaml",
        tmp_path / "configs" / "scoring.yaml",
    ]
    for path in generated_config_paths:
        path.parent.mkdir(exist_ok=True)
        path.write_text("generated: true\n", encoding="utf-8")

    with pytest.raises(smoke.SmokeError) as exc_info:
        smoke.assert_default_artifacts_unchanged(tmp_path, before)

    message = str(exc_info.value)
    assert "default data/reports or generated configs" in message
    assert "created:" in message
    assert "configs/sources.yaml" in message
    assert "configs/entities.yaml" in message
    assert "configs/scoring.yaml" in message
```

- [ ] **Step 3: Run the test and verify RED**

Run:

```bash
uv --no-config run --frozen pytest \
  tests/test_first_run_smoke.py::test_default_artifact_guard_detects_new_repo_config_files -q
```

Expected: the test fails because the current snapshot only includes `data/` and
`reports/`, so no `SmokeError` is raised.

## Task 2: Extend Default Artifact Snapshot To Generated Configs

**Files:**

- Modify: `scripts/check_first_run_smoke.py`

- [ ] **Step 1: Add generated config artifact constant**

Add this constant immediately before `file_digest(...)`:

```python
DEFAULT_GENERATED_CONFIG_ARTIFACT_PATHS = (
    Path("configs/sources.yaml"),
    Path("configs/entities.yaml"),
    Path("configs/scoring.yaml"),
)
```

- [ ] **Step 2: Extend `snapshot_default_artifacts(...)`**

Replace the function body with:

```python
def snapshot_default_artifacts(repo_root: Path) -> dict[Path, str]:
    artifacts: dict[Path, str] = {}
    for directory_name in ("data", "reports"):
        directory = repo_root / directory_name
        if not directory.exists():
            continue
        for path in directory.rglob("*"):
            if path.is_file():
                artifacts[path.relative_to(repo_root)] = file_digest(path)

    for relative_path in DEFAULT_GENERATED_CONFIG_ARTIFACT_PATHS:
        path = repo_root / relative_path
        if path.is_file():
            artifacts[relative_path] = file_digest(path)
    return artifacts
```

- [ ] **Step 3: Update the error wording**

Replace:

```python
raise SmokeError(f"Smoke changed files under default data/reports ({'; '.join(changes)})")
```

with:

```python
raise SmokeError(
    "Smoke changed files under default data/reports or generated configs "
    f"({'; '.join(changes)})"
)
```

- [ ] **Step 4: Run the new test and verify GREEN**

Run:

```bash
uv --no-config run --frozen pytest \
  tests/test_first_run_smoke.py::test_default_artifact_guard_detects_new_repo_config_files -q
```

Expected: the test passes.

## Task 3: Focused Verification And Code Review

**Files:**

- Modify: `scripts/check_first_run_smoke.py`
- Modify: `tests/test_first_run_smoke.py`
- Add: `docs/reviews/opencode-stage-182-code-review-prompt.md`
- Add: `docs/reviews/opencode-stage-182-code-review.md`

- [ ] **Step 1: Run focused verification**

Run:

```bash
uv --no-config run --frozen pytest \
  tests/test_first_run_smoke.py::test_default_artifact_guard_detects_new_repo_data_and_report_files \
  tests/test_first_run_smoke.py::test_default_artifact_guard_detects_new_repo_config_files \
  tests/test_first_run_smoke.py::test_default_artifact_guard_detects_changed_repo_data_and_report_files \
  tests/test_first_run_smoke.py::test_default_artifact_guard_detects_deleted_repo_data_or_report_files -q
uv --no-config run --frozen python scripts/check_first_run_smoke.py --repo-root .
uv --no-config run --frozen ruff check scripts/check_first_run_smoke.py tests/test_first_run_smoke.py
uv --no-config run --frozen ruff format --check scripts/check_first_run_smoke.py tests/test_first_run_smoke.py
```

Expected: all focused tests and checks pass.

- [ ] **Step 2: Create code review prompt**

Create `docs/reviews/opencode-stage-182-code-review-prompt.md` with a prompt
that asks local opencode to review the Stage 182 implementation. The prompt
must require the response to start with:

```text
# Stage 182 Code Review
```

- [ ] **Step 3: Run code review**

Run:

```bash
tmp_review="$(mktemp)"
opencode run --model zhipuai-coding-plan/glm-5.2 --variant max \
  --dir /home/ubuntu/fashion-radar \
  "$(cat docs/reviews/opencode-stage-182-code-review-prompt.md)" > "$tmp_review" 2>&1
sed -n '1,320p' "$tmp_review"
awk 'BEGIN{copy=0} /^# Stage 182 Code Review/{copy=1} copy{print}' "$tmp_review" > docs/reviews/opencode-stage-182-code-review.md
if [ ! -s docs/reviews/opencode-stage-182-code-review.md ]; then cp "$tmp_review" docs/reviews/opencode-stage-182-code-review.md; fi
rm -f "$tmp_review"
```

Expected: completed review output with no critical or important findings. Clean
the artifact so it contains only one final review body if opencode includes
process chatter, ANSI output, command logs, code fences, or multiple drafts.

## Task 4: Release Gate, Release Review, Commit, And Push

**Files:**

- Add: `docs/reviews/opencode-stage-182-release-review-prompt.md`
- Add: `docs/reviews/opencode-stage-182-release-review.md`

- [ ] **Step 1: Run release gate**

Run:

```bash
env -u all_proxy -u ALL_PROXY -u http_proxy -u HTTP_PROXY -u https_proxy -u HTTPS_PROXY -u no_proxy -u NO_PROXY uv --no-config run --frozen pytest -q
uv --no-config run --frozen python scripts/check_first_run_smoke.py --repo-root .
uv --no-config run --frozen python scripts/check_release_hygiene.py --repo-root .
uv --no-config run --frozen ruff check .
uv --no-config run --frozen ruff format --check .
env -u UV_DEFAULT_INDEX -u UV_INDEX_URL -u UV_EXTRA_INDEX_URL UV_NO_CONFIG=1 uv lock --check
git diff --check
rg -n 'ghp_[A-Za-z0-9]+' .
git config --get-all http.https://github.com/.extraheader
```

Expected: all commands pass; token and extraheader checks report no persisted
secrets. For the two absence checks, exit 1 with no output is the expected clean
result.

- [ ] **Step 2: Create and run release review**

Create `docs/reviews/opencode-stage-182-release-review-prompt.md` requiring the
review body to start with:

```text
# Stage 182 Release Review
```

Then run the same temp-file `opencode run --model zhipuai-coding-plan/glm-5.2
--variant max` capture flow used for code review, copying the completed review
to `docs/reviews/opencode-stage-182-release-review.md`.

Expected: completed review output with no critical or important findings. Clean
the artifact if needed.

- [ ] **Step 3: Commit and push**

Run:

```bash
git status --short
git add \
  scripts/check_first_run_smoke.py \
  tests/test_first_run_smoke.py \
  docs/superpowers/specs/2026-06-24-stage-182-first-run-config-artifact-guard-design.md \
  docs/superpowers/plans/2026-06-24-stage-182-first-run-config-artifact-guard-plan.md \
  docs/reviews/opencode-stage-182-plan-review-prompt.md \
  docs/reviews/opencode-stage-182-plan-review.md \
  docs/reviews/opencode-stage-182-code-review-prompt.md \
  docs/reviews/opencode-stage-182-code-review.md \
  docs/reviews/opencode-stage-182-release-review-prompt.md \
  docs/reviews/opencode-stage-182-release-review.md
git commit -m "test: guard first-run config artifacts"
git push origin main
```

Expected: commit succeeds and `main` pushes to GitHub.

## Self-Review Notes

- Spec coverage: Task 1 adds the RED test, Task 2 extends the snapshot and
  message, Task 3 covers focused verification and code review, and Task 4
  covers release gate, release review, commit, and push.
- Placeholder scan: no placeholders or deferred implementation notes.
- Boundary check: the plan monitors only the three generated config filenames,
  not the full `configs/` tree, and does not change smoke command order,
  validators, runtime CLI behavior, collectors, dependencies, lockfiles, source
  acquisition, connectors, scraping, platform APIs, monitoring, scheduling,
  ranking, demand proof, coverage verification, or compliance-review product
  behavior.
