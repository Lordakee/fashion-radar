# Stage 129 PR Template Package Smoke Parity Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Align the pull request template's packaging verification guidance with CI and the upload checklist temp-build/archive-check package smoke path.

**Architecture:** Extend existing docs parity tests to include `.github/pull_request_template.md` for the temp build and package archive checker commands, update the canonical GitHub verification surface matrix for those package commands, then expand the packaging checkbox in the PR template with exact commands.

**Tech Stack:** Python 3.11, pytest docs tests, Markdown GitHub pull request template.

---

## Files

- Modify `tests/test_cli_docs.py`
  - Add a focused PR template package smoke parity test.
- Modify `.github/pull_request_template.md`
  - Expand the packaging/templates verification checkbox with `tmp_build`,
    `uv --no-config build --out-dir "$tmp_build"`, and
    `scripts/check_package_archives.py "$tmp_build"`.
- Create `docs/reviews/opencode-stage-129-plan-review-prompt.md`.
- Create `docs/reviews/opencode-stage-129-plan-review.md`.
- Create `docs/reviews/opencode-stage-129-code-review-prompt.md`.
- Create `docs/reviews/opencode-stage-129-code-review.md`.

The plan-review prompt and plan-review artifact are produced before
implementation begins; the implementation tasks create only the code-review
prompt and code-review artifact.

No runtime product behavior, dependencies, lockfile, package checker behavior,
CI behavior, connectors, scraping, platform APIs, browser automation,
scheduling, source acquisition, demand proof, ranking, coverage verification,
or compliance/audit product behavior is part of this stage.

## Task 1: Add RED PR template package smoke docs tests

**Files:**

- Modify: `tests/test_cli_docs.py`

- [ ] **Step 1: Add focused PR template package smoke test**

After `test_package_archive_smoke_command_is_documented_and_in_ci`, add:

```python
def test_pull_request_template_package_smoke_uses_temp_build_archive_checker() -> None:
    template = _read(PULL_REQUEST_TEMPLATE)
    verification = _markdown_section_exact_heading(template, "Verification")

    assert 'tmp_build="$(mktemp -d)"' in verification
    assert 'uv --no-config build --out-dir "$tmp_build"' in verification
    assert (
        'uv --no-config run --frozen python '
        'scripts/check_package_archives.py "$tmp_build"'
    ) in verification
    assert '"$tmp_build"/*.whl' in verification
    assert "`uv --no-config build` plus installed-wheel smoke" not in verification
```

- [ ] **Step 2: Run the RED test**

Run:

```bash
uv --no-config run --frozen pytest tests/test_cli_docs.py::test_pull_request_template_package_smoke_uses_temp_build_archive_checker -q
```

Expected result: fail because the PR template does not yet include the temp
build directory or archive checker command.

- [ ] **Step 3: Add PR template to canonical package verification surfaces**

In `test_github_verification_surfaces_use_no_config_frozen_uv_run`, add
`pull_request_template` to the surfaces used for:

- `check_package_archives.py`
- `build --out-dir`

- [ ] **Step 4: Run the canonical RED test**

Run:

```bash
uv --no-config run --frozen pytest tests/test_cli_docs.py::test_github_verification_surfaces_use_no_config_frozen_uv_run -q
```

Expected result: fail because the PR template does not yet include the temp
build directory or archive checker command.

## Task 2: Expand PR template packaging verification guidance

**Files:**

- Modify: `.github/pull_request_template.md`

- [ ] **Step 1: Replace packaging checkbox text**

Replace:

```markdown
- [ ] If packaging/templates changed: `uv --no-config build` plus installed-wheel smoke for `fashion-radar --help`, `init`, `doctor`, and `fashion_radar.templates/daily_report.md`.
```

with:

```markdown
- [ ] If packaging/templates changed:
  - `tmp_build="$(mktemp -d)"`
  - `uv --no-config build --out-dir "$tmp_build"`
  - `uv --no-config run --frozen python scripts/check_package_archives.py "$tmp_build"`
  - Installed-wheel smoke from `"$tmp_build"/*.whl` for `fashion-radar --help`, `init`, `doctor`, and `fashion_radar.templates/daily_report.md`.
```

- [ ] **Step 2: Run the GREEN tests**

Run:

```bash
uv --no-config run --frozen pytest tests/test_cli_docs.py::test_pull_request_template_package_smoke_uses_temp_build_archive_checker tests/test_cli_docs.py::test_package_archive_smoke_command_is_documented_and_in_ci tests/test_cli_docs.py::test_github_verification_surfaces_use_no_config_frozen_uv_run -q
```

Expected result: pass.

## Task 3: Focused verification and local code review

**Files:**

- Create: `docs/reviews/opencode-stage-129-code-review-prompt.md`
- Create: `docs/reviews/opencode-stage-129-code-review.md`

- [ ] **Step 1: Run focused docs tests and lint**

Run:

```bash
uv --no-config run --frozen pytest tests/test_cli_docs.py -q -k "pull_request_template_package_smoke_uses_temp_build_archive_checker or package_archive_smoke_command_is_documented_and_in_ci or github_verification_surfaces_use_no_config_frozen_uv_run"
uv --no-config run --frozen ruff check tests/test_cli_docs.py
uv --no-config run --frozen ruff format --check tests/test_cli_docs.py
git diff --check
```

Expected result: selected docs tests, lint, format, and whitespace checks pass.

- [ ] **Step 2: Write Stage 129 code review prompt**

Create `docs/reviews/opencode-stage-129-code-review-prompt.md` with:

```markdown
Review the Stage 129 implementation before release.

Repository: `/home/ubuntu/fashion-radar`

Stage goal:
- Align `.github/pull_request_template.md` packaging verification guidance with
  CI/upload-checklist temp build and package archive checker commands.
- Keep the change docs/test-only.

Files changed:
- `.github/pull_request_template.md`
- `tests/test_cli_docs.py`
- Stage 129 design/plan/review artifacts

Review focus:
1. Does the implementation match the Stage 129 design and plan?
2. Does the PR template include `tmp_build`, `uv --no-config build --out-dir
   "$tmp_build"`, and `scripts/check_package_archives.py "$tmp_build"`?
3. Does `test_github_verification_surfaces_use_no_config_frozen_uv_run` include
   the PR template as a surface for the package archive checker and temp build
   commands?
4. Does the focused docs test avoid requiring the full upload checklist in the
   PR template?
5. Does the stage avoid runtime product behavior, package checker behavior, CI
   behavior, dependencies, lockfile, connectors, scraping, browser automation,
   platform API, monitoring, scheduling, source acquisition, demand proof,
   ranking, coverage verification, and compliance/audit product behavior?

Return:
Start with `# Stage 129 Code Review`, then include:
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
opencode run --model zhipuai-coding-plan/glm-5.2 --variant max --dir /home/ubuntu/fashion-radar "$(cat docs/reviews/opencode-stage-129-code-review-prompt.md)" > "$tmp_review"
sed -n '1,240p' "$tmp_review"
python3 - "$tmp_review" docs/reviews/opencode-stage-129-code-review.md <<'PY'
from pathlib import Path
import re
import sys

raw = Path(sys.argv[1]).read_text(encoding="utf-8")
text = re.sub(r"\x1b\[[0-9;?]*[ -/]*[@-~]", "", raw)
start = text.find("# Stage 129 Code Review")
if start != -1:
    text = text[start:]
cut_markers = ("\n> build ", "\n$ ", "\n-> ", "\n<- ")
cut_positions = [text.find(marker) for marker in cut_markers if text.find(marker) != -1]
if cut_positions:
    text = text[: min(cut_positions)]
lines = [line.rstrip() for line in text.splitlines()]
Path(sys.argv[2]).write_text("\n".join(lines).strip() + "\n", encoding="utf-8")
PY
test -s docs/reviews/opencode-stage-129-code-review.md
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
if rg -n 'ghp_[A-Za-z0-9]+' .; then echo 'GitHub token pattern found in worktree' >&2; exit 1; fi
if [ -n "$(git config --get-all http.https://github.com/.extraheader || true)" ]; then echo 'Persistent GitHub auth header found' >&2; exit 1; fi
```

Expected result: release hygiene, full pytest, ruff, format, lock check,
lockfile diff, whitespace check, token absence assertion, and persistent git
auth-header absence assertion all pass.

- [ ] **Step 2: Commit Stage 129**

Run:

```bash
git status --short --untracked-files=all
git add .github/pull_request_template.md tests/test_cli_docs.py docs/superpowers/specs/2026-06-20-stage-129-pr-template-package-smoke-parity-design.md docs/superpowers/plans/2026-06-20-stage-129-pr-template-package-smoke-parity-plan.md docs/reviews/opencode-stage-129-plan-review-prompt.md docs/reviews/opencode-stage-129-plan-review.md docs/reviews/opencode-stage-129-code-review-prompt.md docs/reviews/opencode-stage-129-code-review.md
git commit -m "Align PR template package smoke guidance"
```

Expected result: one commit containing only Stage 129 docs/test/review
artifacts.

- [ ] **Step 3: Push with temporary auth header**

Run the established temporary-header push pattern without storing credentials in
git config or files:

```bash
AUTH_HEADER="$(printf 'x-access-token:%s' "$GITHUB_TOKEN_FOR_PUSH" | base64 -w0)"
git -c http.https://github.com/.extraheader="AUTHORIZATION: basic ${AUTH_HEADER}" push origin main
unset AUTH_HEADER
git config --get-all http.https://github.com/.extraheader || true
```

Expected result: push succeeds and no persistent GitHub auth header remains.

- [ ] **Step 4: Verify remote and CI**

Run:

```bash
git ls-remote origin refs/heads/main
python3 - <<'PY'
import json
import os
import subprocess
import sys
import time
import urllib.request

repo = "Lordakee/fashion-radar"
sha = subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()
api = f"https://api.github.com/repos/{repo}/actions/runs?head_sha={sha}&per_page=5"
for _ in range(60):
    request = urllib.request.Request(
        api,
        headers={
            "Accept": "application/vnd.github+json",
            **(
                {"Authorization": f"Bearer {os.environ['GITHUB_TOKEN_FOR_PUSH']}"}
                if os.environ.get("GITHUB_TOKEN_FOR_PUSH")
                else {}
            ),
        },
    )
    with urllib.request.urlopen(request, timeout=30) as response:
        payload = json.load(response)
    runs = payload.get("workflow_runs", [])
    if runs:
        run = runs[0]
        status = run.get("status")
        conclusion = run.get("conclusion")
        print(f"{run.get('html_url')} status={status} conclusion={conclusion}")
        if status == "completed":
            if conclusion == "success":
                sys.exit(0)
            sys.exit(f"CI failed with conclusion={conclusion}")
    time.sleep(10)
sys.exit("Timed out waiting for CI run")
PY
```

Then poll the latest GitHub Actions run for the pushed SHA until it reaches a
terminal state.

Expected result: remote `main` points at the Stage 129 commit and CI completes
successfully.
