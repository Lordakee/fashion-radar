## Final Re-Review Verdict: Stage 68

**The template-propagation blocker from the prior rereview is fully resolved.**
Spec, plan, tests, and targeted verification all now handle the template
inheritance explicitly, and the technical assertions were verified against the
real source.

### Prior finding — resolved

- **Template inheritance documented and tested.** Spec lines 33-36 now state
  `external-tool-template` table/model guidance inherits the readiness command
  via the existing `recommended_commands=[*adapter.recommended_commands]` copy,
  while JSON/CSV handoff-row output stays rows-only. Verified against
  `src/fashion_radar/external_tool_templates.py:114` (copy site),
  `:155-158` (JSON renderer emits only `{"items": ...}`), and `:16I now have full context. The `opencode-stage-68-plan-final-rereview.md` is the artifact for *this* review, and its prompt is the final-rereview prompt — both exist on disk but are **not** in the plan's commit step. Let me record the verdict and then summarize.
## Final Re-Review Verdict: Stage 68

**The template-propagation blocker is fully resolved.** All four confirmation points hold:

- **Inheritance** — spec:33-36 documents the `recommended_commands=[*adapter.recommended_commands]` copy (verified at `external_tool_templates.py:114`); plan Task 3 Step 1 tests it.
- **Rows-only JSON/CSV** — plan asserts `not in json_output`/`not in csv_output`; renderers at `external_tool_templates.py:155-173` emit items only.
- **Template test + targeted verification** — `tests/test_external_tool_templates.py` is in Task 3 Step 6, Task 4 Steps 1-2; all signatures verified accurate.
- **Rereview artifacts in commit** — first-rereview pair is in `git add`.

Index math, readiness CLI flags (`cli.py:802-817`), single call-site plumbing, and smoke happy path all verified.

### Remaining Important findings + test gap

**IMPORTANT 1 — Commit step omits this round's artifacts.** `docs/reviews/opencode-stage-68-plan-final-rereview-prompt.md` and `…rereview.md` exist on disk but are absent from plan Task 4 Step 4 `git add` (plan:398). The File Map (plan:40-44) also omits *both* rereview pairs, making it inconsistent with its own commit step. Executing as-written leaves these untracked. Fix: add both paths to the File Map and `git add`; reconcile the File Map with everything it stages.

**IMPORTANT 2 / test gap — No negative cases for new smoke validator branches.** Task 3 Step 4 (plan:275-292) adds three new `SmokeError` paths to `validate_external_tool_adapters`, but `test_validate_external_tool_adapters_requires_print_only_registry_contract` (`test_first_run_smoke.py:1122`) — which tests a negative case for every existing branch — gains none. Happy path is covered; error branches are unguarded. Fix: add negative cases (no `recommended_commands`; missing readiness command; readiness command missing a token).

No Critical findings; no other blocking test gaps.
acts" lists only the original
  four (`plan-review-*`, `code-review-*`) and omits *both* rereview pairs
  entirely, even though the `git add` does include the first rereview pair — so
  the File Map is internally inconsistent with its own commit step.

Executing the plan as written leaves the `plan-final-rereview` files untracked,
which directly violates the "include plan rereview artifacts in the final
commit" item this review was asked to confirm.

**Fix:** Add `docs/reviews/opencode-stage-68-plan-final-rereview-prompt.md` and
`docs/reviews/opencode-stage-68-plan-final-rereview.md` to the File Map's review
artifact list and to the Task 4 Step 4 `git add`. (While there, reconcile the
File Map so it lists every review file the `git add` stages.)

### IMPORTANT 2 / test gap: No negative unit tests for the new smoke validator branches

Plan Task 3 Step 4 (plan:275-292) adds three new `validate_external_tool_adapters`
`SmokeError` paths — `"recommended_commands must be a list"`,
`"missing external-tool-readiness command"`, and `"readiness command missing
{expected}"`. The existing
`tests/test_first_run_smoke.py::test_validate_external_tool_adapters_requires_print_only_registry_contract`
(1122-1143) follows a strict convention of asserting one negative case per
validator branch (contract_version, execution_mode, first adapter id), but the
plan adds no negative cases for the three new branches. The happy path is
covered (fixture gains the readiness command), but the new error branches are
unguarded against future regression.

**Fix:** Extend that test (or add a sibling) with negative cases: fixture
without `recommended_commands`; fixture whose command list omits the readiness
command; readiness command missing one required token.

---

No Critical findings. No other blocking test gaps.
