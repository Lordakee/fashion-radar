Here is the plan review.

---

## Critical

None.

---

## Important

**1. `_reference_entries_by_key` first-entry-wins contradicts the plan spec, creating silent bridge suppression**

The plan spec says: "Value: first `_ReferenceEntry` for that key **with at least one valid paragraph index**." The proposed helper implementation does not filter on that condition:

```python
def _reference_entries_by_key(entries):
    by_key = {}
    for entry in entries:
        if entry.key and entry.key not in by_key:
            by_key[entry.key] = entry# no check on entry.paragraph_indices
    return by_key
```

`_article_reference_entries` deduplicates on `(key, rendered.label.casefold())`, not on `key` alone, so the same reference name can produce multiple `_ReferenceEntry` objects when it appears with different labels across content sections. If the first entry for a given key has `paragraph_indices=()` and a later entry for the same key has valid indices, `_first_valid_entry_paragraph` returns `None` and the bridge is silently omitted despite a valid paragraph existing in the article. The fix is to add `and entry.paragraph_indices` to the insertion guard, so `_reference_entries_by_key` skips empty-index entries and falls through to a subsequent entry that does carry indices. This applies symmetrically to both the current-article map built in `build_row_one_saved_article_local_related_reads` and the per-call candidate map built inside `_evidence_bridges`.

**2. No test for bridge row cap enforcement**

The plan caps `evidence_bridges` at `SAVED_ARTICLE_LOCAL_RELATED_READS_MAX_REFS` but the provided builder tests never exercise that boundary. `test_saved_article_local_related_reads_caps_cards_and_reference_chips` tests reference-chip capping on `references` but not on `evidence_bridges`. If the `len(bridges) >= SAVED_ARTICLE_LOCAL_RELATED_READS_MAX_REFS` break condition in `_evidence_bridges` were accidentally removed or the constant changed, no test would catch it. Add a focused test with 4+ valid shared references confirming `len(card.evidence_bridges) == SAVED_ARTICLE_LOCAL_RELATED_READS_MAX_REFS`.

---

## Minor

**1. Workflow test sentinel uses `<section>` but render produces `<div>`**

`test_stage_380_saved_local_article_related_read_evidence_bridge_stays_generated_site_only` passes:

```python
sentinel_html='<section class="saved-article-local-related-read-evidence-bridge"></section>'
```

The proposed render function wraps the bridge in `<div class="saved-article-local-related-read-evidence-bridge">`. The sentinel is an injection marker only and the tag type is irrelevant to correctness, but using `<div>` would make the sentinel consistent with the actual render output and avoid a confusing divergence between the two.

**2. No render test for bridge inside a lane**

Both new render tests (`_includes_`, `_filters_unsafe_`, `_escapes_`) pass a single-card `_related_reads_model(...)`, which takes the grid (non-lane) code path through `_render_saved_article_local_related_reads`. The acceptance criterion states the bridge must render "inside both lane and non-lane related-read layouts," and the plan does cite `test_render_local_article_page_groups_related_reads_into_lanes` as a verification step—but that test carries no `evidence_bridges`. Add one render test that creates a lane-eligible card (reason `"Shared signal: The Row"`) with a populated `evidence_bridges` tuple and asserts the bridge CSS class appears within the lane markup.

**3. Over-specified rejection list in the `_safe_saved_article_local_related_read_current_href` spec**

The plan description says the guard must "Reject external URLs, page paths, empty strings, whitespace, dot-prefixed paths, slash-containing paths, protocol URLs, `javascript:`, `data:`, and non-paragraph fragments." In the proposed implementation, all of those cases are already eliminated by the single `if not href.startswith("#"): return None` check—none of those rejected forms begin with `#`. The spec description accurately describes the rejection surface but may lead the implementer to add redundant explicit checks. The simpler framing is: "Accept only exact fragment-only hrefs matching `#local-article-paragraph-N` (N≥ 1); reject everything else."

END_OF_REVIEW
