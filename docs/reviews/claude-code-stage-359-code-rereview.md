I have the full diff and the key detail from `templates.py` line 269. Here is the complete re-review.

---

## Re-review: Stage 359 Daily Local Heat Signals

### Issue 1 — `local_articles_by_story_id` None crash path → FIXED

`render_index_html` declares the parameter as `dict[str, RowOneLocalArticle] | None = None` (line 267) and immediately normalises it with `local_articles_by_story_id = local_articles_by_story_id or {}` (line 269), matching the existing pattern used for other callers. The `{}` guard fires before `_render_daily_local_heat_signals` is called, so no None can reach `local_articles_by_story_id.get(story_id)` inside `_daily_local_heat_signal_story_rows`.

### Issue 2 — Sort by capped displayed rows instead of total qualifying count → FIXED

`_daily_local_heat_signal_story_rows` now tracks `local_article_count` independently of the displayed `rows` list:

```python
local_article_count += 1                # counts all qualifying
if len(rows) >= DAILY_LOCAL_HEAT_SIGNALS_MAX_STORIES:
    continue                                       # skips display, keeps counting
```

The `_DailyLocalHeatSignalTopic.local_article_count` field stores the full tally, and `_daily_local_heat_signal_topic_sort_key` uses `-topic.local_article_count` as the third sort criterion. The new `test_render_index_html_sorts_daily_local_heat_signals_by_total_local_article_count` test exercises this explicitly (3-article topic beats a 2-article topic even though only 2 rows are displayed for each).

### Issue 3 — Subtype substring issue → PARTIALLY ADDRESSED, residual low risk

`_daily_local_heat_signal_subtype_label` joins the normalised `type` and `label` fields with a space, then does `token in normalized_text`. Two residual risks:

- `"flat"` would match a label like `"flatform"` (different product category). In practice, source_refs are structured payload values, not free text, so accidental matches are unlikely, but not impossible.
- `"heel"` matches `"heeled"`, `"boot"` matches `"bootleg"`, etc. Same low-severity caveat.

No blocking regression. No word-boundary check was added, but this appears to be an accepted trade-off for MVP scope.

**`templates.py:9554–9567`** — residual, low severity.

### Issue 4 — Missing tests for strict heat gate edge cases → FIXED

`_positive_int_value` correctly rejects `bool`, `str`, `float`, `None`, and zero:

```python
def _positive_int_value(value: object) -> int:
    if isinstance(value, int) and not isinstance(value, bool) and value > 0:
        return value
    return 0
```

`test_render_index_html_includes_daily_local_heat_signals` now exercises:
- `positive_heat_delta_sum: True` (`bool`) → rejected (`Bool Heat Platform` absent)
- `positive_heat_delta_sum: "5"` (`str`) → rejected (`String Heat Shoe` absent)
- `positive_heat_delta_sum: 0, max_heat_delta: 0` → rejected (`Zero Heat Shoe` absent)

Minor gap: `float` (e.g., `5.0`) and `None` are not explicitly tested. Both are handled correctly by the implementation (isinstance check excludes non-int types). Not a blocking issue.

### Issue 5 — Mismatched article href mapping linking story A to story B → FIXED

`_daily_local_heat_signal_story_href` adds an explicit stem-match guard after the href is canonicalised:

```python
if page_href.removesuffix(".html") != story_id:
    return None
```

`_safe_daily_local_heat_signals_page_href` already returns the canonical `{safe_story_id}.html`, so the check reliably catches any mapping where `article_hrefs_by_story_id[story_a] = "story_b.html"`. The new `test_render_index_html_rejects_mismatched_daily_local_heat_signal_article_href` test covers this directly and asserts neither the section nor the mismatched href appears in the output.

The corresponding `_local_article_page_hrefs_by_story_id` in `render.py` builds the mapping from `story.id → article_page_href` derived from the same spec tuple, so in the production render path the mapping is always consistent and the guard acts as a belt-and-suspenders check.

---

## No blocking issues.

**Residual risks (both low):**

| # | Location | Risk |
|---|---|---|
| 3 | `templates.py:9554–9567` `_daily_local_heat_signal_subtype_label` | Substring token matching could misclassify an atypical but valid structured ref value (e.g., a `label` of `"flatform"` would match the `"flat"` token). Low probability given structured payload source. |
| 4 | `test_row_one_render.py` | `float` and `None` heat values not covered by explicit tests. Implementation handles them correctly. |
