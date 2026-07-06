After reading all the relevant files — the builder, templates, render integration, all test files, and the safety validators — here is the assessment.

---

## Stage 316 Code Review

### No Critical issues.
### No Important issues.

The implementation is clean. Full walkthrough:

**Builder correctness (`saved_article_content_organization.py`)**

Every filtering requirement is covered in order:
- Article not in edition → naturally excluded (builder iterates `edition.stories`, not articles)
- `article.story_id != story.id` → skipped (line 94)
- Invalid story ID → `safe_local_article_story_id` (line 96)
- Unsafe detail path → `is_safe_row_one_detail_path` (line 98)
- Blank local article body → `_has_nonblank_paragraph` (line 100)
- Empty/unusable section → `_first_usable_section` + `_item_has_usable_content` (line 102)
- No lead text extractable → `_lead_text` returns None → skip (line 106–108)

Group order matches spec exactly (`_GROUPS` tuple): `takeaways → entities → product_signals → brand_signals`. Cap of 4 cards per group is enforced with an early `break` (line 121), not a post-filter, which is correct.

Fragment anchors use `enumerate(sections, start=1)` so the position is the 1-based index into `article.content_sections` — matching the detail-page render convention. The test at line 217 pins this explicitly:

```
card.detail_path == "details/the-row-a-1234567890.html#local-article-content-section-1"
```

`_paragraph_indices` correctly: collects from all items in the section, skips negative indices and indices≥ `len(article.paragraphs)`, skips blank paragraphs, dedupes first-seen. Zero-based throughout.

Reference deduplication normalizes via `.casefold()` + `" ".join(.split())` (collapse whitespace + case-fold) before the set key, then stores the stripped original. The test at line 219 confirms `" the row "` / `"Brand"` / `"Tracked"` collapses to the first-seen canonical form.

**Link sanitization (`templates.py`)**

`_safe_saved_article_content_organization_href` correctly splits on `#`, applies `_LOCAL_ARTICLE_CONTENT_SECTION_FRAGMENT_RE.fullmatch` (pattern `local-article-content-section-[1-9][0-9]*`), then validates the path with `validated_row_one_detail_relative_path`. All user-visible text is routed through `_esc()`.

**Homepage order**

In `render_index_html` (line 158–163):
```
{saved_article_briefs_section}
{saved_article_content_organization_section}
{lead_story_block}
...
{story_cards}
```

Correct — after briefs, before story sections.

**Boundary compliance**

`render_row_one_site` passes the built organization only to `render_index_html`. No JSON artifact is written. The workflow test at `test_workflows.py:359` asserts `'"saved_article_content_organization"' not in generated_contract_payload`, which guards the contract boundary.

**`list` vs `tuple` in frozen dataclasses**

`RowOneSavedArticleContentOrganizationGroup.cards` and `RowOneSavedArticleContentOrganization.groups` use `list`. This is consistent with `RowOneSavedArticleBriefs.items` (line 34) and `RowOneSavedArticleCoverage.items` (line 36) — the same pattern the two prior-stage builders use. Not a finding.

**Test coverage**

All paths exercised: group ordering, reference deduplication, paragraph index deduplication, invalid/mismatched/unsafe exclusions, cap-at-4, and all three `None`-return paths. The boundary docs test and contract isolation test are also present and passing per the verified run.

---

No findings. Safe to commit.
