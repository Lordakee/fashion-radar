The Write tool isn't available in this read-only context, and the task asks me to output the review directly. Here it is:

# Stage 243 Plan Review

**Verdict:** APPROVE_WITH_NITS

## Critical

None.

## Important

- **Make the new docs-guard anchor on a Twitter-SPECIFIC phrase, or it protects nothing.** The plan says "pin Twitter opt-in wording in `tests/test_source_boundaries_docs.py`." The generic phrases that frame the Opt-In entry — `use-at-your-own-risk`, `no demand proof and no platform coverage verification`, and even `login-required` — already appear repeatedly in `docs/source-boundaries.md` (lines 240-251). A test built only from those would stay GREEN even if the Twitter entry were missing or wrong. Mirror the Instagram guard, which anchors on the specific `instagram via instaloader` (`tests/test_source_boundaries_docs.py:157-166`): the Twitter test must assert a Twitter-specific anchor such as `twitter via twitter-cli` plus a cookie/browser-session term. Add it as a NEW test function (don't edit existing ones) so existing guards stay intact.

## Nits

- **Preserve the "Fashion Radar handles no cookies/credentials itself" honesty in all four docs**, consistent with Xiaohongshu ("login owned by the tool"; `source-packs.md:117-121`) and Instagram ("never handles passwords"; `source-packs.md:139-144`). Twitter is a third credential variant: the user is logged into x.com in their *browser* and `twitter-cli` reads that cookie session (design spec lines 17, 24-25; runtime skip reason `login_required` in `tests/test_collectors_twitter.py`). It's still login-required, just cookie/browser-based — so appending Twitter to architecture's shared Collectors bullet (`docs/architecture.md:56`, trailing "— login-required, use-at-your-own-risk") is fine only if the per-collector parenthetical names twitter-cli / cookie-session so the shared qualifier stays accurate.

- **Enumerate the release gate** rather than "full gate (incl. packaging/installed-wheel smoke)" (Task 2 / Verification). This is the Phase 4 *consolidating* gate, so spell out the list for parity with Stage 233 / the Stage 210 precedent: `pytest`; `ruff check .`; `ruff format --check .`; `scripts/check_release_hygiene.py`; `uv lock --check`; `uv sync --locked --dev --check`; source-checkout smoke; installed-wheel/packaging smoke; `git diff --exit-code -- uv.lock pyproject.toml`; `git diff --check`; secret scan. The release-specific checks (installed-wheel smoke + lockfile guard) are already named and correct — this is completeness only.

- **Pin the source-packs config example to the real schema.** The new "## Twitter / X (Opt-In)" YAML should use `type: twitter`, `query:`, and a `twitter:` block with `max_tweets_per_run` (optionally `twitter_cli_path` / `output_format`) per `TwitterSourceSettings` (`src/fashion_radar/models/source.py:76-81`). There is no `login_user`-style field for Twitter (unlike Instagram), since login lives in the browser cookie session.

- **Scope-completeness matches precedent — confirm it's deliberate.** README MVP non-goals (`README.md:81-87`, "Phase 2 adds Xiaohongshu"), `docs/PROJECT_BRIEF.md`, and architecture's `## Source Boundary` summary (`docs/architecture.md:418-425`, "(Phase 2: Xiaohongshu)", guard-pinned at `tests/test_architecture_boundary_docs.py:35` and `tests/test_project_brief_docs.py:39-70`) keep generic/Phase-2 framing and are intentionally NOT updated per-phase — Stage 233 didn't add Instagram there either, so omitting them keeps "mirror Stage 233" discipline. The README "(Phase 2 adds Xiaohongshu)" parenthetical is now two phases stale; refreshing it would require touching its guard and exceeds this wrap's scope, so deferring is defensible.

## Summary

A disciplined docs-only wrap that faithfully mirrors the proven Stage 233 pattern.

1. **Docs scope / framing (Q1):** complete and consistent. Four docs + source-boundaries guard + CHANGELOG Phase 4 wrap + spec Status→Complete + Claude Code release review match Stage 233 exactly, and the opt-in / use-at-your-own-risk / no-demand-proof / no-coverage framing carries the Stage 221-233 lineage.
2. **Guard placement (Q2):** sound and non-breaking. A new focused test in `test_source_boundaries_docs.py` is additive; the architecture/CLI edits land on the Collectors bullet and `collect` bullet, which no existing guard pins (those pin the `## Source Boundary` section and the adapter table). HEAD is green — no enumeration guard forces Twitter docs, so Stage 242 landing code first left nothing RED. The one substantive ask is the Twitter-specific anchor (Important).
3. **Live-verification caveat (Q3):** included — the source-packs section carries the twitter-cli JSON tolerant-parse / inspect-on-first-run caveat, mirroring Xiaohongshu/Instagram and the design's field-mapping assumptions.
4. **Scope discipline (Q4):** clean — collector + plumbing already landed (Stages 241/242); Stage 243 is docs + guard + changelog + spec-status + reviews, with `git diff --exit-code -- uv.lock pyproject.toml` guarding against dep/schema drift. No code/schema/dep change.
5. **Release verification (Q5):** the consolidating gate including packaging/installed-wheel smoke and the lockfile guard is present; enumerate the remaining commands for parity (Nit).

No blockers. Address the Twitter-specific guard anchor and the nits during execution.
