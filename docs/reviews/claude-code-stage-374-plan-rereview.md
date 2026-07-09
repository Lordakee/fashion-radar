## Re-Review: Stage 374 Saved Local Article Route Health

### Critical

None remain.

### Important

None remain. All five prior Critical/Important findings are resolved:

1. **Renderer route assumptions explicit in tests** ✅ — `test_row_one_status_json_includes_local_article_route_health` and `test_row_one_status_prints_local_article_route_health` now assert the four route/link conditions on the filesystem before invoking the CLI. A renderer that doesn't emit `articles/index.html`, `articles/<story-id>.html`, `href="articles/index.html"` in `index.html`, or the story-id link in the library page will now produce an explicit, actionable assertion failure rather than a confusing `status == "missing"` CLI failure.

2. **Status JSON reuses strict validated route-health object** ✅ — `validate_row_one_generated_site_integrity(...)` now returns the `RowOneLocalArticleRouteHealth` it built with `story_ids=article_sidecars.keys()`, and `row_one_status(...)` passes that exact object to `_build_row_one_status_payload(...)` as `local_article_route_health=`. No second filesystem discovery pass occurs; `article_count` in the JSON reflects the pre-validated sidecar set.

3. **Validator tests cover all four error branches** ✅ — `test_validate_route_health_raises_clear_errors` now specifies all four `pytest.raises` blocks with the correct `match=` patterns: `"articles/index.html"`, `"library link is missing from index.html"`, `"local article route is missing: articles/"`, and `"library page is missing article link"`.

4. **`_overall_status` priority order explicit** ✅ — The full function body is shown. The `unknown` guard (`site not present` or `freshness unknown`) fires first; the `local_article_routes.get("status") != "missing"` condition is folded into the `ready` gate, so a missing route produces `attention`, not `unknown`.

5. **`story_ids` typed as `Iterable[str] | None`** ✅ — Both `build_row_one_local_article_route_health` and `_resolve_story_ids` now carry `Iterable[str] | None`, which accurately expresses the contract and enables type-checker enforcement at call sites.

---

### Minor

Two new minor observations in the updated plan:

**M1. Trailing duplicate assertion in `test_row_one_status_json_includes_local_article_route_health`.**
Line 413 re-asserts `(tmp_path / "articles" / f"{story['id']}.html").is_file()` — identical to the pre-invocation assertion already made at line 390. Harmless, but the duplicate adds noise and could mislead a reader into thinking it is checking a post-invocation side-effect.

**M2. `isinstance(story_ids, str)` guard in `_resolve_story_ids` lacks an explanatory comment.**
The guard wraps a bare string into `(story_ids,)` to prevent character-by-character iteration if a single story ID is passed as a string. The existing comment explains the `safe_local_article_story_id` filter but not this wrapping. A one-liner — `# wrap a bare string so a single story-id isn't iterated character-by-character` — would make the intent self-evident.

Both existing Minor findings from the prior review (M6 comment on re-validation, M7 `missing_library_links=()` when library absent, M8 single-quote comment, M9 `_actions` full signature) have also been addressed.
