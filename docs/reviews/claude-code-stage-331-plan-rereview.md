## Stage 331 Design & Plan Review

### Critical

No Critical findings.

---

### Important

**1. `no_extractable_text` branch condition won't match whitespace — test will fail**

Plan `articles.py:step-5` adds:
```python
if not result.text:
    return _fallback_story_summary_article(..., reason="no_extractable_text")
```

`_extractor("   ")` (Task 1 Step 4 test helper, `test_row_one_articles.py:74`) produces `ArticleExtractionResult(text="   ", skipped=False)`. In Python `not "   "` is `False`, so this branch is never entered. Execution falls through to `_story_local_article_paragraph_sets`, which produces no paragraphs from whitespace, and hits the `no_publishable_paragraphs` fallback instead.

The test asserts `article.reason == "no_extractable_text"` — it will fail with `"no_publishable_paragraphs"`.

**Fix:** Either change the branch condition to `if not result.text or not result.text.strip():`, or update the test to assert `reason == "no_publishable_paragraphs"` and rename it `test_build_row_one_local_articles_marks_whitespace_text_as_summary_fallback`. The design document says "result text was empty" — the intent is to catch whitespace, so the branch condition fix is the right call.

---

### Verdict

One Important issue: **the `no_extractable_text` branch won't fire for whitespace-only text**, causing a guaranteed test failure in Task 1 Step 4. Fix the condition to `not result.text or not result.text.strip()` before implementing Step 5. Everything else — the model default for backward compatibility, the `_fallback_story_summary_article` signature change and its three call sites, the metrics dataclass extension, the template provenance chip, and the docs sentinel — is correctly specified and aligned with the existing code.
