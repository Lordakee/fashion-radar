# Stage 261 Code Review

## Verdict: **Approve with fixes**

Stage 261 successfully implements deterministic ROW ONE editorial synthesis with strong correctness, comprehensive test coverage, and proper boundary adherence. The implementation matches the design specification and adds meaningful editorial context without introducing external dependencies, translation, LLMs, or new product behavior. However, there is one critical bug in the growth ratio handling that must be fixed before commit.

---

## Critical Findings

### 1. Growth ratio formatting bug in `_entity_synthesis`
**Location:** `src/fashion_radar/row_one/edition.py:323`

The code calls `_growth_ratio_label(entity.growth_ratio)` at line 323 but only uses the result inside the `else` branch (line 340). When `entity.growth_ratio is None`, the `growth` variable is still computed as `"n/a"`, but this value is never used because the None-path constructs its own message without the growth variable.

However, there's a logical issue: the code computes `growth` unconditionally, but the `growth` variable is only referenced in the `else` branch. This works correctly but is wasteful. More critically, the test at `tests/test_row_one_edition.py:271` explicitly checks:

```python
assert "n/ax" not in story.signal_context.en
```

This test suggests concern about accidentally inserting `"n/ax"` (the formatted None value plus the "x" suffix) into the output. The current implementation is safe because the None-path doesn't use the `growth` variable, but the code structure is confusing.

**Fix:** Move `_growth_ratio_label` call inside the `else` branch:

```python
def _entity_synthesis(
    entity: EntityReport,
    *,
    section_key: RowOneSectionKey,
) -> tuple[LocalizedText, LocalizedText, LocalizedText]:
    section = _section_title(section_key)
    baseline = entity.baseline_mentions
    if entity.growth_ratio is None:
        signal_context = LocalizedText(
            zh=(
                f"本地窗口记录 {entity.current_mentions} 次当前提及，对比基线 "
                f"{baseline} 次，暂无增长倍数。"
            ),
            en=(
                f"The local window shows {entity.current_mentions} current mentions versus "
                f"{baseline} baseline; growth ratio is unavailable."
            ),
        )
    else:
        growth = _growth_ratio_label(entity.growth_ratio)
        signal_context = LocalizedText(
            zh=(
                f"本地窗口记录 {entity.current_mentions} 次当前提及，对比基线 "
                f"{baseline} 次，增长倍数 {growth}。"
            ),
            en=(
                f"The local window shows {entity.current_mentions} current mentions versus "
                f"{baseline} baseline, a {growth}x growth ratio."
            ),
        )
    return (
        LocalizedText(
            zh=f"{entity.entity_name} 是今日 {section.zh} 中最值得先看的信号之一。",
            en=f"{entity.entity_name} is one of today's priority signals in {section.en}.",
        ),
        signal_context,
        LocalizedText(
            zh=f"先按 {entity.label} 标签阅读，再对照{section.zh}中的同类信号。",
            en=(
                f"Read it as a {entity.label} signal, then compare it with nearby "
                f"{section.en} stories."
            ),
        ),
    )
```

---

## Important Findings

### 2. Excellent stable ordering implementation
**Location:** `src/fashion_radar/row_one/edition.py:131, 149, 164, 168`

The implementation correctly uses three-level sort keys for stable, deterministic ordering:
```python
key=lambda entity: (-entity.heat_score, entity.entity_name.casefold(), entity.entity_name)
```

This handles same-score ties by case-insensitive alphabetical order, then by exact name for "A Brand" vs "a brand" disambiguation. The tests at `test_row_one_edition_orders_top_story_ties_by_name` and `test_row_one_edition_orders_casefold_ties_by_original_name` properly verify this behavior.

### 3. `RowOneSectionKey` typing is properly enforced
**Location:** `src/fashion_radar/row_one/models.py:10-16, 46`

The extracted `RowOneSectionKey` literal type is correctly used throughout models, edition builder, and templates. The test `test_row_one_story_rejects_unknown_section_key` verifies Pydantic validation catches invalid keys. This prevents typos and improves type safety for JSON consumers.

### 4. `--dry-run` validation is correct
**Location:** `src/fashion_radar/cli.py:1436-1439`, `tests/test_row_one_cli.py:209-285`

The CLI now validates the site directory structure in `--dry-run` mode without binding the port. The test `test_row_one_serve_dry_run_does_not_bind_requested_port` confirms no port binding occurs. The validation correctly checks for both the `.row-one-site` marker and `index.html` existence. This is a solid safety improvement.

---

## Minor Findings

### 5. HTML escaping is preserved correctly
**Location:** `src/fashion_radar/row_one/templates.py:95-113, 307-311`

All new synthesis fields use `_esc()` for HTML escaping. The test `test_render_row_one_site_escapes_html_and_omits_unsafe_links` verifies apostrophes are escaped as `&#x27;` in the rendered HTML.

### 6. Language toggle enhancement
**Location:** `src/fashion_radar/row_one/templates.py:296`

The JavaScript now sets `document.documentElement.lang` to `"zh-Hans"` or `"en"`, improving accessibility and semantic correctness. The test verifies this behavior with regex matching.

### 7. JSON output compatibility maintained
**Location:** `tests/test_row_one_render.py:248-253`

The new synthesis fields are correctly serialized to JSON with proper structure. URL sanitization for `source_url` and evidence URLs remains unchanged as verified by `test_render_row_one_site_sanitizes_json_source_url`.

### 8. Documentation matches implementation
**Location:** `docs/row-one.md:41-51`, `tests/test_row_one_docs.py:85-96`

The documentation correctly describes editorial synthesis as deterministic, local-field-derived, and explicitly states what it is NOT (translation, LLM generation, new scoring, demand proof). The boundary test verifies all required phrases are present.

### 9. No new external dependencies
The implementation uses only existing Fashion Radar models, Pydantic, and standard library. No scraping, platform APIs, translation services, LLM calls, paid APIs, or deployment infrastructure was added.

### 10. Test coverage is comprehensive
The test suite covers:
- Entity/candidate/recent-item synthesis generation
- Growth ratio None handling
- Stable ordering with casefold and exact-name tiebreakers
- HTML rendering with escaping
- JSON serialization
- Section key validation
- CLI dry-run validation without port binding
- Documentation boundary assertions

All 56 focused tests passed, and the full gate (1682 tests) passed with Ruff and format checks clean.

---

## Required Fixes Before Commit

1. **Fix growth ratio variable scope** (Critical finding #1): Move `_growth_ratio_label` call inside the `else` branch to eliminate dead code and clarify intent.

---

## Optional Follow-ups

None. The implementation is production-ready after the critical fix.

---

## Summary

Stage 261 delivers a clean, deterministic editorial synthesis layer that organizes ROW ONE stories into readable briefings without adding product complexity or external dependencies. The typing improvements, stable sorting, and dry-run validation enhancements are all valuable. The single critical issue with growth ratio variable scoping is a minor refactor that doesn't affect correctness but should be fixed for code clarity. After this fix, the stage is ready for commit.
