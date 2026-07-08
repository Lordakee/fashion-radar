## Stage 361 Plan Review

Reviewed against the spec, the live codebase (`templates.py`, `render.py`, `test_row_one_render.py`, `test_workflows.py`), and Stage 356–360 patterns.

---

### Critical

None.

---

### Important

**1. Duplicate `Step 4` in Task 1— agentic worker will attempt to implement both or skip one.**

The plan contains two consecutive `Step 4` headers:

```
- [ ] **Step 4: Write failing placement test**   ← orphan: no body, no instructions
- [ ] **Step 4: Write failing empty-section test**   ← real step with content
...
- [ ] **Step 5: Write failing placement test**   ← real placement step
```

The first Step 4 is a revision artifact — the placement test was originally Step 4, then the empty-section test was inserted as a new Step 4 and the placement test bumped to Step 5, but the original header was left in. Remove the orphaned first `Step 4: Write failing placement test` header so the sequence reads Steps 1 → 2 → 3 → 4 (empty-section) → 5 (placement).

---

### Minor

**2. `href: str` / `paragraph_href: str` dataclass fields conflict with spec's conditional link language.**

The spec says "Links are emitted only when the generated local article page href map contains a safe single-file `.html` href" — implying items can render *without* a link. But both fields are typed `str` (not `str | None`), which forces either empty-string sentinel semantics or the precondition that items are only built when a valid href exists. The capsules pattern uses the latter (item is dropped entirely if `href is None`). The plan doesn't state which applies here. Align the dataclass types (`str | None`) and the item-builder filtering rule so renderers can do a simple truthiness check rather than guessing on empty string.

**3. Reason fallback chain is not individually tested.**

The spec defines a four-level priority: `why_it_matters` → first brief section body → first content-section item body → first saved paragraph. The direct render test only exercises the `why_it_matters` path (story 1 has it populated). A small supplemental assertion — one story with blank `why_it_matters` and a populated brief section, one with both blank and a content section item — would confirm the fallback chain without a new test function. Without this, a regression in the brief-section or content-section fallback is invisible until editorial content happens to exercise it.

**4. `_safe_daily_local_article_reading_brief_page_href` signature is not shown.**

The plan names the function in the helper list (Task 2Step 3) but doesn't show its parameter list. Based on the capsules precedent (`_safe_daily_local_article_capsule_page_href(story_id: str, href: object) -> str | None`) and the requirement to check that the filename stem equals the story ID, the function must accept both arguments. Make this explicit in the helper spec to avoid an implementer producing a single-argument version that skips the stem-to-story-id match.

**5. `DAILY_LOCAL_ARTICLE_READING_BRIEF_MAX_GROUPS` assertion location is unspecified.**

Task 2 Step 3 says to "use `DAILY_LOCAL_ARTICLE_READING_BRIEF_MAX_GROUPS` as a sanity cap/assertion when returning rendered groups" but does not say whether this is a runtime `assert`, a slice `[:MAX_GROUPS]`, or a guard that raises. Given that the lane count is fixed at three (hard-coded fill order), a simple `assert len(groups) <= DAILY_LOCAL_ARTICLE_READING_BRIEF_MAX_GROUPS` before returning is the right form. State it explicitly so the implementer doesn't introduce an unintended silent slice.

---

### Summary

No architectural problems, no contract violations, no conflicts with Stages 356–360. The href-safety rules are consistent with Stage 360's `_safe_daily_local_article_capsule_page_href` and cover all the required cases (traversal, leading dot/slash, whitespace, nested path, stem mismatch). Test coverage for filtering, placement, homepage-only behavior, docs boundary, and workflow guard is complete. The sole Important issue — the duplicate Step 4 header — must be resolved before handing to an agentic worker to avoid double-implementation or a missed step.
