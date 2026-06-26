# Stage 208 Plan Review

**Overall:** The stage is useful, correctly scoped to linter-message explainability, and preserves `EntityPackFinding` / matcher behavior. The architecture (deterministic display-term lookup keyed on the same `sorted(context_keys)` loop as Stage 207) is sound. I verified the `context_keys` set is unchanged by the helper refactor and that the watchlist pack does not emit this finding (so docs parity is safe). **There are no Critical findings, but there is one Important finding that will block literal execution.**

## Critical
None.

## Important

**I-1. The "from" message snippet in Task 2 Step 3 does not match the actual current code (execution blocker).**

The plan (lines 233–237) instructs the implementer to change the message FROM:
```python
message=(
    f"Context term is contained in gated alias '{alias.value}'; "
    "choose surrounding context terms that the alias text does not satisfy "
    "by itself."
),
```
But the **actual** current code at `src/fashion_radar/entity_packs.py:498-502` is:
```python
message=(
    "Context term is contained in a gated alias; choose "
    "surrounding context terms so the alias text alone "
    "does not satisfy the gate."
),
```
A literal `edit`-tool replacement will fail with "oldString not found." The same mismatch propagates to the "Example current warning shape" (plan lines 22–25), which shows the alias already present in the current message — **the current message contains no alias text** (the alias lives only in the structured `finding.alias` field).

Fix the plan's "current" example and "from" snippet to quote the real baseline text. This also clarifies a secondary point the plan's prose glosses over: the new message **newly introduces the alias into the message body** (not just the context term), since `assert "'Mary Jane shoes'" in finding.message` only passes once the alias is rendered into the string. That is consistent with the tests, but the Scope section (lines 5, 42–43) should acknowledge the alias is added to the message too, not only the context term named.

## Minor

**M-1. Missing docs-parity guard that Stage 207 carried.** Stage 207's plan included an explicit note: regenerate the table/JSON samples if watchlist lint output changes. Stage 208 omits this. I verified the watchlist pack does **not** emit `contained_context_term_for_gated_alias` (its `findings[0]` is `context_terms_no_effect`), so the message change cannot affect `tests/test_entity_pack_quality_docs.py`. The risk is therefore nil in practice, but a one-line guard note matching Stage 207's wording would make the plan self-documenting. (Task 3 Step 3 does run the docs test, so any regression would be caught early regardless.)

**M-2. `message` is a sort key.** `_sort_findings` (`entity_packs.py:695`) includes `finding.message` in its tuple. Changing the message content can alter relative ordering of equally-(severity, code, entity, alias, field)-keyed findings. Sorting stays fully deterministic, so this is not a correctness issue, but worth a mention for awareness.

## Answers to the review questions

1. **Useful / correctly scoped?** Yes — pure linter-message explainability, no matcher/schema change.
2. **Preserving `EntityPackFinding` + changing only `message` avoids API contract change?** Yes. No fields are added; `message` is free-text. (See M-2 re: sort tie-breaking only.)
3. **Deterministic selection by sorted normalized context key appropriate/consistent with Stage 207?** Yes — it reuses the exact `sorted(context_keys)` loop and the first-match `break`; verified the produced `context_keys` set is identical to the current set comprehension.
4. **First configured display term per key reasonable?** Yes — human-readable and deterministic; duplicate normalized keys are already flagged separately by `duplicate_context_term`.
5. **Tests sufficient?** Yes — single-token (Task 1 Step 1), multi-token (Step 2), and multi-contained-term deterministic selection (Step 3) are all covered. The deterministic test correctly asserts `mary jane` wins over `shoes` via sorted-first and that `'shoes'` does not appear.
6. **Avoids matcher/schema/config/source/dependency/social/scraping changes?** Yes — verified the helper preserves the key set; only the message string changes.
7. **Docs/changelog/review/release gates sufficient?** Yes — plan/code/release OpenCode review gates, full pytest+ruff+lock+smoke verification, and secret-scan before push are all present.

**Recommendation:** Fix I-1 (correct the baseline message text in the "current" example and the Task 2 Step 3 "from" snippet, and acknowledge the alias is newly added to the message body) before starting Task 1. Optionally address M-1 for parity with Stage 207's plan hygiene.
