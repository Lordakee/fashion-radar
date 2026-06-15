## Critical findings

None found.

## Important findings

1. **Docs plan/test mismatch will fail `tests/test_cli_docs.py`**
   - The planned test `test_community_signal_profile_docs_are_linked()` asserts:
     ```python
     assert "examples/community-signal-profile.example.json" in import_doc
     ```
   - But the documentation instructions for `docs/community-signal-import.md` do **not** tell the implementer to mention `examples/community-signal-profile.example.json`.
   - Fix before implementation: explicitly add the example JSON path to the Producer Profile section, e.g. “A checked-in example is available at `examples/community-signal-profile.example.json`.”

2. **No-artifact CLI test is weaker than the hard boundary requires**
   - The proposed no-artifact test uses `CliRunner().invoke(app, ...)` after `fashion_radar.cli.app` has already been imported by the test module.
   - This verifies the command body does not create artifacts, but it does **not** catch artifact creation during real CLI process startup/imports under the temporary cwd/env.
   - Since the hard boundary says the command must not create config/data/report directories, open SQLite, etc., add a subprocess or installed-module-style smoke test from a temp cwd with environment path variables set, for example:
     ```bash
     UV_NO_CONFIG=1 uv run fashion-radar community-signal-profile --format json
     ```
     with cwd/env set to a temp directory and artifact assertions afterward.

3. **“Strict JSON schema” is under-tested**
   - The design says tests should bind the profile to a “strict JSON schema,” but the plan mostly tests key order and field values.
   - The Pydantic model uses `ConfigDict(extra="forbid")`, but no test asserts that extra top-level fields are rejected or that required fields are enforced.
   - Add a direct model validation test, e.g. extra field raises `ValidationError`, missing required field raises `ValidationError`, and `CommunitySignalProducerProfile.model_json_schema()` has `additionalProperties: false`.

4. **Release commit instructions in the plan conflict with repository/session requirements**
   - The implementation plan’s commit command:
     ```bash
     git commit -m "Add community signal producer profile"
     ```
     omits the required co-author trailer from the active developer instruction:
     ```text
     Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>
     ```
   - Fix the plan before execution if commit/push steps are retained.

## Minor findings

1. **The plan hardcodes the CSV header in the new module**
   - This is acceptable because tests bind it to `examples/community-signals.example.csv`, but the implementer should understand this creates a second source of truth guarded by tests rather than deriving from the example/schema at runtime.
   - This is consistent with “print-only” behavior and avoids filesystem reads, so it is not a blocker.

2. **Review artifacts are included as implementation outputs**
   - The plan says to create and commit review artifacts under `docs/reviews/`.
   - That appears to be existing process practice, but it is not part of the product objective. Keep them clearly separated from user-facing docs and ensure they do not introduce release noise or stale prompts.

3. **Profile example privacy test name may be misleading**
   - `test_profile_example_does_not_include_private_payload_fields()` checks prohibited field names are not JSON object keys via `f'"{prohibited}":'`.
   - The profile intentionally includes the prohibited field names as values under `"prohibited_fields"`, so the test is correct but the name could be clearer, e.g. `test_profile_example_lists_prohibited_fields_only_as_contract_values`.

## Missing tests or verification gaps

1. **Real-process no-artifact check**
   - Add subprocess verification from a temp cwd with:
     - `FASHION_RADAR_CONFIG_DIR`
     - `FASHION_RADAR_DATA_DIR`
     - `FASHION_RADAR_REPORTS_DIR`
   - Assert no config/data/report directories, SQLite files, report files, digest files, dashboard state, or workflow artifacts are created.

2. **Invalid `--format` behavior**
   - The design says Typer handles invalid `--format` values before the command body runs.
   - Existing tests cover help/table/json but not invalid values.
   - Add a test for:
     ```bash
     fashion-radar community-signal-profile --format yaml
     ```
     expecting non-zero exit and no artifacts.

3. **No path/config/data/report arguments**
   - The command should not accept path/config/data/report arguments or options.
   - Help test should explicitly assert absence of:
     - `--config-dir`
     - `--data-dir`
     - `--reports-dir`
     - path argument metavars if practical.

4. **Profile model strictness**
   - Add Pydantic validation tests for forbidden extra fields and missing required fields.

5. **Example JSON formatting determinism**
   - The test compares loaded JSON equality, which is good semantically.
   - If byte-for-byte deterministic formatting matters for external tools, also compare the file text to `model_dump_json(indent=2) + "\n"` or whatever newline convention is expected.

6. **Wheel command smoke with artifact assertions**
   - Full verification runs the installed wheel command, but only checks it executes.
   - Add artifact assertions around the installed-wheel command if possible.

## Scope creep risks

1. **Recommended commands include import/review workflow commands**
   - This is in the design, but be careful that the new command only prints these strings and does not try to validate paths, read handoff files, open SQLite, or inspect local state.

2. **Documentation wording around “community”**
   - Avoid implying Fashion Radar now discovers, monitors, ranks, verifies coverage for, or connects to any community/social platform.
   - Keep wording limited to “external user-controlled tools generate sanitized local handoff files.”

3. **Future temptation to derive profile from live files**
   - The print-only command should not read `examples/`, `schemas/`, config directories, data directories, or handoff files at runtime. Tests can read these files; the command should not.

4. **Compliance-review phrasing**
   - The boundary says no compliance-review workflow. Docs should say the command does not provide compliance review and should avoid suggesting the profile can certify legal/platform compliance.

## Approval status for implementation

**Not approved yet.**

The design is sound and within scope, but the Important findings should be fixed in the plan before implementation starts, especially:

1. Add the missing `examples/community-signal-profile.example.json` docs instruction.
2. Strengthen no-artifact verification with a real CLI process from a temp cwd.
3. Add strict Pydantic schema/model validation tests.
4. Correct the commit instruction to include the required co-author trailer if commit/push remains in the plan.
