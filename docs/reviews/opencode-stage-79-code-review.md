Now let me run the new tests to confirm they pass:
I found a regression. Let me confirm the cause:
Let me check whether the other chooser-table cell labels break sibling `_markdown_section` tests:
Let me run the full test suite to surface all Stage 79 regressions:
Let me confirm this test was passing before Stage 79 touched `first-run.md`:
Let me verify the commands referenced in the new CLI roadmap table all exist:
Let me check the review artifacts and confirm the `uv.lock` is correctly left unstaged:
Let me check the CHANGELOG entry placement:
Let me run `git diff --check` for whitespace issues on the in-scope files:
## Stage 79 Code Review

I inspected the full worktree diff, ran the new tests, the full suite, ruff, and `git diff --check`. There is **one Critical finding**.

### Critical

**C1 — The chooser table breaks a pre-existing docs drift test (regression)**

`docs/first-run.md:16` row:

```
| Reset repo-local sample | Cleanup after local experiments. | Removes generated repo-local sample files and keeps placeholder READMEs. | `## Reset The Repo-Local Sample` |
```

The cell text `` `## Reset The Repo-Local Sample` `` contains the literal string `## Reset The Repo-Local Sample`. The helper `_markdown_section` at `tests/test_cli_docs.py:388-391` resolves sections with a plain `text.split(heading, 1)[1]`, so it now matches the chooser cell (offset ~1106) **before** the real heading (offset ~9513). The poisoned section then contains no `bash` block, so `_first_run_reset_commands()` (`tests/test_cli_docs.py:439-441`) returns `[]`.

Failure (full suite: `1 failed, 1135 passed`):

```
tests/test_cli_docs.py::test_first_run_guide_reset_commands_are_narrow_file_deletions
E   AssertionError: assert [] == ['test -f pyproject.toml && test -d examples && { ...']
```

Verified by `git stash push -- docs/first-run.md` → the test passes at HEAD; repopping reproduces the failure. This violates the acceptance criterion *"Docs drift tests pin these sections and phrases"* — a pre-existing pinned docs drift test now fails.

The other three Start-Here cells (`docs/first-run.md:13-16`) embed `## Manual Repo-Local Sample Flow`, `## Automated First-Run Smoke`, `## Installed-Wheel Smoke`. No `_markdown_section`-based test currently targets those headings, so they don't fail today, but they are the same latent hazard.

**Fix:** drop the literal `## ` prefix from the Start-Here column cells — e.g. `[Reset The Repo-Local Sample](#reset-the-repo-local-sample)` or `Reset The Repo-Local Sample section`. The new test `test_first_run_guide_has_beginner_path_chooser` only pins `"Reset repo-local sample"` (Path column) and `"generated repo-local sample files"`, not the `## ` token, so this is safe.

### Important

**I1 — The Stage 79 plan review ships a falsified safety claim**

`docs/reviews/opencode-stage-79-plan-review.md:41` asserts:

> "First-run chooser sits inside the existing `## Choose Your First Run` … `## Prepare A Source Checkout` window without disturbing `_first_run_setup_commands()` / `_first_run_reset_commands()`."

This is exactly the property C1 disproves. The "No Critical findings" verdict in that review (`opencode-stage-79-plan-review.md:12`) rested on this incorrect assurance, which is why implementation proceeded past the gate. The review artifact is in the Stage 79 stage list and will commit a false safety claim. Correct or annotate it before commit.

### Minor

**M1 — Controller prior verification did not include the plan's full `pytest`**

The "Prior Verification" block ran only the 4 new tests + `ruff` on `tests/test_cli_docs.py`. The plan's Task 3 Step 3 (`...-plan.md:401`) mandates a full `uv --no-config run --frozen pytest`, which would have caught C1. No code defect — flagging the verification gap so the gate runs the full suite before release.

**M2 — Plan/example blocks diverge from the implemented docs (already noted in the plan review as M1)**

Still true; non-blocking since the tests are the contract and pass for the new sections.

### Everything else checks out

- `## Start Here` precedes `## What It Does` (`README.md:15,33`); points to `docs/first-run.md`, names Manual repo-local sample as recommended, frames smokes as verification paths, links `docs/entity-packs.md`, keeps local-first boundary language. ✓
- Four-row chooser table exists under `## Choose Your First Run` (`docs/first-run.md:11-16`). ✓
- `## Beginner Roadmap` precedes `## Shared Path Options` (`docs/cli-reference.md:6,23`); every roadmap command (`init`, `migrate-db`, `doctor`, `community-signal-lint`, `import-signals`, `import-signals-dir`, `match`, `report`, `candidates`, `trends`, `imported-signals`, `dashboard`, `entity-pack-lint`) resolves to a real `@app.command`. ✓
- Entity-pack docs describe the optional local matching layer copied after `init` and before first `match`/`report`, with explicit boundary language (`docs/entity-packs.md:3-27`). ✓
- CHANGELOG entry placed under `### Added` with boundary language. ✓
- `ruff check` / `ruff format --check` clean on `tests/test_cli_docs.py`; `git diff --check` clean on all in-scope files; `uv.lock` correctly unstaged (mirror-only rewrite, 1436/1436 URL lines). ✓
- No Stage 79 change adds platform/source-acquisition behavior or claims demand proof, ranking, or platform coverage verification. ✓

**Must fix before commit:** C1 (and re-run the full `pytest` after the fix). **Should fix:** I1.
