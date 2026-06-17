I'll review the two artifacts. Let me read them in parallel.
Let me examine the existing test file and verify the claims about the docs.
Now let me verify the critical claim: whether all six phrases actually exist in all nine listed docs. This determines whether the test passes against existing docs or forces doc changes.
The raw grep is unreliable for multi-word phrases that span newlines (since `_normalized_text` collapses whitespace). Let me re-check using the same normalization the test uses.
I have enough to complete the review. All verifications confirm the test passes against existing docs with no runtime changes.

---

## Stage 71 Plan Review

Controller note after implementation: this review covered the initial
new-constant/new-test draft. The final Stage 71 implementation used the
review feedback to fold the readiness-preflight phrase checks into the existing
adapter docs test with a four-phrase inline tuple, avoiding the duplicate
module-level constant noted below.

### Summary
The spec/plan add a focused, test-only docs drift guard. I verified the test assertions hold against the current docs (with the same whitespace normalization the test uses), so no doc edits are forced. Runtime code is untouched. No connectors/scraping/automation behavior is introduced. The boundary constraints (adapters print-only, no readiness execution, no PATH lookup, readiness listed as optional preflight) are correctly pinned.

**No Critical issues. No Important issues.**

### Minor

1. **Partial overlap with existing coverage** — `tests/test_cli_docs.py:1022` (`test_external_tool_adapter_registry_docs_are_linked_and_bounded`) already asserts `external-tool-adapters` and `print-only` across the same nine docs, and `tests/test_cli_docs.py:1188` (`test_external_tool_readiness_docs_are_linked_and_bounded`) already asserts `external-tool-readiness` across the same doc set. Of the six new phrases, only three (`optional local read-only preflight command`, `does not run readiness`, `PATH lookup`) are genuinely new coverage. Defensible (the test bundles the readiness-preflight *relationship*), but the spec's claim that existing tests "do not specifically pin this readiness-preflight wording" could note the partial overlap honestly.

2. **New constant duplicates an existing one** — `EXTERNAL_TOOL_ADAPTER_READINESS_DISCOVERABILITY_DOCS` (plan step 2) has identical membership to the existing `EXTERNAL_TOOL_READINESS_DOCS` (`tests/test_cli_docs.py:240`) and `EXTERNAL_TOOL_WORKFLOW_DOCS` (`tests/test_cli_docs.py:228`). Reusing one of those would reduce drift surface; a separate named constant is acceptable if intent clarity is preferred.

3. **Plan-review artifacts lack an explicit creation step** — The File Map (`...-plan.md:18-22`) lists four review artifacts, and the commit (`...-plan.md:157`) stages `opencode-stage-71-plan-review-prompt.md` and `opencode-stage-71-plan-review.md`, but Task 1/Task 2 steps only create the two *code-review* files. The plan-review pair is created out-of-band (this review), which is fine — just not documented as a step.

4. **Review-tool invocation vs AGENTS.md** — Plan step `...-plan.md:147` uses `opencode run --model zhipuai-coding-plan/glm-5.2 --variant max`, while `AGENTS.md` documents `claude --effort max --permission-mode plan`. The `opencode-stage-*` naming convention suggests an intentional shift to opencode for stage reviews; flagging only in case AGENTS.md should be reconciled.

### Constraint compliance
- Runtime code unchanged: ✅ (test-only, `tests/test_cli_docs.py`)
- Docs unchanged absent drift: ✅ (verified all 54 assertions pass against current docs)
- Pins concepts not paragraphs: ✅ (stable boundary phrases)
- Adapters print-only / no readiness run / no PATH lookup pinned: ✅
- Readiness as optional preflight pinned: ✅
- No connectors/scraping/automation/APIs/scheduling/etc.: ✅
