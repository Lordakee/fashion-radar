Here are my findings from reading the spec, plan, and all relevant source files.

---

## Critical

**1. Plan assumes `render_row_one_site` produces `articles/index.html`, `articles/<story-id>.html`, and `href="articles/index.html"` in `index.html` — this is not verified in the plan.**

The status tests `test_row_one_status_json_includes_local_article_route_health` and `test_row_one_status_prints_local_article_route_health` both assert `status == "ready"`, which requires all four health conditions to be true. They rely entirely on `_render_status_site_with_local_article(tmp_path)` — the same fixture already used by status tests — producing those routes in the generated site. If the renderer doesn't emit the library link in `index.html` or doesn't generate `articles/index.html`, both tests will pass RED (module missing) but fail GREEN (status comes back `missing` instead of `ready`) with a confusing diagnostic. The plan should add an explicit assertion on the generated files *before* Task 2 Red tests, or provide a manual fixture variant that doesn't depend on renderer behavior.

---

## Important

**2. `local_article_routes` in the status JSON payload is computed by a second, independent call to `build_row_one_local_article_route_health(site_dir)` (discovery path) after the strict validator already ran it with `story_ids=article_sidecars.keys()` (validated-set path).**

The validator in `status_integrity.py` uses the pre-validated story ID set; `_build_row_one_status_payload` in `cli.py` runs discovery on the filesystem. On a valid site these agree, but the design means the filesystem is read twice and the JSON `article_count` reflects discovery rather than the validated set. The plan doesn't acknowledge this divergence or explain why independent discovery is preferable to threading the health object from `status_integrity.py` to the payload builder. The intent should be documented or the implementation should reuse the health object.

**3. `test_validate_route_health_raises_clear_errors` has only one error path shown in the plan; the other three validator branches have no specified test coverage.**

The plan shows one `pytest.raises(ValueError, match="articles/index.html")` example. The validator has four distinct raise paths (library absent, homepage link absent, article page missing, library link missing) plus a fallthrough. An implementor following only the plan sample will write a test with incomplete validator coverage. The plan should specify all four match patterns, e.g.:
- `match="library route is missing: articles/index.html"`
- `match="library link is missing from index.html"`
- `match="local article route is missing: articles/"`
- `match="library page is missing article link"`

**4. `_overall_status` modification is shown only as an addendum condition; the priority ordering against the existing `unknown` gate is not shown.**

The current `_overall_status` returns `"unknown"` first when the site is absent or freshness is unknown. The plan instructs adding `local_article_routes.get("status") == "missing"` → `"attention"`, but doesn't show the full modified function body. If an implementor inserts the new condition before the `unknown` guard, a site with a missing site directory could report `"attention"` instead of `"unknown"`. The plan must show the complete updated function to make the priority clear.

**5. `story_ids: object | None` is too loose a type annotation for `build_row_one_local_article_route_health`.**

The function accepts `object | None` and then iterates, filtering with `isinstance(story_id, str)`. Callers passing `dict_keys[str]` or `frozenset[str]` work fine, but the type admits anything (integers, nested lists) and silently drops non-strings rather than erroring. Use `Iterable[str] | None` to express the real contract and let type checkers catch misuse at call sites.

---

## Minor

**6. `_resolve_story_ids` re-validates supplied story IDs that `_load_article_sidecars` has already validated.**

When `story_ids` is supplied (strict status path), each ID was already validated by `_load_article_sidecars` — which raises `ValueError` on any unsafe stem. The re-application of `safe_local_article_story_id` is harmless but adds noise. A brief comment noting the defensive intent would clarify it is deliberate.

**7. `missing_library_links` is populated with all story IDs when `library_present` is False, producing a misleading dataclass state.**

When `articles/index.html` is absent, `_html_contains_href` returns `False` for every story ID (OSError path), so `missing_library_links` ends up as a full tuple. The validator correctly surfaces "library route is missing" before reaching link checks, so the user-facing error is right. But any consumer that reads the health dataclass directly (not through the validator) sees `missing_library_links` populated when the real cause is a missing library file. Consider setting `missing_library_links = ()` when `library_present` is `False`, or document the invariant.

**8. `_html_contains_href` single-quote fallback is undocumented.**

The helper checks both `href="..."` and `href='...'`. Since this only runs against self-generated HTML that uses double-quoted attributes throughout, the single-quote branch is dead code in practice. A short inline comment — `# generated HTML uses double-quoted attributes; single-quote branch is defensive` — prevents a future reader from wondering whether the generated site actually uses mixed quoting.

**9. Plan's `_actions` signature change inserts `local_article_routes` between `systemd` and the already-present `site_dir`; the existing positional position of `site_dir` is not called out.**

The current `_actions` signature ends with `site_dir: Path`. The plan says "Update `_actions(...)` signature" but the only snippet shown adds `local_article_routes` without spelling out that `site_dir` stays as the final argument. A positional swap here would silently break the refresh action string interpolation. The plan should show the
