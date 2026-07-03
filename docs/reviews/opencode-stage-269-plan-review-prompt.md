Review the Stage 269 ROW ONE plan before implementation.

Context:
- Repo: /home/ubuntu/fashion-radar
- Current branch: main
- Goal: add story display/media readiness to ROW ONE so every app story has a stable display object and the static site has professional visual slots before OpenDesign-generated images are wired later.
- Tech stack: Python 3.11, Pydantic v2, static HTML/CSS/JS renderer, JSON Schema draft 2020-12, pytest, ruff, uv.
- Design spec: docs/superpowers/specs/2026-07-02-stage-269-row-one-display-readiness-design.md
- Implementation plan: docs/superpowers/plans/2026-07-02-stage-269-row-one-display-readiness-plan.md

Please review for:
1. Feasibility and scope control.
2. Whether the plan preserves existing ROW ONE behavior and app contract safety.
3. Whether the display/image sanitation approach is technically reasonable.
4. Whether the proposed parallel worker file ownership avoids write conflicts.
5. Missing tests or likely regressions.
6. Any contradiction with the stated non-goals: no OpenDesign call, no image generation, no new collectors, no deploy/schedule install, no compliance-review product feature.

Return:
- Critical findings first.
- Important findings next.
- Minor findings last.
- If the plan is acceptable, say that explicitly.
