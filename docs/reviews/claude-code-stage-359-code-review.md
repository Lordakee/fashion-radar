Here is the full review of the Stage 359 diff.

---

## HIGH

### templates.py — `local_articles_by_story_id=None` crash path

`render_index_html` declares `local_articles_by_story_id: dict[str, RowOneLocalArticle] | None = None`. `_render_daily_local_heat_signals` is typed with the non-optional `Mapping[str, RowOneLocalArticle]` but receives whatever the caller passed. Inside `_daily_local_heat_signal_story_rows`, the first thing the loop does is:

```python
article = local_articles_by_story_id.get(story_id)   # AttributeError if None
```

The `article_hrefs_by_story_id is None` guard in `_daily_local_heat_signal_story_href` comes *after* this line. Any caller that passes a qualifying `app_payload` (brand/product topic with positive heat and at least one story_id) but omits `local_articles_by_story_id` will get an `AttributeError` at runtime. The existing `test_render_row_one_site_omits_daily_edit_without_usable_payload` only exercises `app_payload={}`, so no briefing_topics are present and the crash path is never reached by the current test suite.

Fix: add `local_articles_by_story_id = local_articles_by_story_id or {}` at the top of `_daily_local_heat_signals` (or `_daily_local_heat_signal_topics`), matching how `article_hrefs_by_story_id` is already treated as optional.

---

## MEDIUM

### templates.py — sort key uses post-cap story count, not qualifying article count

`_daily_local_heat_signal_topic_sort_key` sorts by `-len(topic.stories)`. By the time sort runs, stories have already been capped to `DAILY_LOCAL_HEAT_SIGNALS_MAX_STORIES = 2`, so topics with 3+ qualifying articles and topics with exactly 2 are indistinguishable on this key. The spec says "local article count desc", which most naturally means the total number of qualifying articles for the topic. Both topics fall through to `evidence_count`, which may not be the intended tiebreaker. This only affects ordering when there are ties in the two heat fields and at least one topic originally had more than two qualifying articles.

### templates.py:567-575 — subtype badge `"flat"` is a substring of `"platform"`

`_daily_local_heat_signal_subtype_label` uses `token in normalized_text` substring matching. The token `"flat"` would match a source_ref with `type="platform"` or `label="platform shoe"`, returning the "Flat" badge incorrectly. Similarly `"heel"` matches `"stiletto-heel"` (intended), but also any label that happens to contain the substring. The risk is bounded because only `source_refs` type/label fields are scanned (controlled vocabulary in practice), but a defensive `re.search(r'\bflat\b', ...)` word-boundary check would be safer for the problematic tokens (`flat`, `heel`, `bag`).

---

## LOW

### tests/test_row_one_render.py — heat gate edge cases not covered

The spec calls out that bool, float, string, zero, and None "must not count" for the heat gate. `_positive_int_value` handles all of these correctly, but no test verifies that `positive_heat_delta_sum: True` (bool, which is an int subclass and equals 1), `positive_heat_delta_sum: 1.0` (float), or `positive_heat_delta_sum: "5"` (string) are all rejected. Given the gate's explicit emphasis in the spec, targeted parametrized tests for `_positive_int_value` or inline topic variants would close this gap.

### tests/test_row_one_render.py — `test_render_row_one_site_writes_daily_local_heat_signals_homepage_only` asserts "Margaux bag" in section but `source_refs
