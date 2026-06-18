# Stage 82 Plan Review (opencode)

## Verdict

Plan is acceptable with Important fixes recommended before implementation.
Restoring `uv.lock` from `HEAD` is verified safe (see evidence below).

## Evidence Gathered

- Working tree `uv.lock` vs `HEAD`: 1436 insertions / 1436 deletions, all matching
  lines are pure URL rewrites
  (`pypi.org/simple` -> `pypi.tuna.tsinghua.edu.cn/simple`,
  `files.pythonhosted.org/packages/...` ->
  `pypi.tuna.tsinghua.edu.cn/packages/...`).
- `diff <(git show HEAD:uv.lock | rg -v 'tuna|files.pythonhosted|pypi.org') \
  <(cat uv.lock | rg -v 'tuna|files.pythonhosted|pypi.org')` is empty: no
  version, hash, size, marker, or structural changes. Safe to discard.
- `HEAD:uv.lock` has zero matches for
  `tuna|aliyun|ustc|huaweicloud|mirror|index-url|extra-index-url|find-links`,
  so the public boundary already holds today.
- `docs/dependency-mirrors.md` already contains the `rg -n ... uv.lock` scan at
  line 71 (under `## Project Practice`) and `docs/github-upload-checklist.md`
  contains the same scan at line 46.
- `tests/test_cli_docs.pReview written to `docs/reviews/opencode-stage-82-plan-review.md`.

**Verdict: acceptable with Important fixes.** Restoring `uv.lock` from `HEAD` is verified safe — I confirmed via `diff <(git show HEAD:uv.lock | rg -v 'tuna|files.pythonhosted|pypi.org') <(rg -v 'tuna|files.pythonhosted|pypi.org' uv.lock)` that the working-tree lockfile is a pure URL rewrite (identical versions/hashes/sizes; only `pypi.org`→`tuna` URLs differ).

**Critical:** none.

**Important (fix before implementation):**
1. Task 2's drift-test spec is too vague — enumerate the exact pinned strings (constant name, heading literal, each command, boundary phrase) so the test actually guards the boundary.
2. Section placement of `## Recover A Mirror-Rewritten Lockfile` is unspecified, creating a `_markdown_section_exact_heading` split hazard; state where it sits relative to `## Python` / `## Project Practice`.
3. Relationship to the existing `rg` scan at `docs/dependency-mirrors.md:71` is unclear — declare whether the recovery section is additive vs a near-duplicate.

**Minor:** add a one-line safety justification to the design (pure URL rewrite, verified); note that `opencode-stage-82-*` naming follows stages 78-81 but leaves `REVIEW_PROTOCOL.md` drift-stale (out of scope); document the `! rg ...` exit-code semantics and the deliberate `git restore`-before-`uv lock --check` ordering.

Answers to your four questions are in the file's final section.
relative to
   the existing `## Python` and `## Project Practice` sections. If a test uses
   `_markdown_section_exact_heading`, the section must be a real `## ` heading
   with the exact literal and must not accidentally absorb the existing
   `## Project Practice` scan (or be absorbed by it). Recommend placing it
   after `## Project Practice` as a peer `## ` section.

3. **Relationship to the existing scan at line 71 is unclear.** The new
   section will re-state the `rg` scan and the `UV_NO_CONFIG=1 uv lock --check`
   command that already live under `## Project Practice` and in
   `docs/github-upload-checklist.md`. The plan should say whether the existing
   line 71 block stays, is moved, or is reworded, so the recovery section is
   clearly additive (focused recovery steps: detect -> restore -> verify ->
   gate) rather than a near-duplicate.

## Minor

1. **Safety justification is implicit.** The plan/design do not state that the
   working-tree lockfile is a pure URL rewrite with identical hashes/sizes, so
   a future contributor reading the plan cannot see why `git restore uv.lock`
   is safe without re-running the diff. A one-line note in the design
   ("verified: same versions, hashes, sizes; only registry/sdist/wheel URLs
   differ") would make the safety argument self-documenting.

2. **Review naming vs `docs/REVIEW_PROTOCOL.md`.** The plan uses
   `opencode-stage-82-*` review filenames and an `opencode run --variant max`
   header, while `REVIEW_PROTOCOL.md` prescribes `claude-code-stage-N-*` for
   new reviews. This matches the de-facto convention of stages 78-81 (all
   `opencode-stage-*`), so it is consistent with current practice; flagging
   only because `REVIEW_PROTOCOL.md` is out of scope for this node and is now
   drift-stale relative to actual practice.

3. **`! rg ...` verification semantics.** Task 4's
   `! rg -n '...' uv.lock` relies on bash negation of `rg`'s exit code. This
   is correct, but worth a one-line comment in the plan that the command is
   expected to exit 0 only when the scan finds nothing (current public
   `HEAD:uv.lock` satisfies this). Anyone copying it into a `set -e` script
   should keep the `!` prefix.

4. **`git restore` ordering.** Task 3 runs `git restore uv.lock` before
   `UV_NO_CONFIG=1 uv lock --check`, which is the right order (the check would
   otherwise report the mirror-rewritten file as out of date). Consider noting
   that `uv lock --check` is a secondary guard, not the primary restore
   mechanism, so nobody is tempted to run it first.

## Answers To Review Questions

- **Is restoring `uv.lock` from `HEAD` safe and aligned with the public
  lockfile boundary?** Yes. Verified pure URL rewrite; no version/hash/size
  changes. `HEAD` is already mirror-free. `git restore uv.lock` is the
  correct, minimal recovery.
- **Is the planned documentation precise enough to prevent accidental mirror
  URL commits?** Direction is right, but precision is insufficient (see
  Important #1-#3): the section placement, the exact boundary phrase, and the
  relationship to the existing scan must be pinned by the test.
- **Are the tests and verification commands sufficient?** Verification
  commands are sufficient and match established hygiene. The drift test is
  under-specified and should enumerate exact pinned strings.
- **Markdown split hazards / staging risks?** Split hazard exists for any
  section-scoped assertion (see Important #2). Staging risk is low: Task 5
  stages only Stage 82 files by explicit path and separately confirms
  `uv.lock` is not staged.
