## Verdict

**APPROVE_WITH_NOTES**

The plan is technically sound, correctly scoped, and follows the project's established patterns. No blocking issues were found. One important note on regex compilation placement and a few minor notes are documented below.

---

## Critical Issues

None.

---

## Important Issues

**1. Regex recompilation inside `_local_article_signal_score` — move to caller**

The proposed `_local_article_signal_score` compiles a fresh `re.compile(...)` for each term on every invocation:

```python
def _local_article_signal_score(paragraph: str, terms: list[str]) -> int:
    normalized = paragraph.casefold()
    score = 0
    for term in terms:
        pattern = re.compile(rf"(?<![a-z0-9]){re.escape(term.casefold())}(?![a-z0-9])")
        if pattern.search(normalized):
            score += 1
    return score
```

`_local_article_signal_score` is called once per non-empty paragraph in `_local_article_takeaway_indices`, meaning the same term patterns are recompiled N times per story (once per paragraph). Since `terms` is fixed for a given story, the compiled patterns should be built once in `_local_article_takeaway_indices` and passed into the scoring step. The simplest fix is to inline the scoring loop directly in `_local_article_takeaway_indices` after building the compiled patterns, or to change `_local_article_signal_score` to accept `list[re.Pattern[str]]` instead of `list[str]`. Either approach eliminates redundant compilation without changing external behavior. This is not a correctness bug but is an avoidable inefficiency that a reviewer or linter pass may flag.

**Recommended fix (compile once in the indices helper):**

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
        (index, sum(1 for p in patterns if p.search(paragraphs[index].casefold())))
        for index in non_empty
    ]
    matched = [(index, score) for index, score in scored if score > 0]
    if matched:
        matched.sort(key=lambda item: (-item[1], item[0]))
        return [index for index, _score in matched[:limit]]
    return non_empty[:limit]
```

This keeps `_local_article_signal_score` either as an inline expression or removes it; all unit tests remain unchanged because `_local_article_takeaway_indices` is the externally tested surface.

---

## Minor Notes

**1. Redundant empty-paragraph guard in the updated inner loop**

The updated `_local_article_takeaway_section` loop plan includes:

```python
if not paragraph_en.strip():
    continue
```

`_local_article_takeaway_indices` already filters to `non_empty` indices (paragraphs where `paragraph.strip()` is truthy), so this guard is unreachable under normal flow. It is harmless and defensive, but noting it avoids confusion during code review.

**2. `_local_article_signal_terms` normalizes names before length check**

The helper calls `normalize_row_one_paragraph(ref.name)` before applying `len(term) < 3`. This is correct and consistent with `_local_article_paragraph_indices` at line 249. No action required — just confirming the ordering is intentional.

**3. Section `body` text unchanged**

`_local_article_takeaway_section` currently emits `body=LocalizedText(en="The saved source text points to these immediate reads.",...)`. The plan leaves this unchanged, which is correct for scope. If the body description is ever updated to mention signal-paragraph prioritization, it should go in a future stage rather than here.

**4. `_extractor` helper placement in tests**

The plan places `_extractor` near `_source`. Both are module-level test helpers in `test_row_one_articles.py`. The existing test file defines helpers (`_edition`, `_source`, `_assert_local_article_brief_sections`, `_content_section`, `_content_item`) as module-level functions before the test functions. Placing `_extractor` in that same cluster is correct and consistent.

**5. Task3 local intelligence test constructs the article directly**

`test_build_row_one_local_article_intelligence_uses_curated_first_takeaway` constructs a `RowOneLocalArticle` with pre-built `content_sections` rather than running `build_row_one_local_articles`. The plan correctly notes this test "may pass before Task 2 implementation." Its purpose — locking the local intelligence consumption contract — is sound. The test is correctly scoped as a contract-lock rather than an end-to-end builder test.

**6. `tags` in Task 1, Step 1 test setup**

The signal-dense test sets `story.tags = ["quiet luxury"]` but tags are explicitly excluded from `_local_article_signal_terms`. This is not a bug — it is present in the test to confirm tags do not pollute signal selection. A brief inline comment in the test body would make this intent explicit, though it is not required.

---

REVIEW_COMPLETE
