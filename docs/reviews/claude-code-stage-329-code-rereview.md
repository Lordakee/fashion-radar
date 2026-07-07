I'll analyze the Stage 329 implementation fixes against the three verification points.

## Critical

None.

## Important

None.

All Important findings from the original review have been addressed:

1. **`ready` status systemd requirement** - The spec (design.md:110-116) now explicitly states "and expected user systemd unit files are present" as part of `ready`. The docs (row-one.md:271-274 and cli-reference.md:133-135) document this behavior. Test coverage exists at test_row_one_ops_check.py:126-147with `test_ops_check_reports_attention_when_units_missing_but_site_and_server_ready`.

2. **Duplicate action eliminated** - ops_check.py:223adds a guard `if site.get("status") == "present" and freshness.get("status") == "unknown"` so the runtime-metadata action only emits when site files are present but runtime is corrupt/missing. Test coverage exists at test_row_one_ops_check.py:173-193, explicitly asserting "runtime metadata" is NOT in actions when the site is missing.

3. **Unknown runtime action includes `--output-dir`** - ops_check.py:226 now includes `--output-dir {site_dir}` in the runtime-metadata regeneration guidance.

## Medium

None.

The original Medium #4 finding (missing test for stale + serving_row_one + present → attention) is now covered by `test_ops_check_reports_attention_when_freshness_is_stale_only` at test_row_one_ops_check.py:149-170.

## Minor

**1. No explicit test for runtime-metadata action positive case.**

Tests at lines 196-227 and 230-253 create scenarios where site is present but freshness is unknown (invalid timestamp, unparseable JSON), yet neither test asserts that the runtime-metadata action appears in `payload["actions"]`. The negative test (site missing → no runtime-metadata action) exists at line 191, but the positive case lacks explicit coverage. The implementation is correct by inspection (ops_check.py:223-227), but the gap means a refactor could silently break the action emission.

## Verdict

**Approve.**

All three verification points are satisfied. The spec, docs, and tests now explicitly document that `ready` requires systemd units. The duplicate action bug is fixed with proper guard logic and test coverage. The unknown-runtime action includes `--output-dir`. The one remaining gap (Minor #1) is test coverage for a positive case where the logic is demonstrably correct. The implementation is safe, well-bounded, and the original Important findings have been properly addressed.
