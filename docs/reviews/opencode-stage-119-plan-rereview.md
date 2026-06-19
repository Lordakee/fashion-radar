# Stage 119 Plan Rereview — After I-1 Fix

Re-reviewed the updated design and plan after the I-1 fix and the three
follow-up changes. Read the updated spec, updated plan, prior review, current
`tests/test_review_protocol_docs.py`, and the three target docs
(`AGENTS.md`, `docs/REVIEW_PROTOCOL.md`, `docs/github-upload-checklist.md`).
Also confirmed with `cat -A` that the `xhigh` bullet in `AGENTS.md:19-20`
still wraps with `\n  ` between `reasoning` and `effort`.

**Critical:** None.

**Important:** None — I-1 is fully resolved. `plan.md:114` now uses `_normalized_text(agents_text)`, and I confirmed via `cat -A` that the kept `AGENTS.md:19-20` bullet survives normalization.

**Minor:**
- **m-1**: `plan.md:118` requires `"optional alternate"` in `REVIEW_PROTOCOL.md`, but the plan prescribes no exact intro sentence for that section (unlike the exact prose given for `Before Coding`/`During Development`/`Before GitHub Upload`). Strongly implied by the plan's "optional alternate Claude Code section" description and caught by RED→GREEN, so non-blocking.

The three follow-up changes trace cleanly: optional `claude-code-stage-N-*` naming is now test-enforced (`plan.md:150-159`), exact REVIEW_PROTOCOL prose is prescribed (`plan.md:225-231`), and both stale phrases are forbidden (`plan.md:119-120`). RED and GREEN states both verify against the prescribed edits.

**No Critical or Important blockers remain before implementation.**
 **I-1 is fully resolved.**

## Follow-Up Change Verification

1. **Optional `claude-code-stage-N-...` naming convention guarded.**
   `plan.md:150-159` adds six `claude-code-stage-N-*` record names asserted
   against `protocol_text`. The prescribed REVIEW_PROTOCOL naming block
   (`plan.md:260-266`) lists the same six names. The test and doc edits now
   agree. (Addresses prior M-2.)

2. **Exact active opencode prose for REVIEW_PROTOCOL sections.**
   `plan.md:225-231` now prescribes exact sentences for `Before Coding`,
   `During Development`, and `Before GitHub Upload`, each containing
   `"local opencode"` and/or the model id. These satisfy the
   `"local opencode"` literal required by
   `test_active_review_docs_document_local_opencode_gate` for
   `REVIEW_PROTOCOL.md`. (Addresses prior M-1.)

3. **Stale "older `opencode-*` records" wording forbidden.**
   `plan.md:120` adds `assert "older \`opencode-*\` records" not in
   protocol_text`. The plan instructs replacing the entire sentence at
   `REVIEW_PROTOCOL.md:71-72` (which contains both `"older \`opencode-*\`
   records"` and `"historical audit records"`) with the optional Claude Code
   section. Both absence assertions (`plan.md:119-120`) are satisfied.
   (Addresses prior M-3.)

## RED → GREEN Consistency Trace

**RED (current docs fail new tests):** Confirmed. Current docs say "local
Claude Code" (no `"local opencode"`, no `ACTIVE_OPENCODE_COMMAND`), and
`REVIEW_PROTOCOL.md:71-72` still has both forbidden stale phrases.

**GREEN (prescribed edits satisfy all assertions):** Traced every assertion
in both new test functions against the prescribed doc edits:

- All five terms in `test_active_review_docs_document_local_opencode_gate`
  (`"local opencode"`, `ACTIVE_OPENCODE_COMMAND`, `"zhipuai-coding-plan/glm-5.2"`,
  `"--variant max"`, `"docs/reviews/opencode-stage-N"`) are present in all
  three prescribed doc edits.
- Both `ACTIVE_OPENCODE_COMMAND` and `"reasoning effort to \`xhigh\`"`
  assertions use `_normalized_text` on `agents_text`; the prescribed AGENTS.md
  command block and kept `xhigh` bullet both survive normalization.
- `OPTIONAL_CLAUDE_CODE_COMMAND` is in the prescribed REVIEW_PROTOCOL Claude
  block (`plan.md:253-256`).
- Six `opencode-stage-N-*` names + three `opencode-stage-N-*-rereview.md`
  names are in the prescribed naming section in the asserted order
  (`plan.md:236-246`); `_section(..., "Review Record Naming")` finds them
  because the heading stays at `##` level in the current doc.
- Six `claude-code-stage-N-*` names are asserted against `protocol_text`
  (not `naming_section`), so placement flexibility is fine.

## Minor

### m-1 — `"optional alternate"` literal not prescribed as exact prose

`plan.md:118` asserts `assert "optional alternate" in
normalized_protocol.casefold()`. The plan describes the section as "an
optional alternate Claude Code section" (`plan.md:249`) but, unlike the
exact sentences prescribed for `Before Coding` / `During Development` /
`Before GitHub Upload` (`plan.md:225-231`), gives no exact intro sentence
for this section. A reasonable implementer would title it "Optional
Alternate Route" or similar, and the test enforces it during RED→GREEN, so
this is non-blocking. For consistency with the other exact-prose
prescriptions, consider adding one sentence like "Claude Code is an
optional alternate route only when a stage explicitly requests it."

## Scope And Verification Check

- Files list (`plan.md:15-28`) and "Do not modify" line are unchanged and
  clean: no `src/`, `pyproject.toml`, `uv.lock`, CI, or runtime changes.
- No other test file references `FORBIDDEN_ACTIVE_REVIEW_TERMS` or the two
  removed test function names (grep-confirmed across the repo; remaining
  hits are only in historical plans/specs/reviews and the file being
  edited).
- Verification commands unchanged and sufficient: focused RED, focused
  GREEN, adjacent `test_cli_docs.py`, opencode code review, and full release
  gate with `git diff --exit-code -- uv.lock pyproject.toml`.

## Final Statement

**No Critical blockers. No Important blockers.** I-1 is fully resolved via
`_normalized_text(agents_text)`, and the three follow-up changes (optional
`claude-code-stage-N-*` naming guard, exact REVIEW_PROTOCOL prose, stale
"older `opencode-*` records" absence check) are correctly incorporated
without introducing any new Critical or Important issue. The plan is
internally consistent for TDD implementation. The only remaining item is
Minor m-1 (the `"optional alternate"` literal is implied but not prescribed
as exact prose), which the RED→GREEN test cycle catches, so it does not
block starting Task 1.
