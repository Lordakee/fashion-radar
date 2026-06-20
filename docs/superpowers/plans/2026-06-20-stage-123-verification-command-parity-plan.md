# Stage 123 Verification Command Parity Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Align CI, contributor, PR-template, and GitHub upload verification commands with `uv --no-config run --frozen ...`.

**Architecture:** Add a text-based docs drift test that pins the verification command forms, then update the CI workflow and contributor-facing verification docs to match. Keep ordinary local workflow examples and mirror install examples unchanged.

**Tech Stack:** Python 3.11, pytest docs tests, GitHub Actions YAML, Markdown, uv.

---

## Files

- Modify `tests/test_cli_docs.py`
  - Add constants for `CONTRIBUTING.md` and `.github/pull_request_template.md`.
  - Add a test pinning no-config/frozen verification command parity.
  - Update existing first-run and archive command assertions to the new command
    form.
- Modify `.github/workflows/ci.yml`
  - Use no-config/frozen command forms for release hygiene, first-run smoke,
    lint, format, tests, and package archive checker.
  - Use `uv --no-config build` for the release build.
- Modify `README.md`
  - Use no-config/frozen command forms in the Development verification block.
  - Update the automated first-run source smoke command.
- Modify `CONTRIBUTING.md`
  - Use no-config/frozen command forms in the Verification section only.
- Modify `.github/pull_request_template.md`
  - Use no-config/frozen command forms in the Verification checklist only.
- Modify `docs/github-upload-checklist.md`
  - Use no-config/frozen command forms in the upload and package smoke command
    blocks.
- Modify `docs/first-run.md`
  - Update the automated first-run source smoke command.

No runtime code, dependency, lockfile, connector, scraping, platform API,
monitoring, scheduling, source acquisition, demand proof, ranking, coverage
verification, or compliance/audit product behavior is part of this stage.

## Task 1: Add RED docs test for verification command parity

**Files:**

- Modify: `tests/test_cli_docs.py`

- [ ] **Step 1: Add constants for contributor-facing docs**

After the existing `CI_WORKFLOW` constant, add:

```python
CONTRIBUTING_DOC = ROOT / "CONTRIBUTING.md"
PULL_REQUEST_TEMPLATE = ROOT / ".github" / "pull_request_template.md"
```

- [ ] **Step 2: Update existing command constants**

In `test_package_archive_smoke_command_is_documented_and_in_ci`, change:

```python
hygiene_command = "UV_NO_CONFIG=1 uv run python scripts/check_release_hygiene.py --repo-root ."
build_command = 'UV_NO_CONFIG=1 uv build --out-dir "$tmp_build"'
archive_command = 'UV_NO_CONFIG=1 uv run python scripts/check_package_archives.py "$tmp_build"'
```

to:

```python
hygiene_command = (
    "uv --no-config run --frozen python scripts/check_release_hygiene.py --repo-root ."
)
build_command = 'uv --no-config build --out-dir "$tmp_build"'
archive_command = (
    'uv --no-config run --frozen python scripts/check_package_archives.py "$tmp_build"'
)
```

In `test_first_run_smoke_command_is_documented_and_in_ci`, change:

```python
source_command = "UV_NO_CONFIG=1 uv run python scripts/check_first_run_smoke.py --repo-root ."
```

to:

```python
source_command = (
    "uv --no-config run --frozen python scripts/check_first_run_smoke.py --repo-root ."
)
```

- [ ] **Step 3: Add the new failing test**

Add this test after `test_agent_verification_docs_prefer_no_config_frozen_uv_run`:

```python
def test_github_verification_surfaces_use_no_config_frozen_uv_run() -> None:
    ci_workflow = _read(CI_WORKFLOW)
    readme = _read(README)
    contributing = _read(CONTRIBUTING_DOC)
    pull_request_template = _read(PULL_REQUEST_TEMPLATE)
    checklist = _read(UPLOAD_CHECKLIST)
    first_run_doc = _read(FIRST_RUN_DOC)

    no_config_commands = (
        "uv --no-config run --frozen ruff check .",
        "uv --no-config run --frozen ruff format --check .",
        "uv --no-config run --frozen pytest",
        "uv --no-config run --frozen python scripts/check_release_hygiene.py --repo-root .",
        "uv --no-config run --frozen python scripts/check_first_run_smoke.py --repo-root .",
        'uv --no-config run --frozen python scripts/check_package_archives.py "$tmp_build"',
        'uv --no-config build --out-dir "$tmp_build"',
    )
    for command in no_config_commands:
        if "check_release_hygiene.py" in command:
            surfaces = (ci_workflow, checklist)
        elif "check_first_run_smoke.py" in command:
            surfaces = (ci_workflow, checklist, readme, first_run_doc)
        elif "check_package_archives.py" in command:
            surfaces = (ci_workflow, checklist)
        elif "build --out-dir" in command:
            surfaces = (ci_workflow, checklist, readme, first_run_doc)
        else:
            surfaces = (ci_workflow, readme, contributing, pull_request_template, checklist)
        for surface in surfaces:
            assert command in surface

    stale_verification_commands = (
        "uv run ruff check .",
        "uv run ruff format --check .",
        "uv run pytest",
        "UV_NO_CONFIG=1 uv run python scripts/check_release_hygiene.py --repo-root .",
        "UV_NO_CONFIG=1 uv run python scripts/check_first_run_smoke.py --repo-root .",
        'UV_NO_CONFIG=1 uv run python scripts/check_package_archives.py "$tmp_build"',
        'UV_NO_CONFIG=1 uv build --out-dir "$tmp_build"',
    )
    for surface in (ci_workflow, readme, contributing, pull_request_template, checklist, first_run_doc):
        for command in stale_verification_commands:
            assert command not in surface

    assert "uv run fashion-radar init" in contributing
    assert "uv run fashion-radar dashboard" in contributing
```

- [ ] **Step 4: Run the RED tests**

Run:

```bash
uv --no-config run --frozen pytest tests/test_cli_docs.py::test_package_archive_smoke_command_is_documented_and_in_ci tests/test_cli_docs.py::test_first_run_smoke_command_is_documented_and_in_ci tests/test_cli_docs.py::test_github_verification_surfaces_use_no_config_frozen_uv_run -q
```

Expected result: fail because the docs and CI still use the old command forms.

## Task 2: Update CI and GitHub-facing verification commands

**Files:**

- Modify: `.github/workflows/ci.yml`
- Modify: `README.md`
- Modify: `CONTRIBUTING.md`
- Modify: `.github/pull_request_template.md`
- Modify: `docs/github-upload-checklist.md`
- Modify: `docs/first-run.md`

- [ ] **Step 1: Update CI workflow**

In `.github/workflows/ci.yml`:

- Replace `UV_NO_CONFIG=1 uv run python scripts/check_release_hygiene.py --repo-root .`
  with `uv --no-config run --frozen python scripts/check_release_hygiene.py --repo-root .`.
- Replace `UV_NO_CONFIG=1 uv run python scripts/check_first_run_smoke.py --repo-root .`
  with `uv --no-config run --frozen python scripts/check_first_run_smoke.py --repo-root .`.
- Replace `uv run ruff check .` with `uv --no-config run --frozen ruff check .`.
- Replace `uv run ruff format --check .` with
  `uv --no-config run --frozen ruff format --check .`.
- Replace `uv run pytest` with `uv --no-config run --frozen pytest`.
- Replace `UV_NO_CONFIG=1 uv build --out-dir "$tmp_build"` with
  `uv --no-config build --out-dir "$tmp_build"`.
- Replace `UV_NO_CONFIG=1 uv run python scripts/check_package_archives.py "$tmp_build"`
  with
  `uv --no-config run --frozen python scripts/check_package_archives.py "$tmp_build"`.

- [ ] **Step 2: Update README verification and smoke examples**

In `README.md`, update the automated source-checkout first-run smoke command:

```bash
uv --no-config run --frozen python scripts/check_first_run_smoke.py --repo-root .
```

Update the installed-wheel smoke build command:

```bash
uv --no-config build --out-dir "$tmp_build"
```

Update the `## Development` verification block:

```bash
uv sync --locked --dev
uv --no-config run --frozen ruff check .
uv --no-config run --frozen ruff format --check .
uv --no-config run --frozen pytest
```

- [ ] **Step 3: Update first-run smoke docs**

In `docs/first-run.md`, update the automated source-checkout first-run smoke
command:

```bash
uv --no-config run --frozen python scripts/check_first_run_smoke.py --repo-root .
```

Update the installed-wheel smoke build command:

```bash
uv --no-config build --out-dir "$tmp_build"
```

- [ ] **Step 4: Update contributor verification docs**

In `CONTRIBUTING.md` under `## Verification`, replace:

```bash
uv run ruff check .
uv run ruff format --check .
uv run pytest
```

with:

```bash
uv --no-config run --frozen ruff check .
uv --no-config run --frozen ruff format --check .
uv --no-config run --frozen pytest
```

Leave the `## Local Workflow` and dashboard examples as `uv run fashion-radar
...`.

- [ ] **Step 5: Update pull request template**

In `.github/pull_request_template.md`, replace the three verification checklist
items for ruff and pytest with:

```markdown
- [ ] `uv --no-config run --frozen ruff check .`
- [ ] `uv --no-config run --frozen ruff format --check .`
- [ ] `uv --no-config run --frozen pytest`
```

- [ ] **Step 6: Update upload checklist**

In `docs/github-upload-checklist.md`, update the `## Before Upload` command
block:

```bash
uv --no-config run --frozen ruff check .
uv --no-config run --frozen ruff format --check .
uv --no-config run --frozen pytest
```

Update package smoke command blocks:

```bash
uv --no-config run --frozen python scripts/check_release_hygiene.py --repo-root .
uv --no-config run --frozen python scripts/check_first_run_smoke.py --repo-root .
uv --no-config build --out-dir "$tmp_build"
uv --no-config run --frozen python scripts/check_package_archives.py "$tmp_build"
```

- [ ] **Step 7: Run the focused docs tests**

Run:

```bash
uv --no-config run --frozen pytest tests/test_cli_docs.py::test_package_archive_smoke_command_is_documented_and_in_ci tests/test_cli_docs.py::test_first_run_smoke_command_is_documented_and_in_ci tests/test_cli_docs.py::test_github_verification_surfaces_use_no_config_frozen_uv_run -q
```

Expected result: pass.

## Task 3: Focused verification and local code review

**Files:**

- Create: `docs/reviews/opencode-stage-123-code-review-prompt.md`
- Create: `docs/reviews/opencode-stage-123-code-review.md`

- [ ] **Step 1: Run focused docs tests**

Run:

```bash
uv --no-config run --frozen pytest tests/test_cli_docs.py -q -k "no_config or first_run_smoke or package_archive"
```

Expected result: selected tests pass.

- [ ] **Step 2: Run focused lint and format checks**

Run:

```bash
uv --no-config run --frozen ruff check tests/test_cli_docs.py
uv --no-config run --frozen ruff format --check tests/test_cli_docs.py
```

Expected result: both commands pass.

- [ ] **Step 3: Write Stage 123 code review prompt**

Create `docs/reviews/opencode-stage-123-code-review-prompt.md` with:

```markdown
Review the Stage 123 implementation before release.

Repository: `/home/ubuntu/fashion-radar`

Stage goal:
- Align CI, contributor, PR-template, and GitHub upload verification commands
  with `uv --no-config run --frozen ...`.
- Preserve ordinary local workflow examples and mirror install examples.

Files changed:
- `.github/workflows/ci.yml`
- `README.md`
- `CONTRIBUTING.md`
- `.github/pull_request_template.md`
- `docs/github-upload-checklist.md`
- `docs/first-run.md`
- `tests/test_cli_docs.py`
- Stage 123 design/plan/review artifacts

Review focus:
1. Does the implementation match the Stage 123 design and plan?
2. Do release/agent/CI verification commands use no-config/frozen command
   forms consistently?
3. Are ordinary local workflow examples such as `uv run fashion-radar ...`
   preserved?
4. Are mirror install examples preserved only as local install aids?
5. Does the stage avoid runtime, CLI, dependency, connector, scraping,
   browser automation, platform API, monitoring, scheduling, source
   acquisition, demand proof, ranking, coverage verification, and
   compliance/audit product behavior?

Return:
- Critical findings, if any.
- Important findings, if any.
- Minor findings, if any.
- A final explicit statement whether there are any Critical or Important
  blockers before release.
```

- [ ] **Step 4: Run local opencode code review**

Run:

```bash
tmp_review="$(mktemp)"
opencode run --model zhipuai-coding-plan/glm-5.2 --variant max --dir /home/ubuntu/fashion-radar "$(cat docs/reviews/opencode-stage-123-code-review-prompt.md)" > "$tmp_review"
sed -n '1,220p' "$tmp_review"
python3 - "$tmp_review" docs/reviews/opencode-stage-123-code-review.md <<'PY'
from pathlib import Path
import re
import sys

raw = Path(sys.argv[1]).read_text(encoding="utf-8")
text = re.sub(r"\x1b\[[0-9;?]*[ -/]*[@-~]", "", raw)
start = text.find("# Stage 123 Code Review")
if start != -1:
    text = text[start:]
drop_prefixes = ("-> ", "<- ", "$ ", "> build ")
lines = [
    line.rstrip()
    for line in text.splitlines()
    if not any(line.startswith(prefix) for prefix in drop_prefixes)
]
Path(sys.argv[2]).write_text("\n".join(lines).strip() + "\n", encoding="utf-8")
PY
test -s docs/reviews/opencode-stage-123-code-review.md
rm -f "$tmp_review"
```

Expected result: review artifact is non-empty, contains one coherent review
body, and contains no Critical or Important blockers.

## Task 4: Full release gate, commit, push, and CI

**Files:**

- No new implementation files beyond Task 3.

- [ ] **Step 1: Run the full release gate**

Run:

```bash
uv --no-config run --frozen python scripts/check_release_hygiene.py
env -u ALL_PROXY -u all_proxy uv --no-config run --frozen pytest
uv --no-config run --frozen ruff check .
uv --no-config run --frozen ruff format --check .
env -u UV_DEFAULT_INDEX -u UV_INDEX_URL -u UV_EXTRA_INDEX_URL UV_NO_CONFIG=1 uv lock --check
git diff --exit-code -- uv.lock
git diff --check
```

Expected result: every command exits 0.

- [ ] **Step 2: Check secrets and temporary auth state**

Run:

```bash
rg -n 'ghp_[A-Za-z0-9]+' .
git config --get-all http.https://github.com/.extraheader || true
```

Expected result: no token matches in the repository and no persistent GitHub
extraheader output.

- [ ] **Step 3: Stage the Stage 123 files**

Run:

```bash
git add .github/workflows/ci.yml \
  README.md \
  CONTRIBUTING.md \
  .github/pull_request_template.md \
  docs/github-upload-checklist.md \
  docs/first-run.md \
  tests/test_cli_docs.py \
  docs/superpowers/specs/2026-06-20-stage-123-verification-command-parity-design.md \
  docs/superpowers/plans/2026-06-20-stage-123-verification-command-parity-plan.md \
  docs/reviews/opencode-stage-123-plan-review-prompt.md \
  docs/reviews/opencode-stage-123-plan-review.md \
  docs/reviews/opencode-stage-123-code-review-prompt.md \
  docs/reviews/opencode-stage-123-code-review.md
```

- [ ] **Step 4: Verify staged diff and commit**

Run:

```bash
git diff --cached --stat
git diff --cached | rg -n 'ghp_[A-Za-z0-9]+'
git commit -m "Align verification commands with frozen uv runs"
```

Expected result: commit succeeds and no token scan output appears.

- [ ] **Step 5: Push with temporary GitHub auth header**

Run:

```bash
AUTH_HEADER=$(printf 'x-access-token:%s' '<token supplied by user>' | base64 -w0)
git -c http.https://github.com/.extraheader="AUTHORIZATION: basic ${AUTH_HEADER}" push origin main
unset AUTH_HEADER
git config --get-all http.https://github.com/.extraheader || true
```

Expected result: push succeeds and no persistent GitHub extraheader output
appears.

- [ ] **Step 6: Verify remote SHA and CI**

Run:

```bash
git rev-parse HEAD
git ls-remote origin refs/heads/main
```

Expected result: both SHAs match. Then poll GitHub Actions for the pushed SHA
and require a successful CI conclusion before reporting completion.

## Self-Review

- Spec coverage: the plan covers tests, CI workflow, contributor docs, PR
  template, upload checklist, local code review, release gate, commit, push,
  and CI.
- Marker scan: no unresolved implementation markers remain. The push command
  intentionally uses `<token supplied by user>` as a non-secret stand-in.
- Type consistency: constants, file paths, command strings, and test names
  match the planned edits.
