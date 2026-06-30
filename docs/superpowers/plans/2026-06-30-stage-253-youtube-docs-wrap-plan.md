# Stage 253 Phase 5 YouTube Docs + Release Wrap (Final Mainline) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans.

**Goal:** Close Phase 5 (YouTube) and the entire social-acquisition mainline (Phases 1–5) with docs (cli-reference, source-packs, architecture, source-boundaries Opt-In), a docs-guard, CHANGELOG wrap (all 5 targets complete), a Phase 5 release review by Claude Code, and a consolidated final release gate. Also disambiguate the new live `SourceType.YOUTUBE` collector from the pre-existing `yt_dlp` *manual-import* external-tool adapter, and strip a trailing-whitespace blemish in the Stage 252 code-review artifact.

**Architecture:** Docs + docs-guard + verification + review only; no new code. YouTube collector (252) + plumbing (251) landed; boundary opt-in since Stage 221.

**Tech Stack:** Markdown, Python docs-guard, `uv --no-config run --frozen`, Claude Code + opencode review.

## Scope

**In:**
- `docs/cli-reference.md`: add `youtube` to the `collect` bullet.
- `docs/source-packs.md`: new "## YouTube (Opt-In)" section with config example + yt-dlp install guidance + live-verification caveat + a one-line note distinguishing the live `type: youtube` collector from the pre-existing `yt_dlp` manual-import external-tool adapter.
- `docs/architecture.md`: Collectors bullet — add YouTube (opt-in, no login, use-at-your-own-risk).
- `docs/source-boundaries.md`: Opt-In list — add YouTube (via yt-dlp, no login needed, use-at-your-own-risk, no demand proof / no coverage verification).
- docs-guard: pin YouTube opt-in wording in `tests/test_source_boundaries_docs.py` (anchor on a YouTube-specific phrase like "youtube via yt-dlp").
- `CHANGELOG.md`: Phase 5 wrap entry + a note that all 5 acquisition targets (web + 小红书/IG/X/YouTube) are complete.
- `docs/superpowers/specs/2026-06-30-phase5-youtube-design.md`: Status → Complete.
- Strip trailing whitespace in `docs/reviews/claude-code-stage-252-code-review.md`.
- Phase 5 release review → `docs/reviews/claude-code-stage-253-release-review.md`.

**Out:** any code/schema/dep change.

## Tasks (summary)

- **Task 0 (plan review):** Claude Code; opencode revises. `docs/reviews/claude-code-stage-253-plan-review.md`.
- **Task 1 (docs + guard + changelog, RED→GREEN):** add YouTube opt-in wording to the 4 docs; pin in docs-guard; CHANGELOG Phase 5 + final-mainline note; spec Status; strip the 252 review trailing whitespace.
- **Task 2 (release verification + Claude Code release review + commit):** full enumerated gate (pytest, ruff check/format, hygiene, lock, sync, packaging, installed-wheel smoke, git diff checks, secret scan); `claude --effort max ...` Phase 5 release review; commit "Stage 253: Phase 5 YouTube docs and final mainline wrap"; push.

## Verification

Docs-guard green; full release gate green (incl. packaging/installed-wheel smoke); `git diff --exit-code -- uv.lock pyproject.toml` exits 0; `git diff --check` clean.

## Self-Review

- Final stage of the scraping mainline: web + 4 social platforms all shipped.
- Docs-only wrap; no code/schema/dep change.
- Disambiguates live YouTube collector vs the pre-existing yt_dlp manual-import adapter.
- Opt-in/use-at-your-own-risk framing consistent throughout.
