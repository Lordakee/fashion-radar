# Stage 254 Post-Mainline Boundary Docs Polish Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans.

**Goal:** Post-mainline polish flagged by the Stage 253 final release review: (1) update the `docs/architecture.md` "## Source Boundary" opt-in-social sentence from "Phase 2: Xiaohongshu" to all four social platforms (Phase 2-5), with its guard test; (2) add a dedicated Xiaohongshu opt-in docs-guard in `tests/test_source_boundaries_docs.py` for symmetry with the Instagram/Twitter/YouTube guards.

**Architecture:** Docs + docs-guard only; no code/schema/dep change. The Collectors bullet (`architecture.md`) already lists all four social; this fixes the stale "## Source Boundary" prose + closes the XHS guard asymmetry.

**Tech Stack:** Markdown, Python docs-guard, `uv --no-config run --frozen`, Claude Code + opencode review.

## Scope

**In:**
- `docs/architecture.md` "## Source Boundary": "Opt-in social-platform collection (Phase 2: Xiaohongshu) is use-at-your-own-risk, non-core, ..." → "Opt-in social-platform collection (Phase 2-5: Xiaohongshu, Instagram, Twitter/X, YouTube) is use-at-your-own-risk, non-core, ...".
- `tests/test_architecture_boundary_docs.py`: update the pinned phrase from "opt-in social-platform collection (phase 2: xiaohongshu) is use-at-your-own-risk" to "opt-in social-platform collection (phase 2-5: xiaohongshu, instagram, twitter/x, youtube) is use-at-your-own-risk".
- `tests/test_source_boundaries_docs.py`: add `test_source_boundaries_docs_describe_xiaohongshu_opt_in` asserting a Xiaohongshu-specific anchor ("xiaohongshu (小红书) via xiaohongshu-mcp") + login-required + use-at-your-own-risk + no demand proof / no coverage verification (parity with the Instagram/Twitter/YouTube guards).

**Out:** any code/schema/dep change; the Stage 210 markdown-snippet work (separate stage).

## Tasks (summary)

- **Task 0 (plan review):** Claude Code; opencode revises. `docs/reviews/claude-code-stage-254-plan-review.md`.
- **Task 1 (docs + guards, RED→GREEN):** update architecture + its guard; add XHS guard.
- **Task 2 (focused + Claude Code code review + full gate + commit):** "Stage 254: post-mainline boundary docs polish".

## Verification

Docs-guard modules green; full release gate green; `git diff --exit-code -- uv.lock pyproject.toml` exits 0.

## Self-Review

- Docs + guard only; no code/schema/dep change.
- Removes the "Phase 2 only" staleness + closes the XHS guard asymmetry flagged by the final review.
