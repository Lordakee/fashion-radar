# Stage 380 Plan Review - opencode

## Critical

**1. Stage 380 workflow test calls a helper `_assert_generated_site_only_surface(...)` that does not exist anywhere in the codebase.**

The plan's Task 6 Step 1 references `_assert_generated_site_only_surface(...)`, but the helper is not defined or imported in `tests/`. Existing sibling stages use the established pattern of monkeypatching a specific render function to return an empty string and then calling `test_write_row_one_site_files_writes_local_article_without_mutating_sqlite(tmp_path)`. Rewrite Task 6 Step 1 to use that pattern, and add the Stage 380 contract-key and artifact-stem strings directly to the existing inline denylist assertions.

## Important

**1. The Stage 380 workflow test targets the wrong render function and is redundant with Stage 377.**

The plan currently monkeypatches `_render_saved_article_local_related_reads`, which Stage 377 already neutralizes. Because Stage 380 renders inside a new bridge helper under related-read cards, the Stage 380 generated-site-only test should monkeypatch `_render_saved_article_local_related_read_evidence_bridge` after it is added, so the parent related-read section still renders while only the bridge surface is removed.

**2. Contract-payload and artifact denylist additions are incomplete relative to the established convention.**

The plan adds snake_case and kebab-case variants but omits class-name, human-title, and render-copy variants. Add `RowOneSavedArticleLocalRelatedReadEvidenceBridge`, `Saved Local Article Related-Read Evidence Bridge`, `Evidence bridge`, `证据连接`, `Here ¶`, `Next read ¶`, `本文 ¶`, and `下一篇 ¶` to the contract-payload denylist. Add the title/class-name style variants where applicable to the artifact-stem coverage for consistency with adjacent stages.

## Minor

**1. CSS regression test is not extended for the new bridge selectors.**

Extend `test_row_one_css_includes_saved_article_local_related_reads_styles` with the new `.saved-article-local-related-read-evidence-bridge*` selectors.

**2. `_safe_saved_article_local_related_read_current_href` can be simpler.**

The implementation can accept only hrefs starting with `#` whose fragment matches `_LOCAL_ARTICLE_PARAGRAPH_FRAGMENT_RE`; every other form is rejected by construction.

**3. `_evidence_bridges` has a harmless defensive recheck.**

The plan filters mapped entries with `_first_valid_entry_paragraph(...)`, then rechecks the selected entries when rendering bridge rows. This is defensive and not a blocker.

**4. `_candidate(...)` signature update should be explicit.**

Task 3 should show the new `current_ref_entries_by_key: Mapping[str, _ReferenceEntry]` parameter in `_candidate(...)`.

END_OF_REVIEW
