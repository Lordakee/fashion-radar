Here is the Stage 331 review.

---

## Stage 331 Code Review

### No Critical findings.

---

### Important

**I-1. Missing test: skipped article does not render a detail-page local-article section**
`src/fashion_radar/row_one/templates.py:5454–5459` — the suppression of a skipped article from the detail page relies entirely on the `if not paragraphs: return ""` guard inside `_render_local_article`. That guard is correct and works, but it is exercised only via articles that have paragraphs. No test passes a `RowOneLocalArticle` with `body_source="skipped"` / `paragraphs=[]` to `render_row_one_site` and asserts that no `id="local-article"` section appears in the output HTML. Given the `skipped` path is new in Stage 331, this gap should be covered.

Suggested test skeleton:
```python
def test_render_row_one_detail_suppresses_skipped_local_article(tmp_path) -> None:
    skipped =RowOneLocalArticle(
        story_id="the-row-signal-1234567890",
        url="https://example.com/the-row",
        source_name="Vogue Business",
        extracted_at=AS_OF,
        body_source="skipped",
        skipped=True,
        reason="no_publishable_paragraphs",
    )
    render_row_one_site(
        _edition(), tmp_path,
        local_articles_by_story_id={skipped.story_id: skipped},
    )
    detail_html = (tmp_path / "details" / "the-row-signal-1234567890.html").read_text("utf-8")
    assert 'id="local-article"' not in detail_html
```

**I-2. `uv.lock` is unrelated to Stage 331 and should be excluded**
The entire diff is a mirror-registry swap: every public PyPI registry/artifact
URL changed to a non-public mirror URL. Package versions, hashes, and sizes are
identical throughout — no dependency version change. This is a
development-environment mirror preference unrelated to the provenance feature,
and silently redirecting all future installs to that mirror would be unexpected
to other contributors. Exclude `uv.lock` from the Stage 331 commit and handle it
separately if needed.

---

### Minor

**M-1. `article_count` includes skipped sidecars — "Saved local articles" label is slightly misleading**
`src/fashion_radar/row_one/site_metrics.py:46–47` — `article_count` is incremented unconditionally for all articles, including `skipped` ones with `paragraphs=[]`. The CLI output at `cli.py:2258` reads `"Saved local articles: {payload['article_count']}"`, which now counts articles that were saved as diagnostics with no body text. This is defensible (the sidecar file is saved to disk), but it can confuse an operator seeing `article_count=10`, `skipped_article_count=3` and expecting `paragraph_count` to reflect all10. Consider whether `article_count` should be `extracted + summary_fallback` only (publishable articles), or whether the label should be clarified to "Saved article sidecars." Either is a fine editorial call; it just needs to be decided intentionally.

**M-2. `_local_article_body_source_label` has an unreachable "Skipped" branch**
`src/fashion_radar/row_one/templates.py:5560–5565`:
```python
def _local_article_body_source_label(article: RowOneLocalArticle) -> str:
    if article.body_source == "summary_fallback":
        return "ROW ONE summary fallback"
    if article.body_source == "skipped" or article.skipped:
        return "Skipped"
    return "Extracted article text"
```
A skipped article always has `paragraphs=[]`, so `_render_local_article` returns `""` before calling `_render_local_article_provenance`, making the `"Skipped"` branch dead code in practice. It is not wrong — it is defensive — but it is worth a comment noting that skipped articles never reach the provenance renderer due to the paragraph guard.

**M-3. No render test for `body_source="extracted"` provenance label**
`tests/test_row_one_render.py:1213` tests `summary_fallback` + reason rendering explicitly. There is no corresponding assertion that `body_source="extracted"` produces `"Extracted article text"` in the provenance chip. The existing provenance test at line 966 checks structural elements but not this specific label. Low regression risk since the code path is trivial, but a one-line assertion in the existing test would close the gap.

**M-4. Review and plan/spec docs (`docs/reviews/claude-code-stage-331-*`, `docs/superpowers/...`) are untracked and not referenced by tests**
These working documents appear to be the review and planning artifacts from the stage design process. They are untracked (`??`) and no test asserts anything about their content. Whether to commit them is a workflow decision, not a correctness concern. They look internally consistent with the implementation. If the project convention is to commit boundary-design docs alongside the implementation (as done for Stage 327–328), these are suitable to commit. If they are scratch artifacts, they can be omitted.

---

### Summary

The core provenance mechanics — model field, builder classification, fallback/skipped dispatch, metrics counting, CLI echo, and detail-page chip rendering — are correct and internally consistent. Backward compatibility (`body_source` defaulting to `"extracted"` for old sidecars) is properly handled and tested. The skipped-sidecar flow is technically consistent with the renderer (suppressed via paragraph guard) and metrics (counted separately). The two action items are: add a test for skipped article suppression in the detail page (Important), and exclude `uv.lock` from this commit (Important).
