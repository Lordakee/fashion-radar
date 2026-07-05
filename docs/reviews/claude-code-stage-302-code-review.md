I now have a complete picture of all changed files. Here is the Stage 302 code review.

---

## Stage 302 Code Review

**Base commit:** `0f591ab`
**Reviewer:** Claude Opus4.8
**Date:** 2026-07-05

---

### Verdict: APPROVE

---

### Critical Issues

None.

---

### Important Issues

None.

Both items flagged as Important in the Claude Code plan review were fully addressed before implementation:

**Escaping test** — `test_render_row_one_site_escapes_daily_local_intelligence` now injects `<script>` payloads in the segment title (en + zh), segment item label (en + zh), segment item body (en + zh), and nested reference name. The test asserts raw HTML strings absent (`"<script>Segment</script>" not in html`, `'<img src=x onerror="alert' not in html`) and the corresponding escaped forms present (`"&lt;script&gt;Segment&lt;/script&gt;"`, `"&lt;img src=x onerror=&quot;alert(2)&quot;&gt; nested body"`, `"&lt;script&gt;Nested Ref&lt;/script&gt;"`). The broad negative `'<img src=x onerror="alert' not in html` covers all `onerror` variants including alert(1) in the segment-level `body`.

**`_ReferenceAggregate` dataclass** — The `dict[str, object]` aggregate is fully replaced with a typed `@dataclass` including all former fields plus `segments` and `segment_match_score`. All `# type: ignore` casts that previously accompanied the dict are eliminated.

---

### Minor Notes

**1. No positive assertion for segment-level `body` escaping in the render test.**

The escaping test fixture sets the takeaways section's `body` to `'<img src=x onerror="alert(1)"> segment body'`. The broad negative `'<img src=x onerror="alert' not in html` covers it, but there is no positive assertion such as:

```python
assert '&lt;img src=x onerror=&quot;alert(1)&quot;&gt; segment body' in html
```

This would confirm the segment body is actually rendered (not silently dropped) *and* escaped. The current test proves the XSS is neutralized but not that the visible content survives. Low risk — `_render_daily_local_intelligence_segment` does render `segment.body` when non-empty, and the full-render test `test_render_row_one_site_writes_and_renders_daily_local_intelligence_segments` asserts `"The saved source points to these reads." in html`, confirming segment bodies do render. Not a blocking issue.

**2. Reference meta format is `name / type / label` here, `name (type / label)` elsewhere.**

`_render_daily_local_intelligence_segment_meta` joins reference fields with `" / "` giving `"<The Row> / brand / tracked"`. The detail-page renderer `_render_local_article_content_references` uses `f"{ref.name} ({ref.type} / {ref.label})"`. Both are fully escaped. The inconsistency is cosmetic and within the compact card context the flat separator is reasonable. No issue.

**3. `segment_match_score` field on `_ReferenceAggregate` is not in the plan spec but is correctly used.**

The plan's Task 3 Step 2 dataclass spec omits `segment_match_score: int = 0`. The implementation adds it to support the "later stronger match upgrade" logic (`if segment_match_score > aggregate.segment_match_score`). The field is strictly internal, improves correctness, and is covered by `test_reference_segments_can_upgrade_from_fallback_to_later_match`. This is an improvement over the plan, not a deviation.

**4. `_article_segments()` fallback path in `_reference_segments()` returns only the first segment.**

When no matching reference segment exists, `_reference_segments()` returns `_article_segments(article)[:1]` — one segment instead of up to four. This is intentional for reference cards (compact focused context), and the test `test_build_row_one_local_article_intelligence_uses_matching_reference_segments` indirectly confirms it. Worth a brief comment in the code for future readers, but not a bug.

---

### Boundary Review

Stage 302 remains within the established local-first boundary:

- No scraping, social connectors, source acquisition, demand proof, platform coverage verification, app UI work, paywall bypass, or compliance-review features introduced.
- `data/edition.json` and `row-one-app/v7` are unaffected. The test assertion `assert "local_article_intelligence" not in payload` guards this.
- Segment JSON is written only to the already-separate `data/local-intelligence.json` artifact.
- Homepage HTML renders segments entirely from in-process Pydantic model state, not from new data acquisition.

---

### Correctness Checklist

| Check | Result |
|---|---|
| Segment caps (4segments, 3 items) | ✅ `MAX_SEGMENTS_PER_ITEM = 4`, `MAX_SEGMENT_ITEMS = 3` enforced in `_article_segments` and `_content_section_segment` |
| Matched reference segment preference | ✅ `_reference_segments()` searches `_reference_segment_keys(reference_kind)` first; falls back to `_article_segments()[:1]` |
| Later stronger match upgrade | ✅ `_reference_segment_match_score()` returns 2/1/0; upgrade fires when `score > aggregate.segment_match_score` |
| Product/entity same-name separation | ✅ `_reference_segment_keys("product")` → `("product_signals",)`, `_reference_segment_keys("entity")` → `("entities",)`. Covered by `test_product_reference_segments_do_not_cross_match_same_name_entity` |
| Deterministic sorting | ✅ Unchanged sort keys throughout |
| No full `paragraphs` list in daily intelligence items | ✅ `_content_section_segment` copies only label/body/references/paragraph_indices. `assert "paragraphs" not in dumped` in builder test |
| `data/edition.json` stability | ✅ Test assertion present |
| All template output escaped | ✅ `_esc()` wraps every interpolated value in all three new helpers |
| `extra="forbid"` on both new models | ✅ |
| Segment renders empty-safe | ✅ All three helpers return `""` when list empty or all items filter to empty |

---

### Summary

The implementation is architecturally correct, local-first, deterministic, and fully escaped. All four plan-review concerns (escaping test, dataclass refactor, segment body intent, `"paragraphs" not in dumped` guard) are resolved or deliberately retained with justification. The test suite adds five new builder tests and two new render/artifact tests that would fail for each named regression.1989 tests pass, ruff is clean, and hygiene checks pass.

**APPROVE.** No changes required before commit.
