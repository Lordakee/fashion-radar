## Stage 377 Review — Saved Local Article Related Reads

---

### Critical

**1. `score <= 0` gate admits entries-only candidates with no relationship signal**
`saved_article_local_related_reads.py:174`

```python
if entries:
    score += 5
if score <= 0:
    return None
```

A candidate with non-empty `entries` (content sections) but *no* relationship signal — different section, different source, zero shared references — scores5 and passes the filter. The spec is explicit: "The builder should not create generic fill cards when no relationship signal is present." The fix is to guard on actual signals before scoring:

```python
if not shared_keys and not same_section and not same_source:
    return None
```

The existing `test_saved_article_local_related_reads_filters_unrelated_and_current_article` misses this because the `unrelated` article has *no content sections*, keeping its score at 0. A companion failure: `_reason` would return `"Same source desk"` for such entries-only candidates — a misleading label for a card that should never have been built.

---

### Important

**2. Entries bonus checks only the candidate, not both articles**
`saved_article_local_related_reads.py:172`

```python
if entries:# ← candidate only
    score += 5
```

Spec says "+5 when both articles have content sections." When the current article has no content sections, the bonus still fires, inflating scores by 5. Once finding #1 is fixed (gate on actual signals), this becomes a pure scoring deviation rather than a correctness hole, but it still contradicts the spec and could affect ordering in edge cases.

**3. `_companion_related_story_id_from_href` silently drops content-section fragments**
`render.py:492–498`

The extractor accepts only `#local-article-digest` and `#local-article-paragraph-N` fragments. If the companion builder ever assigns `#local-article-content-section-N` hrefs to `related_items` (which `_safe_saved_article_read_next_cluster_href` in templates accepts), those story IDs are silently excluded from `excluded_story_ids` and can appear in both the companion and the post-body related reads simultaneously. Current tests only exercise paragraph and digest anchors; no test covers a companion `related_item.href` with a content-section fragment.

---

### Minor

**4. Dead validation guards in `_safe_sibling_article_href`**
`saved_article_local_related_reads.py:214–227`

After `if clean != href or clean != expected: return None`, `clean` is guaranteed to equal `f"{story_id}.html"`. Every subsequent guard — `endswith(".html")`, whitespace check, `://`, starts-with, `/`, `\\`, `..` — is already provably false for any string of the form `<safe-story-id>.html`. The redundant checks are harmless but obscure the actual structure of the validation.

**5. Weak placement assertion in render test**
`tests/test_row_one_render.py:3543`

```python
assert article_body.index(...)< article_body.rindex("</div>")
```

`rindex("</div>")` matches the *last* `</div>` in the entire `article_body` slice, which includes closing tags for nested sections and cards. The assertion would still pass if `saved-article-local-related-reads` were placed inside the card HTML rather than after the article body proper. A tighter check — e.g., asserting the related-reads section appears after the `id="local-article"` section and before the first closing `</div>` that ends `local-article-page-article` — would be more precise.

**6. No test for entries-only, no-signal candidate**
`tests/test_row_one_saved_article_local_related_reads.py`

The test for unrelated candidates uses an article with no content sections. There is no test asserting that a candidate whose only "score" comes from having content sections (but no shared references, different section, different source) is excluded. This is the direct test gap that lets finding #1 go undetected.

END_OF_REVIEW
