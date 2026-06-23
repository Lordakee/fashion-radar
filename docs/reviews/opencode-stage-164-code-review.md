# Stage 164 Code Review

## Summary

Stage 164 introduces a shared `lint_formatting` helper module that exposes
`format_count_label` and `format_finding_counts`, then routes the source-pack,
entity-pack, and community-signal (single-file and directory aggregate + per-file)
lint renderers through the new helper. The local `_format_finding_count` is removed
from `source_packs.py`, and the entity/community renderers that previously emitted
fixed plural labels now singularize `1 error`/`1 warning`. The community-signal
quality doc and its docs grammar regression are updated in lockstep. All seven new
tests pass, the focused regression suites pass (128 + 33 + 1), ruff check and
ruff format --check are clean on all eight touched files, and a broader 213-test
sweep across the affected modules passes. The implementation is in scope,
behavior-preserving for Stage 162, and ready for release verification.

## Findings

### Critical

None.

### Important

None.

### Minor

1. Adjacent non-lint count grammar left intentionally inconsistent.
   `src/fashion_radar/community_handoff_check.py:190` and `:208` still emit
   `{count} errors` unconditionally (e.g., `1 errors`), and
   `src/fashion_radar/importers/manual_signals.py:330` does the same for the
   manual-signal dry-run per-file line. These are correctly out of scope for
   Stage 164 (they are not lint table surfaces and the prompt explicitly limits
   work to source/entity/community lint tables), so no change is required here.
   Flagging only so a future stage can decide whether to extend the helper to
   those summary surfaces for consistency. No action needed for this release.

2. `lint_formatting` has no direct unit test. The helper is exercised
   transitively through the three renderer test suites (singular + plural for
   each surface, plus the directory per-file line assertions at
   `tests/test_community_signal_lint.py:760` and `:820`), so coverage is
   adequate. A two-line direct test of `format_count_label` edge cases
   (zero, negative, plural) would be a low-cost hardening addition in a future
   stage but is not required now.

## Verification Assessment

The GREEN evidence in the prompt was reproduced cleanly against the current
working tree:

- Seven new focused tests: 7 passed (`test_entity_pack_lint.py` singular + plural,
  `test_community_signal_lint.py` singular + plural for file and directory,
  `test_cli_docs.py` docs grammar regression).
- `tests/test_source_packs.py tests/test_entity_pack_lint.py
  tests/test_community_signal_lint.py`: 128 passed. Source-pack Stage 162
  regression coverage is preserved by the existing `0 errors`/`1 warning`
  assertions at `tests/test_source_packs.py:298` and `:326`, which continue to
  pass under the shared helper.
- `tests/test_cli.py -k "source_pack_lint or entity_pack_lint or
  community_signal_lint"`: 33 passed, 265 deselected.
- `tests/test_cli_docs.py -k "community_signal_quality"`: 1 passed, 67 deselected.
- `ruff check` and `ruff format --check` on all eight files: clean.
- Additional sweep of `tests/test_entity_packs.py` and
  `tests/test_community_handoff_check.py`: combined 213 passed, confirming the
  shared helper import did not introduce circular-dependency or renderer-side
  regressions in adjacent surfaces.

Scope adherence is correct:

- Directory per-file line keeps `{file.row_count} rows` (and the docs example
  keeps `1 rows`), satisfying the explicit "no row-count grammar changes" scope
  boundary. Only finding-count grammar was changed.
- JSON output paths are untouched; lint model, severity, sorting, strict-mode,
  and CLI command flow are untouched.
- The previously-flagged directory singular test path/prefix mismatch from the
  plan review is fixed: the test at `tests/test_community_signal_lint.py:756`
  matches the rendered `- exports/signals.csv:` prefix exactly and asserts the
  per-file finding-count substring.
- `_format_finding_count` is fully removed from `source_packs.py` (no orphan
  references remain), and `lint_formatting` is a leaf module with no imports
  beyond `from __future__ import annotations`, so there is no circular-import
  or side-effect risk.

## Verdict

Approved for release verification. The objective is met, the shared helper is
appropriately scoped and safe for all three lint surfaces, singular/plural and
source-pack regression risks are covered, directory per-file output changes only
finding-count grammar, docs and docs tests are sufficient, and no out-of-scope
behavior changed. No critical or important findings; the two minor notes are
future-stage considerations and do not block this release.
