# Stage 216 Phase 1 Release Verification + Wrap Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Close Phase 1 (web acquisition: review-flow iron rules, HTML/sitemap source plumbing + real collectors, RSSHub self-host docs) with a consolidated release verification (including package-archive + installed-wheel smoke), a Phase 1 release review by Claude Code, and a roadmap/CHANGELOG wrap marking Phase 1 complete and Phases 2–5 (social) as the next mainline.

**Architecture:** Verification + review + docs stage. No new feature code. Re-confirms the full release gate across all of Phase 1, adds packaging-readiness checks (build wheel + package archives + installed-wheel smoke) that were not run per-sub-stage, runs a single consolidated Phase 1 release review (Claude Code), updates CHANGELOG + the umbrella spec's roadmap note (Phase 1 done; Phase 2 = Xiaohongshu next), and commits.

**Tech Stack:** uv (build, sync, lock), pytest, ruff, `scripts/check_release_hygiene.py`, `scripts/check_package_archives.py`, `scripts/check_first_run_smoke.py`, Claude Code release review, opencode (`glm-5.2 --variant max`).

## Scope

**In scope:**
- Run the complete release gate: full pytest, ruff check + format, release hygiene, uv lock --check, sync --locked --dev --check, first-run smoke, `git diff --exit-code -- uv.lock pyproject.toml`, `git diff --check`.
- Packaging readiness: `uv build` into a temp dir, `scripts/check_package_archives.py`, installed-wheel first-run smoke (per `docs/github-upload-checklist.md`).
- Phase 1 release review by Claude Code (whole-phase coherence: boundaries, the new html/sitemap collectors, fail-closed discipline, docs accuracy, no scope leak into social/Phase 2). Record `docs/reviews/claude-code-stage-216-release-review.md`.
- CHANGELOG: a Phase 1 wrap `### Added`/note summarising Stages 211–215.
- Umbrella spec `docs/superpowers/specs/2026-06-29-phase1-web-collectors-design.md`: add a "Phase 1 Status" note (complete; Phase 2 = Xiaohongshu next, introduces login/credential model).

**Out of scope:** any new collection code, any social platform work (Phase 2+), any schema/dependency change, the login/cookie storage model (Phase 2).

## Tasks (summary)

- **Task 0 (plan review):** Claude Code reviews this plan; opencode revises. `docs/reviews/claude-code-stage-216-plan-review.md`.
- **Task 1 (release gate + packaging):** run the full gate + `uv build` + `check_package_archives.py` + installed-wheel smoke. All must pass.
- **Task 2 (Phase 1 release review):** Claude Code release review of the whole phase → `docs/reviews/claude-code-stage-216-release-review.md`. Fix any Critical/Important.
- **Task 3 (wrap docs):** CHANGELOG Phase 1 note + spec Phase 1 Status note.
- **Task 4 (commit + push):** "Stage 216: Phase 1 web-acquisition release verification and wrap".

## Verification

Full gate + packaging + installed-wheel smoke green; release review APPROVE; `git diff --exit-code -- uv.lock pyproject.toml` exits 0.

## Self-Review

- Consolidates per-stage gates into one Phase 1 release confirmation.
- Adds packaging checks not run per-sub-stage (ensures the optional `article` extra + new modules package cleanly).
- Marks the mainline transition: Phase 1 (web) complete → Phase 2 (Xiaohongshu + login model) next.
- No new code; no scope leak into social.
