# Stage 139 First-Run Workflow Command Argv Design

## Goal

Tighten the remaining first-run smoke workflow command validators that still accept substring drift, so the smoke check verifies exact `fashion-radar` argv for imported-review and community-handoff review steps.

## Background

Recent stages added `validate_expected_external_tool_command()` in `scripts/check_first_run_smoke.py`. That helper parses a rendered shell command with `shlex.split()` and compares the full argv list to `["fashion-radar", *parts]`.

Two validators still use substring membership for important workflow commands:

- `validate_imported_review_workflow()` checks three commands with substring loops:
  - `review_imported_entity_evidence`
  - `review_imported_candidate_phrases`
  - final `review_local_heat_movers`
- `validate_community_handoff_workflow()` checks `review_handoff_readiness` with a substring loop.

Substring checks can accept invalid commands such as `community-handoff-check-dir-extra` because the old expected fragment remains present. They can also miss argument drift such as wrong `--current-days`, extra output flags, or changed directories.

## Scope

Modify only the smoke validator and its tests:

- `scripts/check_first_run_smoke.py`
- `tests/test_first_run_smoke.py`

Add only process artifacts:

- `docs/superpowers/plans/2026-06-21-stage-139-first-run-workflow-command-argv-plan.md`
- `docs/reviews/opencode-stage-139-plan-review-prompt.md`
- `docs/reviews/opencode-stage-139-plan-review.md`
- `docs/reviews/opencode-stage-139-code-review-prompt.md`
- `docs/reviews/opencode-stage-139-code-review.md`

Do not change runtime CLI workflow builders in `src/fashion_radar/*` unless exact validation is impossible without doing so.

## Expected Exact Commands

### Imported Review

Use top-level payload metadata emitted by `ImportedReviewWorkflow`:

- `config_dir`
- `data_dir`
- `as_of`
- `source_name`
- `current_days`
- `baseline_days`

The entity evidence step must split to:

```python
[
    "fashion-radar",
    "imported-entity-evidence",
    "--data-dir",
    data_dir,
    "--as-of",
    as_of,
    "--entity-name",
    "The Row",
    "--entity-type",
    "brand",
    "--current-days",
    str(current_days),
    "--baseline-days",
    str(baseline_days),
    "--source-name",
    source_name,
]
```

If `source_name` is absent or empty, omit the final `--source-name` pair to match the runtime `_optional_source_args()` behavior.

The imported candidates step must split to:

```python
[
    "fashion-radar",
    "imported-candidates",
    "--config-dir",
    config_dir,
    "--data-dir",
    data_dir,
    "--as-of",
    as_of,
    "--source-name",
    source_name,
]
```

Again, omit the final `--source-name` pair when `source_name` is absent or empty.

The final heat movers step must split to:

```python
[
    "fashion-radar",
    "heat-movers",
    "--config-dir",
    config_dir,
    "--data-dir",
    data_dir,
    "--as-of",
    as_of,
]
```

This exact list also preserves the existing invariant that the final heat command must not include `--source-name`.

### Community Handoff

Use existing top-level payload metadata:

- `directory`
- `input_format`
- `pattern`
- `config_dir`
- `as_of`
- `source_name`

The readiness step must split to:

```python
[
    "fashion-radar",
    "community-handoff-check-dir",
    directory,
    "--input-format",
    input_format,
    "--pattern",
    pattern,
    "--config-dir",
    config_dir,
    "--as-of",
    as_of,
    "--source-name",
    source_name,
    "--strict",
]
```

## Fixture Parity

`community_handoff_workflow_payload()` already contains the required top-level metadata.

`imported_review_workflow_payload()` must be updated to mirror the real Pydantic payload from `build_imported_review_workflow()` by adding:

```python
"as_of": "2026-06-13T12:00:00+00:00",
"config_dir": "configs",
"data_dir": "data",
"source_name": "Community Tool Export",
"lookback_days": 7,
"current_days": 7,
"baseline_days": 7,
```

The fixture commands for imported entity deltas and entity evidence must also include `--current-days 7 --baseline-days 7` where the runtime builder emits those flags.

## Test Strategy

Use TDD. Add RED tests that preserve old substrings but drift the real argv:

- Imported entity evidence: change `--current-days 7` to `--current-days 14` while all previous substring fragments remain.
- Imported candidates: change `--config-dir configs` to `--config-dir configsets` so the old `--config-dir` substring remains.
- Final heat movers: change the subcommand to `heat-movers-extra`, preserving the old `fashion-radar heat-movers` substring.
- Community readiness: change the subcommand to `community-handoff-check-dir-extra`, preserving the old `fashion-radar community-handoff-check-dir` substring.

Each new test should fail against the current substring validators because the invalid command is accepted. After implementation, each should raise `SmokeError` with a label that includes the command under validation.

## Verification

Focused verification:

```bash
uv --no-config run --frozen pytest tests/test_first_run_smoke.py -q -k "imported_review_workflow or community_handoff_workflow"
uv --no-config run --frozen pytest tests/test_first_run_smoke.py tests/test_external_tool_contract_parity.py -q
uv --no-config run --frozen ruff check scripts/check_first_run_smoke.py tests/test_first_run_smoke.py
uv --no-config run --frozen ruff format --check scripts/check_first_run_smoke.py tests/test_first_run_smoke.py
uv --no-config run --frozen python scripts/check_first_run_smoke.py --repo-root .
git diff --check
```

Release gate:

```bash
uv --no-config run --frozen python scripts/check_release_hygiene.py
uv --no-config run --frozen pytest -q
uv --no-config run --frozen ruff check .
uv --no-config run --frozen ruff format --check .
env -u UV_DEFAULT_INDEX -u UV_INDEX_URL -u UV_EXTRA_INDEX_URL UV_NO_CONFIG=1 uv lock --check
git diff --check
if rg -n 'ghp_[A-Za-z0-9]+' .; then echo 'GitHub token pattern found in worktree' >&2; exit 1; fi
if git config --get-all http.https://github.com/.extraheader; then echo 'Persistent GitHub auth header configured' >&2; exit 1; fi
```
