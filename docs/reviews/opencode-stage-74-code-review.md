I'll review Stage 74 systematically. Let me start by examining the touched files and the runtime builder they need to match.
Let me examine the runtime builder, the static fixture, and the sibling parity tests to verify the comparison is meaningful.
Now let me read the full test file section with the static fixture, plus the sibling parity tests for context.
Let me check the `external_tool_adapter_commands` helper and `EXTERNAL_TOOL_ADAPTER_BOUNDARIES`, and the sibling parity tests for templates/workflow/readiness.
Now let me verify the parity test passes, plus the Stage 73 negative tests and first-run sequence test that the implementation claims to preserve.
Let me check that the field-mapping `required` flag changes don't silently break other consumers, and that the runtime source files truly are unchanged.
Let me check whether any other consumer in the test file or smoke module still assumes the old (incorrect) required flags for `summary`/`source_name`/`platform`, and look at the spec/plan/review docs briefly.
Let me check the plan doc and the review prompt docs, and run the full pytest to confirm the 1100-test verification claim.
Let me run the full smoke test file plus ruff checks to confirm the implementation verification claim.
I have enough to deliver the review. All code/test verification passes; one documentation defect found.

---

## Stage 74 Code Review

**Critical:** None.
**Important:** None.
**Minor:**

**M1. `docs/reviews/opencode-stage-74-plan-review.md` is corrupted — two concatenated drafts.** Line 23 ends mid-word (`"...already character-i## Stage 74 Plan Review"`) and a second, condensed version of the review begins there. Lines 38-47 are orphaned fragments of the first draft (about `description`/`upstream_tool_examples`/`field_mappings`) that appear *after* the second draft's "Answers to review questions" section and contradict the flow. Recommend rewriting the file as a single coherent review before commit. The `code-review-prompt.md` correctly lists this file as touched, so it will ship in the Stage 74 commit if left as-is.

### Answers to review questions

1. **Parity test uses intended deterministic inputs?** Yes. `tests/test_first_run_smoke.py:1090-1100` calls `build_external_tool_adapter_registry(directory=Path("./exports"), config_dir=Path("./configs"), data_dir=Path("./data"), as_of="2026-06-13T12:00:00Z")` and compares `json.loads(...model_dump_json())` — identical parameter shape to the sibling template/workflow/readiness parity tests (`tests/test_first_run_smoke.py:1103-1149`). `model_dump_json()` is the right fidelity choice (catches `Literal`/enum and datetime rendering).

2. **Fixture remains static?** Yes. `external_tool_adapters_payload()` at `tests/test_first_run_smoke.py:679-728` is still a plain dict literal built from `EXTERNAL_TOOL_ADAPTER_CASES`/`EXTERNAL_TOOL_FIELD_MAPPINGS`/`EXTERNAL_TOOL_ADAPTER_BOUNDARIES` plus the existing `external_tool_adapter_commands(...)` `shlex.join` helper. No delegation to the runtime builder.

3. **Stage 73 negatives + first-run flow preserved?** Yes. Verified by direct run of both tests (pass) and by inspection: the smoke validator `validate_external_tool_adapters` does not inspect `description`, `upstream_tool_examples`, `field_mappings`, or `boundaries`, so the fixture fidelity edits cannot break `test_validate_external_tool_adapters_requires_print_only_registry_contract` (`tests/test_first_run_smoke.py:1465`). The negative mutations target only fields the validator *does* check.

4. **Runtime/external-platform behavior altered?** No. `git diff --stat HEAD` shows only `tests/test_first_run_smoke.py` changed (`+139/-19`); `src/`, `scripts/`, `pyproject.toml`, `uv.lock` untouched.

5. **Critical/Important before commit?** None. Only the doc-quality issue (M1) above.

### Verification re-run (this review)

- `pytest tests/test_first_run_smoke.py::test_external_tool_adapters_payload_matches_real_registry ::test_validate_external_tool_adapters_requires_print_only_registry_contract ::test_run_first_run_flow_uses_deterministic_local_command_sequence` → 3 passed.
- `pytest tests/test_first_run_smoke.py -q` → 53 passed.
- `ruff check` + `ruff format --check` on the test file → clean.
- `git diff --check` → clean.
- Spot-checked fixture fidelity vs runtime: 7 adapter cases match `external_tool_adapters.py:108-233` (ids, descriptions, upstream examples including the 2-entry lists for `x_search_export` and `generic_community_export`); `EXTERNAL_TOOL_FIELD_MAPPINGS` required flags now correctly limited to `url`/`title`/`published_at` matching `COMMUNITY_SIGNAL_REQUIRED_FIELDS` (`community_signal_profile.py:37`); notes match `FIELD_NOTES` (`external_tool_adapters.py:39-48`).

### Scope-boundary check

The change is strictly test-only fixture parity. No new connectors, scraping, browser automation, platform APIs, login/cookie/session/token/proxy/CAPTCHA behavior, media download, monitoring/scheduling, source acquisition, demand proof, ranking, coverage verification, or compliance-review product behavior introduced.

**Recommendation:** Proceed to commit after fixing M1 (rewrite `opencode-stage-74-plan-review.md` as a single coherent document).

### Correction Note

The M1 finding above referred to an earlier corrupted draft of
`docs/reviews/opencode-stage-74-plan-review.md`. The committed Stage 74
plan-review artifact is the cleaned single-review version, so M1 is resolved
and does not remain a release blocker.
