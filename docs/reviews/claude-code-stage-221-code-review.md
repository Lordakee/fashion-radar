# Stage 221 Code Review

**Verdict:** APPROVE

## Critical
_(none)_

## Important
_(none)_

## Nits

**`tests/test_project_brief_docs.py:69-72` — identical tuple elements**
The `test_readme_keeps_project_brief_mvp_non_goal_parity` pair now has the same string for both `brief_phrase` and `readme_phrase`. Functionally correct (both documents use the identical phrase, both assertions will pass), but the symmetry makes it look like a copy-paste artifact rather than an intentional cross-doc parity check. A comment like `# same wording in both docs by design` would make intent clear. Not worth blocking.

## Résumé

All six criteria pass cleanly.

1. **Reversal is narrow** — social collection is framed as opt-in/use-at-your-own-risk throughout; Phase 2 is Xiaohongshu only;IG/X/TikTok stay deferred; no claim that social is a core feature anywhere.
2. **Caveats retained** — no full-platform coverage claim, no demand proof, no platform coverage verification, default workflow still excludes login-based collection, ToS responsibility added explicitly in `PROJECT_BRIEF.md` non-goals.
3. **PROJECT_BRIEF intra-doc consistency** — experimental list entry and non-goals both frame Xiaohongshu as opt-in with identical caveats; no contradiction.
4. **AGENTS.md invariant preserved** — "core workflow usable without … by default" scopes the prohibition correctly without deleting it.
5. **Docs-guard updated consistently** — old ban wording ("non-core platform collection is not part of v0.1.0", "No default connector that needs login cookies…") is gone from both test files; new assertions match the live doc wording exactly.
6. **Scope discipline held** — only `AGENTS.md`, `README.md`, three `docs/` files, and two test files changed; no code, schema, or dependency modifications.
