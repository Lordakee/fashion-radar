# Claude Code Stage 6 Plan Review

Base: `3d97313 feat: add stage 5 cli and dashboard workflow`.

## Summary

Claude Code reviewed the Stage 6 plan against the current repository state and
implemented behavior from Stages 1-5. The plan is safe in scope and does not
require social scraping or risky connectors, but two verification requirements
must be made explicit before Stage 6 implementation.

## Critical

None.

## Important

1. **Dashboard extra resolution/import smoke is missing from the plan.**
   The Stage 6 CI/package contract and task list cover the core wheel smoke and
   packaged-template verification, but do not explicitly install or resolve the
   `dashboard` extra. Add a step that installs the wheel with `[dashboard]` or
   runs `uv sync --extra dashboard`, then imports
   `fashion_radar.dashboard.app` and `fashion_radar.dashboard.queries` without
   launching a Streamlit server.

2. **Packaged template verification must explicitly cover `daily_report.md`.**
   Existing wheel smoke exercises CLI help, `init`, and `doctor`, which cover
   config templates but not the daily report template loaded through
   `importlib.resources`. The Stage 6 plan should require either a report smoke
   or an explicit installed-wheel resource-load check for
   `fashion_radar.templates/daily_report.md`.

## Minor

1. **Some planned files already exist.** README and
   `docs/source-boundaries.md` should be expanded or updated rather than
   clobbered.
2. **Avoid documentation drift.** Reuse or link existing
   `docs/REVIEW_PROTOCOL.md` and `docs/dependency-mirrors.md` rather than
   creating competing material.
3. **Hygiene audit should mention existing agent tooling files.** Confirm
   `AGENTS.md`, `.claude/settings.json`, and `.mcp.json` are intentionally
   published and do not contain secrets or absolute local paths.
4. **Scoring known limits should name real quirks.** Document that entities
   with `current_mentions == 0` are omitted from ranked sections and that the
   current label table has a redundant `stable` fallback.

## Verdict

**Approved after fixes.**

Address the two Important items before Stage 6 implementation. The Minor items
should be handled while writing docs.
