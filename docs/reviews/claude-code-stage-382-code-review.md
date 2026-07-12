## Stage 382Code Review: Local Article Synthesis Brief

No Critical findings.

---

### Important

**`_anchors` hardcodes `2` instead of `LOCAL_ARTICLE_SYNTHESIS_BRIEF_MAX_ANCHORS - 1`**
`local_article_synthesis_brief.py:225`

```python
if len(anchors) >= 2:   # ← should be MAX_ANCHORS - 1
    break
```

The design reserves one slot for a paragraph anchor: collect up to `MAX_ANCHORS - 1` section anchors, then optionally append one paragraph anchor, then slice to `MAX_ANCHORS`. That logic is correct right now because `MAX_ANCHORS = 3`, so `2 == MAX_ANCHORS - 1`. But the `2` is a literal. If `LOCAL_ARTICLE_SYNTHESIS_BRIEF_MAX_ANCHORS` is ever changed, the loop break doesn't follow and the function silently under-produces anchors (e.g. `MAX_ANCHORS = 4` → loop still stops at 2 section anchors → at most 3 total, not 4). The constant and the break should be coupled:

```python
if len(anchors) >= LOCAL_ARTICLE_SYNTHESIS_BRIEF_MAX_ANCHORS - 1:
    break
```

No test currently catches this divergence.

---

### Minor

**1. Redundant index-bounds guard in `_paragraph_candidates` and `_paragraph_anchor`**
`local_article_synthesis_brief.py:209–211, 263–269`

Both functions set `aligned_zh = len(article.paragraphs_zh) == len(article.paragraphs)` and then guard with `if aligned_zh and index < len(article.paragraphs_zh)`. The second condition is always true when `aligned_zh` is true (lengths are equal, so every index in `paragraphs` is valid in `paragraphs_zh`). The guard is harmless but slightly misleading — a reader might think lengths can diverge mid-loop. The `index < len(...)` half can be dropped.

---

**2. Empty `source_name` renders grammatically broken text**
`templates.py:17652`

```python
f"A compact synthesis from {_esc(brief.source_name)}."
```

`build_row_one_local_article_synthesis_brief` computes `source_name` as:

```python
normalize_row_one_paragraph(local_article.source_name) or normalize_row_one_paragraph(story.source_name)
```

If both normalize to empty (blank-only strings in data), `source_name = ""` and the template renders *"A compact synthesis from ."*. This edge case is probably prevented by upstream validation, but there is no fallback and no test covering it. A simple `or "this article"` / `or "本文"` guard at the build site or a blanket check in `build_...` (return `None` when `source_name` is empty) would close it.

---

**3. `_content_title_body_candidates` title-only branch uses a distinct `source_id` key — not covered by tests**
`local_article_synthesis_brief.py:197`

When a section has a title but no body, the function yields:

```python
yield _candidate(f"content_section.{index}.title", title)
```

This uses `.title` as the suffix, while `_content_body_candidates` uses `.body`. That means: if `_content_title_body_candidates` consumes this section via the `.title` key for `thesis`, `_content_body_candidates` will *not* see it as consumed (different source_id) and could re-emit the same section text via `.body` for `article_adds`. In practice the section has no body so `_content_body_candidates` would yield a blank and `_nonblank_localized_text` would filter it — but the asymmetry is subtle and untested. A test with a title-only section exercising both `thesis` and `article_adds` would make the behavior explicit.

---

**4. Empty support produces dangling whitespace in anchor HTML**
`templates.py:17700–17706`

When `anchor.support` is `None` or blank, `support = ""` and the template renders:

```html
<a class="local-article-synthesis-brief-anchor" href="...">
  <strong>...</strong>
  
</a>
```

The `{support}` placeholder leaves an indented blank line. Not a correctness issue, but unnecessary noise in generated HTML. Either emit nothing between `</strong>` and `</a>` when support is empty, or fold the support into the f-string conditionally the way `anchors_block` does it.

---

**5. `reader_move` anchor-branch text doesn't distinguish section vs. paragraph anchors**
`local_article_synthesis_brief.py:293–300`

When any anchors exist, `reader_move` always says *"Read next through the saved body anchors that connect the synthesis to the local article text."* This is correct and safe, but if all generated anchors are paragraph anchors (no content sections), the phrase "saved body anchors" slightly misrepresents them. Cosmetic — no action required unless copy accuracy is a priority.

---

### Summary

No boundary leaks detected: the synthesis brief is correctly scoped to `articles/<story-id>.html`; it does not appear in `index.html`, `articles/index.html`, detail pages, `data/*.json`, or `data/articles/*.json`. Anchor safety is solid — the layered `_safe_local_article_intelligence_href` → `_safe_local_article_synthesis_href` chain rejects `javascript:`, path traversal, out-of-range numbers, paragraph-0, and whitespace-in-fragment. All string interpolations into HTML go through `_esc`. Deduplication logic is deterministic and correct for the current constant. Test coverage for the main paths is thorough.

The one change worth making before landing is coupling the loop-break constant to `LOCAL_ARTICLE_SYNTHESIS_BRIEF_MAX_ANCHORS - 1`.
