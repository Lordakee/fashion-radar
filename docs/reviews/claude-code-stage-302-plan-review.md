---

## Stage 302Plan Review

**Reviewed:** `docs/superpowers/plans/2026-07-05-stage-302-row-one-local-intelligence-segments-plan.md`
**Codebase snapshot:** `0f591ab` (Stage 301)

---

### Verdict: APPROVE_WITH_NOTES

---

### Critical Issues

None.

---

### Important Issues

**1. Escaping test stub is underspecified (Task 4 Step 2)**

The plan says "Extend `test_render_row_one_site_escapes_daily_local_intelligence` so the local article contains a malicious nested content section item and assert the escaped text appears while raw HTML does not" — but does not provide the test body.

This is the primary injection surface of the feature: segment labels, item bodies, and reference names all flow into HTML. If the implementer skips the fixture or uses a safe string by mistake, the RED/GREEN cycle passes but the safety check is hollow. The plan should provide the full test, including a `content_sections` entry whose `label` or `body` contains something like `<script>alert(1)</script>`, and explicit asserts that the literal `<script>` tag is absent from the rendered HTML.

**2. `_aggregate_item()` dict typing will accumulate more `# type: ignore` (Task 3 Step 3)**

`_reference_watch_section()` uses `aggregates: dict[str, dict[str, object]]`. It already has four `# type: ignore[...]` comments for existing fields. Adding `segments: list[RowOneDailyLocalIntelligenceSegment]` as another `object`-typed slot will require at least one more cast at read time. The plan says nothing about this. It won't break anything, but the implementer should either follow the existing pattern consistently (document the cast) or, preferably, introduce a small `_ReferenceAggregate` dataclass / TypedDict to clean up what is already technical debt. Not doing it now is acceptable; ignoring the typing noise silently is not.

---

### Minor Notes

1. **Segment-level `body` may be dead schema weight.** The plan adds `body: LocalizedText | None = None` to `RowOneDailyLocalIntelligenceSegment`, mirroring `RowOneLocalArticleContentSection.body`. In the existing codebase that field is never populated — `_article_takeaway()` and `_reference_source_text()` operate at the item level. If the builder projection never writes this field, it sits in the Pydantic schema and the JSON output as a permanent `null`. Worth confirming intent before coding; if unused, drop it from the segment model.

2. **`extra="forbid"` preservation.** Confirmed: all existing models use it. The two new models in the plan also carry it. No issue.

3. **Artifact isolation confirmed.** `build_row_one_app_payload()` and `_write_local_article_intelligence_file()` are entirely separate code paths. Adding `segments` to `RowOneDailyLocalIntelligenceItem` will appear in `local-intelligence.json` only. The `edition.json` app payload does not serialize `RowOneDailyLocalIntelligenceItem` at all — `row-one-app/v7` is safe.

4. **`"paragraphs" not in dumped` assertion.** The test in Task 2 Step 1 checks `assert "paragraphs" not in item.model_dump(mode="json")`. This is the right guard. The segment model only carries `paragraph_indices`, never the paragraph text itself — confirmed by the model spec in the plan.

5. **`RowOneLocalArticleContentKey` reuse.** Correct. The plan keys segment types to the existing `Literal["takeaways", "entities", "product_signals", "brand_signals"]` rather than introducing a new type.

6. **Test fixture factories.** The proposed test stubs use `_story()`, `_edition()`, and `AS_OF` exactly as they are defined in `tests/test_row_one_local_intelligence.py`. Drop-in compatible.

7. **RED/GREEN discipline.** Each task follows the project's established RED → implement → GREEN loop, verified with `UV_NO_CONFIG=1 uv --no-config run --frozen pytest`. Consistent with prior stages.

---

### Summary

The plan is architecturally sound, local-first, deterministic, and correctly bounded to the existing artifact pipeline. It does not introduce scraping, social connectors, source acquisition, demand proof, platform coverage verification, app UI changes, paywall bypass, or compliance-review features. The two items to address before or during implementation: write the full escaping test stub (Important), and decide whether the segment-level `body` field is intentional or vestigial (Minor).
