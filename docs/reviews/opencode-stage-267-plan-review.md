## Stage 267 Plan Review

### Critical

**C1 — `expected_first_run_flow_commands` is not updated; the deterministic command-sequence test will fail.**
`tests/test_first_run_smoke.py:4374` calls `assert_first_run_flow_commands(captured, ...)`, which is a **strict-equality** check (`captured == expected_first_run_flow_commands(...)`, `test_first_run_smoke.py:1994`). Task 2 adds a new `row-one serve --dry-run` call to `run_first_run_flow` (`scripts/check_first_run_smoke.py:~2827`), and `fake_run_cli` records *every* call into `captured` (`test_first_run_smoke.py:4213`). The resulting extra tuple is not in `expected_first_run_flow_commands` (`test_first_run_smoke.py:1708`), so `test_run_first_run_flow_uses_deterministic_local_command_sequence` fails and Task 2 Step 5's "Expected: PASS" cannot hold. The plan must add a step inserting the serve tuple into `expected_first_run_flow_commands` **between** the `row-one preview` tuple (ends `:1868`) and the `row-one local-ops` tuple (starts `:1869`). Note Task 2 Step 4's `in captured` assertion is *not* a substitute — the strict-equality assertion fails first.

### Important

**I1 — Docs edit risks removing the only `row-one serve --dry-run` mention in `docs/row-one.md`.**
The new docs test asserts `"row-one serve --dry-run" in row_one_doc`. That exact phrase currently appears only at `docs/row-one.md:115` inside the sentence the plan rewrites ("update Daily Readiness And Preview"). Task 3 Step 3 is ambiguous about whether the trailing `--dry-run-serve-url`/`row-one serve --dry-run` sentence is retained. The plan should explicitly instruct keeping that sentence, or the test fails.

### Minor

- **M1** — Task 2 Step 4's standalone `in captured` assertion is redundant once C1 is fixed (strict equality already covers ordering); it adds little and may mislead an implementer into treating it as sufficient. Consider dropping it.
- **M2** — The plan doc ends with a trailing `*** Add File: .../opencode-stage-267-plan-review-prompt.md` block (`plan:444-464`) that inlines the review prompt inside the plan itself rather than creating the file. Presentation noise; consider writing it to `docs/reviews/` as a real artifact.
- **M3** — Release-gate command at `plan:369` combines `UV_NO_CONFIG=1` with `uv --no-config`; redundant but harmless.

### Verified correct
- Preview keeps `JSON:` line and adds `Manifest:` after it (`cli.py:1460`); no build/render behavior change. ✓
- Manifest validator fields match `render.py:122-156` (`contract_version`, `app_contract.path`, `site.index_path/manifest_path`, counts vs `edition.json`, readiness logic). ✓
- `row-one serve --dry-run` for host `127.0.0.1` emits exactly `Open: http://127.0.0.1:8787` (`server.py:25`) and validates the dir without binding a socket; generated site passes `validate_row_one_site_dir`. ✓
- `Mapping` already imported (`check_first_run_smoke.py:14`). ✓
- Scope stays clear of `row-one-app/v1` schema, provenance, collectors, scoring, scheduling, cleanup, deployment, image/LLM, and compliance-review. ✓

### Verdict
**Approve with revisions.** Fix C1 (add the serve command to `expected_first_run_flow_commands` in the correct position) and clarify I1 before implementation; both are quick, localized edits. With those, the plan is feasible and the tests become executable as written.
