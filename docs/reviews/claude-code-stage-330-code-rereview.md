## Stage 330 Post-Review Re-Review

---

### Critical Findings

None.

---

### Important Findings

**1. Commit allowlist is still incomplete — `scripts/check_release_hygiene.py` and `tests/test_release_hygiene.py` are missing**

`plan.md` Step 4 (`git add` line):

```
docs/superpowers/plans/...plan.md docs/reviews scripts/check_first_run_smoke.py
src/fashion_radar/cli.py tests/test_row_one_cli.py tests/test_row_one_docs.py
tests/test_data_retention_docs.py tests/test_first_run_smoke.py tests/test_scheduling_docs.py
```

Cross-checking against `git diff --stat` (base → working tree), both of these appear in the diff with non-trivial changes, but are absent from the `git add` command:

| Missing from allowlist | Lines changed |
|---|---|
| `scripts/check_release_hygiene.py` | +12 / -5 |
| `tests/test_release_hygiene.py` | +66 / 0 |

The original fix correctly added first-run/scheduling files, but the new post-review files — the very files that were added as part of those fixes — were not added to the allowlist. If Step 4 is run as written, the Claude Code review-artifact enforcement and its tests would be left uncommitted.

Fix: add both paths to the `git add` line in plan Step 4.

---

### Review of Each Focus Area

**1. Release-hygiene regex correctness (includes Claude Code, excludes prompts)**

`REVIEW_CAPTURE_ARTIFACT_PATTERN` at `scripts/check_release_hygiene.py:92–96` requires the filename to end with `(?:review|rereview(?:-[0-9]+)?)\.md$`. A prompt file like `claude-code-stage-330-code-review-prompt.md` ends with `-prompt.md`, which cannot match `review.md` or `rereview.md` — so it falls through the first branch entirely. The secondary guard at line 457 (`endswith("-prompt.md")`) then catches it explicitly. The double-layer exclusion is correct and the prompt-exclusion test confirms it.

The `rereview-N` variant (`(?:-[0-9]+)?`) correctly matches `claude-code-stage-330-plan-rereview-2.md` as shown in the untracked file list.

**2. Stage 330 enforcement without retroactive breakage**

`REVIEW_CAPTURE_MIN_STAGE_BY_TOOL` maps `"claude-code"` →330 and `"opencode"` → 159. `is_review_capture_artifact_path` (line 455) looks up the per-tool minimum before comparing. Stage 329 Claude Code artifacts return `False` and are not inspected. The test `test_stage_329_claude_code_legacy_review_artifact_is_not_rechecked` (with process-chatter content that would otherwise fail) confirms this. Correct.

**3. Test coverage of required behaviors**

| Behavior | Covered |
|---|---|
| Empty-output failure | ✅ parametrized case1 |
| Tool-status chatter failure (`Wrote …`) | ✅ parametrized case 2 |
| Prompt-file exclusion | ✅ `test_stage_330_claude_code_review_artifact_prompt_is_ignored` |
| Legacy Stage 329 not rechecked | ✅ `test_stage_329_claude_code_legacy_review_artifact_is_not_rechecked` |
| Process-chatter start failure (`I'll …`, `Let me …`) for Claude Code Stage 330 | ❌ not directly tested |
| Green-path: well-formed Stage 330 Claude Code artifact passes | ❌ not directly tested |

The two missing cases are not Critical/Important — the code path for both is the shared `review_capture_text_findings` function which is exercised by the existing opencode tests. The overall verification run (hygiene check passing with actual artifacts committed) acts as an implicit integration test. These are minor gaps.

**4. Commit allowlist completeness**

Covered above — two files missing. All other changed files are accounted for: `README.md`, `docs/cli-reference.md`, `docs/data-retention.md`, `docs/first-run.md`, `docs/row-one.md`, `docs/scheduling.md`, `scripts/check_first_run_smoke.py`, `src/fashion_radar/cli.py`, `tests/test_data_retention_docs.py`, `tests/test_first_run_smoke.py`, `tests/test_row_one_cli.py`, `tests/test_row_one_docs.py`, `tests/test_scheduling_docs.py`, and the `docs/reviews` and `docs/superpowers/specs/` new files via their explicit paths or the `docs/reviews` directory entry.

**5. Final verification checklist vs. release gates**

Plan Step 3 now includes all required gates: pytest, ruff check, ruff format, `uv lock --check`, `check_release_hygiene.py`, `check_first_run_smoke.py` (repo-rooted), package build, `check_package_archives.py`, wheel install into temp venv, `fashion-radar --help`, `python -m fashion_radar --help`, installed-wheel first-run smoke, `git diff --check`, and tracked-secret scan. This matches the verification run reported in the prompt. No gaps.

**6. Product/runtime drift**

Post-review changes touch only `scripts/check_release_hygiene.py`, `tests/test_release_hygiene.py`, and the plan/review docs. No changes to `src/fashion_radar/` or any installed runtime code. No product drift.

---

### Residual Release Risk

One residual risk: the missing files from the commit allowlist (finding #1 above). If the plan is executed without fixing Step 4, the hygiene enforcement changes ship uncommitted, leaving Claude Code review-artifact quality ungated until noticed and re-committed separately. Fix is a one-line addition to the `git add` command.
