## opencode Stage 379 Code Review — Saved Local Article Cross-Surface Organization Trail

### Critical
None.

### Important
None.

### Minor

1. **Regex anchor inconsistency (cosmetic, zero behavioral impact).** The organization-group-key allow-list is defined twice with slightly different patterns:
   - `saved_article_local_reading_companion.py:38` → `r"[a-z][a-z0-9_]{0,63}"` (no `$`), used via `.fullmatch()`.
   - `templates.py:195` → `r"[a-z][a-z0-9_]{0,63}$"` (trailing `$`), also used via `.fullmatch()`.

   `.fullmatch()` already anchors both ends, so the `$` is redundant and both accept the identical key set (verified: `1bad`, `-bad`, `../bad` rejected; `entities`, `top_stories` accepted). The two render-time validators and the builder therefore agree. No action required; dropping the `$` in `templates.py` would simply make the two definitions textually identical.

### Verification performed
- **Correctness of builder** (`saved_article_local_reading_companion.py:159-199`): `_filing_links` emits at most two links. `_organization_group_href` validates `group.key` against the strict allow-list before emitting `index.html#saved-article-organization-group-<key>`. `_library_card_href_from_detail_path` derives the story id from the canonical `current_detail_path` (not raw `story.id`), requiring `validated_row_one_detail_relative_path`, `parent.name == "details"`, `.html` suffix, and `safe_local_article_story_id`. Unvalidated keys/paths cleanly omit the corresponding link. `_filing_links` is only reached after the `local_links`/`related_items` non-empty guard, so no trail is built for a companion that would not render.
- **Anchor existence** (the core correctness risk): `render.py` builds a single `saved_article_content_organization` and passes the same object to both `render_saved_article_library_html` (→ `_render_saved_article_content_organization_group`, which now emits `id="saved-article-organization-group-<key>"`) and `build_row_one_saved_article_local_reading_companion`. The companion's matched `group` is therefore the same group object rendered in `articles/index.html`. The group anchor is only emitted when the group renders ≥1 card (`templates.py:15074`), and the matched group always contains the current card, so the target cannot be an empty group. Group keys originate from the fixed `_GROUPS` tuple iterated once (`saved_article_content_organization.py:86`), so duplicate in-document IDs are not possible. The card-anchor agreement test (`test_saved_article_cross_surface_card_href_matches_library_card_anchor`) confirms the article-page `index.html#saved-article-library-card-<story-id>` resolves to the library card's `id`, since both derive `<story-id>` from the same canonical `details/<story-id>.html` path (the entry matched by `current_detail_path`).
- **Href safety** (`templates.py:9369-9406`): `_saved_article_local_reading_companion_href` rejects whitespace, `http:`/`https:`/`//`/`javascript:`, then handles same-page `#` anchors, then delegates to `_saved_article_local_reading_companion_cross_surface_href`, which accepts *only* `index.html#saved-article-library-card-<safe-story-id>` and `index.html#saved-article-organization-group-<safe-group-key>` (rejecting all other page paths, absolute/dot-relative paths, and unknown fragments), then falls through to the existing `_saved_article_read_next_cluster_href`. The filing-trail renderer additionally requires `startswith("index.html#")` and `_esc`-escapes both href and labels. The unsafe-href render test confirms external URLs and unknown fragments are dropped while the safe card href survives.
- **Relative-path context**: article pages live at `articles/<story-id>.html`; `index.html#...` correctly resolves to the sibling `articles/index.html`, matching the acceptance criteria. Detail pages (`details/<story-id>.html`) are unaffected and the trail is asserted absent there.
- **Generated-site-only boundaries**: no new JSON artifact, route family, schema, app/runtime/manifest key, or standalone HTML page. The no-leakage render test asserts Stage 379 denylist strings (including `内容归档`) are absent from edition/manifest/runtime JSON and that no trail-named artifacts are written. The workflow monkeypatch test (`test_stage_379_..._stays_generated_site_only`) patches `row_one_render.build_row_one_saved_article_local_reading_companion` with `raising=True` to strip `filing_links` and reuses the broad local-article sentinel, proving the field is presentation-only and does not affect app-facing contracts or SQLite behavior.
- **CSS refactor** (`templates.py:2544-2576`): the `color: var(--ink)` declaration was correctly split out of the shared border selector so that filing-trail/links `<a>` elements receive `var(--accent)` while non-link spans retain `var(--ink)`; `.saved-article-local-reading-companion-links a` end-state is unchanged (still `var(--accent)`), so no visual regression. The CSS-selector guard test was extended.
- **Docs**: the Stage 379 boundary paragraph is inserted above Stage 378 in both `README.md:256` and `docs/row-one.md:473`, matching the docs test which asserts ordering and scoped stale-phrase checks.
- **Tests**: focused suite (400) and full suite (2733) pass; `ruff check` clean on all eight touched files. Builder, render, anchor-resolution, href-filtering, no-leakage, workflow-sentinel, and docs-boundary coverage are all present and consistent with the plan.

Overall: clean, well-scoped, generated-site-only implementation with strong anchor-existence and href-safety guarantees. Approved.

END_OF_REVIEW
