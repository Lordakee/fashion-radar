# Stage 161 Plan Review

## Verdict

No critical, important, or blocking findings. Stage 161 is a narrow, valid next
step after Stage 160, correctly scoped to one summary line in the default human
`source-pack-lint` table, reusing already-computed data and an existing
formatter. The plan is safe to implement as written.

## Independent Verification

I read the design, plan, `src/fashion_radar/source_packs.py`,
`tests/test_source_packs.py`, `tests/test_cli.py`, the docs-boundary test, and
the public pack. I confirmed the current renderer
(`source_packs.py:99-124`) emits `Source pack`, `Sources`, `Types`, `Findings`
only, so the planned RED tests are genuinely RED. I confirmed `tag_counts` is
already computed and sorted in `lint_source_pack` (`source_packs.py:87,94`) and
that `_format_counts` (`source_packs.py:335-338`) returns `none` for empty and
sorted `key=value` otherwise. I hand-counted the public pack tags and confirmed
the plan's documented `Tags:` line
(`accessories=1, beauty=1, ... trade_media=1`, 22 tags) matches the actual
configured sources exactly, in correct alphabetical order, so the docs sample
will not drift from real output.

## Review Answers

1. **Narrow, valid next step after Stage 160?** Yes. Stage 160 was section-aware
   wheel entry-point validation; Stage 161 is an unrelated but equally narrow
   UX improvement to existing local/read-only lint output. It reuses existing
   computed data, adds no schema, no new finding codes, no collection, no
   network, and no scope-boundary change.

2. **Do the planned RED tests prove the human table and CLI lack a `Tags:` line?**
   Yes. The current `render_source_pack_lint_table` has no `Tags:` entry, so
   `test_render_source_pack_lint_table_includes_tag_counts` asserting
   `lines[:5]` with `Tags:` at index 3 will fail RED. The current CLI table
   output also has no `Tags:` line, so adding `assert "Tags:" in result.output`
   to `test_source_pack_lint_prints_table_for_public_pack` (`test_cli.py:9130`)
   will fail RED. The `render_source_pack_lint_table` import resolves cleanly
   because it is already a public top-level function.

3. **Correct to reuse `tag_counts` and `_format_counts(...)`?** Yes. Both are
   stable, already-sorted, and already-used for `Types:`. The placement
   (`Types:` -> `Tags:` -> `Findings:`) matches the design spec, and the empty
   case renders `Tags: none`, consistent with the existing empty-count behavior
   used for `Types:`.

4. **Does the docs update preserve local/read-only and non-data boundaries?**
   Yes. `tests/test_source_pack_quality_docs.py` checks specific boundary
   phrases; the plan only adds a `Tags:` table line and one summary bullet and
   removes no boundary text. The phrase-based assertions continue to pass.

5. **Are verification, code-review, release-review, release-hygiene, commit, and
   push steps complete enough?** Yes. The plan covers focused RED, focused
   GREEN, docs-boundary, lint, and format checks; the full release gate (full
   pytest, first-run smoke, release hygiene, ruff check/format,
   `UV_NO_CONFIG=1 uv lock --check`, `git diff --check`, `ghp_` scan, and
   extraheader scan); local opencode code and release reviews with the clean
   mktemp/jq/sed capture pipeline; a release-hygiene re-run after review
   artifacts are added; and commit + one-shot-header push. The push uses `-c`
   per-command config, so the post-push `git config --get-all ...extraheader`
   remains empty.

6. **Any critical or important findings before implementation?** No.

## Findings

### Critical

None.

### Important

None.

### Minor

- m1: The CLI smoke strengthening (`assert "Tags:" in result.output`) is
  intentionally weak. The design's Risks section explains why (avoid coupling
  the smoke to the full public-pack tag list), and the focused renderer test
  carries the exact ordering/content assertion. This is acceptable, not a
  defect.
- m2: The focused unit test asserts `lines[:5]` with `f"Source pack: {path}"`.
  This is safe because `lint_source_pack` stores `str(path)` and `f"{path}"`
  on a `Path` yields the same string, but the test is mildly stricter than
  needed (it would also catch unrelated header regressions, which is a net
  positive).
- m3: The plan documents a fixed public-pack `Tags:` line in
  `docs/source-pack-quality.md`. I verified it matches the current public pack
  today. If the public pack is edited later, the docs sample will need to be
  re-synced; this is an ordinary maintenance caveat, not a Stage 161 blocker.

## Summary

No blocking findings. The plan is correct, complete, and ready for RED-first
implementation.
