# Stage 133 PR Template Upload Checklist Routing Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a concise PR template route to the canonical GitHub upload checklist for conditional smoke and upload verification.

**Architecture:** Add one docs parity test around the PR template `Verification` section, then add one concise upload-checklist link to `.github/pull_request_template.md`. Keep this docs/test-only and avoid duplicating the upload checklist.

**Tech Stack:** Python 3.11, pytest docs tests, Markdown GitHub pull request template.

---

## Files

- Modify `tests/test_cli_docs.py`
  - Add one PR template upload checklist routing test near the existing PR
    template tests.
- Modify `.github/pull_request_template.md`
  - Add one concise checklist line linking to `docs/github-upload-checklist.md`
    for the full upload/package smoke gate.
- Create `docs/reviews/opencode-stage-133-plan-review-prompt.md`.
- Create `docs/reviews/opencode-stage-133-plan-review.md`.
- Create `docs/reviews/opencode-stage-133-code-review-prompt.md`.
- Create `docs/reviews/opencode-stage-133-code-review.md`.

No CI changes, upload checklist content changes, package archive checker
changes, runtime product behavior changes, dependency changes, `uv.lock`
changes, README/CONTRIBUTING changes, release hygiene changes, connector,
scraping, browser automation, platform API, monitoring, scheduling, source
acquisition, demand proof, ranking, coverage verification, or compliance/audit
product behavior changes are part of this stage.

## Task 1: Add RED PR template upload-checklist routing test

**Files:**

- Modify: `tests/test_cli_docs.py`

- [ ] **Step 1: Add focused docs test**

Add after
`test_pull_request_template_package_smoke_uses_temp_build_archive_checker`:

```python
def test_pull_request_template_routes_conditional_smokes_to_upload_checklist() -> None:
    template = _read(PULL_REQUEST_TEMPLATE)
    verification = _markdown_section_exact_heading(template, "Verification")

    _assert_markdown_link_to_path(verification, "docs/github-upload-checklist.md")
    normalized = _normalized_text(verification).casefold()
    assert "github upload" in normalized
    assert "package smoke gate" in normalized
```

- [ ] **Step 2: Run RED test**

Run:

```bash
uv --no-config run --frozen pytest tests/test_cli_docs.py::test_pull_request_template_routes_conditional_smokes_to_upload_checklist -q
```

Expected result: fail because the PR template `Verification` section does not
yet link to `docs/github-upload-checklist.md`.

## Task 2: Add concise PR template upload checklist route

**Files:**

- Modify: `.github/pull_request_template.md`

- [ ] **Step 1: Add checklist route**

In the `Verification` section, after the existing conditional
dashboard/dependencies checkbox, add:

```markdown
- [ ] If preparing a GitHub upload or package smoke gate, follow [docs/github-upload-checklist.md](../docs/github-upload-checklist.md).
```

Do not copy the upload checklist command blocks into the PR template.

- [ ] **Step 2: Run GREEN docs tests**

Run:

```bash
uv --no-config run --frozen pytest tests/test_cli_docs.py::test_pull_request_template_routes_conditional_smokes_to_upload_checklist tests/test_cli_docs.py::test_pull_request_template_package_smoke_uses_temp_build_archive_checker tests/test_cli_docs.py::test_contributing_and_pr_template_include_release_hygiene_and_source_smoke -q
```

Expected result: pass.

## Task 3: Focused verification and local code review

**Files:**

- Create: `docs/reviews/opencode-stage-133-code-review-prompt.md`
- Create: `docs/reviews/opencode-stage-133-code-review.md`

- [ ] **Step 1: Run focused verification**

Run:

```bash
uv --no-config run --frozen pytest tests/test_cli_docs.py::test_pull_request_template_routes_conditional_smokes_to_upload_checklist -q
uv --no-config run --frozen pytest tests/test_cli_docs.py -q -k "pull_request_template_routes_conditional_smokes_to_upload_checklist or pull_request_template_package_smoke_uses_temp_build_archive_checker or contributing_and_pr_template_include_release_hygiene_and_source_smoke"
uv --no-config run --frozen ruff check tests/test_cli_docs.py
uv --no-config run --frozen ruff format --check tests/test_cli_docs.py
uv --no-config run --frozen python scripts/check_release_hygiene.py --repo-root .
git diff --check
```

Expected result: focused docs tests, lint, format, live hygiene check, and
whitespace check pass.

- [ ] **Step 2: Write Stage 133 code review prompt**

Create `docs/reviews/opencode-stage-133-code-review-prompt.md` with:

```markdown
Review the Stage 133 implementation before release.

Repository: `/home/ubuntu/fashion-radar`

Stage goal:
- Route PR authors from `.github/pull_request_template.md` to the canonical
  `docs/github-upload-checklist.md` for conditional smoke/upload verification.
- Keep the PR template concise and avoid duplicating the full upload checklist.
- Keep the change docs/test-only.

Files changed:
- `.github/pull_request_template.md`
- `tests/test_cli_docs.py`
- Stage 133 design/plan/review artifacts

Review focus:
1. Does the implementation match the Stage 133 design and plan?
2. Does the PR template `Verification` section link to
   `docs/github-upload-checklist.md` for the GitHub upload or package smoke
   gate?
3. Does the test use `_assert_markdown_link_to_path()` instead of overfitting a
   single link path spelling?
4. Does the PR template avoid duplicating the full upload checklist?
5. Does the stage avoid CI changes, upload checklist content changes, package
   checker behavior changes, runtime product behavior changes, dependencies,
   `uv.lock`, README/CONTRIBUTING changes, release hygiene changes, connectors,
   scraping, browser automation, platform API, monitoring, scheduling, source
   acquisition, demand proof, ranking, coverage verification, and
   compliance/audit product behavior?

Return:
Start with `# Stage 133 Code Review`, then include:
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
opencode run --model zhipuai-coding-plan/glm-5.2 --variant max --dir /home/ubuntu/fashion-radar "$(cat docs/reviews/opencode-stage-133-code-review-prompt.md)" > "$tmp_review"
python3 - "$tmp_review" docs/reviews/opencode-stage-133-code-review.md <<'PY'
from pathlib import Path
import re
import sys

raw = Path(sys.argv[1]).read_text(encoding="utf-8")
text = re.sub(r"\x1b\[[0-9;?]*[ -/]*[@-~]", "", raw)
start = text.find("# Stage 133 Code Review")
if start != -1:
    text = text[start:]
cut_markers = ("\n> build ", "\n$ ", "\n-> ", "\n<- ")
cut_positions = [text.find(marker) for marker in cut_markers if text.find(marker) != -1]
if cut_positions:
    text = text[: min(cut_positions)]
lines = [line.rstrip() for line in text.splitlines()]
Path(sys.argv[2]).write_text("\n".join(lines).strip() + "\n", encoding="utf-8")
PY
test -s docs/reviews/opencode-stage-133-code-review.md
rm -f "$tmp_review"
```

Expected result: review artifact is non-empty and contains no Critical or
Important blockers.

## Task 4: Release gate, commit, push, and CI

**Files:**

- Stage all Stage 133 files only.

- [ ] **Step 1: Run release gate**

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

Expected result: all commands pass.

- [ ] **Step 2: Commit Stage 133**

Run:

```bash
git status --short --untracked-files=all
git add .github/pull_request_template.md tests/test_cli_docs.py docs/superpowers/specs/2026-06-21-stage-133-pr-template-upload-checklist-routing-design.md docs/superpowers/plans/2026-06-21-stage-133-pr-template-upload-checklist-routing-plan.md docs/reviews/opencode-stage-133-plan-review-prompt.md docs/reviews/opencode-stage-133-plan-review.md docs/reviews/opencode-stage-133-code-review-prompt.md docs/reviews/opencode-stage-133-code-review.md
git commit -m "Route PR template to upload checklist"
```

Expected result: one commit containing only Stage 133 docs/test/template and
review artifacts.

- [ ] **Step 3: Push with ephemeral credentials**

Use the established one-shot push pattern from the operator shell, deriving the
credential header only in process memory and passing it through `git -c` for
that single command. Do not write the token, derived header, or push command
containing credentials into files, git config, shell profile, or review
artifacts. Clear the temporary shell variable immediately after the push, then
verify no persistent GitHub credential header remains:

```bash
git config --get-all http.https://github.com/.extraheader || true
```

Expected result: push succeeds and no persistent GitHub credential header
remains.

- [ ] **Step 4: Verify remote and CI**

Run:

```bash
git ls-remote origin refs/heads/main
```

Expected result: remote `main` points to the new commit. Poll GitHub Actions for
that SHA until CI completes.
