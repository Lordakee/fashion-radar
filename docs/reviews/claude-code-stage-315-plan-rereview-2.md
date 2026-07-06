## Stage 315 Plan Re-Review (Post Second-Fix Pass)

Checking the two prior-review findings against the current documents.

---

### Prior C1 — Six "does not X" phrase mismatches

The docs paragraph (Task 3 Step 3) now reads:

> "…It does not change `row-one-app/v7`, does not write a new generated JSON artifact, does not add source collection, does not fetch article pages, does not add scoring, and does not add llm calls."

Cross-checking each guarded phrase from `test_row_one_docs_describe_article_readiness_boundary`:

| Guard phrase | Present in docs paragraph? |
|---|---|
| `"does not change \`row-one-app/v7\`"` | ✓ literal match |
| `"does not write a new generated JSON artifact"` | ✓ literal match |
| `"does not add source collection"` | ✓ literal match |
| `"does not fetch article pages"` | ✓ literal match |
| `"does not add scoring"` | ✓ literal match |
| `"does not add llm calls"` | ✓ literal match |

**C1: Fixed.**

---

### Prior I1 — Missing `Site:` assertion in text-output CLI test

Task 2 Step 1 now includes:

```python
assert f"Site: {output_dir}" in result.output
```

**I1: Fixed.**

---

### No New Critical or Important Findings

I spot-checked these additional areas and found no new issues:

- **Recommendation logic**: `_recommendations` only fires "Build or refresh" when `story_count == 0`, not when `edition_payload is None` (which correctly returns a zero-count `RowOneArticleReadinessStoryCoverage`). The payload test with `edition_payload=None` expects that recommendation and gets it. ✓
- **`test_article_readiness_counts_...` assertions**: With two sources (one `row_one_enabled=True`, one `False`), both default-enabled, the `enabled_sources=2` assertion is consistent with `_source_summary` counting `source.enabled` (not `row_one_article.enabled`). The story coverage math — eligible=1, disabled=1, missing=1 — is correct for the three stories provided. ✓
- **`assert not readiness.recommendations`** in the same test: `story_count=3` (not 0), `article_enabled_sources=1` (not 0), `eligible_story_count=1` (not 0) — none of the three recommendation conditions fire. ✓
- **First-run docs phrase `"does not require saved article sidecars"`**: Matches the proposed docs text verbatim. ✓
- **`"row_one_article.enabled: true"` in text-output test**: The minimal config sets all sources to `row_one_article.enabled: false`, so `article_enabled_sources == 0`, which triggers the recommendation containing that exact substring. ✓
- **Stage 315 sentinel slicing (`Stage 315 adds … Stage 310 adds`)**: Consistent with the stated insertion order (315between 314 and 310). ✓

---

### No Critical or Important findings. Ready to implement.

---

### Minor / Nit (deferred, no action required before implementation)

- **M1 (carried)**: No test for `ConfigError` path when `sources.yaml` is missing. The branch is structurally identical to other commands; safe to defer.
- **M2 (carried)**: The Stage 314 boundary update in `test_row_one_docs_describe_local_article_observability_boundary` is described in prose rather than literal code. Intent is unambiguous; an implementor will not be confused.
- **M3 (carried, deliberate)**: Text output omits `organized_section_count` and `source_count`; JSON mode includes them. Acknowledged as intentional scope choice.
