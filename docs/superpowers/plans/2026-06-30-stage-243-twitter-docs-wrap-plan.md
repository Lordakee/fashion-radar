# Stage 243 Phase 4 Twitter Docs + Release Wrap Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans.

**Goal:** Close Phase 4 (X/Twitter) with docs (cli-reference, source-packs, architecture, source-boundaries Opt-In), a docs-guard, CHANGELOG wrap, a Phase 4 release review by Claude Code, and a consolidated release gate. Mirrors Stage 233 (Phase 3 wrap).

**Architecture:** Docs + docs-guard + verification + review only; no new code. Twitter collector (242) + plumbing (241) landed; boundary already opt-in (221).

**Tech Stack:** Markdown, Python docs-guard, `uv --no-config run --frozen`, Claude Code + opencode review.

## Scope

**In:**
- `docs/cli-reference.md`: add `twitter` to the `collect` bullet.
- `docs/source-packs.md`: new "## Twitter / X (Opt-In)" section with config example + twitter-cli install guidance + live-verification caveat.
- `docs/architecture.md`: Collectors bullet — add Twitter (opt-in, cookie/browser-login, use-at-your-own-risk).
- `docs/source-boundaries.md`: Opt-In list — add Twitter (via twitter-cli, cookie/browser-login, use-at-your-own-risk, no demand proof / no coverage verification).
- docs-guard: pin Twitter opt-in wording in `tests/test_source_boundaries_docs.py`.
- `CHANGELOG.md`: Phase 4 wrap entry.
- `docs/superpowers/specs/2026-06-30-phase4-twitter-design.md`: Status → Complete.
- Phase 4 release review → `docs/reviews/claude-code-stage-243-release-review.md`.

**Out:** YouTube (Phase 5); any code/schema/dep change.

## Tasks (summary)

- **Task 0 (plan review):** Claude Code; opencode revises. `docs/reviews/claude-code-stage-243-plan-review.md`.
- **Task 1 (docs + guard + changelog, RED→GREEN):** add Twitter opt-in wording to the 4 docs; pin in docs-guard; CHANGELOG Phase 4 wrap; spec Status.
- **Task 2 (release verification + Claude Code release review + commit):** full gate (incl. packaging/installed-wheel smoke); `claude --effort max ...` Phase 4 release review; commit "Stage 243: Phase 4 Twitter docs and release wrap"; push.

## Verification

Docs-guard green; full release gate green (incl. packaging/installed-wheel smoke); `git diff --exit-code -- uv.lock pyproject.toml` exits 0.

## Self-Review

- Docs-only wrap; no code/schema/dep change.
- Opt-in/use-at-your-own-risk framing consistent with Stages 221-233.
- Live-verification caveat for twitter-cli JSON documented.
- Only YouTube (Phase 5) remains.
