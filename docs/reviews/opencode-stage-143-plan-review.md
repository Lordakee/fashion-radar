# Stage 143 Plan Review

## Findings

### Critical: `data_dir` is not extracted from payload

The replacement loop in `docs/superpowers/plans/2026-06-21-stage-143-community-handoff-command-argv-plan.md` and `docs/superpowers/specs/2026-06-21-stage-143-community-handoff-command-argv-design.md` calls `expected_community_handoff_workflow_command_parts(..., data_dir=data_dir, ...)`, but the existing `validate_community_handoff_workflow()` only extracts `directory`, `input_format`, `pattern`, `config_dir`, `as_of`, and `source_name`.

The payload fixture contains `"data_dir": "data"`, so the plan must add this extraction before the expected-command loop:

```python
data_dir = str(payload.get("data_dir", ""))
```

### Info: readiness error label changes

The current readiness command check uses `label="readiness"`. The planned loop uses the step label `review_handoff_readiness`, so the error text changes from `readiness command` to `review_handoff_readiness command`.

Existing tests should still pass because:

- `test_validate_community_handoff_workflow_rejects_incomplete_readiness_command` matches `--strict`.
- `test_validate_community_handoff_workflow_rejects_wrong_readiness_command_argv` matches `readiness command`, which is still a substring of `review_handoff_readiness command`.

## Verified Items

- The planned argv tuples match `build_community_handoff_workflow()` flag-for-flag, including `--strict` on lint and readiness, `--dry-run` only on dry-run import, and no config/data directory flags on the lint step.
- The RED test should fail before implementation because the current validator only argv-checks `steps[2]`.
- After the loop is added with `data_dir` extraction, each mutation should raise a `SmokeError` with the expected command label.
- Runtime behavior remains unchanged because the plan does not modify `src/fashion_radar/community_handoff_workflow.py`.
- Focused verification is sufficient for the change surface.

## Resolution

The design and plan were updated before implementation to include `data_dir = str(payload.get("data_dir", ""))` next to the existing payload-derived command inputs.

## Verdict

With the `data_dir` extraction correction applied, the plan is sound and ready to execute.
