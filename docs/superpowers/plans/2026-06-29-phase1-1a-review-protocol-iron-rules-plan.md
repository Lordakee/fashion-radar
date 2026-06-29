# Phase 1 · Sub-stage 1a — Review Protocol Iron Rules Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the "opencode-primary / Claude Code optional alternate" review framing in the live protocol docs with the project owner's two iron rules (Claude Code = primary reviewer; opencode `glm-5.2 --variant max` = plan reviser + fallback reviewer), keeping the three review types (plan/code/release), the dual artifact naming, capture hygiene, and the roadmap-focus phrases intact and green.

**Architecture:** Docs-and-guard-test-only change. Rewrite the primacy framing in `AGENTS.md`, `docs/REVIEW_PROTOCOL.md`, `docs/github-upload-checklist.md`, and (if needed) `docs/PROJECT_BRIEF.md`; update the single docs-guard assertion in `tests/test_review_protocol_docs.py` that pins the old "optional alternate" framing. TDD: change the guard test first (RED against current docs), then rewrite the docs (GREEN). No source code, no schema, no dependency, no collector changes.

**Tech Stack:** Markdown docs, Python docs-guard test (`tests/test_review_protocol_docs.py`), `uv --no-config run --frozen pytest`, `ruff`, local Claude Code review (`claude --effort max --permission-mode plan --no-session-persistence`), opencode revision (`opencode run --model zhipuai-coding-plan/glm-5.2 --variant max`).

---

## Key Decision (for Claude Code review)

**Keep the three review types (plan, code, release) and the dual artifact naming.** Iron rule 2 literally mentions plan review and code review per phase; it is silent on release review. **Extension flag (N-4):** retaining the **release review** is an *extension beyond what iron rule 2 literally states* (iron rule 2 mentions only plan and code review); it is accepted pending reviewer confirmation, not part of the literal rule. Interpretation chosen: Claude Code becomes the **primary** reviewer for all three review types (plan, code, release); opencode (`glm-5.2 --variant max`) **revises the plan** based on Claude Code's review plus its own judgment, and is the **fallback reviewer** for any review type when Claude Code is unavailable. This is the minimal-churn interpretation: it does not drop the release gate, does not change artifact filenames, and leaves the naming-order / capture-hygiene / roadmap-phrase guard assertions green. Only the primacy framing ("optional alternate" → "primary"/"fallback"/"revises") changes.

If Claude Code review prefers the stricter literal interpretation (drop the release review, collapse to per-phase plan+code only), revise this plan accordingly before implementation.

## Scope

**In scope:**
- Reframe review primacy in `AGENTS.md` (## Review Gates and ## Agent Runtime Settings).
- Reframe review primacy in `docs/REVIEW_PROTOCOL.md` (## Before Coding, ## During Development, ## Before GitHub Upload, promote the former "Optional Alternate Route" Claude Code section to primary, demote opencode to reviser + fallback; keep ## Review Record Naming, ## Review Capture Hygiene verbatim; keep the three roadmap phrases in ## During Development).
- Reframe the final-review primacy in `docs/github-upload-checklist.md` (## Final Review).
- Check and, only if it pins review primacy, update `docs/PROJECT_BRIEF.md`.
- Update the framing assertion in `tests/test_review_protocol_docs.py`.
- Add a Phase-1 / sub-stage-1a CHANGELOG entry.

**Out of scope (explicitly):**
- No change to review artifact filenames or the `claude-code-stage-N-*` / `opencode-stage-N-*` naming conventions.
- No change to capture-hygiene rules or the redirect-regex guard.
- No change to the roadmap-focus phrases ("source-liveness evidence", "curated public-source coverage", "deterministic matching quality") in `## During Development`.
- No overturn of the social-platform scraping ban (that is Phase 2).
- No source code, schema, dependency, lockfile, collector, model, or DB change.
- No commit of review artifacts generated during this sub-stage beyond the plan/code/release review records themselves.

## File Map

- Modify `tests/test_review_protocol_docs.py` — flip the `"optional alternate"` framing assertion to Claude-Code-primary / opencode-reviser-fallback.
- Modify `AGENTS.md` — `## Review Gates` (lines ~7–20) and `## Agent Runtime Settings` (lines ~22–41).
- Modify `docs/REVIEW_PROTOCOL.md` — `## Before Coding`, `## During Development`, `## Before GitHub Upload`, and the section currently titled `## Optional Alternate Route` (lines ~110–131); leave `## Review Record Naming` and `## Review Capture Hygiene` unchanged.
- Modify `docs/github-upload-checklist.md` — `## Final Review` primacy wording.
- Read-check (modify only if it pins primacy): `docs/PROJECT_BRIEF.md`.
- Modify `CHANGELOG.md` — add sub-stage 1a entry under `[Unreleased] -> ### Changed`.
- Add `docs/superpowers/plans/2026-06-29-phase1-1a-review-protocol-iron-rules-plan.md` (this file).
- Add review artifacts under `docs/reviews/` as the iron-rule flow produces them.

**Label mapping note (N-2):** `stage-211` is the sequential review-artifact ID for Phase 1 sub-stage 1a; both labels are used in parallel (one is the roadmap position, one is the artifact-naming integer).

Do not modify `pyproject.toml` or `uv.lock`.

## Required phrases the rewritten docs MUST still contain (test contracts)

These are asserted by `tests/test_review_protocol_docs.py` and MUST remain present (case-insensitive, whitespace-normalized) after the rewrite, or the GREEN run fails:

- In `AGENTS.md`, `docs/REVIEW_PROTOCOL.md`, `docs/github-upload-checklist.md` (all three): `local opencode`, `opencode run --model zhipuai-coding-plan/glm-5.2 --variant max`, `zhipuai-coding-plan/glm-5.2`, `--variant max`, `docs/reviews/opencode-stage-N`.
- In `AGENTS.md`: `reasoning effort to \`xhigh\`` (Codex subagent rule — unchanged); `docs/reviews/claude-code-stage-N` (new AGENTS.md guard added in Task 1, see I-2); and the five `## Review Gates` hygiene phrases that `test_review_protocol_docs_document_capture_hygiene` asserts against the normalized `## Review Gates` text — `completed review output`, `live-capture stubs`, `duplicated or truncated text`, `tool-status messages`, `empty output` (see I-1).
- In `docs/REVIEW_PROTOCOL.md`: the `claude --effort max --permission-mode plan --no-session-persistence` command; the six `claude-code-stage-N-*-review.md` / `*-rereview.md` names; the six `opencode-stage-N-*-review.md` / `*-rereview.md` names in `## Review Record Naming` in their existing order.
- In `docs/REVIEW_PROTOCOL.md` `## Review Capture Hygiene` and `docs/github-upload-checklist.md` `## Final Review`: every phrase in `REVIEW_CAPTURE_HYGIENE_REQUIRED_PHRASES` (see test lines 23–33), plus the three `opencode-stage-N-{plan,code,release}-review.md` names.
- In `docs/REVIEW_PROTOCOL.md` `## During Development`: `source-liveness evidence`, `curated public-source coverage`, `deterministic matching quality`.
- Nowhere in `docs/REVIEW_PROTOCOL.md`: the literal strings `historical audit records` or `older \`opencode-*\` records`.

## New framing phrases the rewritten docs MUST contain (new test contract)

- `docs/REVIEW_PROTOCOL.md`: `Claude Code` is the **primary** reviewer; opencode **revises the plan**; opencode is the **fallback** reviewer. Concretely the normalized text must contain: `primary reviewer`, `opencode revises the plan`, `fallback` (these are what the updated guard test asserts — see Task 1; the `revises` token is tightened to the full phrase `opencode revises the plan` per N-1).

---

## Task 0: Plan Review (iron rule 2)

**Files:**
- Add: `docs/reviews/opencode-stage-211-plan-review-prompt.md` (the prompt handed to Claude Code)
- Add: `docs/reviews/claude-code-stage-211-plan-review.md` (Claude Code's review output)

- [ ] **Step 1: Hand this plan to local Claude Code for review**

Run (read-only plan mode, no session persistence):

```bash
claude --effort max --permission-mode plan --no-session-persistence \
  --tools Read,Grep,Glob,LS,Bash \
  -p "Review the Phase 1 sub-stage 1a plan at docs/superpowers/plans/2026-06-29-phase1-1a-review-protocol-iron-rules-plan.md for: (1) correctness of the Key Decision (keep 3 review types, Claude Code primary, opencode reviser+fallback) vs the literal iron rule 2; (2) completeness of the Required-phrases test-contract list; (3) whether the New-framing test change is sufficient; (4) any guard test in tests/ that pins review primacy and is missed; (5) scope leaks. Output Verdict (APPROVE/APPROVE_WITH_NITS/REQUEST_CHANGES), Critical, Important, Nits." \
  > docs/reviews/claude-code-stage-211-plan-review.md
```

Expected: a completed review body in the file (no tool-status lines, no ANSI, single verdict).

- [ ] **Step 2: opencode revises the plan per Claude Code's review + its own judgment**

```bash
tmp_review="$(mktemp)"
opencode run --model zhipuai-coding-plan/glm-5.2 --variant max \
  --dir /home/ubuntu/fashion-radar \
  "Here is a Claude Code plan review (docs/reviews/claude-code-stage-211-plan-review.md) for the plan at docs/superpowers/plans/2026-06-29-phase1-1a-review-protocol-iron-rules-plan.md. Apply Critical and Important findings to the plan file directly, using your own judgment. Do not edit any other file. Output a short summary of changes made." \
  > "$tmp_review"
sed -n '1,120p' "$tmp_review"
rm -f "$tmp_review"
```

Expected: plan file updated; Critical/Important findings resolved. If Claude Code returned APPROVE/APPROVE_WITH_NITS with no Critical/Important, this step is a no-op confirmation.

- [ ] **Step 3: If Claude Code was unavailable**, dispatch an independent opencode agent (`glm-5.2 --variant max`) to perform the plan review instead, recorded under `docs/reviews/opencode-stage-211-plan-review.md`.

Proceed to Task 1 only after the plan has no open Critical/Important findings.

---

## Task 1: RED — Update the docs-guard framing assertion

**Files:**
- Modify: `tests/test_review_protocol_docs.py`

- [ ] **Step 1: Replace the "optional alternate" assertion, tighten the `revises` token, and add the `claude-code-stage-N` AGENTS.md guard**

In `test_active_review_protocol_documents_opencode_gate_and_claude_alternate` (lines ~102–156), the current block asserts:

```python
    assert OPTIONAL_CLAUDE_CODE_COMMAND in normalized_protocol
    assert "optional alternate" in normalized_protocol.casefold()
```

Replace those two lines with:

```python
    assert OPTIONAL_CLAUDE_CODE_COMMAND in normalized_protocol
    assert "primary reviewer" in normalized_protocol.casefold()
    assert "opencode revises the plan" in normalized_protocol.casefold()
    assert "fallback" in normalized_protocol.casefold()
    assert "optional alternate" not in normalized_protocol.casefold()
```

Rationale: iron rule 2 makes Claude Code the primary reviewer and opencode the reviser + fallback, so the docs must say `primary reviewer`, `opencode revises the plan`, `fallback`, and must no longer say `optional alternate`. The `revises` token is tightened to the full phrase `opencode revises the plan` so the assertion cannot be satisfied by an unrelated occurrence of the bare word "revises" (review N-1). All other assertions in this test (naming order, commands) stay unchanged.

Then, in `test_active_review_docs_document_local_opencode_gate` (lines ~83–99), add a targeted AGENTS.md guard for the claude-code artifact prefix. After the existing loop's `assert not failures`, append (review I-2):

```python
    agents_text = _read(AGENTS)
    assert "docs/reviews/claude-code-stage-N" in _normalized_text(agents_text)
```

Rationale: Claude Code is now the primary reviewer, so AGENTS.md must document its `claude-code-stage-N` artifact prefix; without this guard a future edit could silently drop the prefix with no test going RED.

- [ ] **Step 2: Run the guard test to confirm RED**

```bash
uv --no-config run --frozen pytest tests/test_review_protocol_docs.py::test_active_review_protocol_documents_opencode_gate_and_claude_alternate -q
```

Expected: FAIL — `AssertionError: assert "optional alternate" not in ...` (the current `docs/REVIEW_PROTOCOL.md` still contains "optional alternate") OR the new `primary reviewer`/`opencode revises the plan`/`fallback` assertions fail because the docs do not yet contain those phrases.

- [ ] **Step 3: Run the full review-protocol docs test module to confirm only the intended test is RED**

```bash
uv --no-config run --frozen pytest tests/test_review_protocol_docs.py -q
```

Expected: `test_active_review_protocol_documents_opencode_gate_and_claude_alternate` AND `test_active_review_docs_document_local_opencode_gate` FAIL — the latter because the new `docs/reviews/claude-code-stage-N` assertion fails against the current AGENTS.md, which only documents `opencode-stage-N` (review I-2); the other tests in the module (`test_review_protocol_docs_document_capture_hygiene`, `test_full_project_review_follow_up_status_tracks_completed_stages`, `test_current_direction_docs_prioritize_liveness_backed_source_coverage`, `test_direct_opencode_review_redirect_regex_catches_shell_variants`) still PASS (they are independent of the primacy framing and the new prefix guard).

---

## Task 2: GREEN — Rewrite review primacy in the docs

**Files:**
- Modify: `AGENTS.md`
- Modify: `docs/REVIEW_PROTOCOL.md`
- Modify: `docs/github-upload-checklist.md`
- Read-check / conditionally modify: `docs/PROJECT_BRIEF.md`

- [ ] **Step 1: Rewrite `AGENTS.md` `## Review Gates` and `## Agent Runtime Settings`**

Keep all existing true statements (submit plan before coding; record artifacts under `docs/reviews/opencode-stage-N-...`; capture-hygiene; fix Critical/Important). Change the primacy: Claude Code is the **primary reviewer** for plan, code, and release reviews; opencode (`glm-5.2 --variant max`) **revises the plan** based on Claude Code's review plus its own judgment, and is the **fallback reviewer** when Claude Code is unavailable. Keep both command blocks (the `opencode run --model zhipuai-coding-plan/glm-5.2 --variant max` block and the `claude --effort max --permission-mode plan --no-session-persistence` block) verbatim. Keep `reasoning effort to \`xhigh\`` for Codex subagents. The normalized text must still contain `local opencode`, the opencode command, `zhipuai-coding-plan/glm-5.2`, `--variant max`, `docs/reviews/opencode-stage-N`.

Suggested wording for the `## Review Gates` lead-in (adapt as needed, keep test-contract phrases):

```markdown
## Review Gates

- Follow the staged review workflow in `docs/REVIEW_PROTOCOL.md`.
- Claude Code is the **primary reviewer** for plan, code, and release reviews.
- Before starting a new stage, submit the objective, architecture, tech stack,
  implementation method, and plan to local Claude Code for review.
- After Claude Code's review, opencode revises the plan based on that review and
  its own judgment. opencode is also the fallback reviewer when Claude Code is
  unavailable.
- After completing a development node, request local Claude Code review of the
  new code before moving to the next stage.
- Record active plan, code, release, and rereview artifacts under
  `docs/reviews/opencode-stage-N-...` and `docs/reviews/claude-code-stage-N-...`.
- Before committing review artifacts, ensure each review record contains
  completed review output and no live-capture stubs, duplicated or truncated
  text, tool-status messages, or empty output.
- Fix critical and important review findings before continuing.
```

Suggested wording for the `## Agent Runtime Settings` lead-in:

```markdown
## Agent Runtime Settings

- When spawning Codex subagents for this project, set the subagent reasoning
  effort to `xhigh`.
- Claude Code is the primary reviewer. Use `--effort max`, read-only plan mode,
  and no session persistence for reviews:

  ```bash
  claude --effort max --permission-mode plan --no-session-persistence \
    --tools Read,Grep,Glob,LS,Bash \
    -p "review prompt..."
  ```

- When opencode revises a plan after Claude Code's review, or acts as the
  fallback reviewer, use GLM 5.2 with the max variant:

  ```bash
  opencode run --model zhipuai-coding-plan/glm-5.2 --variant max \
    --dir /home/ubuntu/fashion-radar "review prompt..."
  ```
```

- [ ] **Step 2: Rewrite `docs/REVIEW_PROTOCOL.md` primacy sections**

Rewrite the lead paragraph and `## Before Coding`, `## During Development`, `## Before GitHub Upload` to state Claude Code is the primary reviewer and opencode revises plans / is the fallback reviewer, preserving the opencode command form (the `tmp_review="$(mktemp)" ... cp "$tmp_review" docs/reviews/opencode-stage-N-...-review.md` block) and adding the parallel Claude Code command form.

Promote the section currently titled `## Optional Alternate Route` (lines ~110–131) to the primary route: rename it to `## Primary Review Route (Claude Code)` and describe Claude Code as primary. Add a new `## opencode Revision And Fallback` section stating `opencode revises the plan` after Claude Code review and serves as fallback reviewer when Claude Code is unavailable, with the opencode command form.

Leave `## Review Record Naming` (lines ~72–91) and `## Review Capture Hygiene` (lines ~93–108) **verbatim**.

In `## During Development`, keep the existing three roadmap phrases verbatim: `source-liveness evidence`, `curated public-source coverage`, `deterministic matching quality`.

The normalized text of the whole file must contain: `primary reviewer`, `opencode revises the plan`, `fallback`, the `claude --effort max --permission-mode plan --no-session-persistence` command, `local opencode`, the opencode command, all six `claude-code-stage-N-*` names, and must NOT contain `optional alternate`, `historical audit records`, or `older \`opencode-*\` records`.

- [ ] **Step 3: Rewrite `docs/github-upload-checklist.md` `## Final Review` primacy**

State that Claude Code performs the final review (primary); opencode is the fallback reviewer. Keep the opencode command, the capture-hygiene phrases (`REVIEW_CAPTURE_HYGIENE_REQUIRED_PHRASES`), and `opencode-stage-N-release-review.md` in the section.

- [ ] **Step 4: Read-check `docs/PROJECT_BRIEF.md` for review-primacy framing**

```bash
rg -n "optional alternate|primary reviewer|opencode|claude code|variant max" docs/PROJECT_BRIEF.md || true
```

If `docs/PROJECT_BRIEF.md` contains `optional alternate` or otherwise pins opencode as primary, update it to the Claude-Code-primary / opencode-reviser-fallback framing. If it does not pin review primacy, leave it unchanged. (No guard test currently asserts PROJECT_BRIEF review primacy, so this step is consistency-only.)

- [ ] **Step 5: Run the guard test to confirm GREEN**

```bash
uv --no-config run --frozen pytest tests/test_review_protocol_docs.py -q
```

Expected: all tests in the module PASS, including the updated `test_active_review_protocol_documents_opencode_gate_and_claude_alternate`.

---

## Task 3: Changelog + Lint + Focused Verification

**Files:**
- Modify: `CHANGELOG.md`

- [ ] **Step 1: Add CHANGELOG entry**

Under `[Unreleased] -> ### Changed` (create the `### Changed` subsection if absent), add newest-first:

```markdown
- Phase 1 sub-stage 1a makes Claude Code the primary reviewer for plan, code,
  and release reviews, with opencode (`zhipuai-coding-plan/glm-5.2 --variant max`)
  revising plans after Claude Code's review and acting as fallback reviewer when
  Claude Code is unavailable. The three review types, artifact naming, review
  capture hygiene, and roadmap-focus wording are unchanged. This is a docs and
  docs-guard change only; no source, schema, dependency, collector, or model
  change.
```

- [ ] **Step 2: Lint and format-check the touched files**

```bash
uv --no-config run --frozen ruff check tests/test_review_protocol_docs.py
uv --no-config run --frozen ruff format --check tests/test_review_protocol_docs.py
```

Expected: clean. (Markdown docs are not ruff-checked; the docs-guard test is their verification.)

- [ ] **Step 3: Confirm no source/dependency drift**

```bash
git diff --exit-code -- uv.lock pyproject.toml
git diff --cached --check
```

Expected: both exit 0 (no dependency or whitespace-damage changes). The `--cached --check` form matches Task 5 Step 3 (review N-3).

---

## Task 4: Code Review (iron rule 2)

**Files:**
- Add: `docs/reviews/claude-code-stage-211-code-review.md` (Claude Code's review of the 1a changes)

- [ ] **Step 1: Hand the 1a diff to local Claude Code for code review**

```bash
git add -A
claude --effort max --permission-mode plan --no-session-persistence \
  --tools Read,Grep,Glob,LS,Bash \
  -p "Review the staged Phase 1 sub-stage 1a changes (docs/REVIEW_PROTOCOL.md, AGENTS.md, docs/github-upload-checklist.md, docs/PROJECT_BRIEF.md, tests/test_review_protocol_docs.py, CHANGELOG.md). Verify: (1) iron rule 2 is accurately reflected (Claude Code primary, opencode revises plans + fallback, glm-5.2 max); (2) every Required-phrase test contract still holds; (3) no capture-hygiene, naming-order, or roadmap-phrase regression; (4) no scope leak into source/schema/deps; (5) the updated guard test is sufficient and correct. Run 'git diff --cached' yourself. Output Verdict, Critical, Important, Nits." \
  > docs/reviews/claude-code-stage-211-code-review.md
```

Expected: APPROVE or APPROVE_WITH_NITS with no Critical/Important.

- [ ] **Step 2: If Critical/Important found**, fix and re-run Step 1 (record rereview under `docs/reviews/claude-code-stage-211-code-rereview.md`). If Claude Code unavailable, dispatch independent opencode agent (`glm-5.2 --variant max`) → `docs/reviews/opencode-stage-211-code-review.md`.

---

## Task 5: Release Verification, Release Review, Commit

**Files:**
- Add: `docs/reviews/claude-code-stage-211-release-review.md`

- [ ] **Step 1: Run the full verification gate**

```bash
uv --no-config run --frozen pytest
uv --no-config run --frozen ruff check .
uv --no-config run --frozen ruff format --check .
uv --no-config run --frozen python scripts/check_release_hygiene.py --repo-root .
env -u UV_DEFAULT_INDEX -u UV_INDEX_URL -u UV_EXTRA_INDEX_URL UV_NO_CONFIG=1 uv lock --check
UV_NO_CONFIG=1 uv sync --locked --dev --check
uv --no-config run --frozen python scripts/check_first_run_smoke.py --repo-root .
git diff --exit-code -- uv.lock pyproject.toml
git diff --check
```

Expected: every command exits 0.

- [ ] **Step 2: Release review by Claude Code**

```bash
claude --effort max --permission-mode plan --no-session-persistence \
  --tools Read,Grep,Glob,LS,Bash \
  -p "Release review for Phase 1 sub-stage 1a. Confirm the full verification gate passed (ask me to run it if needed), the iron-rule review flow was followed (plan reviewed by Claude Code, opencode revision), all review artifacts are clean bodies, and no secrets/cookies/local-state/build artifacts are staged. Output Verdict, Critical, Important, Nits." \
  > docs/reviews/claude-code-stage-211-release-review.md
```

Expected: APPROVE with no Critical/Important.

- [ ] **Step 3: Secret scan + commit**

```bash
git add -A
git diff --cached | rg -n "ghp_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,}|BEGIN (RSA|OPENSSH|PRIVATE) KEY|xox[baprs]-[A-Za-z0-9-]{20,}|sk-[A-Za-z0-9]{20,}" || true
git diff --cached --check
```

Expected: secret scan returns nothing; whitespace check exits 0. Then:

```bash
git commit -m "Phase 1 1a: Claude Code primary reviewer, opencode reviser and fallback"
```

(Do not push unless the user explicitly asks. The user's rule is per-phase; push happens on explicit instruction.)

---

## Self-Review

- **Spec coverage:** The Phase 1 spec Section 8 ("Review protocol docs update") and Section 9 sub-stage 1a are fully covered by Tasks 1–5.
- **Placeholder scan:** No TBD/TODO. Wording suggestions are concrete and labeled "suggested"; the test contracts are the hard verification, so prose variance is acceptable as long as contracts hold.
- **Type/name consistency:** The plan consistently uses `primary reviewer` / `opencode revises the plan` / `fallback` for Claude Code / opencode, and the new guard-test assertions (Task 1) use exactly those tokens (the `revises` token is tightened to the full phrase `opencode revises the plan` per N-1). Task 1 also adds an AGENTS.md `docs/reviews/claude-code-stage-N` guard (I-2). Artifact names referenced (`opencode-stage-N-*`, `claude-code-stage-N-*`, plus the new `opencode-stage-211-*` / `claude-code-stage-211-*` review records) are consistent.
- **Scope:** Docs + one guard test only; no source/schema/deps. Matches the spec's Phase 1 boundary and leaves the social-scraping ban untouched for Phase 2.
- **Iron-rule adherence:** Task 0 (plan → Claude Code → opencode revision), Task 4 (code → Claude Code), Task 5 (release → Claude Code), with opencode fallback documented. Matches iron rule 2.
