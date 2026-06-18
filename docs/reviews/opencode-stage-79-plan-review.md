I'll review the Stage 79 plan. Let me start by reading the spec and plan files, plus check the current state of the repo.
Now let me examine the current docs and tests to verify insertion points and test satisfiability.
The README and tests are already partially implemented in the working tree. Let me verify the remaining docs files and check that the test phrases are satisfiable, plus examine the dirty uv.lock nature.
Let me verify the CLI reference (for the roadmap and "Shared Path Options" heading) and confirm the uv.lock diff is a mirror rewrite.
Let me read the CLI reference roadmap section to verify the table content matches the test, and check the CHANGELOG and existing review artifacts.
I have enough to complete the review. I verified all four docs tests' required terms against both the plan's example prose and the actual working-tree docs (which are already partially implemented), confirmed the dirty `uv.lock` is a pure mirror-URL rewrite that is unstaged, and traced the existing docs-test split points.

---

# Stage 79 Plan Review

**Verdict:** No Critical findings. One Important finding (release-gate blocked by the out-of-stage dirty lock). Plan scope, boundaries, and test satisfiability are sound.

## Critical
None.

## Important

### I1 — `UV_NO_CONFIG=1 uv lock --check` will fail on the dirty working-tree lock
`docs/.../stage-79-...-plan.md:394` (Task 3, Step 3) runs `UV_NO_CONFIG=1 uv lock --check`. The working-tree `uv.lock` is a pre-existing mirror rewrite: every `source.registry` and package URL is flipped from `pypi.org` / `files.pythonhosted.org` to `pypi.tuna.tsinghua.edu.cn` (confirmed via `git diff uv.lock`; HEAD lock is clean, working-tree lock is dirty, 1436/1436 URL-only lines, **not staged**).

`UV_NO_CONFIG=1` forces the default PyPI index, so uv recomputes the lock with `pypi.org` URLs and compares against the on-disk tsinghua lock. By design (per `AGENTS.md`: "Use `UV_NO_CONFIG=1 uv lock --check` ... so user-level uv mirror config cannot affect the public lockfile") this check is exactly what catches mirror-bound URLs, so it will report the lockfile outdated and exit non-zero — blocking release verification through no fault of Stage 79.

The plan acknowledges the dirty lock is out-of-stage (`plan.md:15-18`, `design.md:39-40`) but never reconciles it before this gate. Note the *other* lock guards are fine: the HEAD-lock mirror scan (`plan.md:395-398`) operates on `git show HEAD:uv.lock` (clean) and the staging guard (`plan.md:399`, `428`) only proves `uv.lock` isn't staged.

**Recommended fix:** insert a pre-verification step to restore the public lock in-tree without losing the local mirror convenience, e.g. stage/commit first, then `git stash push -- uv.lock` (or `git checkout HEAD -- uv.lock`) before Step 3, and `git stash pop` after — or simply run Step 3 *after* the commit when the index/tree no longer depends on the working-tree lock. At minimum, state explicitly that `uv lock --check` is expected to be run against a tree where the public lock has been restored.

## Minor

### M1 — Example prose blocks drift from the already-implemented docs (non-blocking)
The working tree already contains an implementation that differs slightly from the plan's literal example blocks, while still satisfying the (authoritative) docs tests:
- CLI roadmap: `plan.md:284-301` shows a `Cleanup` cell of "`init` for regeneration, plus the `Reset The Repo-Local Sample` commands ..." and a trailing entity-pack paragraph; the implemented `docs/cli-reference.md:14-21` instead adds an "Optional entity matching / `entity-pack-lint`" row and a simpler `Cleanup | Reset The Repo-Local Sample` cell. Both satisfy `tests/test_cli_docs.py:482-515`.
- First-run chooser: `plan.md:263-278` example paragraphs vs. `docs/first-run.md:18-37` actual prose — both satisfy `tests/test_cli_docs.py:772-802`.

Not blocking (tests are the contract and both pass), but a fresh implementer following the plan's literal blocks would diverge from what's already in-tree. Consider a one-line note that the test term lists are authoritative and the Markdown blocks are illustrative.

## Answers to the review questions

1. **Tests satisfiable by planned prose?** Yes. All four new tests' required substrings (`test_cli_docs.py:693-720`, `772-802`, `482-515`, `969-993`) are present in both the plan's example blocks and the current working-tree docs. The TDD ordering (Task 1 fail → Task 2 pass) is coherent.
2. **Orientation improved without duplication/scope change?** Yes. Start Here, chooser table, phase roadmap, and entity-pack note are compact pointers to existing detail docs; no new commands, flags, or product behavior.
3. **Insertion points safe?** Yes. README `## Start Here` before `## What It Does` doesn't touch the `## Quickstart` / `### Manual Repo-Local Sample Flow` splits used by `test_readme_documents_manual_sample_flow...` and `_readme_quickstart_commands()`. First-run chooser sits inside the existing `## Choose Your First Run` … `## Prepare A Source Checkout` window without disturbing `_first_run_setup_commands()` / `_first_run_reset_commands()`. CLI roadmap before `## Shared Path Options` and entity-pack intro before `## Lint The Pack` are similarly inert to existing tests.
4. **Entity-pack wording optional + local-only?** Yes. `docs/entity-packs.md:3-27` keeps "optional local matching layer", "copied after `init` and before your first `match` and `report`", and the explicit "only changes local entity matching ... does not add sources / ingestion / live collection ... does not prove demand / rank / verify platform coverage" boundary.
5. **Verification / staging / publish safe with dirty lock?** Staging and publish are safe (explicit `git add` list at `plan.md:408-419` excludes `uv.lock`; HEAD-lock mirror scan and staged-secret scans are correct; tree-equality check at `plan.md:452` would catch any leak). The only unsafe step is I1 above.

## Correction Note

The later Stage 79 code review found that the first-run chooser table originally
embedded literal `` `## ...` `` heading strings. That did disturb
`_first_run_reset_commands()` because the existing `_markdown_section` helper
splits on the first raw heading string. The implementation and plan were
corrected to use normal heading links in the table instead of literal heading
strings, and the full `tests/test_cli_docs.py` coverage should be rerun before
commit.
