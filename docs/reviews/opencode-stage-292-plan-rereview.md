**Verdict: Yes — C1/C2/C3 are resolved in principle. Plan is implementable under TDD.**

Remaining **Important** issues to resolve during implementation (none are blockers):

1. **Cap application method is unspecified.** Plan says paragraphs are "capped by `source.article.max_summary_chars`" but doesn't define *how*: truncate concatenated total? hard-limit paragraph count then truncate? Truncating mid-sentence or including only the first paragraph materially affects both fair-use posture and user value. Pick one rule and unit-test the boundary.

2. **Detail-page scoping must be explicit.** Plan says stale cache is "not read" for current stories, but doesn't state that detail pages are generated *only* for stories in the current edition (not for any file present in `data/articles/`). Confirm detail render iterates current edition story IDs; otherwise orphaned JSON for rotated-out IDs could be served. Add a test.

3. **Source hostname-match tie-breaking is non-deterministic.** "Hostname matching against `source.url`/`seed_urls`" can match multiple sources sharing a host. Specify first-match-by-order vs. skip, and test it.

4. **Kill-switch precedence is undefined.** When both `ROW_ONE_LOCAL_ARTICLES=0` and `local_articles_enabled=True` are set, which wins? Specify (env should win for ops safety) and test.

5. **Default timeout fallback.** Plan defers timeout/retries to `source.http`, but doesn't state behavior when a `SourceDefinition` omits `http.timeout`. Confirm `FashionHttpClient`/`extract_article_with_metadata` already enforces a sane default cap so a misconfigured source can't hang the build; if not, add one.

**Critical: none remaining.**
