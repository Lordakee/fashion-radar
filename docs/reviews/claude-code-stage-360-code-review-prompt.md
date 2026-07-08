# Claude Code Stage 360 Code Review Prompt

Review the current uncommitted Stage 360 diff in `/home/ubuntu/fashion-radar`.

Goal:
- Add generated-site-only Daily Local Article Capsules to the ROW ONE homepage.
- The section must be homepage-only inside `index.html`, after Daily Local Heat Signals and before Saved Article Content Organization.
- It must reuse current-edition stories, saved local article paragraphs, existing body-source labels, story references, generated local article page routes, and existing paragraph anchors.
- It must not change app-facing contracts, schemas, JSON artifacts, fetching, extraction, scoring, ranking, LLM, connector, scheduling, deployment, analytics, personalization, recommendation, or compliance-review behavior.

Review scope:
- `src/fashion_radar/row_one/templates.py`
- `src/fashion_radar/row_one/render.py`
- `tests/test_row_one_render.py`
- `tests/test_row_one_docs.py`
- `tests/test_workflows.py`
- `README.md`
- `docs/row-one.md`
- Stage 360 plan/spec/review docs under `docs/superpowers/` and `docs/reviews/`

Evaluate:
- Spec compliance against `docs/superpowers/plans/2026-07-09-stage-360-daily-local-article-capsules-plan.md`.
- Technical correctness of capsule filtering, capping, ordering, escaping, localization, and paragraph alignment.
- Safety of same-site href generation and rejection of traversal, nested paths, leading dots/slashes, mismatched filenames, empty/missing articles, and unsafe story IDs.
- Generated-site-only and homepage-only boundary.
- Test adequacy and whether focused tests cover regressions.
- CSS reasonableness for desktop/tablet two-column grid and mobile one-column layout.

Return findings ordered by severity:
- Critical
- Important
- Minor

For each finding, include file and line references when possible, explain the issue, and recommend the smallest fix. If there are no Critical or Important findings, say so explicitly.
