# Stage 118 Agent UV Run Hygiene Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Document and test the project rule that mirror-backed installs are allowed, but agent-run verification should use no-config frozen `uv run` so mirror config cannot rewrite `uv.lock`.

**Architecture:** This is a docs/tests-only hygiene node. Add one docs drift test in `tests/test_cli_docs.py`, then add short guidance in the existing dependency/mirror sections of `AGENTS.md`, `README.md`, `docs/dependency-mirrors.md`, and `docs/github-upload-checklist.md`.

**Tech Stack:** Python 3.11, pytest, markdown docs, uv, ruff, local opencode review with `zhipuai-coding-plan/glm-5.2 --variant max`.

---

## Files

- Modify: `AGENTS.md`
- Modify: `README.md`
- Modify: `docs/dependency-mirrors.md`
- Modify: `docs/github-upload-checklist.md`
- Modify: `tests/test_cli_docs.py`
- Create: `docs/reviews/opencode-stage-118-plan-review-prompt.md`
- Create later: `docs/reviews/opencode-stage-118-plan-review.md`
- Create if plan review requires changes: `docs/reviews/opencode-stage-118-plan-rereview-prompt.md`
- Create if plan review requires changes: `docs/reviews/opencode-stage-118-plan-rereview.md`
- Create later: `docs/reviews/opencode-stage-118-code-review-prompt.md`
- Create later: `docs/reviews/opencode-stage-118-code-review.md`

Do not modify `src/`, `pyproject.toml`, `uv.lock`, CI workflows, package
metadata, schemas, collectors, source packs, entity packs, dashboard, scoring,
reports, importers, or runtime behavior.

## Task 0: Plan Review

- [ ] **Step 1: Create the plan review prompt**

Create `docs/reviews/opencode-stage-118-plan-review-prompt.md` asking local
opencode to review the Stage 118 design and plan.

- [ ] **Step 2: Run local opencode plan review**

Run:

```bash
opencode run --model zhipuai-coding-plan/glm-5.2 --variant max --dir /home/ubuntu/fashion-radar "$(cat docs/reviews/opencode-stage-118-plan-review-prompt.md)" > docs/reviews/opencode-stage-118-plan-review.md
```

Expected: review completes and lists no Critical or Important blockers, or
lists blockers to fix before Task 1.

- [ ] **Step 3: Resolve plan blockers before coding**

If the review identifies Critical or Important findings, update this plan or
the design before writing tests.

- [ ] **Step 4: Run focused plan rereview if Critical/Important findings were fixed**

If Step 3 changes this plan or design after a Critical or Important finding,
create `docs/reviews/opencode-stage-118-plan-rereview-prompt.md` and run:

```bash
opencode run --model zhipuai-coding-plan/glm-5.2 --variant max --dir /home/ubuntu/fashion-radar "$(cat docs/reviews/opencode-stage-118-plan-rereview-prompt.md)" > docs/reviews/opencode-stage-118-plan-rereview.md
```

Expected: rereview explicitly lists no remaining Critical or Important
blockers before implementation.

## Task 1: Write Failing Test

- [ ] **Step 1: Add docs drift test**

In `tests/test_cli_docs.py`, after
`test_dependency_mirror_docs_explain_lockfile_recovery`, add:

```python
def test_agent_verification_docs_prefer_no_config_frozen_uv_run() -> None:
    agents = _read(AGENTS_DOC)
    readme = _read(README)
    mirror_doc = _read(DEPENDENCY_MIRRORS_DOC)
    checklist = _read(UPLOAD_CHECKLIST)

    agents_section = _markdown_section_exact_heading(agents, "Dependencies And Mirrors")
    readme_section = _markdown_section_exact_heading(readme, "Development")
    mirror_section = _markdown_section_exact_heading(mirror_doc, "Project Practice")
    checklist_section = _markdown_section_exact_heading(checklist, "Before Upload")

    for section in (agents_section, readme_section, mirror_section, checklist_section):
        normalized = _normalized_text(section).casefold()
        assert "uv --no-config run --frozen" in normalized
        assert "agent-run verification" in normalized
        assert "mirror-backed" in normalized
        assert "uv.lock" in normalized
        assert "frozen mirror install" in normalized
```

- [ ] **Step 2: Run focused RED test**

Run:

```bash
env -u ALL_PROXY -u all_proxy uv --no-config run --frozen pytest \
  tests/test_cli_docs.py::test_agent_verification_docs_prefer_no_config_frozen_uv_run \
  -q
```

Expected: test fails because the four docs do not all contain the exact
agent-run verification guidance yet.

## Task 2: Add Docs Guidance

- [ ] **Step 1: Update `AGENTS.md`**

In `## Dependencies And Mirrors`, after the local mirror install bullet, add:

```markdown
- For agent-run verification commands, prefer `uv --no-config run --frozen ...`
  so user-level mirror config cannot rewrite `uv.lock` during tests, lint, or
  scripted checks. Keep mirror-backed commands as frozen mirror install
  commands, not test or lockfile regeneration commands.
```

Keep the existing `UV_DEFAULT_INDEX=... uv sync --frozen --dev` local mirror
install bullet in the same section.

- [ ] **Step 2: Update `README.md`**

In `## Development`, after the existing public lockfile sentence, add:

```markdown
For agent-run verification, prefer `uv --no-config run --frozen ...` so
user-level mirror config cannot rewrite `uv.lock`; keep mirror-backed commands
as frozen mirror install commands, not test or lockfile regeneration commands.
```

- [ ] **Step 3: Update `docs/dependency-mirrors.md`**

In `## Project Practice`, add:

```markdown
- For agent-run verification, prefer `uv --no-config run --frozen ...` so
  tests, lint, release hygiene, and scripts ignore user-level mirror config and
  cannot rewrite `uv.lock`. Keep mirror-backed commands as frozen mirror
  install commands, not test or lockfile regeneration commands.
```

Keep the existing local mirror install bullets and lockfile recovery section.

- [ ] **Step 4: Update `docs/github-upload-checklist.md`**

In `## Before Upload`, after the mirror install check block and before the
`uv.lock` warning paragraph, add:

```markdown
For agent-run verification, prefer `uv --no-config run --frozen ...` so
user-level mirror config cannot rewrite `uv.lock`. Keep mirror-backed local
operations as frozen mirror install commands, not public test, lockfile, or
release-regeneration commands.
```

- [ ] **Step 5: Run focused GREEN test**

Run:

```bash
env -u ALL_PROXY -u all_proxy uv --no-config run --frozen pytest \
  tests/test_cli_docs.py::test_agent_verification_docs_prefer_no_config_frozen_uv_run \
  -q
```

Expected: the new test passes.

## Task 3: Verification And Review

- [ ] **Step 1: Run adjacent docs tests**

Run:

```bash
env -u ALL_PROXY -u all_proxy uv --no-config run --frozen pytest tests/test_cli_docs.py -q
```

Expected: all CLI/docs tests pass.

- [ ] **Step 2: Create code review prompt**

Create `docs/reviews/opencode-stage-118-code-review-prompt.md` summarizing the
Stage 118 docs/test changes and verification commands.

- [ ] **Step 3: Run local opencode code review**

Run:

```bash
opencode run --model zhipuai-coding-plan/glm-5.2 --variant max --dir /home/ubuntu/fashion-radar "$(cat docs/reviews/opencode-stage-118-code-review-prompt.md)" > docs/reviews/opencode-stage-118-code-review.md
```

Expected: review completes and explicitly lists no Critical or Important
blockers, or lists findings to fix before release.

- [ ] **Step 4: Fix Critical/Important findings**

If review identifies Critical or Important findings, fix them and rerun focused
and adjacent tests.

## Task 4: Release Gate, Commit, Push

- [ ] **Step 1: Run full release gate**

Run:

```bash
uv --no-config run --frozen python scripts/check_release_hygiene.py
env -u ALL_PROXY -u all_proxy uv --no-config run --frozen pytest
uv --no-config run --frozen ruff check .
uv --no-config run --frozen ruff format --check .
env -u UV_DEFAULT_INDEX -u UV_INDEX_URL -u UV_EXTRA_INDEX_URL UV_NO_CONFIG=1 uv lock --check
if rg -n 'tuna|aliyun|ustc|huaweicloud|mirror|index-url|extra-index-url|find-links' uv.lock; then exit 1; fi
git diff --exit-code -- uv.lock pyproject.toml
git diff --check
```

Expected: all commands exit zero.

- [ ] **Step 2: Commit**

Stage only files listed in this plan, then commit:

```bash
git add AGENTS.md README.md docs/dependency-mirrors.md docs/github-upload-checklist.md tests/test_cli_docs.py \
  docs/reviews/opencode-stage-118-plan-review-prompt.md docs/reviews/opencode-stage-118-plan-review.md \
  docs/reviews/opencode-stage-118-code-review-prompt.md docs/reviews/opencode-stage-118-code-review.md \
  docs/superpowers/specs/2026-06-20-stage-118-agent-uv-run-hygiene-design.md \
  docs/superpowers/plans/2026-06-20-stage-118-agent-uv-run-hygiene-plan.md
git commit -m "Document agent uv run hygiene"
```

- [ ] **Step 3: Push with temporary GitHub header**

Use the token only through temporary `extraheader`, then verify no header
remains:

```bash
AUTH_HEADER=$(printf 'x-access-token:%s' '<TOKEN>' | base64 -w0)
git -c http.https://github.com/.extraheader="AUTHORIZATION: basic ${AUTH_HEADER}" push origin main
unset AUTH_HEADER
git config --get-all http.https://github.com/.extraheader || true
```

- [ ] **Step 4: Verify remote CI**

Confirm remote `main` points at the commit and GitHub Actions completes
successfully.
