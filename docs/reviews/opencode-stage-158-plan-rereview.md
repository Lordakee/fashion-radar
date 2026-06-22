## Stage 158 Plan Rereview

I verified every fidelity claim against the real pydantic source models.

### Verdict

**No critical findings. No important findings.** The plan is safe to implement. I-1 from the first review is fully resolved. One new minor finding and two carried-over minor findings (all non-blocking).

---

### Critical
None.

### Important
None. **I-1 is resolved.** Verified against source:

- `community_signal_lint` block now mirrors all 14 fields of `CommunitySignalDirectoryLintResult` (`src/fashion_radar/community_signals.py:87-107`), including `field_counts` (all 8 `ALLOWED_COMMUNITY_SIGNAL_FIELDS` at count 2), `source_name_counts`, and `platform_counts`.
- `candidate_preview` block now mirrors all 12 fields of `CommunityCandidateDirectoryPreview` (`src/fashion_radar/community_candidates.py:53-67`). `directory`/`pattern` correctly dropped (model is `extra="forbid"` with neither field). Window math checks out: `as_of` (2026-06-13) - `current_days` (7) = `current_window_start` (2026-06-06); `baseline_window_start` (2026-05-07) = `as_of` - 37 days. Consistent with sibling `community_candidates_payload(directory=True)` at `tests/test_first_run_smoke.py:343-359`.
- The new `test_validate_community_handoff_check_dir_rejects_nested_count_drift` test addresses M-2. Error path verified: `assert_equal` (`scripts/check_first_run_smoke.py:499-501`) raises `SmokeError("community-handoff-check-dir lint row_count expected 2, got 5")`, which contains the `"lint row_count"` match substring.
- Top-level payload matches all `CommunityHandoffDirectoryCheckResult` fields (`src/fashion_radar/community_handoff_check.py:47-65`). `expected_first_run_flow_commands()` diff context (Task 1 Step 3) correctly references the current `--strict` terminator at `tests/test_first_run_smoke.py:1691-1704`.

### Minor

**M-4 (new): `import_dry_run.findings` omitted from fixture.** The real `ManualSignalDirectoryDryRunResult` (`src/fashion_radar/importers/manual_signals.py:119-132`) always serializes `findings` (default `[]`), but the plan's `import_dry_run` block leaves it out. Same category as the original I-1, just narrower (one default-valued list field). Non-blocking because the validator does not read `import_dry_run.findings`; it only affects drift detection for that single field. Suggest adding `"findings": []` for full parity with the lint block (which already includes it).

**M-1 (carried over, accepted):** No payload-parity test. Prior review accepted this as "acceptable to skip given real smoke coverage." Still applies.

**M-3 (carried over, accepted):** `candidate_preview = None` path. Prior review noted as documentation only. Validator correctly requires a dict for the OK first-run contract.

---

### Answers to review questions

1. **Does the updated fixture resolve the important fidelity issue?** Yes. Fully resolved and verified against `community_signals.py:87`, `community_candidates.py:53`, and `community_handoff_check.py:47`.
2. **Safe to implement without critical or important issues?** Yes.
3. **Are remaining findings minor enough to proceed?** Yes. M-4 is a one-line optional cleanup (`"findings": []` in `import_dry_run`); M-1 and M-3 were already accepted.

Recommendation: proceed to implementation. Optionally add `"findings": []` to `import_dry_run` for full fixture parity, but this is not blocking.
