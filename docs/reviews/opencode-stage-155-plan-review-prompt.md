# Stage 155 Plan Review Prompt

You are reviewing the Stage 155 implementation plan for `/home/ubuntu/fashion-radar`.

Goal: Derive `tests/test_package_archives.py` package archive fixture names,
wheel `dist-info` paths, sdist root paths, and positive expected metadata strings
from `scripts/check_package_archives.py` helper functions instead of duplicating
`fashion_radar-0.1.0`.

Relevant files:
- `docs/superpowers/specs/2026-06-22-stage-155-package-archive-fixture-metadata-parity-design.md`
- `docs/superpowers/plans/2026-06-22-stage-155-package-archive-fixture-metadata-parity-plan.md`
- `tests/test_package_archives.py`
- `scripts/check_package_archives.py`

Please review:
- Whether the node is correctly tests-only and does not alter package validation behavior.
- Whether the derived constants should come from existing checker helpers.
- Whether positive fixtures and expected messages should use derived constants.
- Whether intentionally wrong negative fixture names should remain explicit.
- Whether the proposed guard test proves fixture names are routed through derived constants.
- Whether the verification commands are sufficient.

Return findings first with severity and file/line references. If there are no
blocking issues, say that explicitly.
