---

**Stage 381Plan Review — Saved Local Article Related-Read Connection Brief**

---

## Critical

**C1 — Broken test assertion: `"1 local reads"` will never match**

`test_render_local_article_page_related_read_connection_brief_uses_only_safe_cards` (Task 4, Step 2) asserts:

```python
assert "1 local reads" in section_html
```

With `card_count=1`, `_count_label(1, "local read", "local reads")` returns `"1 local read"` (singular — see `templates.py:15631`). The assertion tests for the plural form at count1, so it will fail after a correct GREEN implementation and will never pass without either corrupting the singularisation logic or changing the assertion. Fix: change the assertion to `"1 local read"`.

---

## Important

**I1 — `signal_count` and `source_count` are computed asymmetrically; the metrics widget can misrepresent**

The builder computes:
- `signal_count = len(_related_read_connection_signal_reference_keys(clean_cards))` — iterates **all cards, all references, uncapped**; can exceed `MAX_REFS`.
- `source_count = len(source_names)` — where `source_names` is capped at `MAX_REFS`; counts only displayed sources.

The deduplication-and-caps test confirms this: `brief.signal_count ==4` while `len(brief.signal_references) == 3`. The metrics widget would render `"4 signals"` alongside only 3 signal chips, while `"3 sources"` exactly matches the 3 source chips. This is misleading at the product level (the number exceeds what is shown) and inconsistent at the spec level (the prose says `signal_count` is "the count of unique displayed `card.references`" — "displayed" implies the capped set, but the implementation counts beyond the cap). Choose one definition for both counters — total unique or displayed unique — and apply it consistently. If total unique is intended, `source_count` should also be derived independently of `source_names`. If displayed is intended, `signal_count` should use `len(signal_references)`.

**I2 — Task 2 "Add imports" instruction would create a duplicate import block in `test_row_one_saved_article_local_related_reads.py`**

The existing import block at lines 18–25 already contains `SAVED_ARTICLE_LOCAL_RELATED_READS_MAX_CARDS`, `SAVED_ARTICLE_LOCAL_RELATED_READS_MAX_REFS`, `RowOneSavedArticleLocalRelatedReadCard`, `build_row_one_saved_article_local_related_read_lanes`, and `build_row_one_saved_article_local_related_reads`. The plan's Task 2 instruction says "Add imports:" and lists all five of those names again alongside the three new additions (`RowOneSavedArticleLocalRelatedReadEvidenceBridge`, `RowOneSavedArticleLocalRelatedReadConnectionBrief` [once implemented], `build_row_one_saved_article_local_related_read_connection_brief`). A naive "add" produces two `from fashion_radar.row_one.saved_article_local_related_reads import (...)` blocks; ruff will flag it, but it makes the RED description misleading — the step says "FAIL because `build_row_one_saved_article_local_related_read_connection_brief` does not exist," but import duplication would also cause an error. Change the instruction to "Update the existing import block to add: …" listing only the three new names.

---

## Minor

**M1 — `_render_saved_article_local_related_read_connection_metric` produces no trailing newline between concatenated spans**

The four metric calls are concatenated with `+` directly:
```python
metrics = (
    _render_saved_article_local_related_read_connection_metric(...)
    + _render_saved_article_local_related_read_connection_metric(...)
    + ...
)
```
The helper's f-string ends with `</span>"""` and contains no trailing `\n`, so the four `<span>` blocks run together without line breaks. This is inconsistent with the rest of `templates.py`'s indentation style (all other multi-element block helpers separate entries with `\n`). No functional impact, but adjust the helper to append `\n` or add a `"\n".join(...)` call at the call site to stay consistent.

**M2 — CSS insertion point is imprecise**

The plan says "Add after `.saved-article-local-related-read-lane-header p`" (line 2670). The related-read CSS continues after that rule with card, grid, reference, action, and evidence-bridge rules (lines 2674–2732). It is not stated whether the new block should go before or after the evidence-bridge rules. Since the brief renders *before* lanes/cards in the HTML, placing its CSS *before* `.saved-article-local-related-read-card` (line 2674) is more logical. Clarify the intended insertion position.

**M3 — Redundant `.strip()` guard in `_render_saved_article_local_related_read_connection_tags`**

The helper checks `reference.name.strip()` before adding a signal chip, but `build_row_one_saved_article_local_related_read_connection_brief` already guards on `not name` after `normalize_row_one_paragraph(reference.name)`, so a blank name cannot reach `signal_references`. The guard is harmless but adds noise inconsistent with how the existing reference-chip renderer (`_render_saved_article_local_related_read_references`) operates — that one also checks `reference.name.strip()` directly, so it matches the existing pattern. Leave or remove either way, but note the double-guard so the implementer does not treat it as meaningful safety logic.

---

END_OF_REVIEW
