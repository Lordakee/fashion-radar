# Stage 213Plan Review

**Verdict:** APPROVE_WITH_NITS

## Critical

None.

## Important

**1. `published_at=None` silent blow-up when `started_at` is not passed**

`_published_at(raw, started_at)` falls back to `started_at`, but `collect(self, source, *, started_at=None)` accepts `None`. If trafilatura returns no date and `started_at` is `None` (direct test call or future caller), `CollectedItem(published_at=None)` raises a Pydantic `ValidationError` from inside the `try` block — the runner catches it as `CollectorResult.failed`, which is the wrong outcome. Fix: at the top of `collect`, bind `started_at = started_at or datetime.now(tz=UTC)` (same pattern the runner uses at `runner.py:48`), or make `_published_at` fall back to `datetime.now(UTC)` when both args are falsy. The helper description in the plan only says "except → started_at", which silently propagates `None`.

**2. Missing explicit TDD cases for the two named fallbacks**

The plan describes `_fallback_title` and `_published_at` as implementation helpers but does not list tests for them in the Task2 test enumeration. Given the TDD mandate these should be explicit:

- *title fallback*: trafilatura JSON has no `"title"` key (or empty string) → `CollectedItem.title` is the URL-derived string from `_fallback_title`, not empty.
- *published_at parse failure*: trafilatura returns an unparseable date string → `CollectedItem.published_at` equals `started_at`, not a `ValidationError`.

Both are reachable production paths; both need a test to survive the TDD gate.

**3. Spec / plan divergence on `extract_article` vs `extract_article_with_metadata`**

Section 5.4 of the spec says "reuse `collectors.article.extract_article`", but the plan (correctly) calls the new `extract_article_with_metadata` to capture title + date. The spec is stale on this detail. No code risk, but the doc-update task (Task 3) should update Section 5.4 so the spec matches the implementation.

## Nits

**N1. JSON API note for future readers.** `trafilatura.extract(output_format="json")` returns `None` (not `"{}"`) when nothing is extracted — the `if not raw` guard handles this. The date key is `"date"`, which the plan uses correctly. No change needed, just worth a brief inline comment in `extract_article_with_metadata` near the `json.loads` block so the next reader doesn't have to verify the API again.

**N2. Redundant per-URL `trafilatura is None` check.** `extract_article_with_metadata` guards `if trafilatura is None: return _skipped(url, "extractor_unavailable")`. When called from `HtmlCollector.collect`, this is unreachable (the run-level `extractor_available()` gate fires first). The guard is still correct to keep — it makes `extract_article_with_metadata` self-contained for reuse by Stage 214's `SitemapCollector` — but a one-line comment noting this prevents a future reader from deleting it as "dead code".

**N3. Runner test isolation confirmed — no action needed.** Stage 212's enrichment-skip test uses `SuccessfulCollector` fakes with a custom `collectors=` dict; `HtmlCollector` is never instantiated. Switching to real extraction does not affect it. ✓

**N4. `CollectorResult.skipped` signature match confirmed.** `base.py:93` signature is `skipped(source, *, reason, started_at, finished_at)`. The plan's call `CollectorResult.skipped(source, reason="extractor_unavailable", started_at=started_at)` is an exact match. ✓

**N5. `get_response` → `RobotsResponse` protocol confirmed.** `httpx.Response` has both `status_code: int` and `text: str`, satisfying the `RobotsResponse` structural protocol at `robots.py:10–12`. ✓

## Résumé

Architecture solide : l'approche additive préserve `extract_article` intact, le JSON trafilatura est correctement géré (`"date"`, `"title"`, `"text"`), la fermeture du client en `finally` est propre, et l'isolation des tests du runner est confirmée. Un seul correctif technique est vraiment nécessaire avant le TDD : initialiser `started_at` en tête de `collect` pour éviter le `ValidationError` silencieux sur `published_at=None`. Les deux cas de test manquants (titre de repli, échec de parsing de date) doivent être ajoutés à la liste Task 2 — ce sont des chemins de production réels couverts par les helpers mais absents de l'inventaire de tests.
