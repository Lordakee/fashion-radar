Here is the review of the Stage 319 diff against the specified checklist.

---

## Escaping

All user-sourced text goes through `_esc()` before interpolation into the template:

- `summary_en`/`summary_zh`: cleaned via `_display_summary_text()` first, then `_esc()`. The test confirms `<b>` HTML is stripped and `<script>` is entity-encoded. ✓
- `story.signal_context.en`/`.zh`: `_esc()` applied directly. Test asserts `Signal context &lt;script&gt;alert(1)&lt;/script&gt;.` ✓
- `story.source_name`: `_esc()` ✓
- `ref.name` in `_render_detail_signal_briefing_ref`: `_esc(ref.name)` ✓ — test confirms `Signal &lt;script&gt;Brand&lt;/script&gt;` renders correctly and raw `<script>Brand</script>` does not appear.
- Cue `title.en/zh` and `body.en/zh`: all `_esc()` ✓
- Paragraph link `href`: constructed from `_local_article_paragraph_anchor(int)` (safe integer-derived anchor), then `_esc(href)` ✓

No escaping issues found.

---

## Placement Before Summary

In `render_detail_html()`:

```python
{detail_information_map}
{detail_signal_briefing}
<section id="summary">
```

Panel is after `Detail Information Map` and immediately before `<section id="summary">`. Matches spec. Test asserts `panel_start < html.index('id="summary"')`. ✓

---

## Reference Dedupe / Cap

`_detail_signal_briefing_references` deduplicates by `(normalize_row_one_paragraph(ref.name).casefold(), ref.type.casefold(), ref.label.casefold())`. Order is preserved (entity → designer → product → local article content sections). Cap is `DETAIL_SIGNAL_BRIEFING_MAX_REFS = 8`, enforced in the `add()` closure for story refs and via an explicit early `return` for local article refs. The early-return guard in the innermost loop is redundant but not incorrect — `add()` already no-ops past cap for story refs. The cap test asserts exactly 8 refs when11 are available. ✓

One note: the dedup key uses `normalize_row_one_paragraph(ref.name)` (an existing helper) rather than raw `ref.name`. This is consistent with how the project normalizes names elsewhere and matches the spec's intent.

---

## Local Article Cue Cap

Cap of 3 (`DETAIL_SIGNAL_BRIEFING_MAX_CUES`) is respected. The implementation pre-decrements `max_brief_cues` to 2 when any content cues exist, reserving a slot for them. The test fixture confirms:4 brief sections + 2 content sections → 2 brief + 1 content = 3 total, and the 3rd brief section ("Signal Context") and 2nd content section ("Products") are both excluded. ✓

---

## Paragraph Anchor Safety

`_first_valid_local_article_paragraph_index` collects `paragraph_indices` from all section items, then passes through `_valid_local_article_paragraph_indices(indices, rendered_indices)` — the same two-helper gate used by existing paragraph rendering. Only integer indices that refer to actually-rendered paragraphs produce a link. `None` is handled silently (no link rendered). The test confirms `href="#local-article-paragraph-1"` is present and `href="#local-article-paragraph-2"` is absent (only first valid index linked per content section). ✓

---

## JSON / Schema / Runtime / Manifest Contract Drift

- No new fields added to `RowOneEdition`, `RowOneStory`, or any schema model.
- No writes to `edition.json`, `manifest.json`, `runtime.json`, or any new artifact.
- `test_workflows.py` adds two new negative assertions: `'"detail_signal_briefing"' not in generated_contract_payload` and `'"signal_briefing"' not in generated_contract_payload`, confirming no Stage-319 keys leak into contract payloads. ✓
- `data/*.json` top-level allowlist unchanged. ✓

---

## No Critical or Important Issues Found

All six checklist areas are clean.

---

## Minor (out of scope for this review, noted for completeness)

1. **`why_it_matters` absent from the briefing panel.** The spec defines four cards including "Why It Matters / 为什么重要" using `story.why_it_matters`. The implementation renders three cards and never reads `why_it_matters` in the briefing context (it still renders in the existing lower `#why-it-matters` section). Whether this is intentional simplification or a missed card is worth confirming.

2. **Card label drift vs. spec.** Spec names: "Source Context / 来源背景" and "Names To Track / 需要关注". Implementation uses "Context / 背景" and "References / 引用对象". Evidence count is placed in the Signal card rather than a Source Context card. No runtime or contract impact.

3. **Paragraph link text.** Implementation renders "Paragraph N / 段落 N"; spec calls for "Saved paragraph N / 保存段落 N". Cosmetic only.

4. **Brief-section slot reservation.** When content cues exist, `max_brief_cues` is decremented to 2, so≥3 brief sections + non-empty content yields 2 brief + 1 content rather than the spec's "prefer brief" reading of 3 brief first. Cap of 3 is respected either way.
