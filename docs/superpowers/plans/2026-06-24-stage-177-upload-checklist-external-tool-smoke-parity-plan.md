# Stage 177 Upload Checklist External-Tool Smoke Parity Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Keep `docs/github-upload-checklist.md` aligned with README and `docs/first-run.md` by naming every local external-tool JSON contract surface that the automated first-run smoke already validates.

**Architecture:** Docs/test-only. Reuse the existing `FIRST_RUN_EXTERNAL_TOOL_SMOKE_PHRASES` tuple in `tests/test_cli_docs.py` to guard the upload checklist smoke section, then add one concise checklist paragraph mirroring the README/first-run external-tool smoke wording. Runtime smoke scripts, CLI behavior, payloads, and adapter behavior remain unchanged.

**Tech Stack:** Markdown, pytest, existing `tests/test_cli_docs.py` helpers/constants, `uv --no-config run --frozen`, local opencode review with `zhipuai-coding-plan/glm-5.2 --variant max`.

---

## Files

- Modify: `tests/test_cli_docs.py`
  - Extend `test_upload_checklist_documents_first_run_smoke_boundary` to assert
    every phrase in `FIRST_RUN_EXTERNAL_TOOL_SMOKE_PHRASES`.
- Modify: `docs/github-upload-checklist.md`
  - Add the external-tool JSON contract smoke paragraph in the package smoke
    section.
- Add: `docs/superpowers/specs/2026-06-24-stage-177-upload-checklist-external-tool-smoke-parity-design.md`
- Add: `docs/superpowers/plans/2026-06-24-stage-177-upload-checklist-external-tool-smoke-parity-plan.md`
- Add: `docs/reviews/opencode-stage-177-plan-review-prompt.md`
- Add after plan review: `docs/reviews/opencode-stage-177-plan-review.md`
- Add after implementation: `docs/reviews/opencode-stage-177-code-review-prompt.md`
- Add after implementation: `docs/reviews/opencode-stage-177-code-review.md`
- Add after release verification: `docs/reviews/opencode-stage-177-release-review-prompt.md`
- Add after release verification: `docs/reviews/opencode-stage-177-release-review.md`

## Task 1: Add RED Upload Checklist Smoke Docs Test

**Files:**

- Modify: `tests/test_cli_docs.py`

- [ ] **Step 1: Extend the existing checklist smoke test**

In `test_upload_checklist_documents_first_run_smoke_boundary`, immediately after
the existing final assertion:

```python
    assert (
        "The smoke also validates sample rows, matched starter entities, report content, "
        "trend deltas, empty untracked candidates, and directory handoff dry-run counts."
    ) in normalized
```

add:

```python
    for term in FIRST_RUN_EXTERNAL_TOOL_SMOKE_PHRASES:
        assert term in normalized
```

- [ ] **Step 2: Run RED focused test**

Run:

```bash
uv --no-config run --frozen pytest tests/test_cli_docs.py::test_upload_checklist_documents_first_run_smoke_boundary -q
```

Expected before docs update: the test fails because
`docs/github-upload-checklist.md` does not yet include the local external-tool
JSON contract smoke paragraph.

## Task 2: Update Upload Checklist Smoke Claim

**Files:**

- Modify: `docs/github-upload-checklist.md`

- [ ] **Step 1: Add the external-tool smoke paragraph**

After:

```markdown
The smoke also validates sample rows, matched starter entities, report content,
trend deltas, empty untracked candidates, and directory handoff dry-run counts.
```

add:

```markdown
The automated first-run smoke also validates local external-tool JSON
contracts: `external-tool-adapters --format json` across all eight adapters,
plus the `external-tool-template --adapter rednote_mcp --format json`,
`external-tool-workflow --adapter rednote_mcp --format json`, and
`external-tool-readiness --adapter rednote_mcp --format json` outputs generated
with the `rednote_mcp` adapter. These are command-output contract checks only;
they do not run adapters or upstream external/community tools, do not call
platform APIs, and do not perform source acquisition.
```

- [ ] **Step 2: Run GREEN focused checks**

Run:

```bash
uv --no-config run --frozen pytest tests/test_cli_docs.py::test_upload_checklist_documents_first_run_smoke_boundary -q
uv --no-config run --frozen pytest tests/test_cli_docs.py -q -k "upload_checklist or first_run_smoke"
uv --no-config run --frozen ruff check tests/test_cli_docs.py
uv --no-config run --frozen ruff format --check tests/test_cli_docs.py
```

Expected: all focused tests and checks pass.

## Task 3: Review, Release Gate, Commit, And Push

**Files:**

- Add: `docs/reviews/opencode-stage-177-code-review-prompt.md`
- Add: `docs/reviews/opencode-stage-177-code-review.md`
- Add: `docs/reviews/opencode-stage-177-release-review-prompt.md`
- Add: `docs/reviews/opencode-stage-177-release-review.md`

- [ ] **Step 1: Create code review prompt**

Create `docs/reviews/opencode-stage-177-code-review-prompt.md` with a prompt
that asks local opencode to review the Stage 177 implementation. The prompt
must require the response to start with:

```text
# Stage 177 Code Review
```

- [ ] **Step 2: Run code review**

Run:

```bash
tmp_review="$(mktemp)"
opencode run --model zhipuai-coding-plan/glm-5.2 --variant max \
  --dir /home/ubuntu/fashion-radar \
  "$(cat docs/reviews/opencode-stage-177-code-review-prompt.md)" > "$tmp_review" 2>&1
sed -n '1,320p' "$tmp_review"
cp "$tmp_review" docs/reviews/opencode-stage-177-code-review.md
rm -f "$tmp_review"
```

Expected: completed review output with no critical or important findings. Clean
the artifact if opencode includes process chatter, ANSI output, command logs, or
multiple drafts.

- [ ] **Step 3: Run release gate**

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

Expected: all commands pass; token and extraheader checks report no secrets.

- [ ] **Step 4: Create and run release review**

Create `docs/reviews/opencode-stage-177-release-review-prompt.md` requiring the
review body to start with:

```text
# Stage 177 Release Review
```

Then run the same temp-file `opencode run --model zhipuai-coding-plan/glm-5.2
--variant max` capture flow used for code review, copying the completed review
to `docs/reviews/opencode-stage-177-release-review.md`.

Expected: completed review output with no critical or important findings. Clean
the artifact if needed.

- [ ] **Step 5: Commit and push**

Run:

```bash
git status --short
git add \
  docs/github-upload-checklist.md \
  tests/test_cli_docs.py \
  docs/superpowers/specs/2026-06-24-stage-177-upload-checklist-external-tool-smoke-parity-design.md \
  docs/superpowers/plans/2026-06-24-stage-177-upload-checklist-external-tool-smoke-parity-plan.md \
  docs/reviews/opencode-stage-177-plan-review-prompt.md \
  docs/reviews/opencode-stage-177-plan-review.md \
  docs/reviews/opencode-stage-177-code-review-prompt.md \
  docs/reviews/opencode-stage-177-code-review.md \
  docs/reviews/opencode-stage-177-release-review-prompt.md \
  docs/reviews/opencode-stage-177-release-review.md
git commit -m "docs: align upload checklist smoke contracts"
git push origin main
```

Expected: commit succeeds and `main` pushes to GitHub.

## Self-Review Notes

- Spec coverage: Task 1 adds the RED checklist docs guard, Task 2 updates the
  upload checklist smoke claim, and Task 3 covers review, release gate, commit,
  and push.
- Placeholder scan: no placeholders or deferred implementation notes.
- Boundary check: runtime smoke logic, CLI behavior, external-tool payloads,
  adapters, templates, workflows, readiness builders, source acquisition,
  connectors, scraping, browser automation, platform APIs, MCP execution, login
  or cookie behavior, monitoring, scheduling, demand proof, ranking, coverage
  verification, compliance-review product features, install hints, mirror
  hints, dependencies, and lockfiles remain out of scope.
