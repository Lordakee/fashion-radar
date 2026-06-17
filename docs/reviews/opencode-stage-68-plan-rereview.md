I'll read the three files to perform the re-review.
Now let me verify the plan's technical accuracy against the actual codebase to confirm the proposed assertions match reality.
Let me verify the CLI test, the readiness CLI signature, and the smoke validator/fixture to confirm the plan's assertions are technically accurate.
Now let me verify the smoke validator/fixture and check for any other order-sensitive references the plan might have missed.
Let me read the smoke validator, the fixture, and the tests that consume the fixture to confirm the plan handles all of them.
Let me check for any `recommended_commands` count assertions and inspect the first-run flow test that consumes the fixture.
Let me inspect the docs drift tests and confirm there are no count-based or content-based assertions the plan would silently violate.
Let me run one final comprehensive check for any `recommended_commands` references or count/content assertions across all tests that the plan might have missed.
This is significant — `external_tool_templates.py:114` copies `adapter.recommended_commands`. Let me investigate whether the plan's change leaks into the template contract and its tests.
## Re-Review Verdict: Stage 68

**All three first-round items are now addressed:**

1. **`test_external_tool_adapters_command_filters_adapter_and_quotes_paths`** — Plan Task 3 Step 2 (plan:202-229) now dedicates a full step to it, replacing the `[1]`-only check with a loop over `readiness_command = commands[1]` and `manifest_command = commands[2]` plus distinguishing command-name assertions. Verified against `tests/test_cli.py:582` (matches the "before") and the instaloader readiness/manifest shapes. ✓
2. **Quoting-test intent (index `1` preserved, `2` shifted)** — Plan Task 1 Step 3 (plan:100-117) now states explicitly: keep existing `[1]` assertions (they now validate readiness quoting) **and** add a parallel `[2]` block for the shifted manifest. Verified both commands for `x_search_export` emit all four quoted substrings. ✓
3. **Risk enumeration** — Spec Risks section (spec:125-133) now lists all six order-sensitive surfaces (both adapter tests, the CLI filter test, the smoke fixture, the validator, and the first-run flow invocation). ✓

Index-shift math (manifest `[1]→[2]`, dry-run `[5]→[6]`, non-dry-run `[6]→[7]`), the readiness flag set vs `cli.py:802-816`, the `_recommended_commands` single-call-site signature change, and the smoke fixture+validator happy-path/negative-path ordering were all verified correct.

---

## Remaining Important Finding + Blocking Test Gap

### IMPORTANT: Plan silently propagates the readiness command into `external-tool-template` via an untested copy, and omits templates from scope/verification

`src/fashion_radar/external_tool_templates.py:114` builds each template with `recommended_commands=[*adapter.recommended_commands]`. After Stage 68, every `ExternalToolTemplate.recommended_commands` also grows from 8→9 and the table renderer (`external_tool_templates.py:222-224`) prints the readiness command line — yet:

- **Spec claims otherwise.** Spec line 33 says *"No changes to `external-tool-template` JSON/CSV output."* That is narrowly true for the `items`-only JSON/CSV renderers (`external_tool_templates.py:155-173`), but the **model `model_dump()` and the `--format table` output do change**, and the spec/plan never acknowledge this. The plan's code-review scope (Task 4 Step 3, plan:339) only promises `external-tool-readiness`/`external-tool-workflow` semantics stay unchanged — a reviewer is given no signal to check template output.
- **Blocking test gap.** No test in `tests/test_external_tool_templates.py` asserts the count or content of `recommended_commands` (they only check field ordering, the `"Recommended commands:"` header presence, and handoff `items`). So whether the readiness command *should* or *should not* appear in template output is entirely unguarded — the same silent-drift class as the original IMPORTANT-1.
- **Verification blind spot.** The plan's targeted runs (Task 3 Step 5 at plan:289; Task 4 Step 1 at plan:305) omit `tests/test_external_tool_templates.py` entirely. Only the full suite in Task 4 Step 2 would exercise it, and since no assertion guards the field, even that passes vacuously.

**Fix before implementation:** Decide intent and make it explicit —
- If the readiness command *should* appear in template guidance (consistent with the adapter registry): amend the spec's out-of-scope wording to "no changes to template *items/JSON/CSV handoff output*; template `recommended_commands` and table output gain the readiness command," add a template test asserting `external-tool-readiness` is present in `build_external_tool_template(...).recommended_commands`, and add `tests/test_external_tool_templates.py` to the Task 3/4 targeted verification lists.
- If it should *not* (template stays purely handoff-row-focused): filter the readiness command out at the copy site (`external_tool_templates.py:114`) and add a template test asserting it is absent.

Either way, the propagation must be documented and tested before this plan is safe to execute.

No other Critical or Important findings; no further blocking test gaps found.
