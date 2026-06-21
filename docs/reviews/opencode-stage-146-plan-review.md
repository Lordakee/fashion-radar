# Stage 146 Plan Review

## Findings

**No blocking issues.** The plan is sound: the RED tests prove the coordinated metadata-and-command drift gap, the pinning closes it without changing runtime behavior, the constants match the first-run contract, and verification coverage is appropriate.

### Low-Severity Plan Correction

The original plan text for the community handoff replacement showed four semantic assignments as one contiguous block:

```python
input_format = str(payload.get("input_format", ""))
pattern = str(payload.get("pattern", ""))
as_of = str(payload.get("as_of", ""))
source_name = str(payload.get("source_name", ""))
```

In `scripts/check_first_run_smoke.py`, these lines are interleaved with path fields (`directory`, `config_dir`, `data_dir`). A literal replacement would fail. The plan was corrected to split the replacement into two edits, keeping path fields payload-derived.

## Review Answers

### RED Test Viability

Both planned RED tests should fail before implementation with `DID NOT RAISE`:

- Imported review mutates `source_name`, `as_of`, `lookback_days`, `current_days`, and `baseline_days`, then rewrites matching commands. The current validator rebuilds expected argv from those drifted payload values.
- Community handoff mutates `source_name`, `as_of`, `input_format`, and `pattern`, then rewrites matching commands. The current validator likewise rebuilds expected argv from those drifted payload values.

After metadata pinning, the imported review test should raise on a pinned metadata field such as `as_of`, and the community handoff test should raise on `input_format` or another pinned semantic field.

### Path Fields

`directory`, `config_dir`, and `data_dir` should remain payload-derived. They are runtime paths that legitimately vary between source-checkout and installed-mode smoke execution. Pinning them would risk breaking installed-mode smoke runs.

### Pinned Constants

The planned constants match fixtures and runtime defaults:

- `EXPECTED_WORKFLOW_AS_OF = "2026-06-13T12:00:00+00:00"` matches serialized fixture output.
- `EXPECTED_COMMUNITY_HANDOFF_INPUT_FORMAT = "csv"` matches the handoff fixture and smoke invocation.
- Imported review day windows are all `7`, matching fixture values and builder defaults.
- Existing `SOURCE_NAME` and `DIR_PATTERN` match the community fixtures and runtime defaults.

### Runtime Behavior

Runtime behavior remains unchanged because only `scripts/check_first_run_smoke.py`, `tests/test_first_run_smoke.py`, and documentation/review artifacts are in scope. The runtime builders remain untouched.

### Verification

Focused verification is sufficient for the stage:

- `pytest -k "imported_review_workflow or community_handoff_workflow"`
- full `tests/test_first_run_smoke.py`
- ruff check/format on touched Python files
- `git diff --check`

The release gate then adds full-suite pytest, repo-wide ruff, lock check, release hygiene, and token/auth checks.

**Verdict: Proceed after the low-severity plan correction, which has been applied.**
