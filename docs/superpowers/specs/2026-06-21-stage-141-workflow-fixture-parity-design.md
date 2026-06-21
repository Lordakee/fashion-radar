# Stage 141 Workflow Fixture Parity Design

## Goal

Add exact parity tests for the imported-review and community-handoff workflow smoke fixtures against their real Pydantic builders, then update the hand-maintained fixtures to include the full nested step metadata emitted by runtime code.

## Background

The first-run smoke tests use hand-maintained JSON fixtures for command validators:

- `imported_review_workflow_payload()`
- `community_handoff_workflow_payload()`

Stage 139 aligned top-level imported-review fields and command args, but the nested `steps` still do not fully mirror builder output.

The runtime builders define `extra="forbid"` models:

- `build_imported_review_workflow()` in `src/fashion_radar/imported_review_workflow.py`
- `build_community_handoff_workflow()` in `src/fashion_radar/community_handoff_workflow.py`

Fixture drift can hide missing metadata from validator tests. Existing external-tool fixtures already have parity tests against real builders; Stage 141 extends that pattern to these two workflow fixtures.

## Scope

Modify only tests and stage artifacts:

- `tests/test_first_run_smoke.py`
- `docs/superpowers/plans/2026-06-21-stage-141-workflow-fixture-parity-plan.md`
- `docs/reviews/opencode-stage-141-plan-review-prompt.md`
- `docs/reviews/opencode-stage-141-plan-review.md`
- `docs/reviews/opencode-stage-141-code-review-prompt.md`
- `docs/reviews/opencode-stage-141-code-review.md`

Do not change runtime builders or smoke validator behavior.

## Design

Import the workflow builders in `tests/test_first_run_smoke.py`:

```python
from fashion_radar.community_handoff_workflow import build_community_handoff_workflow
from fashion_radar.imported_review_workflow import build_imported_review_workflow
```

Add two parity tests near the existing external-tool builder parity tests:

```python
def test_imported_review_workflow_payload_matches_real_builder() -> None:
    expected = json.loads(
        build_imported_review_workflow(
            config_dir=Path("configs"),
            data_dir=Path("data"),
            as_of="2026-06-13T12:00:00Z",
            source_name="Community Tool Export",
        ).model_dump_json()
    )

    assert imported_review_workflow_payload() == expected
```

```python
def test_community_handoff_workflow_payload_matches_real_builder() -> None:
    expected = json.loads(
        build_community_handoff_workflow(
            directory=Path("/tmp/export"),
            config_dir=Path("configs"),
            data_dir=Path("data"),
            input_format="csv",
            pattern="*.csv",
            as_of="2026-06-13T12:00:00Z",
            source_name="Community Tool Export",
        ).model_dump_json()
    )

    assert community_handoff_workflow_payload() == expected
```

Use `model_dump_json()` plus `json.loads()` to match the existing parity test style and JSON payload shape.

## Fixture Updates

`imported_review_workflow_payload()` needs each step to include:

- `order`
- `purpose`
- `suggested_effect`

`community_handoff_workflow_payload()` already includes `suggested_effect` for every step but needs:

- `order`
- `purpose`

The exact values come from the runtime builders:

### Imported Review Step Metadata

1. `summarize_imported_sources`
   - purpose: `Summarize retained imported source-name labels.`
   - suggested_effect: `read_only`
2. `refresh_stored_matches`
   - purpose: `Refresh stored local matches using configured entities.`
   - suggested_effect: `updates_local_matches`
3. `compare_imported_entities`
   - purpose: `Compare stored matched imported entities across collected-at windows.`
   - suggested_effect: `read_only`
4. `review_imported_entity_evidence`
   - purpose: `Review retained imported rows behind one selected matched entity.`
   - suggested_effect: `read_only`
5. `review_imported_candidate_phrases`
   - purpose: `Review observed candidate phrases from retained imported rows after stored matches are refreshed.`
   - suggested_effect: `read_only`
6. `review_unmatched_imported_rows`
   - purpose: `Review retained imported rows without stored matches.`
   - suggested_effect: `read_only`
7. `review_local_heat_movers`
   - purpose: `Review local observed heat movement after imported rows are matched.`
   - suggested_effect: `read_only`

### Community Handoff Step Metadata

1. `lint_handoff_directory`
   - purpose: `Lint local community handoff files before import.`
2. `preview_candidate_phrases`
   - purpose: `Preview aggregate candidate phrases before import.`
3. `review_handoff_readiness`
   - purpose: `Review local handoff readiness before import.`
4. `dry_run_directory_import`
   - purpose: `Validate matched local files through the importer without writing rows.`
5. `import_directory_signals`
   - purpose: `Import the validated local handoff rows into local SQLite.`
6. `print_post_import_review`
   - purpose: `Print the local post-import review checklist.`

## TDD Strategy

1. Add the imports and parity tests first.
2. Run the two tests and observe RED failures due to missing nested step metadata.
3. Update the fixture dictionaries with exact metadata.
4. Run the two tests again and observe GREEN.

## Verification

Focused verification:

```bash
uv --no-config run --frozen pytest tests/test_first_run_smoke.py -q -k "workflow_payload_matches_real_builder or imported_review_workflow or community_handoff_workflow"
uv --no-config run --frozen pytest tests/test_first_run_smoke.py -q
uv --no-config run --frozen ruff check tests/test_first_run_smoke.py
uv --no-config run --frozen ruff format --check tests/test_first_run_smoke.py
git diff --check
```

Release gate:

```bash
uv --no-config run --frozen python scripts/check_release_hygiene.py
env -u all_proxy -u ALL_PROXY -u http_proxy -u HTTP_PROXY -u https_proxy -u HTTPS_PROXY -u no_proxy -u NO_PROXY uv --no-config run --frozen pytest -q
uv --no-config run --frozen ruff check .
uv --no-config run --frozen ruff format --check .
env -u UV_DEFAULT_INDEX -u UV_INDEX_URL -u UV_EXTRA_INDEX_URL UV_NO_CONFIG=1 uv lock --check
git diff --check
if rg -n 'ghp_[A-Za-z0-9]+' .; then echo 'GitHub token pattern found in worktree' >&2; exit 1; fi
if git config --get-all http.https://github.com/.extraheader; then echo 'Persistent GitHub auth header configured' >&2; exit 1; fi
```
