# Stage 120 Opencode Review Capture Hygiene Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Document and test a safer local opencode review capture workflow so committed review artifacts contain completed review output, not live-capture stubs, status-line telemetry, duplicated verdicts, or empty output.

**Architecture:** This is a docs/tests-only process hygiene node. Add a focused docs drift test in `tests/test_review_protocol_docs.py`, verify it fails against the current docs, then update `AGENTS.md`, `docs/REVIEW_PROTOCOL.md`, and `docs/github-upload-checklist.md` to satisfy the new capture hygiene contract.

**Tech Stack:** Python 3.11, pytest, markdown docs, uv, ruff, local opencode review with `zhipuai-coding-plan/glm-5.2 --variant max`.

---

## Files

- Modify: `AGENTS.md`
- Modify: `docs/REVIEW_PROTOCOL.md`
- Modify: `docs/github-upload-checklist.md`
- Modify: `tests/test_review_protocol_docs.py`
- Create: `docs/reviews/opencode-stage-120-plan-review-prompt.md`
- Create later: `docs/reviews/opencode-stage-120-plan-review.md`
- Create if plan review requires changes: `docs/reviews/opencode-stage-120-plan-rereview-prompt.md`
- Create if plan review requires changes: `docs/reviews/opencode-stage-120-plan-rereview.md`
- Create later: `docs/reviews/opencode-stage-120-code-review-prompt.md`
- Create later: `docs/reviews/opencode-stage-120-code-review.md`

Do not modify `src/`, `pyproject.toml`, `uv.lock`, CI workflows, package
metadata, schemas, collectors, source packs, entity packs, dashboard, scoring,
reports, importers, runtime behavior, or historical review artifacts outside
Stage 120.

## Task 0: Plan Review

- [ ] **Step 1: Create the plan review prompt**

Create `docs/reviews/opencode-stage-120-plan-review-prompt.md` asking local
opencode to review the Stage 120 design and plan.

- [ ] **Step 2: Run local opencode plan review with temporary capture**

Run opencode to a temporary file, inspect it, then copy the completed review body
into the final artifact:

```bash
tmp_review="$(mktemp)"
opencode run --model zhipuai-coding-plan/glm-5.2 --variant max --dir /home/ubuntu/fashion-radar "$(cat docs/reviews/opencode-stage-120-plan-review-prompt.md)" > "$tmp_review"
sed -n '1,260p' "$tmp_review"
cp "$tmp_review" docs/reviews/opencode-stage-120-plan-review.md
rm -f "$tmp_review"
```

Expected: review completes and lists no Critical or Important blockers, or
lists blockers to fix before Task 1. The final artifact is a coherent review
body, not a live-capture stub.

- [ ] **Step 3: Resolve plan blockers before coding**

If the review identifies Critical or Important findings, update this plan or
the design before writing tests.

- [ ] **Step 4: Run focused plan rereview if Critical/Important findings were fixed**

If Step 3 changes this plan or design after a Critical or Important finding,
create `docs/reviews/opencode-stage-120-plan-rereview-prompt.md` and run the
same temporary-capture workflow, writing the final reviewed output to
`docs/reviews/opencode-stage-120-plan-rereview.md`.

Expected: rereview explicitly lists no remaining Critical or Important blockers
before implementation.

## Task 1: Write Failing Capture Hygiene Test

- [ ] **Step 1: Add capture hygiene constants and test**

In `tests/test_review_protocol_docs.py`, after `OPTIONAL_CLAUDE_CODE_COMMAND`,
add:

```python
REVIEW_CAPTURE_HYGIENE_REQUIRED_PHRASES = (
    "review capture hygiene",
    "capture the completed reviewer output",
    "directly into the target review record",
    "do not commit live-capture stubs",
    "do not commit tool status lines such as `Wrote`",
    "one coherent review body",
    "one verdict",
    "do not duplicate approval phrases",
    "if the review times out, record the timeout honestly",
)
```

After the existing tests, add:

```python
def test_review_protocol_docs_document_capture_hygiene() -> None:
    agents_text = _read(AGENTS)
    protocol_text = _read(REVIEW_PROTOCOL)
    checklist_text = _read(UPLOAD_CHECKLIST)
    agents_section = _section(agents_text, "Review Gates")
    assert "## Review Capture Hygiene" in protocol_text
    protocol_section = _section(protocol_text, "Review Capture Hygiene")
    checklist_section = _section(checklist_text, "Final Review")
    failures: list[str] = []

    for label, text in (
        ("docs/REVIEW_PROTOCOL.md##Review Capture Hygiene", protocol_section),
        ("docs/github-upload-checklist.md##Final Review", checklist_section),
    ):
        normalized = _normalized_text(text).casefold()
        for phrase in REVIEW_CAPTURE_HYGIENE_REQUIRED_PHRASES:
            if phrase.casefold() not in normalized:
                failures.append(f"{label} is missing {phrase!r}")

    assert "opencode-stage-N-plan-review.md" in protocol_section
    assert "opencode-stage-N-code-review.md" in protocol_section
    assert "opencode-stage-N-release-review.md" in protocol_section
    assert "opencode-stage-N-release-review.md" in checklist_section
    assert "> docs/reviews/opencode-stage-N-plan-review.md" not in protocol_text
    assert "> docs/reviews/opencode-stage-N-release-review.md" not in protocol_text
    normalized_agents = _normalized_text(agents_section).casefold()
    for phrase in (
        "completed review output",
        "live-capture stubs",
        "duplicated or truncated text",
        "tool-status messages",
        "empty output",
    ):
        assert phrase.casefold() in normalized_agents
    assert not failures, "\n".join(failures)
```

- [ ] **Step 2: Run focused RED test**

Run:

```bash
env -u ALL_PROXY -u all_proxy uv --no-config run --frozen pytest tests/test_review_protocol_docs.py -q
```

Expected: the new test fails because `docs/REVIEW_PROTOCOL.md` has no
`## Review Capture Hygiene` section and the final-review checklist does not yet
mention live-capture stubs, `Wrote` status lines, coherent review bodies,
duplicate approval phrases, or timeout handling.

## Task 2: Update Review Capture Hygiene Docs

- [ ] **Step 1: Update `AGENTS.md` review gates**

In `## Review Gates`, after the bullet that records active review artifacts
under `docs/reviews/opencode-stage-N-...`, add:

```markdown
- Before committing review artifacts, ensure each local opencode record contains
  completed review output and no live-capture stubs, duplicated or truncated
  text, tool-status messages, or empty output.
```

- [ ] **Step 2: Update `docs/REVIEW_PROTOCOL.md` command examples**

Replace both active opencode command examples so they capture to a temporary
file first and then copy into the final review artifact after inspection.

Plan review command block:

```bash
tmp_review="$(mktemp)"
opencode run --model zhipuai-coding-plan/glm-5.2 --variant max \
  --dir /home/ubuntu/fashion-radar "$(cat docs/reviews/opencode-stage-N-plan-review-prompt.md)" > "$tmp_review"
sed -n '1,260p' "$tmp_review"
cp "$tmp_review" docs/reviews/opencode-stage-N-plan-review.md
rm -f "$tmp_review"
```

Release review command block:

```bash
tmp_review="$(mktemp)"
opencode run --model zhipuai-coding-plan/glm-5.2 --variant max \
  --dir /home/ubuntu/fashion-radar "$(cat docs/reviews/opencode-stage-N-release-review-prompt.md)" > "$tmp_review"
sed -n '1,260p' "$tmp_review"
cp "$tmp_review" docs/reviews/opencode-stage-N-release-review.md
rm -f "$tmp_review"
```

- [ ] **Step 3: Add `docs/REVIEW_PROTOCOL.md` capture hygiene section**

After the historical-record preservation sentence and before
`## Optional Alternate Route`, add:

```markdown
## Review Capture Hygiene

This review capture hygiene rule applies to
`docs/reviews/opencode-stage-N-plan-review.md`,
`docs/reviews/opencode-stage-N-code-review.md`, and
`docs/reviews/opencode-stage-N-release-review.md`. Capture the completed
reviewer output to a temporary file first, inspect it, and then copy only one
coherent review body directly into the target review record.

Do not commit live-capture stubs, duplicated or truncated text, empty output,
multiple top-level review drafts, or more than one verdict. Do not commit tool
status lines such as `Wrote`, and do not duplicate approval phrases. If the
review times out, record the timeout honestly instead of presenting partial
output as approval.
```

- [ ] **Step 4: Update `docs/github-upload-checklist.md` final review**

After the current final-review naming paragraph, add:

```markdown
Before upload, confirm the final local opencode release-review artifact contains
review capture hygiene notes. Capture the completed reviewer output into a
temporary file first, inspect it, and copy one coherent review body directly
into the target review record. Do not commit live-capture stubs, duplicated or
truncated text, empty output, multiple top-level review drafts, more than one
verdict, or partial output as approval. Do not commit tool status lines such as
`Wrote`, and do not duplicate approval phrases. If the review times out, record
the timeout honestly instead of treating partial output as approval.
```

- [ ] **Step 5: Run focused GREEN test**

Run:

```bash
env -u ALL_PROXY -u all_proxy uv --no-config run --frozen pytest tests/test_review_protocol_docs.py -q
```

Expected: all review protocol docs tests pass.

## Task 3: Verification And Review

- [ ] **Step 1: Run adjacent docs tests**

Run:

```bash
env -u ALL_PROXY -u all_proxy uv --no-config run --frozen pytest tests/test_review_protocol_docs.py tests/test_cli_docs.py -q
```

Expected: review protocol docs tests and CLI/docs drift tests pass.

- [ ] **Step 2: Run focused formatting/lint checks**

Run:

```bash
uv --no-config run --frozen ruff check tests/test_review_protocol_docs.py
uv --no-config run --frozen ruff format --check tests/test_review_protocol_docs.py
```

Expected: both commands pass.

- [ ] **Step 3: Create code review prompt**

Create `docs/reviews/opencode-stage-120-code-review-prompt.md` summarizing the
Stage 120 docs/test changes and verification commands.

- [ ] **Step 4: Run local opencode code review with temporary capture**

Run the same temporary-capture workflow, writing the final reviewed output to
`docs/reviews/opencode-stage-120-code-review.md`.

Expected: review completes and explicitly lists no Critical or Important
blockers, or lists findings to fix before release.

- [ ] **Step 5: Fix Critical/Important findings**

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
git add AGENTS.md docs/REVIEW_PROTOCOL.md docs/github-upload-checklist.md tests/test_review_protocol_docs.py \
  docs/reviews/opencode-stage-120-plan-review-prompt.md docs/reviews/opencode-stage-120-plan-review.md \
  docs/reviews/opencode-stage-120-code-review-prompt.md docs/reviews/opencode-stage-120-code-review.md \
  docs/superpowers/specs/2026-06-20-stage-120-opencode-review-capture-hygiene-design.md \
  docs/superpowers/plans/2026-06-20-stage-120-opencode-review-capture-hygiene-plan.md
git commit -m "Document opencode review capture hygiene"
```

Include any Stage 120 rereview prompt/result files if plan review required them.

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

## Handoff Summary Requirement

At the end of this stage, write a concise Handoff Summary containing:

- repo status;
- verified commands;
- uncommitted files;
- next step.
