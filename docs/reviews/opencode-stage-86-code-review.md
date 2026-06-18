I'll review the Stage 86 implementation. Let me start by reading all the relevant files.
Now let me read the implementation files to verify they match the plan.
Let me verify the helper functions to ensure the test is correctly scoped.
Let me read the helper functions and check the prior commit to understand the context.
Let me check a couple more things — duplicate test names, and verify the docs sections actually contain the expected structure.
I have everything needed for the review. Let me verify the test would not pass from unrelated text by checking what else might contain the key phrases.
I now have everything needed for the review.

---

# Stage 86 Code Review Findings

## Severity-Ordered Findings

### Critical
None.

### Important
None.

### Minor / Info (optional, non-blocking)
None worth flagging. The implementation even adopts the canonical Stage 85 phrase "advisory local provenance label guidance" (addressing the plan-review M1 note), so cross-doc wording is consistent.

---

## Review Question Answers

**1. Does the implementation match the Stage 86 plan and scope?**
Yes. Working tree (`git status`) touches only the allowed files: `README.md`, `docs/cli-reference.md`, `tests/test_cli_docs.py`, plus Stage 86 spec/plan/review artifacts under `docs/superpowers/` and `docs/reviews/`. No changes to `src/`, schemas, lint/import behavior, adapter/template/workflow/readiness behavior, dependency manifests, `uv.lock`, CI workflows, `AGENTS.md`, or `docs/REVIEW_PROTOCOL.md`. Prose matches `plan.md:94-99` and `114-119` verbatim, and the new test matches `plan.md:46-70` verbatim, placed immediately after `test_external_tool_adapter_registry_docs_are_linked_and_bounded` at `tests/test_cli_docs.py:1539` as required by Task 2. Table headers and row values are unchanged (the adjacent registry test still passes).

**2. Does the wording preserve the advisory-only meaning of `suggested_platform_labels`?**
Yes. Both insertions (`README.md:147-150`, `docs/cli-reference.md:129-133`) say the column "reflects `suggested_platform_labels` as advisory local provenance label guidance for the optional handoff `platform` field", reinforce with "local provenance suggestions only", and close with the full negation set: "not a schema enum, not a linter restriction, not platform coverage, and not demand proof". This is harmonized with the Stage 85 canonical sentence locked at `tests/test_cli_docs.py:1245-1255`, and consistent with `tests/test_external_tool_contract_parity.py` (which only asserts membership of the label in the advisory list, not enforcement). No schema/coverage/demand-proof implication.

**3. Is the docs drift test scoped tightly enough and unlikely to pass from unrelated text?**
Yes. `_markdown_section(text, "## What It Does Not Do")` captures README lines 85–222 (terminates at `\n## Quickstart` per `tests/test_cli_docs.py:392`), and `_markdown_section(text, "## Local Import And Community Handoff")` captures cli-reference lines 80–243. I verified via `rg`:
- `"platform label column"` and `"advisory local provenance label guidance"` appear **nowhere else** in either doc — zero false-positive risk for those terms.
- The boundary negations (`not a schema enum`, `not a linter restriction`, `not demand proof`) appear only in the new prose within the captured sections. `"not platform coverage"` does occur at `README.md:488,497`, but those lines are **outside** `## What It Does Not Do` (which ends before `## Quickstart` at line 223), and the test requires all 8 terms conjunctively (including the unique phrases above), so the test cannot pass from unrelated text. The `"known adapter ids:"` sentinel additionally anchors each section to the adapter table neighborhood.

**4. Are there any Critical or Important issues that must be fixed before final verification, commit, and push?**
No. There are no Critical or Important blockers. Targeted verification was reproduced during this review: `test_external_tool_adapter_platform_label_docs_are_advisory` and the adjacent `test_external_tool_adapter_registry_docs_are_linked_and_bounded` both pass (2 passed in 1.52s). Test name is unique (`rg` returns a single definition). CLI reference indentation (2 spaces) correctly continues the `external-tool-adapters` bullet item without breaking the list.

**Recommendation:** Proceed to Task 6 full verification, commit, and push.
