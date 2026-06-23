# Stage 182 First-Run Config Artifact Guard Design

## Objective

Extend the first-run smoke default-artifact guard so it detects accidental
repo-local generated config writes under `configs/`.

## Background

The first-run smoke currently snapshots repo-local `data/` and `reports/`
before and after the smoke flow. Stage 51 release review recorded a minor
follow-up: the automated smoke uses temporary config directories, but the guard
would not catch a future regression that writes generated runtime config files
to the repo-local default config directory.

The target generated config files are:

- `configs/sources.yaml`
- `configs/entities.yaml`
- `configs/scoring.yaml`

The guard should not scan the entire `configs/` tree because the repository
intentionally contains tracked examples, source packs, entity packs, and other
static config assets.

## Scope

In scope:

- Add a focused failing test in `tests/test_first_run_smoke.py`.
- Extend `scripts/check_first_run_smoke.py::snapshot_default_artifacts` so it
  includes the three generated repo-local config files when present.
- Update the default-artifact error label from `default data/reports` to include
  generated configs.
- Add Stage 182 plan/review artifacts.

Out of scope:

- Changing smoke command order or command arguments.
- Changing first-run sample data, entity expectations, report/trend validators,
  imported-signal validators, or artifact workspace assertions.
- Scanning every file under `configs/`.
- Treating tracked example configs, entity packs, source packs, or templates as
  generated artifacts.
- Runtime CLI behavior, config initialization behavior, collectors, dashboards,
  dependencies, lockfiles, source acquisition, connectors, scraping, platform
  APIs, monitoring, scheduling, ranking, demand proof, coverage verification,
  or compliance-review product features.

## Technical Approach

Add a constant in `scripts/check_first_run_smoke.py`:

```python
DEFAULT_GENERATED_CONFIG_ARTIFACT_PATHS = (
    Path("configs/sources.yaml"),
    Path("configs/entities.yaml"),
    Path("configs/scoring.yaml"),
)
```

Keep scanning the existing `data/` and `reports/` directories recursively.
Then check each generated config path explicitly and add its digest to the same
snapshot when it exists and is a file. This lets the existing created, changed,
and deleted diff logic work for generated config files without scanning static
config assets.

Update the error message to:

```text
Smoke changed files under default data/reports or generated configs (...)
```

Add a test that:

1. Captures `before = snapshot_default_artifacts(tmp_path)`.
2. Creates `configs/sources.yaml`, `configs/entities.yaml`, and
   `configs/scoring.yaml`.
3. Asserts `assert_default_artifacts_unchanged(...)` raises `SmokeError`.
4. Asserts the message includes `created:` and all three generated config paths.

## Acceptance Criteria

- A new test proves repo-local generated config files are detected when created
  after the default-artifact snapshot.
- Existing data/report created, changed, and deleted artifact guard tests still
  pass.
- `snapshot_default_artifacts` does not scan all of `configs/`.
- The smoke error message includes generated configs in the guarded surface.
- Focused first-run smoke tests pass.
- Ruff check and format check pass for touched files.
- Full release gate remains clean before commit.
