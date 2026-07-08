Here is the review of the Stage 359 design and plan.

---

## Stage 359 Daily Local Heat Signals — Plan Review

### 1. Product fit

Fit is good. The section directly answers the user's question: "among today's locally saved fashion stories, which brands and products have heat right now, and where can I read the coverage?" `positive_heat_delta_sum` and `max_heat_delta` capture the current-edition rise signal. Local article gating ensures every link has real text behind it. Bag and shoe subtype badges from `source_refs` cover the newly-hot-product use case explicitly. The six-topic / two-story-per-topic cap keeps the section compact and scannable.

### 2. Reuse of `briefing_topics` — duplication and conflict

No duplication and no conflict.

- `briefing_topics_payload(...)` is already called in `render_row_one_site` and its result is already placed into `app_payload["daily_digest"]["briefing_topics"]`. Stage 359 reads from that in-memory dict — it does not call `briefing_topics_payload` a second time or re-aggregate topics.
- Daily Edit and Signal Synthesis render editorial narrative, not heat-ranked topic lists. No overlap.
- Stage 357 Daily Local Key Signals Digest works from a typed `RowOneDailyLocalKeySignalsDigest` model and renders grouped key-signal entries. It does not consume `positive_heat_delta_sum` or `max_heat_delta`.
- Stage 358 Daily Local Signal Momentum works from a typed `RowOneSavedArticleDailySignalLeaderboard` model and renders concentration counts (`article_count`, `source_count`). It does not consume heat delta fields.

The heat delta fields are surfaced nowhere else on the homepage. Stage 359 is strictly additive.

### 3. Homepage placement

Technically sound. The template body at lines 362–364 of `templates.py` currently reads:

```python
{daily_local_key_signals_digest_section}
{daily_local_signal_momentum_section}
{saved_article_content_organization_section}
```

Inserting `{daily_local_heat_signals_section}` between momentum and organization is a one-line template edit plus the corresponding new variable computed earlier in `render_index_html`. This matches the exact pattern used for every prior section insertion. The placement test's `html.index(...)` ordering assertions are the right verification.

### 4. Local article gating

The triple gate is sufficient:

1. Story ID is a string that passes `safe_local_article_story_id(...)`.
2. Story ID exists in `local_articles_by_story_id` with `_usable_local_article_paragraph_count > 0`.
3. Story ID exists in the generated-page href map.

This matches how other sections prevent dead links. Topics whose story IDs all fail the gate return an empty string for the whole topic, and the outer renderer returns an empty string when no topics survive — consistent with every other conditional section in `render_index_html`.

### 5. Href safety validation

The validation logic described in the plan ("validate each mapping value is a single safe local article page filename") is underspecified for an implementer. The existing `_safe_daily_local_signal_momentum_page_href` at line 9055 of `templates.py` already does exactly this: PurePosixPath single-part check, no leading `.`/`/`/`//`, no spaces, `.html` suffix required, `safe_local_article_story_id` on the stem. **The plan should name this function explicitly as the pattern to mirror** for `_daily_local_heat_signal_story_href`. Either extract a shared private helper (e.g. `_safe_local_article_page_href_filename`) or replicate the same exact logic. Leaving it as prose risks the implementer writing a weaker check.

### 6. Contract and scope discipline

Clean. The non-goals list covers every prohibited category. The docs denylist is comprehensive and appropriately avoids banning the bare word `heat` since prior stages legitimately mention heat deltas and heat scores. The `_local_article_page_hrefs_by_story_id` helper in render.py is a pure dict extraction from an already-computed sequence — no new computation, no file I/O, no new data path. Workflow guards cover all naming variants (snake_case, kebab-case, both casing directions). This is airtight.

### 7. Escaping and tests

The test fixture covers the right attack surface: `<script>` and `<b>` in topic titles, `<Business>` in source names, a traversal `"../unsafe"` story ID, a missing-local story ID, a zero-heat product topic, and a positive-heat designer topic that should be excluded in this MVP. The assertions verify raw tags do not appear and the escaped text does. One small gap: the plan's rules say the renderer reads raw dicts from `app_payload`. The implementation **must use `.get()` at every dict level** (`app_payload.get("daily_digest", {}).get("briefing_topics", [])`) rather than direct indexing — the test fixture always provides a well-formed payload, so a direct-indexing bug would pass tests but crash on a missing key in production. This should be stated explicitly in Step 2 of Task 2.

### 8. Concrete corrections before implementation

**Correction 1 — Name the href-safety pattern (Task 2, Step 2):**  
Change the rule "validate each mapping value is a single safe local article page filename" to: "validate each mapping value using the same PurePosixPath logic as `_safe_daily_local_signal_momentum_page_href`." Either extract a shared helper or copy the exact logic (single-part path, no whitespace, no leading `.`/`/`/`//`, `.html` suffix, `safe_local_article_story_id` on the stem). This prevents a weaker reimplementation.

**Correction 2 — Defensive dict access (Task 2, Step 2):**  
Add an explicit rule: access `briefing_topics` with `(app_payload or {}).get("daily_digest", {}).get("briefing_topics", [])`. Direct indexing would raise `KeyError` or `TypeError` when `app_payload` is `None` or `daily_digest` is absent. All other raw-dict readers in `templates.py` use `.get()`.

**Minor note — `_positive_int` helper (Task 2, Step 2):**  
The plan lists `_positive_int(...)` as a helper to add but does not specify its contract. Clarify: it should return `True` for `isinstance(v, int) and v > 0` and `False` for floats, strings, `None`, or zero. This matters because `briefing_topics` values come from an untyped dict and a float `5.0` should not pass the heat gate.

No other corrections are needed. The architecture, ordering logic, scope boundary, test coverage structure, and workflow guards are all sound.
