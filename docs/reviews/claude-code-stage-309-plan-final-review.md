I've read the full plan. Checking each of the six rereview items and scanning for new issues.

---

## Verdict

**Approve with Important fixes**

---

## Remaining Critical/Important Findings

**Unsafe-URL test assertion is logically inverted (Task 3, Step 3, lines 404–408)**

The plan says to render a local article with `url="javascript:alert(1)"` and then assert:
```python
assert "Original URL" in detail_html        # ← wrong
assert 'class="local-article-provenance-link"' not in detail_html
```
The renderer (Task 3, Step 4) only emits the text "Original URL" inside the `<a class="local-article-provenance-link">` element. When `_safe_external_url` returns `None` the anchor is never written — so "Original URL" will also be absent. The assertion `assert "Original URL" in detail_html` will fail on an unsafe URL, contradicting the suppression logic.

Fix: change that assertion to `assert "Original URL" not in detail_html`. The three-line block should read:
```python
assert "javascript:alert" not in detail_html
assert "Original URL" not in detail_html
assert 'class="local-article-provenance-link"' not in detail_html
```

---

## Minor Findings

- **`_story_sort_key` direction is implicit (Task 2, Step 4).** The plan says "sort source pairs first, cluster after sorting" and the clustering test expects `coach-b` (heat_delta=9) to become canonical, implying `_story_sort_key` sorts highest-heat first. This is consistent with the existing `heat_movers` behaviour, but the plan never states the sort direction. A one-line comment confirming "sorted descending by heat so the highest-delta story becomes canonical" would prevent ambiguity during implementation.

- **`_append_reference` is called but not introduced (Task 2, Step 3).** The plan uses it in `_append_story_article_aggregate` without defining or citing it. If it is pre-existing, a brief parenthetical "(existing helper)" alongside its call site would prevent the implementor from searching or accidentally duplicating it.

- **Rereview-file git add in Task 7 Step 4.** The `git add` command already includes the rereview docs (`claude-code-stage-309-plan-rereview-prompt.md`, `claude-code-stage-309-plan-rereview.md`). A note confirming the final rereview files (`claude-code-stage-309-plan-final-review*`) from the current git status are also expected to be staged would close the gap, since those files are listed as untracked in the opening status snapshot but absent from the `git add` line.
