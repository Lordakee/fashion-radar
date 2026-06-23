# Stage 162 Plan Review

## Summary

Stage 162 is a narrow, well-scoped grammar fix to the `source-pack-lint` human
table summary. The design and plan are aligned with `AGENTS.md` scope
boundaries, the `REVIEW_PROTOCOL.md` workflow, and the existing source-pack
renderer. No critical or important findings block implementation.

## Review Questions

### 1. Is Stage 162 correctly scoped to source-pack human output only?

Yes. The spec's scope section is explicit: in scope is a source-pack-local
formatter and the single renderer `render_source_pack_lint_table(...)`. Out of
scope enumerates entity-pack lint, community-signal lint, directory lint, JSON
output, lint semantics, strict-mode behavior, CLI flow, docs churn, and every
collection/platform/compliance boundary listed in `AGENTS.md`. The plan's Files
section touches only `src/fashion_radar/source_packs.py`,
`tests/test_source_packs.py`, and Stage 162 review artifacts. JSON output
(`SourcePackLintResult.model_dump_json`) is untouched, preserving the stable
automation interface documented in `docs/source-pack-quality.md`.

### 2. Do the planned RED tests prove the current grammar gap without broadening into entity-pack or community-signal lint output?

Yes. All three RED test moves are confined to `tests/test_source_packs.py` and
construct only `SourcePackFinding`, `SourcePackFindingSeverity`, and
`SourcePackLintResult` from `fashion_radar.source_packs`:

- The Stage 161 single-warning expectation at
  `tests/test_source_packs.py:324` (`"0 errors, 1 warnings, 0 info"`) is
  flipped to `"0 errors, 1 warning, 0 info"`, which fails today against the
  fixed-plural renderer at `src/fashion_radar/source_packs.py:109-112`.
- The new singular test asserts `"1 error, 1 warning, 1 info"`, which fails
  today.
- The new plural regression test asserts `"2 errors, 2 warnings, 2 info"`,
  which passes today and guards the non-one wording after implementation.

No entity-pack, community-signal, or directory lint test files are referenced.
The RED state is provable from the current renderer code.

### 3. Is the local `_format_finding_count(...)` helper an appropriate narrow implementation?

Yes. The helper is private (`_` prefix), local to `source_packs.py`, pure
(no I/O, no state), explicitly typed (`count: int, singular: str, plural: str
-> str`), and takes caller-supplied singular/plural strings so the renderer
keeps full control of wording. Using it three times (error/warning/info)
reasonably removes duplication versus inlining. Keeping `info` as both the
singular and plural argument matches current product language in
`docs/source-pack-quality.md` and avoids introducing a new `infos` word.

The helper is intentionally distinct from the existing `_format_counts(...)`
(which formats a `Mapping[str, int]` as `key=value` pairs or `none`); the names
and signatures are not confusable. The spec's Risks section correctly flags
that adjacent lint renderers share the same fixed-plural pattern and defers a
shared cross-lint helper to a separate future stage, which is the right scope
discipline.

### 4. Are verification, code-review, release-review, release-hygiene, commit, and push steps complete enough?

Yes. The plan covers the full `REVIEW_PROTOCOL.md` lifecycle:

- Focused verification runs the RED trio, the broader source-pack suite,
  `tests/test_source_pack_quality_docs.py`, CLI source-pack lint tests, and
  ruff check/format on every touched file.
- The release gate mirrors `docs/REVIEW_PROTOCOL.md` and the design's
  Verification block: full pytest with proxy env unset, first-run smoke,
  release hygiene, ruff, public lockfile check via
  `UV_NO_CONFIG=1 uv lock --check`, `git diff --check`, `ghp_` secret scan,
  and GitHub `extraheader` audit.
- Code-review and release-review prompts are created and run through local
  opencode with `zhipuai-coding-plan/glm-5.2 --variant max`, with rereview
  required on critical/important findings.
- Release hygiene is re-run after the release review, matching the protocol's
  "capture then verify" intent.
- Commit lists only Stage 162 files plus the four review artifacts, and push
  uses the `x-access-token` extraheader pattern.

The verification surface is sufficient for a change of this size.

### 5. Are there any critical or important findings before implementation?

No critical or important findings. The plan is internally consistent: helper
name and renderer references match across spec, plan, and current source; the
`info` singular==plural decision is explicit; zero counts remain plural
because `0 != 1`; and the Stage 161 regression that surfaced this gap is
covered by the updated expectation.

## Findings

### Critical

None.

### Important

None.

### Minor

- M1 (docs taste): The design's "Current Gap" code block reads as if the
  renderer hardcodes `1 warnings`; in practice that string only appears in the
  Stage 161 test expectation at `tests/test_source_packs.py:324`. The renderer
  itself emits whatever count flows through `result.warning_count`. Consider
  one sentence clarifying that the gap is observed via the single-warning test
  expectation, not a literal in-source string. Non-blocking.
- M2 (commit message): `fix: polish source pack finding count labels` is
  accurate but vague. Something like
  `fix: singularize source-pack lint finding counts` would read better in a
  changelog and make the human-output-only intent obvious. Style preference
  only.
- M3 (future-shared-helper note): The spec already acknowledges adjacent lint
  renderers may want the same grammar later. When that stage arrives, the
  local helper should move to a shared internal module (not a public API) and
  the move should be its own reviewed stage. Noting here so the deferral is
  tracked.

## Verdict

No blocking findings. The plan is approved for implementation as written,
optionally incorporating M1-M3 polish before the code-review step.
