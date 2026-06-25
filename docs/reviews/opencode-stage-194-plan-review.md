I'll review the Stage 194 design and implementation plan. Let me read all the required files in parallel.
Now let me read the remaining required files in parallel.
Now let me read the plan, README, and test files.
Now let me examine the CLI implementation and the existing trends tests to verify the parity claims.
Let me read the existing `trends` baseline tests and the existing `trend_explanations` tests to verify the parity of the planned mirrors.
Let me verify the CHANGELOG structure and double-check a critical detail in the planned docs guard wording.
Let me re-verify the exact current wording case-insensitively, since my first grep was case-sensitive.
I have completed a thorough review. Let me verify one final detail about the existing test's assertion patterns to confirm parity claims before writing findings.
# Stage 194 Plan Review

I read all required files, verified the production CLI handling (`cli.py:1604-1621` for `trend_explanations_command` vs `cli.py:1528-1545` for `trends_command`), confirmed the existing `trends` baseline tests (`tests/test_cli.py:8426` and `:8454`), and cross-checked the planned docs guards against the planned replacement text and current doc wording.

## Critical findings

None.

## Important findings

**I1 — Docs guard / replacement wording mismatch will fail the plan's own Step 7 verification.**

The new guard in Task 3, Step 2 (`test_current_direction_docs_prioritize_liveness_backed_source_coverage`) asserts, for the PROJECT_BRIEF section:

```python
assert "external/community handoff expansion remains frozen" in _normalized_text(
    sections["docs/PROJECT_BRIEF.md##Current Review-Aligned Priorities"]
).casefold()
```

But the Task 3, Step 5 PROJECT_BRIEF replacement (plan lines 354-355) writes:

> `Experimental/community handoff expansion remains frozen while these remaining core gaps are addressed.`

After `.casefold()`, the section text contains `experimental/community handoff expansion remains frozen`. The asserted phrase `external/community handoff expansion remains frozen` is **not** a substring (`exper…` vs `exter…` diverge at the 3rd character). I confirmed via `rg` that the only current occurrence of this phrase across the four direction docs is `Experimental/community` in `docs/PROJECT_BRIEF.md:173`, so there is no other location that would satisfy the guard.

Consequence: Task 3 Step 7 (`pytest ... test_current_direction_docs_prioritize_liveness_backed_source_coverage ...`) will fail even after the docs edit is applied correctly, so the plan as written cannot reach its stated acceptance criterion ("Focused tests ... pass before commit"). Fix one side to match the other — either change the guard phrase to `experimental/community handoff expansion remains frozen`, or change the PROJECT_BRIEF replacement bullet to use `external/community`. Either is a one-word fix.

## Minor findings

**M1 — Redundant "source" in the full-project review follow-up bullet.** The Task 3 Step 4 replacement writes "use source-liveness evidence to expand **source** curated public-source coverage" (plan lines 332-334). This reads as a duplicated word and is inconsistent with the other three doc updates, which all say "broaden/expand curated public-source coverage". The docs guard still passes (`curated public-source coverage` is a substring), but the wording should be cleaned to `expand curated public-source coverage`.

**M2 — Slight ambiguity in the follow-up-status required-phrase tuple.** Task 3 Step 1 says "update ... so the required phrases include:" a 7-item block, then "Remove the old required phrase: `trend/heat explanation`". The existing test also asserts Stage 188/189/190/191 phrases. "include" reads as augmentation, but a literal "replace the tuple" reading would drop the Stage 188-191 assertions. The proposed replacement text contains all of Stages 188-193, so either reading passes; recommend stating explicitly that the Stage 188-191 phrases are retained so the test keeps its historical coverage.

## Review answers

1. **Coverage parity gap, not a defect?** Yes. The design and plan correctly frame the Stage 193 note as cosmetic coverage symmetry. I verified the production handling already exists verbatim at `cli.py:1604-1621` (mirroring `cli.py:1528-1545`), and the Stage 193 code rereview explicitly called it "cosmetic coverage symmetry, not a defect."
2. **Right mirrors?** Yes. `test_trend_explanations_command_invalid_baseline_writes_nothing` mirrors `test_trends_command_rejects_invalid_baseline_before_data_dir_creation` (`tests/test_cli.py:8426`) and `test_trend_explanations_command_rejects_baseline_at_or_after_as_of` mirrors `:8454`. Inputs, `exit_code == 1`, and `not data_dir.exists()` match. The command-specific strings asserted (`Could not explain trend deltas: invalid --baseline-as-of`, `Could not explain trend deltas: baseline-as-of must be before as-of`) exactly match production at `cli.py:1612` and `cli.py:1618`. The ordering test is marginally stronger than its `trends` analog (asserts the full prefix), which is acceptable.
3. **Avoid production edits unless a focused test fails?** Yes. Both error paths sit inside the `try` block before `db_path = default_database_path(data_dir)` (`cli.py:1629`), so no `data_dir`/SQLite creation occurs — the `not data_dir.exists()` assertions will hold with no production change. The "smallest production fix only if a test fails" stance is correct and aligned with the Stage 193 rereview.
4. **Full-project review update limited to `Current Follow-Up Status`?** Yes. The plan replaces only that bullet list; the docs guard extracts only that section via `_section(text, "Current Follow-Up Status")`; the historical Critical/Important/Strengths/Recommended-Next-Steps sections are explicitly out of scope and untouched.
5. **Direction correctly marks Stage 190/193 complete and redirects?** Yes. All four direction-doc edits and the follow-up status treat `source-liveness` and `trend-explanations` as existing capabilities, redirect next work to source-liveness-backed curated public-source coverage and deterministic matching quality, and the follow-up bullet carries the explicit "without claiming demand proof or platform coverage verification" disclaimer. (Subject to M1 wording cleanup.)
6. **Avoids prohibited surfaces/features?** Yes. The stage is strictly test-only + docs-only. Files touched are `tests/test_cli.py`, `tests/test_review_protocol_docs.py`, four direction docs, the full-project review status, CHANGELOG, and review artifacts. No new CLI command/flag/output field, no TrendDelta/TrendComparison/HeatMoversReport/schema changes, no external-tool/community/imported surface changes, and the out-of-scope list in the design matches the AGENTS.md boundaries (no scraping, platform APIs, monitoring, scheduling, ranking, demand proof, coverage verification, compliance-review). README/PROJECT_BRIEF replacements restate the external/community/imported freeze.

## Verdict

The plan is sound in scope, architecture, and intent, and correctly stays within the v0.1.x freeze. However, **I1 is an internal inconsistency that will make the plan's own Task 3 Step 7 verification fail when followed verbatim**, so it must be reconciled before implementation begins.

Fix I1 (one-word alignment between the guard phrase and the PROJECT_BRIEF replacement), and optionally clean up M1/M2. After I1 is resolved, this plan is acceptable. Because an Important finding remains open, I am withholding the approval phrase at this time.

**Not yet approved — resolve Important finding I1, then this is approvable for Stage 194 implementation.**
