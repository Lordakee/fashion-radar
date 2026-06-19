# Stage 119 Review Protocol Opencode Alignment Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make local opencode with `zhipuai-coding-plan/glm-5.2 --variant max` the documented active review route while preserving Claude Code `--effort max` as an explicit alternate route.

**Architecture:** This is a docs/tests-only process alignment node. First replace the stale review-protocol docs drift tests with active-opencode assertions, verify they fail against the current docs, then update the three workflow docs to satisfy the new assertions.

**Tech Stack:** Python 3.11, pytest, markdown docs, uv, ruff, local opencode review with `zhipuai-coding-plan/glm-5.2 --variant max`.

---

## Files

- Modify: `AGENTS.md`
- Modify: `docs/REVIEW_PROTOCOL.md`
- Modify: `docs/github-upload-checklist.md`
- Modify: `tests/test_review_protocol_docs.py`
- Create: `docs/reviews/opencode-stage-119-plan-review-prompt.md`
- Create later: `docs/reviews/opencode-stage-119-plan-review.md`
- Create if plan review requires changes: `docs/reviews/opencode-stage-119-plan-rereview-prompt.md`
- Create if plan review requires changes: `docs/reviews/opencode-stage-119-plan-rereview.md`
- Create later: `docs/reviews/opencode-stage-119-code-review-prompt.md`
- Create later: `docs/reviews/opencode-stage-119-code-review.md`

Do not modify `src/`, `pyproject.toml`, `uv.lock`, CI workflows, package
metadata, schemas, collectors, source packs, entity packs, dashboard, scoring,
reports, importers, or runtime behavior.

## Task 0: Plan Review

- [ ] **Step 1: Create the plan review prompt**

Create `docs/reviews/opencode-stage-119-plan-review-prompt.md` asking local
opencode to review the Stage 119 design and plan.

- [ ] **Step 2: Run local opencode plan review**

Run:

```bash
opencode run --model zhipuai-coding-plan/glm-5.2 --variant max --dir /home/ubuntu/fashion-radar "$(cat docs/reviews/opencode-stage-119-plan-review-prompt.md)" > docs/reviews/opencode-stage-119-plan-review.md
```

Expected: review completes and lists no Critical or Important blockers, or
lists blockers to fix before Task 1.

- [ ] **Step 3: Resolve plan blockers before coding**

If the review identifies Critical or Important findings, update this plan or
the design before writing tests.

- [ ] **Step 4: Run focused plan rereview if Critical/Important findings were fixed**

If Step 3 changes this plan or design after a Critical or Important finding,
create `docs/reviews/opencode-stage-119-plan-rereview-prompt.md` and run:

```bash
opencode run --model zhipuai-coding-plan/glm-5.2 --variant max --dir /home/ubuntu/fashion-radar "$(cat docs/reviews/opencode-stage-119-plan-rereview-prompt.md)" > docs/reviews/opencode-stage-119-plan-rereview.md
```

Expected: rereview explicitly lists no remaining Critical or Important
blockers before implementation.

## Task 1: Write Failing Review Protocol Test

- [ ] **Step 1: Replace stale active-Claude assertions**

In `tests/test_review_protocol_docs.py`, replace
`FORBIDDEN_ACTIVE_REVIEW_TERMS`, `test_active_review_docs_use_claude_code_not_opencode`,
and `test_active_review_protocol_documents_claude_code_gate` with:

```python
ACTIVE_OPENCODE_COMMAND = (
    "opencode run --model zhipuai-coding-plan/glm-5.2 --variant max"
)
OPTIONAL_CLAUDE_CODE_COMMAND = (
    "claude --effort max --permission-mode plan --no-session-persistence"
)


def _normalized_text(text: str) -> str:
    return " ".join(text.split())


def test_active_review_docs_document_local_opencode_gate() -> None:
    failures: list[str] = []

    for path in ACTIVE_REVIEW_DOCS:
        normalized = _normalized_text(_read(path))
        normalized_lower = normalized.casefold()
        for term in (
            "local opencode",
            ACTIVE_OPENCODE_COMMAND,
            "zhipuai-coding-plan/glm-5.2",
            "--variant max",
            "docs/reviews/opencode-stage-N",
        ):
            if term.casefold() not in normalized_lower:
                failures.append(f"{path.relative_to(ROOT)} is missing {term!r}")

    assert not failures, "\n".join(failures)


def test_active_review_protocol_documents_opencode_gate_and_claude_alternate() -> None:
    agents_text = _read(AGENTS)
    protocol_text = _read(REVIEW_PROTOCOL)
    naming_section = _section(protocol_text, "Review Record Naming")
    checklist_text = _read(UPLOAD_CHECKLIST)
    normalized_protocol = _normalized_text(protocol_text)
    normalized_checklist = _normalized_text(checklist_text)

    assert ACTIVE_OPENCODE_COMMAND in _normalized_text(agents_text)
    assert "reasoning effort to `xhigh`" in _normalized_text(agents_text)
    assert ACTIVE_OPENCODE_COMMAND in normalized_protocol
    assert ACTIVE_OPENCODE_COMMAND in normalized_checklist
    assert OPTIONAL_CLAUDE_CODE_COMMAND in normalized_protocol
    assert "optional alternate" in normalized_protocol.casefold()
    assert "historical audit records" not in protocol_text
    assert "older `opencode-*` records" not in protocol_text

    review_record_names = (
        "opencode-stage-N-plan-review.md",
        "opencode-stage-N-code-review.md",
        "opencode-stage-N-release-review.md",
    )
    for record_name in review_record_names:
        assert record_name in naming_section

    assert (
        naming_section.index(review_record_names[0])
        < naming_section.index(review_record_names[1])
        < naming_section.index(review_record_names[2])
    )

    rereview_record_names = (
        "opencode-stage-N-plan-rereview.md",
        "opencode-stage-N-code-rereview.md",
        "opencode-stage-N-release-rereview.md",
    )
    for record_name in rereview_record_names:
        assert record_name in naming_section

    assert (
        naming_section.index(rereview_record_names[0])
        < naming_section.index(rereview_record_names[1])
        < naming_section.index(rereview_record_names[2])
    )

    optional_claude_names = (
        "claude-code-stage-N-plan-review.md",
        "claude-code-stage-N-code-review.md",
        "claude-code-stage-N-release-review.md",
        "claude-code-stage-N-plan-rereview.md",
        "claude-code-stage-N-code-rereview.md",
        "claude-code-stage-N-release-rereview.md",
    )
    for record_name in optional_claude_names:
        assert record_name in protocol_text
```

- [ ] **Step 2: Run focused RED test**

Run:

```bash
env -u ALL_PROXY -u all_proxy uv --no-config run --frozen pytest tests/test_review_protocol_docs.py -q
```

Expected: the tests fail because the current active docs still document Claude
Code as the active route, forbid opencode wording, and list `opencode-*`
records as historical-only.

## Task 2: Update Active Review Docs

- [ ] **Step 1: Update `AGENTS.md` review gates**

In `## Review Gates`, make the active route local opencode:

```markdown
- Follow the staged review workflow in `docs/REVIEW_PROTOCOL.md`.
- Before starting a new stage, submit the objective, architecture, tech stack,
  implementation method, and plan to local opencode with
  `zhipuai-coding-plan/glm-5.2 --variant max` for review.
- After completing a development node, run fresh verification and request
  local opencode review of the new code before moving to the next stage.
- Record active plan, code, release, and rereview artifacts under
  `docs/reviews/opencode-stage-N-...`.
- Fix critical and important review findings before continuing.
```

In `## Agent Runtime Settings`, keep the Codex subagent `xhigh` bullet and
replace the active Claude Code command block with:

````markdown
- When invoking local opencode for plan or code review, use GLM 5.2 with the max
  variant:

  ```bash
  opencode run --model zhipuai-coding-plan/glm-5.2 --variant max \
    --dir /home/ubuntu/fashion-radar "review prompt..."
  ```

- If a stage explicitly switches review back to local Claude Code, use
  `--effort max`, read-only plan mode, and no session persistence:

  ```bash
  claude --effort max --permission-mode plan --no-session-persistence \
    --tools Read,Grep,Glob,LS,Bash \
    -p "review prompt..."
  ```
````

- [ ] **Step 2: Update `docs/REVIEW_PROTOCOL.md`**

Rewrite the active review route so the plan and release command examples use:

```bash
opencode run --model zhipuai-coding-plan/glm-5.2 --variant max \
  --dir /home/ubuntu/fashion-radar "review prompt..."
```

Use exact active wording equivalent to:

- `Before Coding`: "Ask local opencode with
  `zhipuai-coding-plan/glm-5.2 --variant max` to review the plan."
- `During Development`: "Local opencode review of newly added code
  (`docs/reviews/opencode-stage-N-code-review.md`)."
- `Before GitHub Upload`: "Ask local opencode with
  `zhipuai-coding-plan/glm-5.2 --variant max` for final code and documentation
  review."

The `Review Record Naming` section must list:

```text
docs/reviews/opencode-stage-N-plan-review.md
docs/reviews/opencode-stage-N-code-review.md
docs/reviews/opencode-stage-N-release-review.md
```

and:

```text
docs/reviews/opencode-stage-N-plan-rereview.md
docs/reviews/opencode-stage-N-code-rereview.md
docs/reviews/opencode-stage-N-release-rereview.md
```

Replace the historical-only opencode sentence with an optional alternate Claude
Code section that includes:

```bash
claude --effort max --permission-mode plan --no-session-persistence \
  --tools Read,Grep,Glob,LS,Bash \
  -p "review prompt..."
```

and the optional `docs/reviews/claude-code-stage-N-...` naming convention:

```text
docs/reviews/claude-code-stage-N-plan-review.md
docs/reviews/claude-code-stage-N-code-review.md
docs/reviews/claude-code-stage-N-release-review.md
docs/reviews/claude-code-stage-N-plan-rereview.md
docs/reviews/claude-code-stage-N-code-rereview.md
docs/reviews/claude-code-stage-N-release-rereview.md
```

- [ ] **Step 3: Update `docs/github-upload-checklist.md` final review**

In `## Final Review`, make the active route local opencode:

```markdown
3. Run a final local opencode code and documentation review with
   `zhipuai-coding-plan/glm-5.2 --variant max`.
```

Use this command form:

```bash
opencode run --model zhipuai-coding-plan/glm-5.2 --variant max \
  --dir /home/ubuntu/fashion-radar "review prompt..."
```

Add two sentences:

```markdown
Follow `docs/REVIEW_PROTOCOL.md` for review record naming and record the final
review as `docs/reviews/opencode-stage-N-release-review.md`.
Claude Code `--effort max` remains an optional alternate route only when a
stage explicitly requests it.
```

- [ ] **Step 4: Run focused GREEN test**

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

- [ ] **Step 2: Create code review prompt**

Create `docs/reviews/opencode-stage-119-code-review-prompt.md` summarizing the
Stage 119 docs/test changes and verification commands.

- [ ] **Step 3: Run local opencode code review**

Run:

```bash
opencode run --model zhipuai-coding-plan/glm-5.2 --variant max --dir /home/ubuntu/fashion-radar "$(cat docs/reviews/opencode-stage-119-code-review-prompt.md)" > docs/reviews/opencode-stage-119-code-review.md
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
git add AGENTS.md docs/REVIEW_PROTOCOL.md docs/github-upload-checklist.md tests/test_review_protocol_docs.py \
  docs/reviews/opencode-stage-119-plan-review-prompt.md docs/reviews/opencode-stage-119-plan-review.md \
  docs/reviews/opencode-stage-119-code-review-prompt.md docs/reviews/opencode-stage-119-code-review.md \
  docs/superpowers/specs/2026-06-20-stage-119-review-protocol-opencode-alignment-design.md \
  docs/superpowers/plans/2026-06-20-stage-119-review-protocol-opencode-alignment-plan.md
git commit -m "Align review protocol with local opencode"
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

## Handoff Summary Requirement

At the end of this stage, write a concise Handoff Summary containing:

- repo status;
- verified commands;
- uncommitted files;
- next step.
