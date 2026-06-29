# Stage 221 Social Boundary Evolution Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Evolve the project's social-platform boundary from "forbidden" to "opt-in, user-login-required, use-at-your-own-risk" so the Phase 2 Xiaohongshu collector (Stage 222) is authorised, while retaining every still-true caveat (no full-coverage claim, no demand proof, no platform coverage verification, users respect ToS).

**Architecture:** Docs + docs-guard-test-only change. The reversal is narrow and specific (verified by grep): two assertion groups must change — (a) "No default connector that needs login cookies, proxy pools, CAPTCHA bypass, or paywall bypass" and (b) "non-core platform collection is not part of v0.1.0" — plus matching prose in AGENTS.md, README.md, docs/source-boundaries.md, docs/architecture.md, docs/PROJECT_BRIEF.md. Everything that says "no full-platform coverage claim", "no demand proof", "no platform coverage verification", "broad platform collection not in the DEFAULT workflow", or "users respect ToS" STAYS (still true). No source code, no schema, no dependency change.

**Tech Stack:** Markdown docs, Python docs-guard tests, `uv --no-config run --frozen pytest`, Claude Code + opencode (`glm-5.2 --variant max`) review.

## Scope

**In scope (the actual reversals):**
1. `docs/PROJECT_BRIEF.md` "Non-Goals For MVP": change the login-cookie bullet to opt-in framing; add an opt-in social note (Phase 2 = Xiaohongshu). **Also update the "Free-First Boundary" section's "Experimental sources can be added later" list (lines ~53–59)** so Xiaohongshu is no longer listed as a future-experimental item — annotate that Phase 2 activates it as an opt-in connector (or move the bullet to the Optional section). No test change (that block is untested), but it must stay consistent with the Non-Goals update so the two PROJECT_BRIEF sections do not contradict each other.
2. `README.md` "What It Does Not Do": mirror the PROJECT_BRIEF change (the parity test requires this).
3. `AGENTS.md`: lead paragraph + Scope Boundaries — reflect opt-in social (Phase 2: Xiaohongshu), keep core-workflow-without-login-by-default.
4. `docs/source-boundaries.md`: Connector Risk Tiers — add an explicit opt-in social tier note (login-required, use-at-your-own-risk); keep "Broad platform collection in the default workflow" out of scope (default still excludes social).
5. `docs/architecture.md` Source Boundary: "non-core platform collection is not part of v0.1.0" → opt-in social (Phase 2: Xiaohongshu) is use-at-your-own-risk, non-core, no demand proof / no coverage verification.
6. Docs-guard tests updated to the new wording:
   - `tests/test_project_brief_docs.py` (`test_project_brief_docs_keep_mvp_non_goals_boundary` + `test_readme_keeps_project_brief_mvp_non_goal_parity`).
   - `tests/test_architecture_boundary_docs.py` (`test_architecture_source_boundary_keeps_core_scope_and_local_import_limits`).
   - `tests/test_source_boundaries_docs.py` ("The project does not provide full social-platform coverage." STAYS — still asserted).

   (Counting note: "2 assertion groups" in the Architecture above = the ~8 individual asserted phrases named in the spec, counted by change-group, not by individual phrase.)

**Out of scope:** the Xiaohongshu collector code (Stage 222); Instagram/X/YouTube (Phases 3-5); any change to the still-true caveats; any source/schema/dep change; removing the "default workflow excludes broad platform collection" rule.

## Key wording contracts

The reversal must keep these phrases present (still asserted by docs-guards / required for honesty):
- "no demand proof", "no platform coverage verification", "full-platform ... coverage claim" caveats — UNCHANGED.
- "broad platform collection in the default workflow" remains out of scope — UNCHANGED.

The reversal changes these (new pinned wording):
- PROJECT_BRIEF + README (parity): "Login-based social-platform collection is opt-in and use-at-your-own-risk; it is not on by default, provides no demand proof and no platform coverage verification, and users are responsible for each platform's terms." (Phase 2 adds Xiaohongshu.)
- architecture Source Boundary: "Opt-in social-platform collection (Phase 2: Xiaohongshu) is use-at-your-own-risk and non-core; it provides no demand proof and no platform coverage verification."

## Tasks (summary)

- **Task 0 (plan review):** Claude Code reviews this plan (esp. the framing — is "opt-in/use-at-your-own-risk" the right reversal vs a harder "social now supported"?); opencode revises. `docs/reviews/claude-code-stage-221-plan-review.md`.
- **Task 1 (RED → GREEN):** update the docs-guard assertions first (RED), then rewrite the 5 docs to the new framing (GREEN). This includes the `docs/PROJECT_BRIEF.md` "Free-First Boundary" experimental-list update (Important: Xiaohongshu → Phase 2 opt-in; untested block, prose-only, must stay consistent with the Non-Goals update). Run the 3 docs-guard modules. **AGENTS.md lead-paragraph invariant (Nit 2):** the revision must PRESERVE the invariant that the CORE/default workflow needs no login cookies (only the opt-in social connector does) — scope the existing "no login cookies" sentence to the default workflow, do NOT delete it.
- **Task 2 (focused + Claude Code review + full gate + commit):** focused docs-guard pytest; ruff; full release gate; `claude --effort max ...` review; commit "Stage 221: evolve social boundary to opt-in use-at-your-own-risk"; push.

## Verification

Docs-guard green; full release gate green; `git diff --exit-code -- uv.lock pyproject.toml` exits 0; `git diff --check` clean.

## Self-Review

- Narrow, specific reversal (2 assertion groups + 5 docs) — not a blanket delete.
- Every still-true caveat retained (no full-coverage claim, no demand proof, no coverage verification, default workflow excludes broad collection, users respect ToS).
- Authorises Phase 2 Xiaohongshu (Stage 222) without overclaiming (IG/X/YouTube still deferred).
- No code/schema/dep change.
