All five verification targets confirmed clean against the current source.

---

**I1 — Singular lead (the only Important finding from the prior review)**

`saved_article_local_related_reads.py:165`:
```python
local_read_count = f"{card_count} local {'read' if card_count == 1 else 'reads'}"
```
Both `lead` branches (`signal_references` and context) interpolate `local_read_count`, so `card_count=1` yields `"1 local read"` in both. The builder test `test_saved_article_local_related_read_connection_brief_uses_context_lead_without_signals` (line 841-845) now asserts the corrected singular form and the correct Chinese form (`"1 篇本地阅读"`). **Fixed. ✓**

---

**Evidence bridge count reflects only rendered bridges**

`templates.py:9525-9544`: `_saved_article_local_related_read_connection_brief_cards` re-wraps each renderable card, stripping any bridge whose `current_href` fails `_safe_saved_article_local_related_read_current_href` or whose `candidate_href` fails `_safe_saved_article_local_related_read_href`. The builder then sums `len(card.evidence_bridges)` on these filtered cards, so the count matches only bridges that would render. The render test `test_render_local_article_page_includes_related_read_connection_brief_before_lanes` asserts `"1 bridge"` in the brief HTML for the safe-bridge setup (line 3899). **Correct. ✓**

---

**Metric values have English and Chinese variants**

`templates.py:9554-9585`: each `_render_saved_article_local_related_read_connection_metric` call receives a `LocalizedText` with both `en` (`_count_label(...)`) and `zh` (e.g. `f"{brief.card_count} 篇本地阅读"`, `f"{brief.source_count} 个来源"`, `f"{brief.signal_count} 个信号"`, `f"{brief.evidence_bridge_count} 条证据连接"`). The render test asserts `"2 个来源"`, `"1 个信号"`, `"1 条证据连接"` in `metrics_html` at lines 3900-3902. **Correct and tested. ✓**

---

**reference.name and reference.label escaping inside the brief markup**

`templates.py:9633-9638`: `_esc(reference.name)` and `_esc(reference.label)` both called inside `_render_saved_article_local_related_read_connection_tags`. The escape test (`test_row_one_render.py:3990-3992`) explicitly asserts `"Brand &lt;script&gt;alert(&quot;label&quot;)&lt;/script&gt;" in brief_html`, confirming `reference.label` is escaped within the brief chip markup. **Correct and tested. ✓**

---

**Workflow sentinel**

`test_workflows.py:1696-1786`:
- Monkeypatches `_render_saved_article_local_related_read_connection_brief` with `raising=True` into a recording wrapper that calls through to the original.
- Also monkeypatches `build_row_one_saved_article_local_related_reads` to inject a real `RowOneSavedArticleLocalRelatedReads` with one safe card into every article page, ensuring the renderer is exercised.
- Asserts `calls` is non-empty (renderer was invoked).
- Asserts the brief selector appears in at least one `articles/*.html` (excluding `articles/index.html`).
- Asserts brief selector absent from `index.html`, all `details/*.html`, and all `data/articles/*.json` cached payloads.

**Correct and fully exercised. ✓**

---

No remaining Critical or Important findings.

END_OF_REVIEW
