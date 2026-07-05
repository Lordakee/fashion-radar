# Verdict

**APPROVE_WITH_NOTES**

The Stage 306 plan is correctly scoped, deterministic, contract-preserving, and adheres to project boundaries. After applying the one Important revision below, the plan is ready for implementation. No Critical issues. No forbidden scope introduced.

# Critical Issues

None.

# Important Issues

**1. Endorse Claude Code's regex recompilation finding — revise Task 2 Step 2/3 before implementation**

Claude Code's Important note is correct and worth adopting. The proposed `_local_article_signal_score` calls `re.compile(...)` once per term per paragraph, so for a story with `T` signal terms and `P` non-empty paragraphs the same `T` patterns are compiled `P` times (i.e. `T * P` compilations per story, multiplied across every story in every edition).

Adopt Claude Code's recommended restructuring: build the compiled `re.Pattern[str]` list once inside `_local_article_takeaway_indices`, then score inline:

```python
def _local_article_takeaway_indices(
    story: RowOneStory,
    paragraphs: list[str],
    *,
    limit: int = 3,
) -> list[int]:
    non_empty = [index for index, paragraph in enumerate(paragraphs) if paragraph.strip()]
    terms = _local_article_signal_terms(story)
    patterns = [
        re.compile(rf"(?<![a-z0-9]){re.escape(term.casefold())}(?![a-z0-9])")
        for term in terms
    ]
    scored = [
        (index, sum(1 for pattern in patterns if pattern.search(paragraphs[index].casefold())))
        for index in non_empty
    ]
    matched = [(index, score) for index, score in scored if score > 0]
    if matched:
        matched.sort(key=lambda item: (-item[1], item[0]))
        return [index for index, _score in matched[:limit]]
    return non_empty[:limit]
```

This keeps the externally tested surface (`_local_article_takeaway_indices`) and all five Task 1 tests unchanged, and removes the separate `_local_article_signal_score` helper. The plan's File Map and Step 2 should be revised accordingly (drop the standalone score helper, fold scoring into the indices helper).

# Minor Notes

**1. Boundary regex interacts with non-ASCII reference names**

The pattern `(?<![a-z0-9])...(?![a-z0-9])` only guards against ASCII alphanumerics. For Latin-script names it correctly rejects `Row` inside `brown`, but for any future CJK reference names of length ≥ 3 the boundary check is effectively a no-op because CJK characters are not in `[a-z0-9]`. This is acceptable for v0.1.0 (the `len(term) < 3` filter still blocks 1–2 character CJK names and the fallback remains intact) and is consistent with the existing substring-based `_local_article_paragraph_indices`. No action required; flag for awareness only.

**2. Substring-overlap score inflation is deterministic but worth noting**

If `entity_refs` contains both a short name and a longer name that contains it on a word boundary (e.g. `Row` and `The Row`), a paragraph mentioning `The Row` scores +2 while a paragraph mentioning only `Zendaya` scores +1. The Task 1 near-miss test correctly fixes the `Row`/`The Row` case at assertion level, so behavior is locked. The plan's deterministic `(-score, original_index)` tiebreak keeps ordering stable. No change needed.

**3. Redundant `if not paragraph_en.strip(): continue` in the updated `_local_article_takeaway_section` loop**

Endorse Claude Code's Minor Note 1: `_local_article_takeaway_indices` already returns only non-empty indices, so this guard is unreachable. Harmless and defensive; safe to keep or drop. No action required.

**4. Task 3 test correctly scoped as a contract lock**

`test_build_row_one_local_article_intelligence_uses_curated_first_takeaway` constructs `RowOneLocalArticle` directly with pre-built `content_sections` rather than driving `build_row_one_local_articles`. This is the right design: it locks the Daily Local Intelligence consumption contract independently of builder internals and is consistent with the existing `test_build_row_one_local_article_intelligence_preserves_article_content_segments` pattern at test_row_one_local_intelligence.py:234. The plan correctly flags it as expected to pass before Task 2 lands.

**5. Existing content-section test assertion update is arithmetically correct**

I traced the Task 2 Step 6 assertion update for `test_build_row_one_local_articles_adds_content_sections_from_story_refs_and_paragraphs`. With `entity_refs=[The Row, Zendaya]`, `product_refs=[Margaux]`, `designer_refs=[Mary-Kate Olsen]`:
- Para 0 ("...The Row demand.") → score 1
- Para 1 ("...Zendaya...Margaux...") → score 2
- Para 2 ("...Mary-Kate Olsen...") → score 1

`(-score, index)` sort yields `[1, 0, 2]`, matching the plan's expected `[[1], [0], [2]]`. The five new Task 1 tests' expected indices also check out against the proposed algorithm.

**6. Review artifact inventory at Task 5 Step 5**

The commit list references `docs/reviews/opencode-stage-306-plan-review-prompt.md` and `docs/reviews/opencode-stage-306-plan-review.md` but no task step explicitly creates the prompt file. This is consistent with prior stages (the prompt is the input that triggers this review), but the implementer should ensure both files exist on disk before `git add` runs, otherwise the commit will fail. No plan revision required — operational note only.

**7. Scope boundary compliance confirmed**

The plan touches only `src/fashion_radar/row_one/articles.py`, the three named test files, `README.md`, `docs/row-one.md`, and review artifacts. No template/CSS redesign, no `row-one-app/v7`, no `data/edition.json`, no schema, no model, no source acquisition, no scraping, no social connectors, no scheduler, no monitoring, no image generation, no dependencies, no platform coverage verification, no demand proof, and no compliance-review product features. Section key remains `takeaways`; app/data contracts remain stable; original paragraph indices are preserved; bilingual alignment and first-three fallback are retained.
