# Claude Code Plan Review Prompt

You are Claude Code reviewing a new open source project plan before implementation starts.

Project: Fashion Radar.

Objective: Build a free-first local Python tool that collects public fashion signals, identifies brands/designers/celebrities/products/trends, computes heat changes, and generates daily reports plus a Streamlit dashboard.

Please review these planning files:

- `docs/PROJECT_BRIEF.md`
- `docs/superpowers/specs/2026-06-11-fashion-radar-design.md`
- `docs/superpowers/plans/2026-06-11-fashion-radar-implementation-plan.md`

Review focus:

1. Is the goal clear and realistically scoped for a GitHub-ready MVP?
2. Is the free-first source strategy sound?
3. Are unstable social-platform tools correctly treated as experimental rather than core?
4. Is the technical stack appropriate?
5. Is the architecture modular enough for future connectors?
6. Are the phase gates and Claude Code review workflow sufficient?
7. Are there hidden compliance, data integrity, or operational risks?
8. Which parts of the implementation plan should be changed before coding begins?

Return findings ordered by severity:

- Critical: must fix before coding.
- Important: should fix before coding.
- Minor: can improve but does not block coding.

Also include a short "Proceed / Do Not Proceed" recommendation.

