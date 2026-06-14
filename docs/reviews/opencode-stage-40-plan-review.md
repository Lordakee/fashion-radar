# Opencode Stage 40 Plan Review

## Critical Findings

None.

## Important Findings

1. **Ruff format check on Markdown may be a no-op.** Task 3 Step 2 runs
   `uv run ruff format --check docs/REVIEW_PROTOCOL.md docs/github-upload-checklist.md`.
   Ruff is a Python formatter; by default it only processes `.py` files, so this
   command likely reports "N files left unchanged" without actually validating
   the Markdown prose. If this is an established project convention carried over
   from prior stages, keep it for consistency, but consider adding a meaningful
   documentation lint (e.g., `rg`-based forbidden-phrase checks, or a Markdown
   linter if one is already a dev dependency) so the gate has real teeth.

2. **No explicit historical-preservation assertion.** The plan states older
   Claude Code records must remain untouched, but the verification section does
   not assert it. Add a guard such as:

   ```bash
   git diff --name-only | rg '^docs/reviews/claude-code' \
     && { echo "FAIL: historical review files modified"; exit 1; } || true
   git diff --name-only | rg '^docs/superpowers/plans/' \
     && { echo "FAIL: historical plans modified"; exit 1; } || true
   ```

3. **`opencode run --file` flag syntax should be confirmed.** Task -1 Step 2
   and Task 3 Step 3 rely on `opencode run -m <model> --file <path> ...`. Verify
   the local opencode build accepts `--file` (some builds use `@path` or a
   different attachment flag). If the flag differs, the review-prompt capture
   step will fail before any review happens.

## Minor Findings

1. **No pre-flight cleanliness check.** Task 1 begins editing without confirming
   `git status` is clean or that the working branch matches the plan's intent.
   A one-line `git status --porcelain` check at the top of Task 1 would prevent
   accidental staging of unrelated files.

2. **Task -1 numbering is unconventional** but documented in the superpowers
   plan template, so acceptable. Consider a one-line note that negative task
   numbers denote pre-implementation review gates.

3. **"Fresh tests" in Task 1 Step 2 is vague** for a documentation-only change.
   Clarify that for this stage "fresh tests" means the documentation-focused
   `rg` checks plus the release verification block, not the Python test suite.

4. **Approval phrases are distinct and correct** (`APPROVED FOR STAGE 40
   OPENCODE REVIEW WORKFLOW` for plan, `APPROVED FOR STAGE 40 COMMIT AND PUSH`
   for release). No action needed; noted for traceability.

5. **Handoff Summary requirement** is good. Consider adding "review artifacts
   produced" as an explicit bullet so the audit trail is visible at handoff.

## Scope Compliance

- Change is documentation-only. No source, tests, dependencies, lockfiles,
  CI, schema, commands, connectors, scraping, platform automation, schedulers,
  watchers, or monitors are touched. Aligned with `AGENTS.md` scope boundaries.
- Historical `docs/reviews/claude-code-*` and prior staged plans are preserved
  as audit history. Correct.
- Free-first / local-first principle is respected: the gate uses a local
  opencode model, no paid APIs or bypass tooling introduced.

## Verdict

The plan is well-scoped, correctly preserves historical records, keeps the
review-gated structure intact, and matches the project's documentation-only
intent for this stage. The Important findings are verification-hardening
additions, not architectural defects, and can be addressed without changing the
plan's structure. The plan is acceptable to execute.

```text
APPROVED FOR STAGE 40 OPENCODE REVIEW WORKFLOW
```
