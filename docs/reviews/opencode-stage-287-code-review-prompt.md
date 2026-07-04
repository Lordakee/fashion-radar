# Stage 287 Code Review Prompt (opencode fallback)

You are reviewing the Stage 287 implementation for Fashion Radar / ROW ONE.

## Objective

Stage 287 adds a deterministic top-level `signal_synthesis` app payload and homepage section for ROW ONE. It should let app clients and the static site show local observed brand, product, designer, and person signals that need review, without adding collectors, platform integrations, LLM/image calls, new dependencies, scoring/ranking/story-ID changes, scheduler/server changes, deployment changes, or compliance-review product features.

## Claude Code Availability

Claude Code should be attempted first with maximum effort. If local authentication fails, this prompt is the opencode fallback review using model `zhipuai-coding-plan/glm-5.2` with variant `max`.

## Changed Scope To Review

- `src/fashion_radar/row_one/render.py`
- `src/fashion_radar/row_one/templates.py`
- `schemas/row-one-app.schema.json`
- `schemas/row-one-manifest.schema.json`
- `src/fashion_radar/cli.py`
- `scripts/check_first_run_smoke.py`
- `tests/test_row_one_app_contract.py`
- `tests/test_row_one_render.py`
- `tests/test_row_one_cli.py`
- `tests/test_first_run_smoke.py`
- `tests/test_row_one_docs.py`
- `README.md`
- `docs/row-one.md`
- Stage 287 plan and review artifacts under `docs/superpowers/plans/` and `docs/reviews/`

## Requirements

Review whether:

1. `row-one-app/v6` is correctly required everywhere a new top-level app field matters.
2. `signal_synthesis` derives deterministically from existing story payloads and `briefing_topics_payload(stories)`.
3. `signal_synthesis` stays local-observed/review-required and does not claim demand proof, platform heat, verified coverage, or broad popularity.
4. Schema constraints reject malformed nested groups/signals and unsafe detail hrefs.
5. Homepage rendering escapes all text and renders only safe detail links.
6. CLI status and first-run smoke validators catch missing or drifted `signal_synthesis`.
7. Tests cover populated, empty, no-reference, mapping parity, render escaping, docs, CLI, and smoke behavior.
8. No unrelated behavior, dependencies, generated report artifacts, lockfile edits, or public mirror config were introduced.

## Output Format

Return exactly these sections:

- Verdict
- Critical Findings
- Important Findings
- Minor Findings
- Recommended Fixes

For each Critical or Important finding, include file/line evidence, why it matters, and the smallest safe fix. If there are no Critical or Important findings, say so explicitly.
