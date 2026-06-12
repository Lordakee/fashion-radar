Approved for Stage 16 upload

- `Critical:` None.
- `Important:` None.
- `Minor:`
  - Consider adding one focused test for JSON object top-level strictness with an otherwise valid `{"items": [...], "extra": ...}` payload. The implementation correctly rejects this via `set(payload) == {"items"}`, but the current test only covers `{"items": {}}`; an explicit extra-key test would protect the “strict top-level shape” requirement.
  - Consider adding a CLI assertion for non-`--strict` warning-only files exiting `0` in a dedicated test. `test_community_signal_lint_does_not_create_project_artifacts` currently covers this indirectly with a warning-only CSV and `exit_code == 0`, so behavior is covered, but a named test would make the contract more obvious.

Review notes:

- The allowed field set in `src/fashion_radar/community_signals.py` matches `schemas/community-signals.schema.json` and is protected by `test_community_signal_linter_allowed_fields_match_schema`.
- Prohibited fields emit `prohibited_field` only; unrelated extras emit `unknown_field`; CSV over-wide rows emit `csv_extra_cells`.
- JSON shape is stricter than `import-signals`, accepting only a top-level list or an object with exactly `items` as a list.
- Import-readiness uses `ManualSignalRow.model_validate()` and mirrors the fallback `source_name.strip() or "Manual Import"` behavior from `load_manual_signal_rows()`.
- The CLI command is read-only: it calls only the linter/rendering path, does not construct engines, initialize schema, store rows, collect, match, score, report, package digests, or touch dashboard state.
- Table and JSON output are deterministic via sorted counts/findings and stable Pydantic model field order.
- Error/warning exit behavior matches the goal: errors always exit non-zero; warnings exit non-zero only with `--strict`.
- Invalid files are converted to `invalid_file` findings and avoid tracebacks.
- Documentation consistently frames the feature as local file diagnostics, not source acquisition, platform monitoring, compliance/audit, or market-wide claims.
