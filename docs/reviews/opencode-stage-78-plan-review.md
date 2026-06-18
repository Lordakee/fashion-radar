I'll review the Stage 78 plan and spec. Let me start by reading both documents and gathering context.
Now let me verify the plan against the actual codebase. I'll examine the builders, models, and existing tests in parallel.
Now let me examine the workflow and readiness builders to verify the command index maps, plus the template builders.
Now let me examine the template builder and the community_signals lint function, plus the existing docs test file.
I found a significant concern in the docs drift test. Let me verify the lint function signature/result shape and check the existing docs file structure plus the dirty `uv.lock` state.
Let me verify the docs insertion point and check the existing `community-signal-import.md` structure, plus confirm the verification commands.
Let me verify whether the plan's `uv lock --check` verification step actually passes against the dirty worktree `uv.lock`, since this is a key safety question.
`uv lock --check` passes (exit 0) even with the mirror-rewritten working-tree `uv.lock`, and the mirror scan in the plan targets `git show HEAD:uv.lock` (clean). Let me verify no existing docs test depends on the two sections being adjacent, and run a quick baseline check of the relevant test files.
I have completed verification. Here is my review.

---

# Stage 78 Adapter Contract Parity Gate — Plan Review

## Verdict

The **core parity test module (Task 1) is sound** — I verified every builder signature, model shape, command-index map, and the lint result interface against current `src/`. The command parity maps are exactly correct, the banned-token test has no false-positive risk on the current command set, and the dirty working-tree `uv.lock` is handled safely (verified empirically). **However, there is one Critical defect**: the Task 2 docs drift test is mutually inconsistent with the docs prose the plan tells the implementer to write, so the plan's own "Expected: all pass" checkpoint is unreachable as written.

---

## Critical

### C1. Docs drift test cannot pass against the docs subsection the plan specifies
`docs/superpowers/plans/2026-06-18-stage-78-adapter-contract-parity-plan.md:317-343` vs `:368-386`

The test in Task 2 Step 1 and the prose in Task 2 Step 3 disagree in three ways, so Task 2 Step 5 (`:405-408`, "Expected: all pass") will fail for an implementer who follows both blocks verbatim.

1. **Missing literal phrase.** The first assertion block (`:329`) requires `"dry-run import guidance remains separate from real import guidance"` in raw text. The subsection prose (`:380-381`) only says "dry-run import guidance remain aligned" — the required phrase never appears.

2. **Case mismatch.** The second block (`:333-342`) checks lowercase terms against `normalized = _normalized_doc_text(...)` (`:319`), but that helper (`tests/test_cli_docs.py:311-312`) only collapses whitespace — it does **not** casefold. So `"json/csv template output remains importable rows only"` (`:334`) cannot match the doc's `"JSON/CSV template output remains importable rows only"` (`:380`, uppercase `JSON/CSV`). The repo's own convention is `.casefold()` on the normalized text (see `tests/test_cli_docs.py:534`, `:541`, `:1167`).

3. **Distributed-negation substrings absent.** The prose "It does not add connectors, fetch URLs, … prove demand, rank sources, or verify platform coverage." (`:383-385`) distributes one `does not` across a list, so the literal substrings `"does not prove demand"`, `"does not rank sources"`, and `"does not verify platform coverage"` (`:337-340`) never occur as substrings and each assertion fails.

**Fix (pick one and apply consistently):**
- Make the prose literally contain every required term (add a standalone sentence "Dry-run import guidance remains separate from real import guidance." and standalone "It does not prove demand. It does not rank sources. It does not verify platform coverage.") **and** either match case in the test or `.casefold()` the normalized text; or
- Change the test to `_normalized_doc_text(...).casefold()` and replace the impossible substrings with terms that actually appear (e.g. `"prove demand"`, `"rank sources"`, `"verify platform coverage"`, `"dry-run import guidance remain aligned"`).

Either way, Task 2 Step 2's "Expected before docs update: the test fails" must fail for the *intended* reason (subsection absent), and Task 2 Step 5 must pass for the *right* reason (prose satisfies the terms). Today the test would fail both before *and* after the docs edit.

---

## Important

None beyond C1. The substantive parity gate (Task 1) and the release/stage/publish chain (Task 3) are correct.

---

## Minor

### M1. `COMMUNITY_SIGNAL_IMPORT_DOC` is not defined — make the add unconditional
The constant does not exist anywhere in `tests/` today (grep: 0 matches). The plan says "If `COMMUNITY_SIGNAL_IMPORT_DOC` is not already defined, add …" (`:345-349`). The conditional is dead and easy to skim past; the test references the name at `:318-319` before the definition instruction. State it as a definite "Add `COMMUNITY_SIGNAL_IMPORT_DOC = ROOT / "docs" / "community-signal-import.md"` near the other `ROOT / ...` constants (`tests/test_cli_docs.py:16-28`)."

### M2. `uv lock --check` does not detect the mirror contamination — keep the explicit `rg` guard
Verified in the current worktree: `UV_NO_CONFIG=1 uv lock --check` exits 0 despite the working-tree `uv.lock` being mirror-rewritten (`pypi.org` → `tuna.tsinghua.edu.cn`). So the plan's real protection against mirror leakage is `git show HEAD:uv.lock | rg 'tuna|aliyun|...'` (`:452-454`) plus the staging guard (`:456`, `:480`). These are present and correct, but do not let a future edit drop the `rg` scan on the assumption that `uv lock --check` covers it — it does not.

### M3. `Path("./exports")` normalizes to `"exports"`
`DIRECTORY = Path("./exports")` (`:66`) yields `str(DIRECTORY) == "exports"` (leading `./` stripped by `PurePath`). This is deterministic and identical across all builder calls, so every parity assertion still holds — but the generated commands will contain `--directory exports` rather than `--directory ./exports`. No correctness impact; noting only because it can confuse a reader diffing test output against the docs/profile examples that use `./exports`.

---

## Question-by-question answers

1. **Public builders / model shapes correct?** Yes for Task 1. Confirmed `build_external_tool_adapter_registry`, `build_external_tool_template`, `render_external_tool_template_{json,csv}`, `build_external_tool_workflow`, `build_external_tool_readiness`, `build_community_signal_profile`, `lint_community_signal_file` all exist with the kwargs shown; `ExternalToolAdapterFieldMapping.model_dump(mode="json")` yields `{field,required,note}`; `CommunitySignalLintResult.ok` (property, `community_signals.py:82-84`) and `.valid_row_count` (`:64`) match the `:205-212` assertions; template `items` envelope `{"items": [...]}` matches `:198-200`.
2. **Deterministic across machines?** Yes. Fixed `AS_OF`, `which=lambda _command: None` for readiness (`:246`, `:285`), `tmp_path` for rendered files, pure builders, and stable `parse_datetime_utc(...).isoformat()`. (See M3 for a cosmetic path note.)
3. **Command parity maps correct?** Yes — verified all 9 entries in `WORKFLOW_RECOMMENDED_COMMAND_STEPS` (`:81-91`) and all 4 in `READINESS_RECOMMENDED_COMMAND_STEPS` (`:93-98`) against `external_tool_adapters.py:357-488` (indexes 0–8) and the step `name`→command wiring in `external_tool_workflow.py:170-423` and `external_tool_readiness.py:303-445`. Shared-step reuse and dry-run separation (`:234-235`, `:253`) are correct.
4. **Banned-token false positives?** No risk on the current command set. Matching is exact whole-token after `shlex.split`, so `tiktok_api` and the quoted value `'TikTok-Api Export'` do not collide with `api`. Install hints are (correctly) excluded — they live on `checks[].install_hint`, not in `steps[].command`/`recommended_commands`.
5. **Docs/tests visibility without over-constraining?** Appropriate *scope*, but the docs drift test is unsatisfiable as written — see C1. Once C1 is fixed, the anchor is well-placed between `## External Tool Adapter Registry` (`docs/community-signal-import.md:158`) and `## External Tool Template Rows` (`:189`), and no existing docs test splits on those two headings (grep: none), so insertion is safe.
6. **Verification / staging / publish safe with dirty `uv.lock`?** Yes. `UV_NO_CONFIG=1 uv lock --check` passes in the dirty worktree (verified, exit 0); the mirror scan reads `git show HEAD:uv.lock` (clean); staging uses an explicit file list (`:465-474`) with `! git diff --cached --name-only | rg -x 'uv.lock'` guards (`:480`); commit and the Git Data API publish use `HEAD^{tree}`, which excludes the working-tree `uv.lock`; post-publish tree-parity check (`:504`) confirms. The pre-existing mirror rewrite stays out of scope as required.
