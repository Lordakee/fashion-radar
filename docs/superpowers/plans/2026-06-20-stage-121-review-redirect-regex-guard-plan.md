# Stage 121 Review Redirect Regex Guard Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace narrow direct-review-file redirection substring checks with a regex guard that catches common `opencode run ... > docs/reviews/opencode-stage-N-...` variants while preserving the safe temp-file capture workflow.

**Architecture:** This is a tests-only hardening node. Add a failing unit-style docs test for the regex helper, then introduce the helper and replace the existing two literal absence assertions with a scan across `ACTIVE_REVIEW_DOCS`.

**Tech Stack:** Python 3.11, pytest, regex via Python `re`, uv, ruff, local opencode review with `zhipuai-coding-plan/glm-5.2 --variant max`.

---

## Files

- Modify: `tests/test_review_protocol_docs.py`
- Create: `docs/reviews/opencode-stage-121-plan-review-prompt.md`
- Create later: `docs/reviews/opencode-stage-121-plan-review.md`
- Create if plan review requires changes: `docs/reviews/opencode-stage-121-plan-rereview-prompt.md`
- Create if plan review requires changes: `docs/reviews/opencode-stage-121-plan-rereview.md`
- Create later: `docs/reviews/opencode-stage-121-code-review-prompt.md`
- Create later: `docs/reviews/opencode-stage-121-code-review.md`

Do not modify `AGENTS.md`, `docs/REVIEW_PROTOCOL.md`,
`docs/github-upload-checklist.md`, `src/`, `pyproject.toml`, `uv.lock`, CI
workflows, package metadata, schemas, collectors, source packs, entity packs,
dashboard, scoring, reports, importers, runtime behavior, or historical review
artifacts outside Stage 121.

## Task 0: Plan Review

- [ ] **Step 1: Create the plan review prompt**

Create `docs/reviews/opencode-stage-121-plan-review-prompt.md` asking local
opencode to review the Stage 121 design and plan.

- [ ] **Step 2: Run local opencode plan review with temporary capture**

Run:

```bash
tmp_review="$(mktemp)"
opencode run --model zhipuai-coding-plan/glm-5.2 --variant max --dir /home/ubuntu/fashion-radar "$(cat docs/reviews/opencode-stage-121-plan-review-prompt.md)" > "$tmp_review"
sed -n '1,220p' "$tmp_review"
cp "$tmp_review" docs/reviews/opencode-stage-121-plan-review.md
rm -f "$tmp_review"
```

Expected: review completes and lists no Critical or Important blockers, or
lists blockers to fix before Task 1.

- [ ] **Step 3: Resolve plan blockers before coding**

If the review identifies Critical or Important findings, update this plan or
the design before writing tests.

## Task 1: Write Failing Regex Unit Test

- [ ] **Step 1: Add import and failing helper test**

In `tests/test_review_protocol_docs.py`, add `import re` below
`from __future__ import annotations`.

After `_normalized_text`, add this test before existing docs tests:

```python
def test_direct_opencode_review_redirect_regex_catches_shell_variants() -> None:
    unsafe_examples = (
        "opencode run --model zhipuai-coding-plan/glm-5.2 --variant max >docs/reviews/opencode-stage-N-plan-review.md",
        "opencode run --model zhipuai-coding-plan/glm-5.2 --variant max >> docs/reviews/opencode-stage-N-code-rereview.md",
        'opencode run --model zhipuai-coding-plan/glm-5.2 --variant max 1> "./docs/reviews/opencode-stage-N-release-review.md"',
        "opencode run --model zhipuai-coding-plan/glm-5.2 --variant max &> 'docs/reviews/opencode-stage-N-plan-rereview.md'",
        'opencode run --model zhipuai-coding-plan/glm-5.2 --variant max \\\n+  --dir /home/ubuntu/fashion-radar "prompt" > docs/reviews/opencode-stage-N-release-review.md',
    )
    for example in unsafe_examples:
        assert _direct_opencode_review_redirect(example), example

    safe_example = """tmp_review="$(mktemp)"
opencode run --model zhipuai-coding-plan/glm-5.2 --variant max \\
  --dir /home/ubuntu/fashion-radar "prompt" > "$tmp_review"
sed -n '1,260p' "$tmp_review"
cp "$tmp_review" docs/reviews/opencode-stage-N-release-review.md
"""
    assert not _direct_opencode_review_redirect(safe_example)
```

This test intentionally references `_direct_opencode_review_redirect` before it
exists.

- [ ] **Step 2: Run focused RED test**

Run:

```bash
env -u ALL_PROXY -u all_proxy uv --no-config run --frozen pytest \
  tests/test_review_protocol_docs.py::test_direct_opencode_review_redirect_regex_catches_shell_variants \
  -q
```

Expected: test fails with `NameError: name '_direct_opencode_review_redirect' is not defined`.

## Task 2: Implement Regex Helper And Replace Guard

- [ ] **Step 1: Add compiled regex and helper**

After `_normalized_text`, add:

```python
DIRECT_OPENCODE_REVIEW_REDIRECT = re.compile(
    r"opencode\s+run\b[^\n]*(?:\\\n[^\n]*)*"
    r"\s(?:&>>|&>|1>>|1>|>>|>)\s*(?:\\\n\s*)?"
    r"[\"']?(?:\./)?docs/reviews/opencode-stage-N-"
    r"(?:plan|code|release)-(?:review|rereview)\.md[\"']?",
    re.IGNORECASE,
)


def _direct_opencode_review_redirect(text: str) -> re.Match[str] | None:
    return DIRECT_OPENCODE_REVIEW_REDIRECT.search(text)
```

- [ ] **Step 2: Replace literal redirect assertions**

In `test_review_protocol_docs_document_capture_hygiene`, replace:

```python
assert "> docs/reviews/opencode-stage-N-plan-review.md" not in protocol_text
assert "> docs/reviews/opencode-stage-N-release-review.md" not in protocol_text
```

with:

```python
redirect_failures: list[str] = []
for path in ACTIVE_REVIEW_DOCS:
    text = _read(path)
    if match := _direct_opencode_review_redirect(text):
        redirect_failures.append(
            f"{path.relative_to(ROOT)} documents direct opencode final-file "
            f"redirection: {match.group(0)!r}"
        )

assert not redirect_failures, "\n".join(redirect_failures)
```

- [ ] **Step 3: Run focused GREEN tests**

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

- [ ] **Step 2: Run focused lint/format**

Run:

```bash
uv --no-config run --frozen ruff check tests/test_review_protocol_docs.py
uv --no-config run --frozen ruff format --check tests/test_review_protocol_docs.py
```

Expected: both commands pass.

- [ ] **Step 3: Create code review prompt**

Create `docs/reviews/opencode-stage-121-code-review-prompt.md` summarizing the
Stage 121 tests-only change and verification commands.

- [ ] **Step 4: Run local opencode code review with temporary capture**

Run the temporary-capture workflow, writing the final reviewed output to
`docs/reviews/opencode-stage-121-code-review.md`.

Expected: review completes and explicitly lists no Critical or Important
blockers, or lists findings to fix before release.

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
git add tests/test_review_protocol_docs.py \
  docs/reviews/opencode-stage-121-plan-review-prompt.md docs/reviews/opencode-stage-121-plan-review.md \
  docs/reviews/opencode-stage-121-code-review-prompt.md docs/reviews/opencode-stage-121-code-review.md \
  docs/superpowers/specs/2026-06-20-stage-121-review-redirect-regex-guard-design.md \
  docs/superpowers/plans/2026-06-20-stage-121-review-redirect-regex-guard-plan.md
git commit -m "Harden review redirect guard"
```

Include any Stage 121 rereview prompt/result files if plan review required them.

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
