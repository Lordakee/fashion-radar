# Stage 131 Verification Surface Parity Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Align `CONTRIBUTING.md` and `.github/pull_request_template.md`
verification sections with the release hygiene and source-checkout first-run
smoke commands already required by CI and the upload checklist.

**Architecture:** Add a focused docs test for the two contributor-facing
verification sections, update the canonical verification-surface test for the
same commands, then add the missing command lines to `CONTRIBUTING.md` and the
PR template.

**Tech Stack:** Markdown docs and existing pytest docs tests in
`tests/test_cli_docs.py`.

---

## Files

- Modify `tests/test_cli_docs.py`
  - Add a focused verification-section parity test.
  - Update canonical verification-surface expectations.
- Modify `CONTRIBUTING.md`
  - Add local release hygiene and source-checkout first-run smoke commands to
    the `Verification` block.
- Modify `.github/pull_request_template.md`
  - Add the same two commands to the `Verification` checklist before
    conditional packaging/dashboard bullets.
- Create `docs/reviews/opencode-stage-131-plan-review-prompt.md`.
- Create `docs/reviews/opencode-stage-131-plan-review.md`.
- Create `docs/reviews/opencode-stage-131-code-review-prompt.md`.
- Create `docs/reviews/opencode-stage-131-code-review.md`.

The plan-review prompt and plan-review artifact are produced before
implementation begins; the implementation tasks create only the code-review
prompt and code-review artifact.

No runtime product behavior, CI behavior, dependency changes, `uv.lock`
changes, package checker behavior, README development-block expansion,
connectors, scraping, browser automation, platform APIs, monitoring,
scheduling, source acquisition, demand proof, ranking, coverage verification,
or compliance/audit product behavior is part of this stage.

## Task 1: Add RED docs tests

**Files:**

- Modify: `tests/test_cli_docs.py`

- [ ] **Step 1: Add focused contributor verification parity test**

After the existing package-smoke docs tests, add:

```python
def test_contributing_and_pr_template_include_release_hygiene_and_source_smoke() -> None:
    contributing = _markdown_section_exact_heading(_read(CONTRIBUTING_DOC), "Verification")
    pull_request_template = _markdown_section_exact_heading(
        _read(PULL_REQUEST_TEMPLATE), "Verification"
    )

    for section in (contributing, pull_request_template):
        assert (
            "uv --no-config run --frozen python scripts/check_release_hygiene.py --repo-root ."
            in section
        )
        assert (
            "uv --no-config run --frozen python scripts/check_first_run_smoke.py --repo-root ."
            in section
        )
```

- [ ] **Step 2: Tighten canonical verification surfaces**

In `test_github_verification_surfaces_use_no_config_frozen_uv_run`:

- for `check_release_hygiene.py`, change surfaces from
  `(ci_workflow, checklist)` to
  `(ci_workflow, contributing, pull_request_template, checklist)`;
- for `check_first_run_smoke.py`, change surfaces from
  `(ci_workflow, checklist, readme, first_run_doc)` to
  `(ci_workflow, contributing, pull_request_template, checklist, readme, first_run_doc)`.

- [ ] **Step 3: Run RED tests**

Run:

```bash
uv --no-config run --frozen pytest tests/test_cli_docs.py::test_contributing_and_pr_template_include_release_hygiene_and_source_smoke tests/test_cli_docs.py::test_github_verification_surfaces_use_no_config_frozen_uv_run -q
```

Expected result: fail because `CONTRIBUTING.md` and the PR template do not yet
include the two commands.

## Task 2: Update contributor-facing verification docs

**Files:**

- Modify: `CONTRIBUTING.md`
- Modify: `.github/pull_request_template.md`

- [ ] **Step 1: Update `CONTRIBUTING.md` verification commands**

In the `## Verification` command block, add these commands before ruff/pytest:

```bash
uv --no-config run --frozen python scripts/check_release_hygiene.py --repo-root .
uv --no-config run --frozen python scripts/check_first_run_smoke.py --repo-root .
```

Keep packaging/templates and dashboard/dependencies follow-on bullets concise
and delegated to existing conditional guidance.

- [ ] **Step 2: Update PR template verification checklist**

In `.github/pull_request_template.md`, add checklist items before the
conditional packaging/dashboard bullets:

```markdown
- [ ] `uv --no-config run --frozen python scripts/check_release_hygiene.py --repo-root .`
- [ ] `uv --no-config run --frozen python scripts/check_first_run_smoke.py --repo-root .`
```

- [ ] **Step 3: Run GREEN tests**

Run:

```bash
uv --no-config run --frozen pytest tests/test_cli_docs.py::test_contributing_and_pr_template_include_release_hygiene_and_source_smoke tests/test_cli_docs.py::test_github_verification_surfaces_use_no_config_frozen_uv_run -q
```

Expected result: pass.

## Task 3: Focused verification and local code review

**Files:**

- Create: `docs/reviews/opencode-stage-131-code-review-prompt.md`
- Create: `docs/reviews/opencode-stage-131-code-review.md`

- [ ] **Step 1: Run focused verification**

Run:

```bash
uv --no-config run --frozen pytest tests/test_cli_docs.py::test_contributing_and_pr_template_include_release_hygiene_and_source_smoke tests/test_cli_docs.py::test_github_verification_surfaces_use_no_config_frozen_uv_run -q
uv --no-config run --frozen pytest tests/test_cli_docs.py -q -k "contributing or github_verification_surfaces"
uv --no-config run --frozen ruff check tests/test_cli_docs.py
uv --no-config run --frozen ruff format --check tests/test_cli_docs.py
git diff --check
```

Expected result: focused docs tests, lint, format, and whitespace checks pass.

- [ ] **Step 2: Write Stage 131 code review prompt**

Create `docs/reviews/opencode-stage-131-code-review-prompt.md` with:

```markdown
Review the Stage 131 implementation before release.

Repository: `/home/ubuntu/fashion-radar`

Stage goal:
- Align `CONTRIBUTING.md` and `.github/pull_request_template.md` verification
  sections with the local release hygiene and source-checkout first-run smoke
  commands already required by CI and the upload checklist.
- Keep the change docs/test-only.

Files changed:
- `tests/test_cli_docs.py`
- `CONTRIBUTING.md`
- `.github/pull_request_template.md`
- Stage 131 design/plan/review artifacts

Review focus:
1. Does the implementation match the Stage 131 design and plan?
2. Do `CONTRIBUTING.md` and the PR template both include the local release
   hygiene command and the source-checkout first-run smoke command in their
   `Verification` sections?
3. Does the canonical verification-surface test now require those two commands
   on `contributing` and `pull_request_template` while keeping existing
   CI/checklist/README/first-run smoke expectations?
4. Does the stage avoid package archive behavior changes, README development
   block expansion, dependency/lockfile/CI/runtime product changes, connectors,
   scraping, browser automation, platform APIs, monitoring, scheduling, source
   acquisition, demand proof, ranking, coverage verification, and
   compliance/audit product behavior?

Return:
Start with `# Stage 131 Code Review`, then include:
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
opencode run --model zhipuai-coding-plan/glm-5.2 --variant max --dir /home/ubuntu/fashion-radar "$(cat docs/reviews/opencode-stage-131-code-review-prompt.md)" > "$tmp_review"
sed -n '1,240p' "$tmp_review"
python3 - "$tmp_review" docs/reviews/opencode-stage-131-code-review.md <<'PY'
from pathlib import Path
import re
import sys

raw = Path(sys.argv[1]).read_text(encoding="utf-8")
text = re.sub(r"\x1b\[[0-9;?]*[ -/]*[@-~]", "", raw)
start = text.find("# Stage 131 Code Review")
if start != -1:
    text = text[start:]
cut_markers = ("\n> build ", "\n$ ", "\n-> ", "\n<- ")
cut_positions = [text.find(marker) for marker in cut_markers if text.find(marker) != -1]
if cut_positions:
    text = text[: min(cut_positions)]
lines = [line.rstrip() for line in text.splitlines()]
Path(sys.argv[2]).write_text("\n".join(lines).strip() + "\n", encoding="utf-8")
PY
test -s docs/reviews/opencode-stage-131-code-review.md
rm -f "$tmp_review"
```

Expected result: review artifact is non-empty and contains no Critical or
Important blockers.

## Task 4: Full release gate, commit, push, and CI

**Files:**

- No new implementation files beyond Task 3.

- [ ] **Step 1: Run full release gate**

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

- [ ] **Step 2: Commit Stage 131**

Run:

```bash
git status --short --untracked-files=all
git add tests/test_cli_docs.py CONTRIBUTING.md .github/pull_request_template.md docs/superpowers/specs/2026-06-21-stage-131-verification-surface-parity-design.md docs/superpowers/plans/2026-06-21-stage-131-verification-surface-parity-plan.md docs/reviews/opencode-stage-131-plan-review-prompt.md docs/reviews/opencode-stage-131-plan-review.md docs/reviews/opencode-stage-131-code-review-prompt.md docs/reviews/opencode-stage-131-code-review.md
git commit -m "Align contributor verification surfaces"
```

Expected result: one commit containing only Stage 131 docs/test/review
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
```

Then poll the latest GitHub Actions run for the pushed SHA until it reaches a
terminal state.

Expected result: remote `main` points at the Stage 131 commit and CI completes
successfully.
