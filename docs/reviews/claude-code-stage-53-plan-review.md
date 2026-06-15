## Critical

None.

## Important

None.

There are no Critical or Important findings that must be fixed before coding.

## Minor

1. **Docs drift test is useful but somewhat permissive**
   - The proposed `test_community_signal_import_doc_keeps_profile_recommended_command_order` matches the design intent, but it only checks that the profile command names appear as a subsequence anywhere in `docs/community-signal-import.md`.
   - This is not blocking, but it could pass even if the commands are spread across unrelated prose examples.
   - If desired, scope it to the directory handoff/preflight section or assert the documented “local sequence” sentence includes the same command names in order.

2. **CLI invalid output-format test can be slightly simplified**
   - The proposed `community-candidates-dir --format xml` parser test is meaningful and aligns with existing parser-guard tests.
   - It currently prepares a full fixture and monkeypatches config/directory loaders. That is acceptable and consistent with nearby tests, but the parser should reject before needing the fixture contents.
   - Not blocking; the current approach proves the command body is not entered.

3. **Review-record and upload steps are process tasks, not Stage 53 product changes**
   - The plan’s Task 4 adds `docs/reviews/*` files and includes commit/upload/Actions steps.
   - This does not violate the test/docs-only constraint, but it is broader than the design’s product-facing changes.
   - Keep those as release-process steps, not as implementation logic, and ensure they do not mask the core Stage 53 diff.

## Evaluation

### 1. Match with design and current codebase

The plan matches the design and current codebase.

- `PROHIBITED_COMMUNITY_SIGNAL_FIELDS` is centrally defined in `src/fashion_radar/community_signals.py`, and parameterizing over it is the right guardrail.
- Current JSON lint behavior intentionally accepts only:
  - top-level arrays, or
  - objects whose only key is `items`.
- Therefore the proposed JSON top-level prohibited-key trap test matches existing behavior: extra top-level keys should produce `invalid_file`, not row-level `prohibited_field`.
- Current CSV lint behavior treats extra cells under the `None` key as `csv_extra_cells`, removes the `None` key before raw-field checks, and therefore should not treat extra cell values as field names. The proposed trap test matches that behavior.
- `community-candidates-dir` uses `CommunityCandidatesOutputFormat = Literal["table", "json"]`; Typer should reject `--format xml` before entering the command body. The proposed parser test is aligned.
- `build_community_signal_profile().recommended_commands` currently has the planned command sequence:
  1. `community-signal-lint-dir`
  2. `community-candidates-dir`
  3. `import-signals-dir --dry-run`
  4. `import-signals-dir --imported-at "$AS_OF"`
  5. `imported-review-workflow`

### 2. Test meaningfulness and brittleness

The proposed tests are meaningful.

- The prohibited-field parameterization directly guards against drift in the community contract.
- The CSV extra-cell and JSON top-level-key trap tests are valuable because they document intentional boundary behavior rather than accidentally broadening prohibited-field detection.
- The profile command test uses `shlex.split`, which is appropriate for validating command semantics without brittle raw-string comparisons.
- The CLI parser test verifies validation happens before config loading or directory preview work.
- The docs drift test is useful, though a bit broad/permissive as noted under Minor.

### 3. Proposed assertions vs current intentional behavior

No proposed assertion appears to conflict with current intentional behavior.

Specific checks:

- `result.error_count == 1` for each prohibited field should hold because extra manual-import fields are currently tolerated by the importer model but flagged by community lint.
- `result.valid_row_count == 1` should hold because the otherwise-valid row remains import-ready even with extra/prohibited fields.
- `csv_extra_cells` should be the only finding in the CSV extra-cell trap because the allowed fields are complete and populated.
- JSON top-level extra/prohibited keys should remain `invalid_file`, not `prohibited_field`.
- The profile dry-run command currently omits `--imported-at`; the plan’s assertion matches the profile’s current sequence.
- The import command currently includes `--imported-at`; the plan’s assertion matches current behavior.

### 4. Safe split across disjoint write scopes

Yes, the implementation can be split safely across mostly disjoint scopes:

1. **Lint guardrails**
   - `tests/test_community_signal_lint.py`

2. **Producer profile guardrails**
   - `tests/test_community_signal_profile.py`

3. **CLI parser guardrail**
   - `tests/test_cli.py`

4. **Docs drift + docs clarification**
   - `tests/test_cli_docs.py`
   - `docs/community-signal-import.md`

5. **Changelog / process docs**
   - `CHANGELOG.md`
   - optionally `docs/reviews/*`

The only coordination needed is between the docs drift test and `docs/community-signal-import.md`, because that test depends on the documented command order.

### 5. Blocking issues before coding

No Critical or Important issues need to be fixed before implementation begins.
