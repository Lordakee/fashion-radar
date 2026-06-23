# Stage 160 Plan Review Prompt

Review the Stage 160 design and implementation plan for Fashion Radar.

Files to review:

- `docs/superpowers/specs/2026-06-23-stage-160-wheel-entry-points-console-scripts-design.md`
- `docs/superpowers/plans/2026-06-23-stage-160-wheel-entry-points-console-scripts-plan.md`
- Existing implementation context:
  - `scripts/check_package_archives.py`
  - `tests/test_package_archives.py`
  - `pyproject.toml`

Objective:

Make the package archive checker validate that expected wheel entry points are
present under `[console_scripts]`, not merely anywhere in `entry_points.txt`.

Proposed implementation:

- Parse `entry_points.txt` with `configparser.ConfigParser(interpolation=None)`.
- Set `parser.optionxform = str` before parsing.
- Require each expected project script under the `console_scripts` section.
- Return deterministic errors for missing entries, target mismatches, and
  malformed entry-point metadata.
- Keep the change confined to package archive validation.

Review questions:

1. Is this the right narrow Stage 160 after Stage 159?
2. Do the tests fail before implementation and prove wrong-group, missing,
   wrong-target, and malformed-entry-point behavior?
3. Is `ConfigParser(interpolation=None)` plus `optionxform = str` appropriate
   for wheel entry-point metadata?
4. Are error messages and no-traceback behavior reasonable?
5. Does the plan preserve product scope boundaries: no social connectors,
   scraping, browser automation, platform APIs, login/session/cookie behavior,
   monitoring, scheduling, source acquisition, demand proof, ranking, coverage
   verification, or compliance-review product features?
6. Are any release-gate or review-gate steps missing?

Return critical, important, and minor findings. If there are no blocking
findings, say so explicitly.
