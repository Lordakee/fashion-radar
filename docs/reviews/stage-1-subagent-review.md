# Stage 1 Subagent Review

Date: 2026-06-11

Status: Historical Stage 1 review. Critical and important findings must be
checked against the current code before entering Stage 2.

## Resolution Notes

- Packaged config templates were added under `src/fashion_radar/templates/`.
- `doctor` now fails for missing required config files and reports invalid
  config without a traceback.
- Config and normalized models now forbid unknown fields.
- Config versions are constrained to version `1`.
- `safe_single_word` aliases require a non-empty reason.
- Duplicate entity names and invalid parent references are rejected.
- `alias_pattern()` is case-insensitive; context-aware disambiguation remains a
  Stage 2 matcher requirement.
- Public `uv.lock` was regenerated without mirror-bound URLs.
- CI uses locked sync and a wheel-installed CLI smoke test.

## Critical

1. `fashion-radar init` reads templates from repository-root `configs/`, which fails after wheel/normal installation unless templates are packaged. Move templates into package resources or explicitly include them in wheel/sdist.

## Important

1. `doctor` returns success when required config files are missing.
2. `doctor` does not catch `ConfigError`, so invalid YAML/config can show a traceback.
3. Pydantic models currently allow unknown fields by default.
4. `safe_single_word` does not require a non-empty reason.
5. Alias context rules must be documented as a Stage 2 matcher contract.
6. Example context terms are too broad for future matching if used directly.
7. `alias_pattern()` is case-sensitive and needs a clear normalized-input contract.
8. `uv.lock` was generated using a regional mirror and should not commit mirror-bound URLs.
9. Stage 2 needs a clear SQLAlchemy dependency decision.
10. CI should add locked sync and installed CLI smoke tests.

## Minor

1. `dev` extra duplicates uv dependency group.
2. Plain `uv sync` installs dev because of `default-groups`.
3. Config version fields should be constrained to `1`.
4. Source URL should be validated before Stage 3.
5. Entity active window fields should be typed as datetimes.
6. Duplicate entity names and parent references should be checked before Stage 2.
7. `.env.example` implies env vars not yet wired into CLI.
