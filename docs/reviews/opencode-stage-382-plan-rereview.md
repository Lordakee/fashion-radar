**Tracing original findings:**

| Finding | Status in revised plan |
|---|---|
| CC-C1 (consumed-field exclusivity) | Fixed — lines 130-149 add consumed-source set + normalized-text set + return `None` when <2 distinct cards |
| CC-I1 (href helper duplication) | Fixed — lines 64-67, 248-249, 538-541 forbid `_safe_local_article_synthesis_href`, require calling existing helper directly |
| CC-I2 (thesis re-consumes editorial_takeaway) | Fixed — lines 165, 171-173 guard with "only if `lead` did not already consume it" + explicit ban on `editorial_takeaway` brief-section key |
| CC-I3 (sentinel fixture forcing) | Fixed — lines 622-625 clarify patch replaces renderer, "no extra fixture coupling or builder forcing is needed" |
| OC-Important#1 (`editorial_takeaway` key nonexistent) | Fixed — lines 134-137, 155-157, 171-173 remove the key everywhere; only `story.editorial_takeaway` used |
| OC-Important#2 (`why_it_matters` triple duplication) | Fixed — lines 150-163 demote `why_it_matters` to last-resort; acceptance criteria lines 259-262 |

All six original Critical/Important findings are resolved. Now checking whether the C1 fix introduced new issues in the specified focus areas.

---

## Stage 382 Re-Review — Remaining Critical and Important Findings

### Critical

None.

### Important

**R1 — Two-card partial-render dedup rule is incompatible with the all-required-fields data contract (data-model correctness)**

The C1 fix introduced a three-state dedup policy (lines 143-149):

- fewer than two distinct cards → return `None`;
- **two distinct cards derivable → "render the available distinct cards and keep the section"** (lines 146-149);
- three distinct cards → render all.

But the data contract declares all three narrative fields as required, non-optional:

```python
class RowOneLocalArticleSynthesisBrief:
    lead: LocalizedText
    thesis: LocalizedText
    article_adds: LocalizedText      # all three required, no Optional
```

(lines 102-105), and the render layer assumes all three always exist:

- the HTML blueprint hardcodes three `<article class="local-article-synthesis-brief-card">` elements (lines 233-236);
- the cards mapping binds all three labels to all three fields unconditionally (lines 244-246);
- the render rules specify only "omit the entire section if the builder returns `None`" (line 250) — there is **no conditional single-card omission rule**, no "skip empty field" check, and no guidance on how the builder represents a card that has no distinct text after dedup.

Concrete failure path: a sparse local article where `lead` consumes `story.editorial_takeaway`, `thesis` consumes `brief.signal_context`, and every `article_adds` candidate (first content-section body, first item body, first paragraph) was already consumed or is empty. Per the rule the builder must still emit a brief (2 distinct cards ≥ threshold), but `article_adds: LocalizedText` cannot be populated with meaningful text and the renderer has no instruction to omit the third card — yielding either an empty card body under a "What the article adds" heading or an implementer guessing at behavior the plan does not define.

Additionally, Task 2's RED-test list (lines 344-370) has **no named test for the 2-card partial case**, even though line 149 explicitly says "tests should cover this sparse but still useful case." The regression net therefore does not match the documented dedup behavior.

**Fix required before implementation (pick one and specify it):**

1. Make the variable-card-count explicit in the data model — e.g., change `lead`/`thesis`/`article_adds` to `LocalizedText | None`, or replace the three named fields with `cards: tuple[RowOneLocalArticleSynthesisCard, ...]` — and add a render rule that omits any card whose field is `None`/empty; **or**
2. Simplify the dedup policy to "return `None` unless all three cards have distinct meaningful text" (drop the 2-card partial case entirely), keeping the current required-fields data model and 3-card render blueprint; **or**
3. Keep the 2-card case but add an explicit render rule ("omit any card whose field renders empty after `_esc(...)`) and add a named RED test `test_build_local_article_synthesis_brief_renders_two_cards_when_third_is_exhausted` to Task 2.

Any of the three closes the gap; the plan must not leave the builder output shape, the renderer omission logic, and the test all unspecified for the same scenario.

---

All other Critical and Important findings from both the Claude Code and opencode plan reviews have been addressed in the revised plan. The remaining scope areas — duplication prevention (consumed-source + normalized-text dedup), href-safety reuse (direct call to existing helper), render/workflow/docs test boundaries (sentinel test, denylist placement, docs paragraph + stale-phrase checks), and generated-site-only scope (no JSON artifacts, no routes, no schema fields, no collection/scraping/LLM/connector/scheduling) — are clean.

END_OF_REVIEW
