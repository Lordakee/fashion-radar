# Stage 162 Code Review

## Summary

Stage 162 ships a minimal, well-targeted grammar fix to the `source-pack-lint`
human table summary. The diff is confined to `src/fashion_radar/source_packs.py`
(+9/-2) and `tests/test_source_packs.py` (+83/-1). The implementation matches
the design and plan exactly: a private local helper `_format_finding_count(...)`
is added near `_format_counts(...)`, and only the `Findings:` line in
`render_source_pack_lint_table(...)` is changed to call it. Entity-pack,
community-signal, and directory lint renderers remain verbatim (confirmed by
`git diff --stat` showing no change to `entity_packs.py` or
`community_signals.py`). No critical or important findings block release
verification.

## Review Questions

### 1. Does source-pack table output now render `1 error`, `1 warning`, and `1 info` while preserving `0 errors`, `0 warnings`, and `0 info`?

Yes. `_format_finding_count` at `src/fashion_radar/source_packs.py:344-346`
selects the singular label iff `count == 1`, otherwise the plural:

```python
def _format_finding_count(count: int, singular: str, plural: str) -> str:
    label = singular if count == 1 else plural
    return f"{count} {label}"
```

Behavior by count:

- `0` uses the plural labels (`0 errors`, `0 warnings`, `0 info`), preserved by
  `test_render_source_pack_lint_table_includes_tag_counts` at line 298.
- `1` uses the singular labels (`1 error`, `1 warning`, `1 info`), covered by
  `test_render_source_pack_lint_table_singularizes_one_finding_count` at line
  331 and the updated `..._shows_none_for_empty_tag_counts` at line 326.
- `2` uses the plural labels (`2 errors`, `2 warnings`, `2 info`), covered by
  `test_render_source_pack_lint_table_keeps_plural_finding_counts` at line 363.

`info` is intentionally passed `('info', 'info')`, so it renders identically
for all counts, matching the existing product wording.

### 2. Are source-pack JSON output, lint semantics, strict-mode behavior, and CLI command flow unchanged?

Yes.

- JSON output: `SourcePackLintResult.model_dump_json` is untouched. The
  `test_lint_result_json_shape_is_stable` test at `tests/test_source_packs.py:236`
  still pins the exact payload key order and values, and it passes. The CLI
  JSON path at `src/fashion_radar/cli.py:625-626` is unchanged.
- Lint semantics: `lint_source_pack`, `_lint_sources`, severity assignment,
  `_sort_findings`, and the `error_count`/`warning_count`/`info_count`
  properties at `src/fashion_radar/source_packs.py:44-54` are unchanged. The
  renderer still consumes the same properties, only the label selection
  differs.
- Strict-mode behavior: `source_pack_lint_command` at
  `src/fashion_radar/cli.py:631-638` still gates the exit code on
  `has_errors or (strict and has_warnings)`, computed directly from
  `finding.severity`, independent of the rendered text.
  `test_source_pack_lint_strict_exits_nonzero_on_warnings` continues to pass.
- CLI command flow: the renderer call site at `src/fashion_radar/cli.py:628`
  is unchanged; `render_source_pack_lint_table(result)` still returns the
  lines the CLI echoes.

### 3. Are tests sufficient and scoped to source-pack lint output?

Yes. The new tests are confined to `tests/test_source_packs.py`, import only
from `fashion_radar.source_packs`, and construct `SourcePackLintResult`
directly so they exercise the renderer in isolation without touching file I/O
or lint semantics. Coverage spans zero, singular, and plural counts for all
three severities. The Stage 161 `Tags: none` regression expectation at line
326 was correctly updated from `1 warnings` to `1 warning`, closing the gap
that surfaced this stage. The plural regression test at line 363 guards
against a future over-eager singularization.

### 4. Are entity-pack and community-signal lint outputs intentionally untouched?

Yes. `git diff --stat` shows zero changes to `src/fashion_radar/entity_packs.py`
and `src/fashion_radar/community_signals.py`. Both still emit the fixed
plural wording:

- `entity_packs.py:124-125`: `f"Findings: {result.error_count} errors, ..."`
- `community_signals.py:286-287` and `:316-317`: same fixed plural wording.
- The per-file line at `community_signals.py:325-326` is also unchanged.

This matches the spec's explicit out-of-scope list and the plan's "leave
adjacent renderers alone" discipline. The inconsistency between source-pack
(singularized) and the other lint surfaces is now visible but was correctly
deferred to a separate stage per the design's Risks section.

### 5. Are there any critical or important findings before release verification?

No critical or important findings. Verification re-run locally matches the
prompt's reported results:

- `pytest tests/test_source_packs.py tests/test_source_pack_quality_docs.py -q`
  returned 17 passed.
- `pytest tests/test_cli.py -q -k "source_pack_lint"` returned 7 passed, 291
  deselected.
- `ruff check` and `ruff format --check` on the touched files returned clean.

## Findings

### Critical

None.

### Important

None.

### Minor

- M1 (test assertion style): The two new tests at lines 360 and 407 use
  `assert "Findings: ..." in lines`, while the adjacent renderer tests at
  lines 293 and 321 use the stronger exact-slice form `lines[:5] == [...]`.
  Both styles are valid, and the `in` form is sufficient because the
  `Findings:` line is always at index 4, but aligning on the slice form would
  make the test suite internally consistent and would also catch accidental
  reordering of the summary header. Non-blocking style preference.
- M2 (negative-count edge case): `_format_finding_count` would render
  `-1 errors` for a negative count because the branch only special-cases
  `count == 1`. This is unreachable today since `error_count`,
  `warning_count`, and `info_count` are derived from `_count_findings`, which
  sums non-negative generators. Worth a one-line guard or a `count < 0`
  assertion only if the helper is later promoted to a shared module. Not
  actionable for Stage 162.
- M3 (cross-lint grammar consistency): Now that source-pack singularizes,
  entity-pack and community-signal output reads as
  `Findings: 1 errors, 1 warnings, 1 info` when a single finding of each
  severity is present. The spec and plan review already track this as a
  deferred follow-up stage. Reiterating here so the inconsistency is visible
  at release time; no action required in this node.

## Verdict

No blocking findings. The change is correct, minimal, well-tested, and
faithful to the design and plan. Approved to proceed to the full release
gate, release review, and release hygiene.
