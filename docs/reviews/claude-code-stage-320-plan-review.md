Good — the existing workflow test already asserts contract versions at lines 393–395, so version-stability coverage is pre-existing. Here is the full review.

---

## Stage 320Plan and Spec Review

### Verdict

**No Critical or Important issues.** Four minor notes follow.

---

### Is this a reasonable next node after Stage 319?

Yes. Stage 319 brought a Signal Briefing panel to individual detail pages. Stage 320 applies the same editorial-synthesis idea to the homepage. The progression is coherent and the scope is deliberately narrower (read-only, HTML-only, no new data contracts).

---

### Homepage placement

Correct and non-disruptive. The plan inserts `{daily_edit}` between `{signal_synthesis}` and `{daily_local_intelligence}` in the f-string body of `render_index_html()`. The current template order is `edition_brief → signal_synthesis → daily_local_intelligence → saved_* → lead_story → briefing_*`, so the insertion lands at position 4 in the spec's target sequence without displacing any existing section.

---

### App contract / source-acquisition layer

The plan stays cleanly within the `app_payload` dict that is already passed into `render_index_html()`. It adds one private call (`_render_daily_edit(app_payload)`) and a set of private helper functions in `templates.py`. No new function parameters, no new JSON artifacts, no new schemas, no new collection or LLM calls.

---

### Test sufficiency

| Coverage area | Where tested | Verdict |
|---|---|---|
| Section present on populated page | Task 1 Step 1 | ✓ |
| Bilingual titles | Task 1 Step 1 | ✓ |
| Ordering (after brief/synthesis, before lead) | Task 1 Step 1 | ✓ |
| Omission when payload empty / None | Task 1 Step 2 | ✓ |
| HTML escaping | Task 1 Step 3 | ✓ |
| `javascript:` and external URL rejection | Task 1 Step 3 | ✓ |
| Safe fallback href | Task 1 Step 3 | ✓ |
| Signals → briefing_topics fallback | Task 1 Step 4 | ✓ |
| Read Next from digest blocks | Task 1 Step 4 | ✓ |
| CSS selectors + mobile collapse | Task 1 Step 5 | ✓ |
| HTML present in workflow output | Task 3 Step 1 | ✓ |
| `daily_edit` / `daily_information_layer` absent from contract JSON | Task 3 Step 1 | ✓ |
| Contract versions unchanged | Pre-existing at workflow test lines 393–395 | ✓ (pre-existing) |
| Docs boundary phrases | Task 3 Step 3 | ✓ |

---

### Private helper vs. separate module

Keeping everything inside `templates.py` is the right call here. The helpers are homepage-only view builders that consume existing payload shapes and produce HTML strings. Splitting them into a separate module would add an import boundary and a new file with no architectural benefit at this scope. The pattern already used by `_render_signal_synthesis`, `_render_briefing_topics`, and `_render_daily_local_intelligence` is the correct precedent.

---

### Minor findings

**Minor1 — Positioning test does not guard against daily_edit sliding past daily_local_intelligence**

The primary render test (Task 1 Step 1) asserts:

```python
assert index_html.index('class="signal-synthesis"') < section_start
assert section_start < index_html.index('class="lead-story"')
```

Per the spec target order, `daily_edit` must also appear before `daily_local_intelligence`. The existing assertions do not catch a regression where the insertion point accidentally ends up after the local-intelligence block. Adding:

```python
assert section_start < index_html.index('class="daily-local-intelligence"')
```

closes this gap with one line.

---

**Minor 2 — Card builder steps 5–8 omit the hardcoded `title` values**

The plan shows the card-dict shape (`"title": LocalizedText(en="...", zh="...")`) and what to read for `body`/`meta`/`href`, but never states the literal title strings for each card. The test in Step 1 makes them implicit requirements (`"What To Know"`, `"今日重点"`, etc.), so the implementer will find them — but it creates a read-the-test-to-find-the-spec situation. A one-line note in each of steps 5–8 such as _"Title: `LocalizedText(en="What To Know", zh="今日重点")`"_ removes the ambiguity at zero cost.

---

**Minor 3 — Signals fallback test only exercises `groups: []`, not signals-with-no-usable-name**

The spec and plan both say: fall back to `briefing_topics` when there are no signals with a non-empty `name`. The fallback test in Task 1 Step 4 uses `"groups": []` (no groups at all), which is a different code path from `"groups": [{"signals": [{"name": "", ...}]}]` (groups exist but every signal name is blank). Both paths must reach the fallback, but only one is exercised. This is low risk because the primary fallback test still demonstrates the feature works, but adding a second fixture with a non-empty group containing a nameless signal would fully cover the stated condition.

---

**Minor 4 — `_safe_daily_edit_href` allowlist includes anchors that may not always exist**

The helper allows `#briefing-topics` and `#briefing-path` as valid in-page targets. Those anchors are only rendered when `briefing_topics` and `briefing_path` produce non-empty strings (i.e. when there is usable payload for them). A card that links to `#briefing-topics` when no topics section was generated will produce a link that scrolls to nothing. This is not a security issue, but a no-op UX issue. It may be acceptable as-is — the existing site already has this class of optional anchor — but it is worth a comment in `_safe_daily_edit_href` noting that callers are responsible for verifying the anchor exists before emitting the href.

---

### No other risks or conflicting requirements identified

The boundary docs paragraph is comprehensive (21 explicit negative assertions). The commit step stages only the expected files. The full-verification sequence (focused tests → ruff → full pytest → lock check → hygiene script) matches the project standard. No schema, story-ID, detail-route, or LLM-call changes are present anywhere in the plan.
