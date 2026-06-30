# Stage 233 Phase 3 Instagram Docs + Release Wrap Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans.

**Goal:** Close Phase 3 (Instagram) with docs (cli-reference, source-packs, architecture, source-boundaries Opt-In), a docs-guard, CHANGELOG wrap, a Phase 3 release review by Claude Code, and a consolidated release gate. Mirrors Stage 223 (Phase 2 wrap).

**Architecture:** Docs + docs-guard + verification + review only; no new code. The Instagram collector (Stage 232) and plumbing (231) already landed; the social boundary already evolved to opt-in (Stage 221). This stage makes the docs consistent and runs the consolidated Phase 3 release gate.

**Tech Stack:** Markdown, Python docs-guard, `uv --no-config run --frozen`, Claude Code + opencode review.

## Scope

**In:**
- `docs/cli-reference.md`: add `instagram` to the `collect` bullet.
- `docs/source-packs.md`: new "## Instagram (Opt-In)" section with config example + instaloader install/login guidance + live-verification caveat (instaloader API field names vary).
- `docs/architecture.md`: Collectors bullet — add Instagram (opt-in, login-required, use-at-your-own-risk).
- `docs/source-boundaries.md`: Opt-In list — add Instagram (via instaloader, login-required, use-at-your-own-risk, no demand proof / no coverage verification).
- docs-guard: pin the Instagram opt-in wording in `tests/test_source_boundaries_docs.py` (Opt-In section).
- `CHANGELOG.md`: Phase 3 wrap entry.
- `docs/superpowers/specs/2026-06-30-phase3-instagram-design.md`: Status → Complete.
- Phase 3 release review by Claude Code → `docs/reviews/claude-code-stage-233-release-review.md`.

**Out:** Xiaohongshu (done), X (Phase 4), YouTube (Phase 5); any code/schema/dep change.

## Tasks (summary)

- **Task 0 (plan review):** Claude Code; opencode revises. `docs/reviews/claude-code-stage-233-plan-review.md`.
- **Task 1 (docs + guard + changelog, RED→GREEN):** add Instagram opt-in wording to the 4 docs; pin in docs-guard; CHANGELOG Phase 3 wrap; spec Status.
- **Task 2 (release verification + Claude Code release review + commit):** full gate (pytest, ruff, hygiene, lock, sync, smoke, packaging/installed-wheel smoke); `claude --effort max ...` Phase 3 release review; commit "Stage 233: Phase 3 Instagram docs and release wrap"; push.

## Verification

Docs-guard green; full release gate green (incl. packaging/installed-wheel smoke); `git diff --exit-code -- uv.lock pyproject.toml` exits 0.

## Self-Review

- Docs-only wrap; no code/schema/dep change.
- Opt-in/use-at-your-own-risk framing consistent with Stages 221/222.
- Live-verification caveat for instaloader API documented.
- Phase 3 release gate consolidated (per-stage gates already green).
