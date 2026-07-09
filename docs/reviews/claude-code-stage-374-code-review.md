All2656 tests pass. Here are the findings.

---

## Critical

None.

---

## Important

**1. `_html_contains_href` uses literal string matching — fragile for generated-site changes**

`local_article_route_health.py:140-145`

The check only matches `href="..."` or `href='...'`. It does not handle spaces around `=`, mixed-case `HREF`, or a `./`-prefixed path (`href="./articles/index.html"`). For today's generator output this is correct, but the route health logic will silently report `missing` links if the renderer ever changes its href formatting. There is no test that documents the exact href format the generator produces and that this check relies on.

**Recommendation:** Either add a comment on `_html_contains_href` naming the generator convention it depends on, or add a narrow test that calls the real renderer and asserts the href format is exactly `href="<path>"`.

---

**2. `_resolve_story_ids` silently accepts a bare `str` as a single-element collection**

`local_article_route_health.py:121-137`

The public type annotation is `story_ids: Iterable[str] | None`. A bare `str` is a valid `Iterable[str]`, but iterating it would yield individual characters — almost certainly all failing `safe_local_article_story_id`. The implementation guards against this with `isinstance(story_ids, str)`, wrapping it in a one-tuple. The test at line 153 exercises this path, so the behavior is intentional. But the guard is invisible to callers: someone removing it in the future would silently break the string case with no type error. The annotation should either be tightened to exclude `str` (`Sequence[str] | None` or `list[str] | set[str] | None`) or explicitly documented.

---

**3. `validate_row_one_local_article_route_health` only surfaces the first failure condition**

`local_article_route_health.py:94-114`

The validator raises on the first truthy condition in priority order: missing library → missing homepage link → missing article pages → missing library links. The spec lists all four error messages as independently reachable, but with this order a site that has both a missing homepage link and missing article pages shows only the homepage link error. An operator who fixes the link and re-runs status will immediately see the next error. This is not a bug in normal operation, but the spec's four-message list implies each condition has equal diagnostic reach. No test covers a multi-condition `missing` object to confirm expected error priority.

---

## Minor

**4. Unreachable fallthrough `raise` in `validate_row_one_local_article_route_health`**

`local_article_route_health.py:114`

```python
raise ValueError("row-one local article route health is missing")
```

Given the construction logic in `build_row_one_local_article_route_health`, `status == "missing"` implies at least one of `not library_present`, `not homepage_library_link_present`, `missing_article_pages`, or `missing_library_links` is truthy. The fallthrough can never fire. It is harmless defensive code but is dead code.

---

**5. `not_applicable` dataclass carries misleading boolean flags**

`local_article_route_health.py:29-37`

When there are no sidecars the returned object has `library_present=False` and `homepage_library_link_present=False`. A consumer reading the JSON payload sees `"library_present": false` under `"status": "not_applicable"` — technically accurate but semantically inconsistent with the other fields being meaningful only when `article_count > 0`. The spec is silent on what values these flags should hold for `not_applicable`. No change required, but a code comment would help.

---

**6. `test_stage_374_saved_local_article_route_health_stays_generated_site_only` does not strictly verify non-invocation during generation**

`tests/test_workflows.py` (new test)

The test monkeypatches `build_row_one_local_article_route_health` and `validate_row_one_local_article_route_health` to no-ops and then delegates to the full site-write test. Because the site-write path never calls those functions, the monkeypatching has no effect on the test outcome — it passes regardless of whether the patch is present. The real boundary guarantee comes from the contract payload assertions (`"local_article_route_health" not in generated_contract_payload` etc.), which are inherited from the base test. The monkeypatching overstates the isolation proof. Not a defect in coverage, but the test's expressed intent is not what it actually enforces.

---

**7. `not_applicable` payload shape is not covered by `test_route_health_payload_is_stable`**

`tests/test_row_one_local_article_route_health.py:183-200`

The stable-payload test only exercises the `ready` path. If the `not_applicable` shape ever diverged (e.g. omitting a key), no test would catch it. The dataclass equality test (`test_route_health_is_not_applicable_without_saved_article_sidecars`) would still pass. A complementary `row_one_local_article_route_health_payload(...)` assertion for the `not_applicable` object would close this gap.

---

**8. Human `row-one status` and `row-one ops-check` report different levels of detail for route health**

`cli.py:2240-2244` vs `cli.py:2370`

`status` prints `Local article routes: ready (1 saved local article)` (with count), while `ops-check` prints `Local article routes: ready` (status only). This asymmetry is intentional per spec. No change needed, but it means an operator switching between the two commands sees a different verbosity level for the same signal. Worth documenting if the outputs are compared side-by-side.
