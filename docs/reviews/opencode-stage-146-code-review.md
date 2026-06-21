# Stage 146 Code Review

## Findings

**No blocking issues.** The changes do exactly what the design and plan
require: they pin first-run smoke semantic metadata before exact argv
validation so coordinated metadata-and-command drift is rejected, while
keeping runtime path fields payload-derived and runtime behavior unchanged.

### Verification Performed

I confirmed the RED tests genuinely prove the prior gap by stashing only
`scripts/check_first_run_smoke.py` and re-running the new tests against the
unchanged test file:

- `test_validate_imported_review_workflow_rejects_coordinated_metadata_command_drift`
  failed with `DID NOT RAISE`.
- `test_validate_community_handoff_workflow_rejects_coordinated_metadata_command_drift`
  failed with `DID NOT RAISE`.

After restoring the implementation, both tests pass. This is a true RED ->
GREEN cycle, not a post-hoc rationalization.

Focused verification on the working tree:

- `uv --no-config run --frozen pytest tests/test_first_run_smoke.py -q -k "coordinated_metadata_command_drift"` -> 2 passed.
- `uv --no-config run --frozen pytest tests/test_first_run_smoke.py -q -k "imported_review_workflow or community_handoff_workflow"` -> 26 passed.
- `uv --no-config run --frozen pytest tests/test_first_run_smoke.py -q` -> 103 passed.
- `uv --no-config run --frozen ruff check scripts/check_first_run_smoke.py tests/test_first_run_smoke.py` -> All checks passed.
- `uv --no-config run --frozen ruff format --check scripts/check_first_run_smoke.py tests/test_first_run_smoke.py` -> 2 files already formatted.
- `git diff --check` -> clean.

## Review Answers

### RED Tests Prove The Prior Gap

Both new tests are real coordinated-drift tests, not single-field tests:

- `tests/test_first_run_smoke.py:1997` mutates `source_name`, `as_of`,
  `lookback_days`, `current_days`, and `baseline_days` together, and rewrites
  every matching command fragment (`--lookback-days 7` -> `--lookback-days 14`,
  `'Community Tool Export'` -> `'Other Source'`, the `as_of` timestamp, etc.)
  so the payload stays internally consistent. Under the prior validator, the
  expected argv was rebuilt from the drifted top-level metadata, so this
  payload was accepted. Confirmed by the RED run above.
- `tests/test_first_run_smoke.py:2083` mutates `source_name`, `as_of`,
  `input_format`, and `pattern`, and rewrites both `--input-format csv` and
  `--format csv` (the runtime builder emits `--input-format` for the lint /
  candidates / readiness commands and `--format` for `import-signals-dir`),
  plus `'*.csv'` -> `'*.json'` and the timestamp / source-name fragments.
  Coverage of both `--input-format` and `--format` is required because the
  runtime builder uses both argument names; the test handles this correctly.

The `replace_workflow_command_fragments` helper
(`tests/test_first_run_smoke.py:741`) asserts every step has a string
`command`, so a future fixture change that drops a command field would surface
as a test setup error rather than a silent pass.

The `pytest.raises(..., match=...)` regexes are alternations over the pinned
field labels. The validators evaluate the pinned assertions in field order, so
the first drifted field raises and its label appears in the `SmokeError`
message produced by `assert_equal` (`scripts/check_first_run_smoke.py:375`),
which `re.search` matches. The regex is intentionally permissive (any drifted
field label) rather than pinned to one specific field, so it is robust to
minor ordering changes.

### Semantic Metadata Pinned, Path Fields Payload-Derived

`scripts/check_first_run_smoke.py`:

- Imported review validator (`scripts/check_first_run_smoke.py:883`):
  - Semantic assertions added at `scripts/check_first_run_smoke.py:897-913`
    for `as_of`, `source_name`, `lookback_days`, `current_days`,
    `baseline_days`.
  - Semantic command-builder inputs at `scripts/check_first_run_smoke.py:916-920`
    now use the pinned constants.
  - Path fields `config_dir` and `data_dir` remain payload-derived at
    `scripts/check_first_run_smoke.py:914-915`.
- Community handoff validator (`scripts/check_first_run_smoke.py:948`):
  - Semantic assertions added at `scripts/check_first_run_smoke.py:970-977`
    for `input_format`, `pattern`, `as_of`, `source_name`.
  - Semantic command-builder inputs at
    `scripts/check_first_run_smoke.py:979-980,983-984` now use the pinned
    constants.
  - Path fields `directory`, `config_dir`, and `data_dir` remain
    payload-derived at `scripts/check_first_run_smoke.py:978,981-982`.

The pinned constants (`scripts/check_first_run_smoke.py:24-28`) match the
existing fixture payloads in `tests/test_first_run_smoke.py:564,653` and the
existing smoke constants `SOURCE_NAME` and `DIR_PATTERN`. The community
handoff assertions reuse `DIR_PATTERN` rather than introducing a parallel
constant, avoiding constant drift.

The prior defensive coercions (`str(payload.get("source_name", "") or "")`,
etc.) are no longer needed for the semantic fields because the values now come
from module-level string constants. The path-field coercions
(`str(payload.get("config_dir", ""))`, etc.) are intentionally retained.

### Runtime Behavior Unchanged

Runtime behavior is preserved:

- `git diff 3b7960e1e845251b207c3d8bbf3899517bd2ecad -- src/` is empty.
- `git diff --stat 3b7960e1e845251b207c3d8bbf3899517bd2ecad` shows only
  `scripts/check_first_run_smoke.py` and `tests/test_first_run_smoke.py`
  changed.
- The two modified validators are first-run smoke output checkers, not
  workflow builders. They consume the JSON printed by the runtime builders
  (`scripts/check_first_run_smoke.py:2231,2333`) and reject malformed output;
  they do not feed values back into the runtime, the CLI, scheduling, the
  dashboard, or any compliance-review product feature.
- Path fields remain payload-derived, so installed-mode smoke runs that pass
  different `config_dir`, `data_dir`, or `directory` values still validate
  correctly.

### Verification Coverage Is Sufficient

The stage's focused verification is appropriate for the change scope:

- New RED tests pass GREEN.
- All imported-review and community-handoff workflow tests pass (26 tests).
- Full smoke test file passes (103 tests), which covers every other smoke
  surface that could regress from the constant additions or the validator
  edits.
- Ruff check and format on the touched Python files are clean.
- `git diff --check` is clean.

The release gate in the plan
(`docs/superpowers/plans/2026-06-22-stage-146-workflow-metadata-pinning-plan.md:348-363`)
additionally runs the full pytest suite, repo-wide ruff, lock check, release
hygiene, and GitHub token / auth-header checks before commit, which is the
correct gate for this scope.

**Verdict: Proceed. No critical or important findings.**
