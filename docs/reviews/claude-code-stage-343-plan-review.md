Now I have enough to render a complete verdict.

---

## Stage 343Plan Review

### Architecture Assessment — Q1

The plan fits cleanly into the existing renderer. `_render_saved_article_content_organization_group_summary()` follows the exact pattern already established by `_render_saved_article_content_organization_card()`: gate on `_safe_saved_article_content_organization_href`, aggregate, return empty string on no safe cards. All reused helpers (`_safe_saved_article_content_organization_href`, `validated_row_one_detail_relative_path`, `normalize_row_one_paragraph`, `_esc`, `_count_label`, `Sequence`) are already imported at the top of `templates.py`. No model, schema, contract, or pipeline changes. Architecture is sound.

---

### Findings

#### IMPORTANT — Workflow assertion may silently skip or actively fail

**Location:** Task 3, Step 3 — the proposed addition to `test_write_row_one_site_files_writes_local_article_without_mutating_sqlite`.

The plan adds this inside the existing `if articles_html_path.exists():` block:

```python
assert 'class="saved-article-content-organization-summary"' in articles_html
```

This is unconditional. The existing workflow test fixture exercises the real write pipeline from SQLite. If the fixture data does not include at least one non-empty saved article content organization group, the assertion will **fail at the TDD step**, or worse, if added after implementation it will vacuously pass only when the fixture happens to include such data.

The existing parallel pattern is instructive — the saved signal index assertion is guarded:

```python
if "saved-signal-index-support-row" in articles_html:
    assert "saved-signal-index-support-excerpt" in articles_html
```

**Required fix:** Either guard the assertion similarly:

```python
if 'class="saved-article-content-organization-group"' in articles_html:
    assert 'class="saved-article-content-organization-summary"' in articles_html
```

Or confirm the fixture always produces at least one populated content organization group before leaving this unconditional. If the latter, add a comment stating that invariant.

---

#### MINOR — Design says "recurring" but implementation uses first-seen order

**Location:** `_saved_article_content_organization_summary_refs()` — Task 2, Step 3.

The design spec says "recurring reference chips" (implying frequency-ranked selection), but the implementation collects the first N unique references in card-iteration order. If the most frequent reference across10 cards happens to be the 6th unique reference encountered, it will be excluded by the cap.

This is consistent with how other parts of the codebase handle reference aggregation (no frequency sorting elsewhere) and is acceptable for a first pass. Worth documenting in a comment so the behavior is explicit, e.g.: `# First-seen order; references from early cards are prioritized up to the cap.`

Not a blocker, but the design language should match the implementation or the implementation should note the divergence.

---

#### MINOR — `_saved_article_content_organization_detail_path_key` partially duplicates existing helper

**Location:** Task 2, Step 3.

The proposed private helper:

```python
def _saved_article_content_organization_detail_path_key(href: str) -> str:
    path, _separator, _fragment = href.partition("#")
    safe_path = validated_row_one_detail_relative_path(path)
    return str(safe_path) if safe_path is not None else ""
```

is functionally equivalent to the existing `_saved_article_library_detail_path_key(href: str) -> str | None` (line 4982), which does the same validation but returns `None` instead of `""`. The new helper's callers use `discard("")`, so either form works.

Not a blocker — the new helper's empty-string sentinel fits its set-comprehension usage clearly. But if `_saved_article_library_detail_path_key` is reused instead, two fewer lines of code and zero new surface. Implementer's call.

---

#### MINOR — Missing test for same-article multi-section dedup

There is no test case where two cards reference the same article path (same file, different `#local-article-content-section-N` anchors), verifying that the saved article count is 1, not 2. The logic is straightforward — path stripping before set insertion — but explicit coverage would close this gap.

Not a blocker; can be added alongside the other render tests.

---

### Q2 — Test Sufficiency

Tests cover the four critical axes (metrics counting, unsafe card filtering, reference escaping/capping, CSS selectors) and the docs and workflow guards are correctly scoped. The four render tests are well-constructed. The only gap is the same-article/multi-section dedup case noted above. Coverage is sufficient for green-lighting implementation.

### Q3 — Compatibility Risks

No hidden risks. Safe-href filtering, paragraph index type guards, and reference dedup/escaping all mirror existing implementations in the same file exactly. `normalize_row_one_paragraph` + `casefold()` for source dedup is consistent with prior usage. `_esc` handles all injected strings. No ordering dependency on group rendering.

### Q4 — Contract / Artifact / Scope Leakage

None. The plan stays entirely in `templates.py` HTML rendering + tests + docs. No new JSON keys in app payload, no new files written by the renderer, no model changes. The workflow negative-assertion list (contract keys + artifact paths) is thorough and correctly covers the obvious naming variations.

### Q5 — Required Changes Before Implementation

One required fix (IMPORTANT above):

> Verify whether the workflow fixture produces content organization HTML, and conditionally guard the workflow `articles_html` assertion accordingly.

The three MINOR findings are improvements but do not block implementation.

---

**Verdict: Approved for implementation pending the workflow assertion guard fix.** The plan is architecturally sound, well-scoped, and the test suite is appropriately thorough. Resolve the workflow assertion conditionality before or during Task 3 Step 3.
