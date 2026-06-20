# Stage 125 Issue Template Verification Command Parity Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Align GitHub bug report issue-template verification examples with no-config/frozen uv run commands.

**Architecture:** Extend the existing text-based docs drift test to include `.github/ISSUE_TEMPLATE/bug_report.yml`, then update only the bug report verification placeholder. Preserve ordinary local CLI examples such as `uv run fashion-radar doctor`.

**Tech Stack:** Python 3.11, pytest docs tests, GitHub issue-template YAML.

---

## Files

- Modify `tests/test_cli_docs.py`
  - Add a `BUG_REPORT_TEMPLATE` constant.
  - Include the bug report template in the ruff/pytest command parity check.
  - Include the bug report template in the stale verification command ban.
  - Assert `uv run fashion-radar doctor` and `UV_NO_CONFIG=1 uv lock --check`
    remain present in the template.
- Modify `.github/ISSUE_TEMPLATE/bug_report.yml`
  - Replace stale ruff/pytest placeholder commands with
    `uv --no-config run --frozen ...`.
- Create `docs/reviews/opencode-stage-125-plan-review-prompt.md`.
- Create `docs/reviews/opencode-stage-125-plan-review.md`.
- Create `docs/reviews/opencode-stage-125-code-review-prompt.md`.
- Create `docs/reviews/opencode-stage-125-code-review.md`.

No runtime product code, dependencies, lockfile, connectors, scraping, platform
APIs, browser automation, scheduling, source acquisition, demand proof, ranking,
coverage verification, or compliance/audit product behavior is part of this
stage.

## Task 1: Add RED issue-template docs drift test coverage

**Files:**

- Modify: `tests/test_cli_docs.py`

- [ ] **Step 1: Add the bug report template constant**

After the existing `PULL_REQUEST_TEMPLATE` constant, add:

```python
BUG_REPORT_TEMPLATE = ROOT / ".github" / "ISSUE_TEMPLATE" / "bug_report.yml"
```

- [ ] **Step 2: Read the bug report template in the parity test**

In `test_github_verification_surfaces_use_no_config_frozen_uv_run`, after:

```python
pull_request_template = _read(PULL_REQUEST_TEMPLATE)
```

add:

```python
bug_report_template = _read(BUG_REPORT_TEMPLATE)
```

- [ ] **Step 3: Require no-config/frozen ruff and pytest commands in the bug report template**

In the `else` branch for ruff/pytest commands, change:

```python
surfaces = (ci_workflow, readme, contributing, pull_request_template, checklist)
```

to:

```python
surfaces = (
    ci_workflow,
    readme,
    contributing,
    pull_request_template,
    bug_report_template,
    checklist,
)
```

- [ ] **Step 4: Include the bug report template in the stale command ban**

In the stale-command surface tuple, add `bug_report_template` between
`pull_request_template` and `checklist`:

```python
    for surface in (
        ci_workflow,
        readme,
        contributing,
        pull_request_template,
        bug_report_template,
        checklist,
        first_run_doc,
    ):
```

- [ ] **Step 5: Preserve local issue-template examples**

Before the existing CONTRIBUTING preservation assertions, add:

```python
    assert "uv run fashion-radar doctor" in bug_report_template
    assert "UV_NO_CONFIG=1 uv lock --check" in bug_report_template
```

- [ ] **Step 6: Run the RED test**

Run:

```bash
uv --no-config run --frozen pytest tests/test_cli_docs.py::test_github_verification_surfaces_use_no_config_frozen_uv_run -q
```

Expected result: fail because the bug report template still uses `uv run
pytest`, `uv run ruff check .`, and `uv run ruff format --check .`.

## Task 2: Update bug report verification placeholder

**Files:**

- Modify: `.github/ISSUE_TEMPLATE/bug_report.yml`

- [ ] **Step 1: Replace stale ruff/pytest placeholder commands**

In the `verification` placeholder, replace:

```yaml
        uv run pytest
        uv run ruff check .
        uv run ruff format --check .
```

with:

```yaml
        uv --no-config run --frozen pytest
        uv --no-config run --frozen ruff check .
        uv --no-config run --frozen ruff format --check .
```

Keep these existing lines unchanged:

```yaml
        uv run fashion-radar doctor
        UV_NO_CONFIG=1 uv lock --check
```

- [ ] **Step 2: Run the GREEN test**

Run:

```bash
uv --no-config run --frozen pytest tests/test_cli_docs.py::test_github_verification_surfaces_use_no_config_frozen_uv_run -q
```

Expected result: pass.

## Task 3: Focused verification and local code review

**Files:**

- Create: `docs/reviews/opencode-stage-125-code-review-prompt.md`
- Create: `docs/reviews/opencode-stage-125-code-review.md`

- [ ] **Step 1: Run focused docs tests and lint**

Run:

```bash
uv --no-config run --frozen pytest tests/test_cli_docs.py -q -k "github_verification_surfaces or no_config"
uv --no-config run --frozen ruff check tests/test_cli_docs.py
uv --no-config run --frozen ruff format --check tests/test_cli_docs.py
```

Expected result: selected tests, lint, and format checks pass.

- [ ] **Step 2: Write Stage 125 code review prompt**

Create `docs/reviews/opencode-stage-125-code-review-prompt.md` with:

```markdown
Review the Stage 125 implementation before release.

Repository: `/home/ubuntu/fashion-radar`

Stage goal:
- Align `.github/ISSUE_TEMPLATE/bug_report.yml` verification examples with
  no-config/frozen uv run commands.
- Preserve ordinary local CLI examples in the issue template.

Files changed:
- `.github/ISSUE_TEMPLATE/bug_report.yml`
- `tests/test_cli_docs.py`
- Stage 125 design/plan/review artifacts

Review focus:
1. Does the implementation match the Stage 125 design and plan?
2. Does the bug report template use no-config/frozen ruff and pytest
   verification commands?
3. Does the test reject stale `uv run pytest` and `uv run ruff ...` examples in
   the bug report template without rejecting `uv run fashion-radar doctor`?
4. Does the stage avoid runtime, CLI, dependency, connector, scraping,
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

- [ ] **Step 3: Run local opencode code review**

Run:

```bash
tmp_review="$(mktemp)"
opencode run --model zhipuai-coding-plan/glm-5.2 --variant max --dir /home/ubuntu/fashion-radar "$(cat docs/reviews/opencode-stage-125-code-review-prompt.md)" > "$tmp_review"
sed -n '1,220p' "$tmp_review"
python3 - "$tmp_review" docs/reviews/opencode-stage-125-code-review.md <<'PY'
from pathlib import Path
import re
import sys

raw = Path(sys.argv[1]).read_text(encoding="utf-8")
text = re.sub(r"\x1b\[[0-9;?]*[ -/]*[@-~]", "", raw)
start = text.find("# Stage 125 Code Review")
if start != -1:
    text = text[start:]
cut_markers = ("\n> build ", "\n$ ", "\n→ ", "\n<- ")
cut_positions = [text.find(marker) for marker in cut_markers if text.find(marker) != -1]
if cut_positions:
    text = text[: min(cut_positions)]
lines = [line.rstrip() for line in text.splitlines()]
Path(sys.argv[2]).write_text("\n".join(lines).strip() + "\n", encoding="utf-8")
PY
test -s docs/reviews/opencode-stage-125-code-review.md
rm -f "$tmp_review"
```

Expected result: review artifact is non-empty and contains no Critical or
Important blockers.

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

- [ ] **Step 3: Stage the Stage 125 files**

Run:

```bash
git add .github/ISSUE_TEMPLATE/bug_report.yml \
  tests/test_cli_docs.py \
  docs/superpowers/specs/2026-06-20-stage-125-issue-template-verification-command-parity-design.md \
  docs/superpowers/plans/2026-06-20-stage-125-issue-template-verification-command-parity-plan.md \
  docs/reviews/opencode-stage-125-plan-review-prompt.md \
  docs/reviews/opencode-stage-125-plan-review.md \
  docs/reviews/opencode-stage-125-code-review-prompt.md \
  docs/reviews/opencode-stage-125-code-review.md
```

- [ ] **Step 4: Verify staged diff and commit**

Run:

```bash
git diff --cached --stat
git diff --cached | rg -n 'ghp_[A-Za-z0-9]+' || true
git commit -m "Align issue template verification commands"
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

- Spec coverage: the plan covers failing docs tests, issue-template update,
  focused verification, local code review, full release gate, commit, push, and
  CI.
- Marker scan: no unresolved implementation markers remain. The push command
  intentionally uses `<token supplied by user>` as a non-secret stand-in.
- Type consistency: constants, file paths, command strings, and test names
  match across tasks.
