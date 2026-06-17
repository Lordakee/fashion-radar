# Stage 71 Adapter Readiness Docs Guard Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a docs drift guard for the documented readiness-preflight relationship between `external-tool-adapters` and `external-tool-readiness`.

**Architecture:** This is a test-only docs guard. It extends the existing adapter registry docs test in `tests/test_cli_docs.py`; runtime code and generated adapter output remain unchanged.

**Tech Stack:** Python 3.11, pytest, ruff, uv.

---

## File Map

- Modify `tests/test_cli_docs.py`
  - Add a small readiness-preflight relationship phrase set inside the existing
    adapter registry docs test.
  - Assert those phrases across the existing adapter docs loop.
- Create review artifacts:
  - `docs/reviews/opencode-stage-71-plan-review-prompt.md`
  - `docs/reviews/opencode-stage-71-plan-review.md`
  - `docs/reviews/opencode-stage-71-code-review-prompt.md`
  - `docs/reviews/opencode-stage-71-code-review.md`

## Task 1: Add Focused Docs Drift Guard

**Files:**
- Modify: `tests/test_cli_docs.py`

- [ ] **Step 1: Run the current external-tool adapter docs test**

Run:

```bash
uv --no-config run --frozen pytest tests/test_cli_docs.py::test_external_tool_adapter_registry_docs_are_linked_and_bounded -q
```

Expected: pass.

- [ ] **Step 2: Add the readiness-preflight phrase set**

Inside `test_external_tool_adapter_registry_docs_are_linked_and_bounded`,
immediately before the existing docs loop, add:

```python
    readiness_preflight_terms = (
        "external-tool-readiness",
        "optional local read-only preflight command",
        "itself remains print-only",
        "does not run readiness or perform PATH lookup",
    )
```

- [ ] **Step 3: Assert the phrase set in the existing docs loop**

In the same test, inside the first loop over `readme`, `import_doc`,
`quality_doc`, `cli_reference`, `checklist`, `boundaries`, `architecture`,
`agents`, and `changelog`, add:

```python
        for term in readiness_preflight_terms:
            assert term.casefold() in normalized
```

The resulting loop should keep the existing adapter identity assertions:

```python
    for text in (
        readme,
        import_doc,
        quality_doc,
        cli_reference,
        checklist,
        boundaries,
        architecture,
        agents,
        changelog,
    ):
        normalized = _normalized_text(text).casefold()
        assert "external-tool-adapters" in normalized
        assert "external social/community tool adapter registry" in normalized
        assert "local producer-discovery registry" in normalized
        for term in readiness_preflight_terms:
            assert term.casefold() in normalized
```

- [ ] **Step 4: Run the focused adapter docs test**

Run:

```bash
uv --no-config run --frozen pytest tests/test_cli_docs.py::test_external_tool_adapter_registry_docs_are_linked_and_bounded -q
```

Expected: pass against the existing docs. If it fails, update only the missing
doc wording needed to restore the Stage 68/71 documented boundary.

- [ ] **Step 5: Run the docs test file**

Run:

```bash
uv --no-config run --frozen pytest tests/test_cli_docs.py -q
```

Expected: pass.

## Task 2: Review, Verification, And Commit

**Files:**
- Create: `docs/reviews/opencode-stage-71-code-review-prompt.md`
- Create: `docs/reviews/opencode-stage-71-code-review.md`
- Include Stage 71 spec/plan/review artifacts in commit.

- [ ] **Step 1: Run lint and format checks**

Run:

```bash
uv --no-config run --frozen ruff check tests/test_cli_docs.py
uv --no-config run --frozen ruff format --check tests/test_cli_docs.py
```

Expected: both pass.

- [ ] **Step 2: Run release and whitespace checks**

Run:

```bash
uv --no-config run --frozen python scripts/check_release_hygiene.py
git diff --check
```

Expected: both pass.

- [ ] **Step 3: Run the full test suite**

Run:

```bash
uv --no-config run --frozen pytest
```

Expected: pass.

- [ ] **Step 4: Request implementation code review**

Create `docs/reviews/opencode-stage-71-code-review-prompt.md` with the Stage 71
goal, scope, touched files, and verification results. Run:

```bash
opencode run --model zhipuai-coding-plan/glm-5.2 --variant max --dir /home/ubuntu/fashion-radar "$(cat docs/reviews/opencode-stage-71-code-review-prompt.md)" > docs/reviews/opencode-stage-71-code-review.md
```

Fix Critical/Important findings before proceeding.

- [ ] **Step 5: Commit**

Run:

```bash
git add tests/test_cli_docs.py docs/superpowers/specs/2026-06-17-stage-71-adapter-readiness-docs-guard-design.md docs/superpowers/plans/2026-06-17-stage-71-adapter-readiness-docs-guard-plan.md docs/reviews/opencode-stage-71-plan-review-prompt.md docs/reviews/opencode-stage-71-plan-review.md docs/reviews/opencode-stage-71-code-review-prompt.md docs/reviews/opencode-stage-71-code-review.md
git commit -m "Add adapter readiness docs guard"
```

- [ ] **Step 6: Publish and verify CI**

Prefer the GitHub Git API path used in recent stages if local git HTTPS push
continues to fail in this environment. Confirm `main` and `origin/main` align,
the remote URL/token config stay clean, and GitHub Actions CI succeeds.
