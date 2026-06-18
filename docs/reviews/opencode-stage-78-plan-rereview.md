I'll review the three files to verify C1 is resolved and check for remaining issues.
Now let me verify the actual test helpers and the docs structure to confirm C1 is truly resolved.
I've confirmed the helper behavior. Let me empirically verify whether the raw-text phrase check actually passes against the planned prose, since this is the crux of C1.
## Rereview Verdict: C1 is **NOT** fully resolved — one residual Critical remains.

I empirically simulated the docs drift test against the exact prose block the plan instructs the implementer to write. The second assertion block now passes (the `.casefold()` and standalone-`It does not …` sentence fixes are correct), but **the first block still fails on its last term**.

### C1 (residual). Raw-text phrase check still cannot pass — line wrap inserts a newline

`docs/superpowers/plans/2026-06-18-stage-78-adapter-contract-parity-plan.md:336` (test term) vs `:382-383` (prose).

The test asserts `"Dry-run import guidance remains separate from real import guidance." in text` against raw `_read()` output (`tests/test_cli_docs.py:307-308`, which is `read_text` — newlines preserved). But the planned prose wraps that exact sentence across two source lines:

- line 382 ends `…Dry-run import guidance remains`
- line 383 starts `separate from real import guidance.`

So the raw file contains `…remains\nseparate from real import guidance.` — the substring with a single space never occurs. Verified raw slice: `'Dry-run import guidance remains\nseparate from real import guidance.\n'`. The assertion fails both before and after the docs edit, so Task 2 Step 5's "Expected: all pass" is still unreachable. This is the same C1 failure mode the first review named.

**Recommended fix (smallest, most consistent):** move that one term out of the raw `text` block and into the `normalized` (`.casefold()`) block. `_normalized_doc_text` (`tests/test_cli_docs.py:311-312`) does `" ".join(text.split())`, which collapses the newline to a space, so the sentence then matches — exactly like the other mixed-case multi-word sentences already sitting in the normalized block. The raw block should keep only terms guaranteed to lie within a single source line (headings, inline-code tokens). Alternatively, force the sentence onto one source line in the prose — but that is more fragile.

### Confirmed fixed
- M1: `COMMUNITY_SIGNAL_IMPORT_DOC` is now added unconditionally (`plan:315-319`). Resolved.
- C1 sub-parts (case mismatch, distributed negation): resolved by `.casefold()` and the standalone `It does not add connectors…` / `It does not prove demand.` / `It does not rank sources.` / `It does not verify platform coverage.` sentences — all PASS in the normalized block.

### No other Critical/Important findings
- Task 1 (parity tests): unchanged and sound — builder signatures, command-index maps, lint result shape, and banned-token exactness all hold.
- Task 3 / dirty `uv.lock` release safety: intact. `UV_NO_CONFIG=1 uv lock --check` exits 0 in the dirty worktree, so the real guard is the `git show HEAD:uv.lock | rg 'tuna|aliyun|…'` scan plus the `! git diff --cached … uv.lock` staging guards — both present and correct. Commit/publish uses `HEAD^{tree}`, excluding the working-tree lockfile.

Fix C1 (residual), then the plan is implementable end-to-end with the dirty out-of-stage `uv.lock` left unstaged.
