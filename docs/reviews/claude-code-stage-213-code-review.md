# Stage 213 Code Review

**Verdict:** APPROVE_WITH_NITS

---

## Critical

None.

---

## Important

**`extraction_failed` skip reason untested for `extract_article_with_metadata`** (`tests/test_collectors_article.py`)
The spec lists `extraction_failed` among the skip reasons that must be covered. Every other reason (`disabled`, `paywalled_domain`, `extractor_unavailable`, `robots_disallowed`, `no_extractable_text`) has a dedicated test, but there is no test that makes `html_fetcher` or `trafilatura.extract` raise and asserts `reason == "extraction_failed"`. The code path is trivially correct, but the gap contradicts the stated coverage goal.

**README forward-references Stage 214** (`README.md`, line 35)
> "plus configured HTML seed pages **(and sitemap discovery)** via trafilatura"

Stage 213 explicitly excludes sitemap discovery; that lands in 214. `CHANGELOG.md` and `source-boundaries.md` are correctly scoped. README is the only public-facing doc that asserts it already works.

---

## Nits

**Spec step 3 still says `source_url=url`** (`docs/superpowers/specs/…-design.md`, step 3 of the HtmlCollector section)
The actual field in `CollectedItem` is `url=`, not `source_url=`. Step 3 also says "title from trafilatura metadata or `<title>`" but the fallback is URL-path-segment / netloc, not HTML `<title>` parsing. Step 2 was correctly updated; step 3 was not.

**`type(…, (), {…})()` should be `SimpleNamespace(…)`** (`article.py`, `extract_article_with_metadata` robots fallback branches)
Both inline anonymous-class constructions (`RobotsCheckFallback`) are in a position where `SimpleNamespace(allowed=..., reason=...)` is both clearer and the established pattern in the test file for the same purpose.

**`reason = "allowed"` in the `can_fetch` branch is dead** (`article.py`, same block)
When `can_fetch` returns `True`, the synthesised `check.reason` is `"allowed"`, but `check.allowed=True` means the skip branch is never reached and the value is never read. Harmless but confusing.

**`UnavailableRobots` (`.check()`) branch not exercised for `extract_article_with_metadata`** (`tests/test_collectors_article.py`)
`UnavailableRobots` is used to test `extract_article` but not `extract_article_with_metadata`, leaving the `hasattr(robots_checker, "check")` branch of the new function uncovered at unit level. Minor, since the production `RobotsPolicyChecker` uses `.check()` and pytest passes, but a small copy-paste of the existing `test_extract_article_reports_robots_unavailable` case would close it.

---

## Résumé

The implementation is correct and well-scoped: `extract_article` is untouched, `extract_article_with_metadata` cleanly adds JSON-mode extraction with all six skip reasons, `HtmlCollector` correctly binds `started_at`, fail-closes on `extractor_available()`, resolves seeds, manages the HTTP client lifetime, and satisfies both `CollectedItem` contracts (non-empty title, non-None `published_at`). The HTML test suite is thorough. Two issues worth a follow-up commit: add an `extraction_failed` test case, and remove the premature sitemap mention from README.
