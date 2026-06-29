# Phase 1 Release Review (Stage 216)

**Verdict:** APPROVE_WITH_NITS

---

## Critical

None.

---

## Important

**1. Missing opencode plan-revision artifacts for Stages 211–215.**
The iron-rule cycle is: plan → CC plan review → opencode revision → implement → CC code review. `docs/reviews/` has `claude-code-stage-N-plan-review.md` and `claude-code-stage-N-code-review.md` for all five stages, but no `opencode-stage-N-plan-review.md` for any of them (Stage 210 is the last one present). The primary-review gate was honoured; the revision step was not recorded. No functional defect, but the protocol was not fully followed.

**2. `architecture.md` "Source Boundary" section is stale.**
`docs/architecture.md:420` still reads: *"The core collector set is RSS, RSSHub-compatible feeds, and GDELT."* The Collectors bullet at line 56 is correct (mentions HTML seed collection and sitemap discovery), but the named "Source Boundary" heading directly contradicts it. A reader consulting that section gets the wrong picture.

---

## Nits

**N1. `AGENTS.md` Scope Boundaries are outdated.**
Line 67: *"`v0.1.0` core sources are RSS/Atom and GDELT."* HTML and SITEMAP are now core; this line was never updated. Low blast-radius since the actual collectors and source-boundaries docs are accurate, but it will confuse a future agent reading that file.

**N2. `source-packs.md` missing HTML/SITEMAP YAML examples.**
Spec §8 explicitly calls for "HTML/sitemap source examples + self-hosted RSSHub guidance" in `source-packs.md`. The RSSHub Docker section landed (Stage 215). The parallel HTML/sitemap YAML config examples did not. The CLI reference and architecture docs are correct; only the source-packs guide is missing the concrete snippets.

**N3. Unnecessary article-extractor construction for HTML/SITEMAP sources.**
`runner.py:73–74` creates a `FashionHttpClient` + `RobotsPolicyChecker` for enrichment whenever `source.article.enabled` is True — which is the default. For HTML/SITEMAP sources the enrichment is then correctly skipped at lines 93–96, and the client is properly closed, so this is not a correctness bug. Adding `and source.type not in {SourceType.HTML, SourceType.SITEMAP}` to the guard on line 73 would avoid the unnecessary allocation.

---

## Résumé

Phase 1 delivers its stated goal coherently: RSS/RSSHub + HTML seeds + sitemap discovery, all robots-respecting, all routed through the existing collector/runner/health infrastructure, with correct fail-closed behaviour when the optional `article` extra is absent. No social-platform, cookie, login, proxy, or demand-proof scope leaked. The fail-closed guard (`extractor_available()` → `CollectorResult.skipped`) is present in both `HtmlCollector` and `SitemapCollector`, and the runner's enrichment-skip guard (`source.type not in {HTML, SITEMAP}`) is correct. Review-flow docs accurately describe the iron rules; all five stages have Claude Code plan and code reviews. The two Important findings are a process-compliance gap (missing opencode revision records) and a single stale doc section — neither blocks the web-acquisition capability. Automated gates (1 551tests, ruff, hygiene, lock, smoke, wheel) all passed.
