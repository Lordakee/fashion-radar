I've now reviewed the plan against the existing checklist, the Stage 82 recovery doc it points to, and the test helpers. Writing the review.
Review written to `docs/reviews/opencode-stage-83-plan-review.md`.

**Verdict: acceptable with Important fixes.** No Critical; the node stays inside the docs/test-only boundary.

**Important (4):**
1. **Link form is wrong for the file location** — the plan prescribes `[docs/dependency-mirrors.md](docs/dependency-mirrors.md)`, which from `docs/github-upload-checklist.md` resolves to `docs/docs/dependency-mirrors.md` and breaks on GitHub. Use the sibling form `[dependency-mirrors.md](dependency-mirrors.md)` (or a `#recover-a-mirror-rewritten-lockfile` anchor). The `_assert_markdown_link_to_path` helper would happily pass on the broken form.
2. **Drift-test pinned strings under-specified** — same gap Stage 82's review flagged; enumerate link/anchor, the `Recover A Mirror-Rewritten Lockfile` literal, and the operational phrase.
3. **Don't scope the test to `## Before Upload`** — that section spans ~275 lines and absorbs all historical stage checks; use whole-file substring presence or a tight new `###` subheading.
4. **Pointer vs duplication unresolved** — checklist lines 37-47 already have the inline `UV_NO_CONFIG=1` block and the `rg` scan; the reminder must be a 1-2 sentence pointer, and the test must not pin command strings that already live elsewhere.

**Minor (4):** cross-pin the heading literal to the Stage 82 test; pin placement to the line-47 area (not vague "under Before Upload"); re-flag `REVIEW_PROTOCOL.md` drift; commit message style is fine.

Full details, evidence, and answers to the four review questions are in the review file.
-scoped drift assertion meaningful.

## Critical

None. The node stays inside the docs/test-only boundary and does not touch
runtime code, manifests, `uv.lock`, `AGENTS.md`, or `docs/REVIEW_PROTOCOL.md`.

## Important (fix before implementation)

1. **The prescribed link form is wrong for the file location.** Task 2 of
   the plan says to write `[docs/dependency-mirrors.md](docs/dependency-mirrors.md)`.
   From `docs/github-upload-checklist.md` that target resolves to
   `docs/docs/dependency-mirrors.md` and breaks on GitHub. Use the sibling
   form `[dependency-mirrors.md](dependency-mirrors.md)` (matches the
   checklist's existing `../examples/...` sibling-relative convention) or a
   section anchor
   `[Recover A Mirror-Rewritten Lockfile](dependency-mirrors.md#recover-a-mirror-rewritten-lockfile)`.
   The drift test must assert the *correct* relative path, not the README's
   repo-root form; otherwise the test is self-consistent with a broken link.

2. **Test scope and pinned strings are under-specified (same gap as Stage
   82 plan review Important #1).** Task 2 says "pin the new reminder and
   link" without enumerating: (a) the exact link/anchor, (b) the section
   name literal `Recover A Mirror-Rewritten Lockfile`, (c) a short
   operational phrase. Enumerate these so the test guards the boundary
   instead of just asserting `dependency-mirrors.md` appears somewhere.

3. **Do not use `_markdown_section_exact_heading(..., "Before Upload")` for
   the new test.** That section spans lines 9-285 and absorbs every
   historical stage docs check; a substring assertion scoped to it is
   indistinguishable from a whole-file substring assertion but with more
   failure modes. Either assert substring presence in the whole file (the
   reminder is brand-new content, so this is non-brittle) or introduce a
   tight new `###` subheading and scope to that.

4. **Pointer vs duplication is unresolved.** The checklist already has the
   inline `UV_NO_CONFIG=1 uv lock --check` block (lines 37-41) and the
   `rg` scan (lines 43-47); `dependency-mirrors.md` already has the full
   recovery path; Stage 82 re-listed the `rg` scan a third time at line 83.
   The reminder must be a 1-2 sentence *pointer* (restore a mirror-rewritten
   `uv.lock` before upload, see `<link>`), and the test must NOT pin
   command strings that already live elsewhere, otherwise the test will
   fight future cleanup of the duplication.

## Minor

1. **Cross-pin to the Stage 82 test.**
   `test_dependency_mirror_docs_explain_lockfile_recovery` (line 700)
   already pins `Recover A Mirror-Rewritten Lockfile` and the README link.
   The new checklist test should pin the same section-name literal so the
   two tests fail together if the heading is renamed.

2. **Placement ambiguity (Stage 82 Important #2 repeats).** "Under the
   `Before Upload` section" is too vague. Pin placement to "immediately
   after the existing `rg -n '...' uv.lock` block that ends the mirror
   checks (around line 47), before the `Historical boundary checks`
   paragraph at line 49" so future edits keep the mirror narrative
   contiguous.

3. **`REVIEW_PROTOCOL.md` drift still flagged.** Stage 82 noted the
   `opencode-stage-N-*` naming leaves `docs/REVIEW_PROTOCOL.md` drift-stale
   relative to actual practice; Stage 83 continues the same convention.
   Out of scope per the plan, but worth re-flagging since the gap is
   widening.

4. **Commit message style.** `Document upload checklist mirror recovery`
   matches Stage 82's `Document mirror lockfile recovery` imperative form.
   No change needed.

## Answers To Review Questions

- **Checklist placement near existing upload/lockfile checks clear?** Not
  yet - "under `Before Upload`" is too coarse; pin it to the line-47 area
  (see Important #4 and Minor #2).
- **Reminder operational and not too verbose?** Direction is right, but
  the design's "tell contributors to restore... then use the public lock
  checks" wording risks re-stating commands; keep it to a 1-2 sentence
  pointer with the link (see Important #4).
- **Test scope adequate and non-brittle?** Adequate if it (a) pins the
  correct sibling-relative link, (b) pins the section-name literal, and
  (c) avoids the over-broad `Before Upload` section scope (see Important
  #1-#3). As written in the plan it is under-specified and would pass on
  a broken link.
- **Markdown split or staging risks?** Split risk is low if the test uses
  whole-file substring presence; staging risk is low because Task 5 stages
  by explicit path and re-confirms `uv.lock` is not staged. The only real
  split hazard is using `_markdown_section_exact_heading("Before Upload")`
  (see Important #3).
