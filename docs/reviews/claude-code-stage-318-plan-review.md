Here is the Stage 318 plan review.

---

## Stage 318 Plan Review — Summary

**No Critical or Important issues found.** Safe to implement as written.

---

### Checklist

**Reasonable next stage after 316–317?**
Yes.316 organized article content, 317 added paragraph previews, 318 adds internal navigation. Clean presentation-layer progression — no new data, no new artifacts, no schema changes.

**Files scoped correctly?**
Yes. Only `templates.py` carries production changes. None of the forbidden files are touched.

**Tests sufficient?**

| Dimension | Coverage |
|---|---|
| Same-section first, edition order | `test_render_row_one_detail_continue_reading_prioritizes_same_section_and_fallbacks` |
| Current story excluded | same test — `"The Row signal" not in rail_html` |
| Unsafe paths skipped | same test — `"Unsafe Story" not in rail_html` |
| Duplicate target paths skipped | same test — `"Duplicate Story" not in rail_html` |
| Cap at three | same test — `rail_html.count('class="continue-reading-card"') == 3` |
| Omission for one-story edition | `test_render_row_one_detail_continue_reading_omits_without_related_stories` |
| Escaping | same first test — `"Same Section &lt;Story&gt;"` |
| Sibling href (not `details/…`) | same first test — positive and negative href assertions |
| Editorial takeaway fallback | `test_render_row_one_detail_continue_reading_uses_editorial_takeaway_fallback` |
| Rail in workflow output | `test_write_row_one_site_files_writes_local_article_without_mutating_sqlite` |
| Contract payload clean | same workflow test — `'"continue_reading"' not in` |
| SQLite immutability | same workflow test — second-item before/after assertions |
| Docs boundary | `test_row_one_docs_describe_detail_continue_reading_boundary` |

All spec-required dimensions are covered.✓

**External-link aggregator risk?**
None. All links derive from `RowOneEdition.stories[*].detail_path` (internal generated pages). `_detail_continue_reading_href` extracts only the filename, dropping the `details/` prefix. No external URLs introduced. ✓

---

### Critical

None.

---

### Important

None.

---

### Minor

**1 — Dead `if card` filter in `_render_detail_continue_reading`**

`_detail_continue_reading_stories` already calls `_detail_continue_reading_href` and skips any story returning `None`. Every story it returns has a valid href. The card renderer calls `_detail_continue_reading_href` a second time and returns `""` on `None`, but that branch is unreachable. The outer `[card for card in cards if card]` filter is dead code.

Not a bug — defense-in-depth is harmless — but a future reader may incorrectly assume unsafe paths can reach the card renderer. Worth a comment explaining the intent, or remove the redundant guard in the card renderer.

---

**2 — CSS specificity: excerpt text renders muted, not ink**

```css
/* specificity (0,1,1) — applies to ALL <span> descendants */
.continue-reading-card span { color: var(--muted); }

/* specificity (0,1,0) — sets color on the container only */
.continue-reading-excerpt { color: var(--ink); }
```

`.continue-reading-excerpt` wraps `<span data-lang="en">` and `<span data-lang="zh">` children. Those inner spans match `.continue-reading-card span` at higher specificity and render `var(--muted)`, not `var(--ink)`. The container rule is overridden for its own text content.

If the intent is ink-colored excerpt text, use:
```css
.continue-reading-excerpt span { color: var(--ink); }
```
If muted is intentional, remove `.continue-reading-excerpt { color: var(--ink) }` entirely. The current state is ambiguous — worth resolving during Step 3.

---

**3 — Workflow test `...` placeholders don't anchor insertion points**

Task 2 Step 1 uses `...` in three places for "existing code continues here." The implementer needs to read the full `test_write_row_one_site_files_writes_local_article_without_mutating_sqlite` body to find correct positions for the second-item setup (before site-write), the `before` captures, and the `after` captures plus `assert "continue-reading"`. No plan change needed — just a reminder to read the existing test before editing.

---

**4 — `_section_title` not flagged as a pre-existing helper**

The card renderer calls `_section_title(edition, story.section_key)`. The function already exists at `templates.py:4444`. No implementation work needed; minor documentation gap only.

---

### Verdict

**Safe to implement.** Fix Minor 2 (CSS specificity) during Step 3. The other three minors require no blocking action.
