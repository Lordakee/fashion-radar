# Stage 161 Code Review

Stage 161 adds a deterministic `Tags:` summary line to the default human table
output of `fashion-radar source-pack-lint`. Implementation matches the design
and plan, stays within scope, and reuses existing internals.

## Critical Findings

None.

## Important Findings

None.

## Minor Findings

1. **Empty-tags case is not directly asserted.** The design (`## Expected
   Behavior`) explicitly states a valid pack with no tags should render
   `Tags: none`, mirroring `_format_counts`. Current coverage is transitive
   (via the shared empty-`type_counts`/`_format_counts` path) and via the
   `--strict`/`missing_tags` CLI tests, but no renderer test asserts the empty
   `tag_counts` -> `Tags: none` line directly. A one-line assertion on a
   tag-less pack would close that gap and lock the documented behavior.

2. **Docs JSON sample `tag_counts` is illustrative, not exhaustive.**
   `docs/source-pack-quality.md:82-85` shows
   `"tag_counts": {"industry_news": 5, "gdelt": 10}` as a representative
   excerpt, while the table sample above now lists the full 22-tag set. This is
   pre-existing and acceptable as an illustrative JSON shape example, but the
   slight asymmetry could confuse a reader comparing the two blocks. Optional:
   add a short note that the JSON `tag_counts` sample is abbreviated.

3. **Redundant double-sort (pre-existing, shared pattern).**
   `lint_source_pack` returns `dict(sorted(tag_counts.items()))`
   (`source_packs.py:94`) and `_format_counts` re-sorts
   (`source_packs.py:339`). Harmless and identical to how `type_counts` is
   already handled. Not worth changing for this stage.

## Review Questions

1. **Does the renderer reuse existing `tag_counts` and `_format_counts(...)`?**
   Yes. `source_packs.py:108` renders
   `f"Tags: {_format_counts(result.tag_counts)}"`. `tag_counts` is already
   computed and sorted in `lint_source_pack` (`source_packs.py:87,94`) and is
   an existing field on `SourcePackLintResult` (`source_packs.py:41`). No new
   computation or helper was introduced.

2. **Does the CLI table output include `Tags:` without changing JSON shape?**
   Yes. The CLI delegates table rendering to `render_source_pack_lint_table`,
   so the new line appears in default output with no command-layer change. JSON
   shape is unchanged: `tag_counts` was already a stable key
   (`test_lint_result_json_shape_is_stable` still passes, asserting the exact
   key order including `tag_counts`). `--format json` output is unaffected.

3. **Are tests sufficient and scoped to source-pack lint output?**
   Yes. `test_render_source_pack_lint_table_includes_tag_counts` asserts the
   exact first five rendered lines, including `Tags: gdelt=2, runway=1,
   shoes=1` positioned between `Types:` and `Findings:` and the sorted
   deterministic counts. The CLI smoke
   (`test_source_pack_lint_prints_table_for_public_pack`) asserts `"Tags:" in
   result.output` without over-coupling to the full public-pack tag list, per
   the plan's risk note. Scope is correctly limited to source-pack lint output;
   no other tests assert against the source-pack renderer line count/order, so
   the inserted line causes no collateral breaks (confirmed by focused run:
   `3 passed`).

4. **Does the docs update preserve local/read-only and non-data boundaries?**
   Yes. All boundary phrases required by `tests/test_source_pack_quality_docs.py`
   (local/read-only, no fetch/collect/SQLite/artifact creation, non-compliance,
   non-data JSON, availability/demand limits) remain intact. The new `Tags:`
   line and bullet describe configured source tags only - not fetched,
   collected, ranked, or demand data. The documented table sample was verified
   against the live renderer and matches the real public-pack output exactly.

5. **Are there any critical or important findings before release verification?**
   No. No blocking findings. The change is a minimal, deterministic display
   addition that reuses existing data and formatting, leaves JSON shape and
   lint semantics untouched, and is covered by focused RED-to-GREEN tests plus
   docs boundary tests. Safe to proceed to the full release gate and release
   review.
