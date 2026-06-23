# Stage 183 Plan Review

## Summary

The Stage 183 plan adds a single test-only regression guard proving wheel
`entry_points.txt` console-script names are matched case-sensitively. The
objective, fixture design, placement, scope discipline, and verification
commands are all sound. No runtime checker change is required; a full logic
trace confirms the current checker already rejects the proposed fixture, so the
plan correctly stays test-only.

## Per-Question Findings

### 1. Does the plan satisfy the objective (guard console-script names as case-sensitive)?

Yes. The new `test_rejects_wheel_entry_points_console_script_name_case_mismatch`
builds a wheel whose `entry_points.txt` uses `Fashion-Radar = fashion_radar.cli:app`
and asserts the checker rejects it as missing the lowercase `fashion-radar` entry
(exit 1, exact stderr substring, no Traceback). This is a direct guard of
case-sensitive name matching.

### 2. Is the proposed fixture meaningful for catching a future removal of `parser.optionxform = str`?

Yes, and it is well-targeted. The fixture varies only the script *name* case
(`Fashion-Radar`) while keeping the section (`[console_scripts]`) and the target
(`fashion_radar.cli:app`) correct. Tracing `scripts/check_package_archives.py:375-404`:

- With `parser.optionxform = str` (line 386) present, the option key is stored
  case-preserved as `Fashion-Radar`, so `console_scripts.get("fashion-radar")`
  (line 396) returns `None` and the "missing console_scripts entry" error fires
  (line 398) → exit 1 → test passes.
- If that line is removed, ConfigParser lowercases option keys, so the key becomes
  `fashion-radar`, the lookup succeeds with the matching target, no error fires,
  exit 0 → test fails.

The fixture therefore fails open exactly when the case-preservation guard is
removed, which is precisely the regression the stage targets. Using mixed case
(`Fashion-Radar`) rather than all-caps also reflects a realistic malformed-wheel
scenario and isolates the case-sensitivity behavior cleanly.

### 3. Is the planned test placement and assertion shape consistent with existing package archive tests?

Yes. The test is inserted immediately after
`test_rejects_wheel_entry_points_console_script_wrong_target`
(`tests/test_package_archives.py:1118`), keeping the `entry_points.txt`
console-script family grouped. It reuses the same `WHEEL_FILES | {...}` override
pattern, `write_wheel`/`write_sdist`/`run_checker` helpers, `build_dir = tmp_path
/ "dist"` setup, and `result.returncode == 1` + `in result.stderr` assertion shape
as its neighbors. The asserted message
`entry_points.txt is missing console_scripts entry: fashion-radar = fashion_radar.cli:app`
matches the literal produced at `check_package_archives.py:398`.

### 4. Does the plan stay test-only unless the new test exposes a real checker defect?

Yes. Both the spec and the plan (Task 1, Step 3) explicitly gate any runtime
change on the test exposing a genuine case-sensitivity defect, and the trace
above shows the current checker already rejects the fixture, so no runtime change
is expected. The self-review notes reaffirm the boundary (metadata, dependency
files, lockfiles, scope boundaries remain untouched).

### 5. Are focused verification commands sufficient before the full release gate?

Yes. Task 2, Step 1 runs the full `tests/test_package_archives.py` module plus
`ruff check` and `ruff format --check` on the single touched file. Because the
change is test-only and touches no runtime code (absent a real defect), this is
sufficient focused verification; the complete release gate in Task 3 (full
`pytest`, first-run smoke, release hygiene, repo-wide ruff, `UV_NO_CONFIG=1 uv
lock --check`, `git diff --check`, secret/extraheader absence checks) then
provides full coverage. All commands use the AGENTS.md-compliant `uv --no-config
run --frozen` and `UV_NO_CONFIG=1 uv lock --check` conventions.

## Critical

None.

## Important

None.

## Minor

- The new test hardcodes the literal `fashion-radar = fashion_radar.cli:app` in
  both the fixture and the assertion, while a neighbor
  (`test_rejects_wheel_entry_points_without_console_script`,
  `tests/test_package_archives.py:1074`) derives the expected line from
  `EXPECTED_METADATA.console_script_lines`. Both styles appear in the file and
  hardcoding is acceptable for this case-mismatch test, but deriving from
  `EXPECTED_METADATA.console_script_lines` would keep it robust if the script set
  ever changes. Not a blocker.
- The new test adds `assert "Traceback" not in result.stderr`, which its immediate
  neighbor `test_rejects_wheel_entry_points_console_script_wrong_target` omits.
  This is consistent with the broader file convention and the spec's explicit
  "Assert no traceback leaks" requirement, so it is fine (arguably a small
  improvement). Noted only for completeness.

## Verdict

Approve implementation. The plan is accurate, the fixture is meaningful and
correctly traced, placement/assertions are consistent, scope is appropriately
test-only, and focused verification plus the full release gate are sufficient.
The minor notes are optional polish and do not block proceeding.
