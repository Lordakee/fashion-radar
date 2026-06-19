I'll review the Stage 119 design and plan. Let me read the relevant files in parallel.
Now let me read the prior review findings and check the relevant test helpers in parallel.
Let me verify the critical detail about the `xhigh` assertion and check for any other tests that touch these docs.
I've reviewed the design, plan, three target docs, the current test file, and the Stage 117/118 review history. I also confirmed no other test file (e.g. `test_cli_docs.py`) asserts on the review-gate wording, so there are no cross-file conflicts. Here is my review.

---

# Stage 119 Plan Review Findings

## Summary

The alignment intent is correct and long overdue (this resolves the carried M-3/M-4 flags from Stage 117 and 118). Scope is clean docs/tests-only, Claude Code is preserved as an explicit optional alternate, and most test assertions trace cleanly to the prescribed doc text. **However, one test assertion cannot pass as written**, which blocks the planned RED→GREEN flow.

## Critical
None.

## Important

### I-1 — `xhigh` assertion reads raw text and will fail against the line-wrapped bullet
Plan Task 1 Step 1 (`...plan.md:114`) prescribes:

```python
assert "reasoning effort to `xhigh`" in agents_text
```

where `agents_text = _read(AGENTS)` is the **raw, non-normalized** file text. Task 2 Step 1 (`plan.md:180`) explicitly says to **keep** the Codex `xhigh` bullet, which in `AGENTS.md:19-20` is line-wrapped:

```
- When spawning Codex subagents for this project, set the subagent reasoning
  effort to `xhigh`.
```

Confirmed via `cat -A`: between `reasoning` and `effort` lies `\n  ` (newline + two spaces), so the contiguous substring `"reasoning effort to \`xhigh\`"` is **absent** from the raw text. Task 2 Step 4's "Expected: all review protocol docs tests pass" will therefore fail at this assertion even with perfect doc edits — the test is internally inconsistent with the planned AGENTS.md text.

**Fix (pick one before coding):**
1. Normalize: `assert "reasoning effort to \`xhigh\`" in _normalized_text(agents_text)` (every other assertion in this test already normalizes), or
2. Simplify to a token check that survives wrapping, e.g. `assert "`xhigh`" in agents_text` and `assert "reasoning" in _normalized_text(agents_text)`, or
3. Prescribe unwrapping the AGENTS.md bullet onto a single line in Task 2 Step 1.

## Minor

### M-1 — REVIEW_PROTOCOL section rewrites are under-specified
Task 2 Step 2 gives exact command blocks and naming-list text, but only *directs* ("must say local opencode is active") for the `Before Coding`, `During Development`, and `Before GitHub Upload` sections without exact prose. `test_active_review_docs_document_local_opencode_gate` requires the literal phrase `"local opencode"` in `REVIEW_PROTOCOL.md`. This is trivially achievable (change "Ask local Claude Code" → "Ask local opencode"), but for consistency with the other two steps (which give exact text) and to avoid the Stage 117-I5-style inference burden, consider prescribing the exact replacement sentences.

### M-2 — Optional `claude-code-stage-N-...` naming convention is not test-enforced
The design (`design.md:43-44`) and plan Task 2 Step 2 (`plan.md:237`) call for documenting the optional `docs/reviews/claude-code-stage-N-...` naming convention, but no assertion guards it. The alternate route is only guarded by `OPTIONAL_CLAUDE_CODE_COMMAND` and `"optional alternate"`. Acceptable, but the alternate *naming* could silently drift.

### M-3 — `"historical audit records" not in protocol_text` is a narrow absence check
The test only forbids the exact phrase `"historical audit records"`. A rewrite like "older opencode records are historical only" would pass the test while partially preserving the stale framing. The active-opencode assertions elsewhere compensate, so non-blocking, but the acceptance criterion (`design.md:95-96`) is slightly stronger than the test.

## Review Answers

1. **Active route aligned to opencode `glm-5.2 --variant max`?** Yes — design `§Decision` and plan Tasks 2.1–2.3 consistently make `opencode run --model zhipuai-coding-plan/glm-5.2 --variant max` the active plan/code/release route across all three docs; artifact naming moves to `opencode-stage-N-...`. ✓
2. **Claude Code `--effort max` preserved as optional alternate without contradiction?** Yes — design `design.md:42-44`, plan AGENTS.md fallback block (`plan.md:192-200`), REVIEW_PROTOCOL optional section (`plan.md:228-237`), and checklist sentence (`plan.md:260-262`) all frame it as "only when a stage explicitly requests it." No contradiction with the active route. ✓
3. **Test internally consistent with planned doc text + existing helpers?** **No — see I-1.** All other assertions trace cleanly. Existing helpers (`_read`, `_section`, `ACTIVE_REVIEW_DOCS`, `ROOT`, `AGENTS`, `REVIEW_PROTOCOL`, `UPLOAD_CHECKLIST`) all exist and are reused correctly; only `_normalized_text` is new. No other test file asserts on this content (grep-confirmed), so `test_cli_docs.py` adjacent run is safe.
4. **Docs/tests-only with no runtime/dependency/`uv.lock`/CI/connector/scraping/scheduling/monitoring/source-acquisition/ranking/coverage/compliance behavior?** Yes — Files list (`plan.md:15-28`) and explicit "Do not modify" line are clean; Task 4 adds `git diff --exit-code -- uv.lock pyproject.toml` and `git diff --check`. ✓
5. **Verification commands sufficient?** Yes — focused RED (Task 1.2), focused GREEN (Task 2.4), adjacent docs tests (Task 3.1), opencode code review (Task 3.3), and full release gate (Task 4.1: hygiene, full pytest, ruff check+format, `uv lock --check`, marker scan, lockfile diff, `git diff --check`). ✓

## Final Statement

**There is one Important blocker (I-1) before implementation.** The `xhigh` assertion reads raw `agents_text` and will fail against the line-wrapped bullet the plan tells the implementer to keep, so Task 2 Step 4 cannot go green as written. Resolve I-1 (normalize the assertion, or simplify it, or prescribe unwrapping the bullet) before Task 1. **No Critical blockers.** Once I-1 is fixed, the plan is internally consistent, scope-pure, and correctly aligns the active review route to local opencode while preserving Claude Code as an explicit optional alternate.
