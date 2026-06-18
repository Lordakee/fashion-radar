I'll review the Stage 89 plan. Let me read the relevant files first.
Let me verify some assumptions about the existing review file conventions before finalizing findings.
I have enough context. Here are my findings.

---

# Stage 89 Plan Review — Findings

## Important

### I-1. Stage 89 review artifacts use `opencode-stage-89-*` naming, deepening the long-standing drift that Stage 89 is uniquely positioned to fix

**Where:**
- `docs/superpowers/plans/2026-06-18-stage-89-review-protocol-code-record-plan.md:28-33` (Task 1 creates `docs/reviews/opencode-stage-89-plan-review-prompt.md` / `opencode-stage-89-plan-review.md`)
- `docs/superpowers/plans/2026-06-18-stage-89-review-protocol-code-record-plan.md:115-120` (Task 4 creates `opencode-stage-89-code-review-prompt.md` / `opencode-stage-89-code-review.md`)
- vs. `docs/REVIEW_PROTOCOL.md:57-58,64-65` (the section Stage 89 updates, which prescribes `claude-code-stage-N-*`)
- vs. `docs/REVIEW_PROTOCOL.md:68-69` ("Older `opencode-*` records under `docs/reviews/` are historical audit records and do not need rewriting.")
- vs. `AGENTS.md:25` (`claude --effort max --permission-mode plan ...`)
- vs. `tests/test_review_protocol_docs.py:16-22` (`FORBIDDEN_ACTIVE_REVIEW_TERMS` locks claude-code into active docs)

**Why it matters:** Stage 89 is the first stage since Stage 43 to modify the protocol's "Review Record Naming" section. The whole stated goal is "aligning the naming convention with the existing protocol requirement." But Stage 89's *own* review artifacts will use `opencode-stage-89-*`, not the `claude-code-stage-89-*` pattern the protocol mandates. Stage 77 already flagged this exact gap as needing resolution (`docs/reviews/opencode-stage-77-plan-review.md:13-17`), and Stage 83 noted the drift is widening (`docs/reviews/opencode-stage-83-plan-rereview.md:18`).

It does not break any test (`FORBIDDEN_ACTIVE_REVIEW_TERMS` only scans `AGENTS.md`, `REVIEW_PROTOCOL.md`, `docs/github-upload-checklist.md`, not `docs/reviews/`), so this is not a test-level blocker. But it is a documented-convention blocker for a stage whose entire purpose is convention alignment.

**Recommended fix (pick one):**
- Rename the Stage 89 artifacts to `claude-code-stage-89-plan-review.md` / `claude-code-stage-89-code-review.md` and invoke `claude --effort max --permission-mode plan` per `AGENTS.md:25`, **or**
- Add an explicit "Out-of-scope carry-forward" note in the Stage 89 plan acknowledging the persistent `opencode-*` artifact drift, so the contradiction with the protocol's "historical" framing is at least documented rather than silently reproduced.

---

## Minor / Informational

### M-1. Test asserts substring presence only; does not lock in ordering

`tests/test_review_protocol_docs.py` (Task 2 replacement, plan lines 50-60) checks `record_name in protocol_text` for each of the six names. It does not verify that `code-review` sits *between* `plan-review` and `release-review` as the design (`docs/superpowers/specs/2026-06-18-stage-89-review-protocol-code-record-design.md:37-38`) requires. A future regression that scrambled the order would still pass. Consider asserting on the literal multi-line block, or assert `protocol_text.index(plan) < protocol_text.index(code) < protocol_text.index(release)`.

### M-2. Procedural sections still do not reference the new record names

`docs/REVIEW_PROTOCOL.md:21-28` ("During Development") says "Local Claude Code review of newly added code" without naming the record file. Stage 89 adds the file name to the "Review Record Naming" section (lines 52-66) but does not cross-reference it from the procedural step. Optional polish: add a parenthetical `(record: docs/reviews/claude-code-stage-N-code-review.md)` to step 2 of "During Development" so the alignment is fully bidirectional.

### M-3. Commit message is conventional but does not reference the stage

Plan line 151: `git commit -m "Document code review record names"`. Adequate; mention only because recent project commits typically carry stage context.

---

# Answers To Review Questions

1. **Does the plan correctly align the record naming section with the existing code-review requirement?** — Yes for the naming section itself. `docs/REVIEW_PROTOCOL.md:26` already requires "Local Claude Code review of newly added code," and Task 3 correctly inserts `claude-code-stage-N-code-review.md` between plan and release records, plus `claude-code-stage-N-code-rereview.md` in the follow-up block. (See M-2 for the missed cross-reference opportunity.)

2. **Does the test assertion shape cover both review and rereview names without overreaching into historical `opencode-*` records?** — Yes. The six-name loop in plan lines 50-60 covers plan/code/release × review/rereview. It does not mention `opencode-*` at all, so it does not overreach into historical records. (See M-1 for the missing ordering check.)

3. **Is the scope safely docs/test-only?** — Yes. Touched files are limited to `docs/REVIEW_PROTOCOL.md`, `tests/test_review_protocol_docs.py`, and Stage 89 review artifacts. No `src/`, schema, manifest, `uv.lock`, CI workflow, `AGENTS.md`, or `docs/github-upload-checklist.md` changes. No forbidden behaviors (scraping, connectors, platform APIs, etc.) introduced.

4. **Are the verification commands sufficient?** — Yes. Task 4 runs the focused test, the full file, `ruff check`, `ruff format --check`, and `git diff --check`. Task 5 adds full pytest, full ruff, `uv lock --check`, the mirror-URL scan, the `uv.lock`/`pyproject.toml` diff guard, and the cached-secret scan. Red/green discipline is preserved (Task 2 expects FAIL, Task 4 expects PASS).

5. **Are there any Critical or Important blockers before implementation?** — One Important blocker: **I-1**. The Stage 89 review artifacts should be renamed to `claude-code-stage-89-*` (matching the protocol Stage 89 is editing), or the plan should explicitly document the `opencode-*` drift as carry-forward. No Critical blockers. M-1, M-2, M-3 are non-blocking polish.

---

Per `AGENTS.md`, fix I-1 (and optionally M-1/M-2) before implementation.
