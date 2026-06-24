# Stage 188 Plan Review

## Summary

The stage is well-scoped: a test-only isolation fix for the proxy-sensitive
collector/workflow tests (full-project review C1) plus minimal roadmap
corrections that re-align the project with the brief. The root-cause analysis is
accurate, the fix is correctly kept out of `src/`, and no out-of-scope product
behavior is introduced. One Important inconsistency in the RED->GREEN flow of the
new guard test must be fixed before implementation; the rest are minor clarity
refinements.

Verified facts underpinning the review:
- `SourceDefinition.article.enabled` defaults to `True`
  (`src/fashion_radar/models/source.py:35`).
- `collect_sources` eagerly builds the default article extractor when no
  `article_extractor` is supplied and `source.article.enabled` is true
  (`src/fashion_radar/collectors/runner.py:71-74`).
- That path constructs `FashionHttpClient(source.http)`
  (`src/fashion_radar/collectors/runner.py:131`), which builds
  `httpx.Client(...)` (`src/fashion_radar/utils/http.py:30`); under
  `ALL_PROXY=socks5h://...` this raises the proxy-related import error already
  captured in `docs/reviews/opencode-full-project-review.md:10-27`.
- The four RED tests named in the design match the four failures in the
  full-project review exactly.

## Critical

None.

## Important

### I1 — The new workflow guard test cannot reach GREEN as written

`docs/superpowers/plans/2026-06-24-stage-188-proxy-test-isolation-and-roadmap-correction-plan.md:42-65`
(Task 1, Step 1) adds
`test_collect_configured_sources_with_injected_collectors_ignores_proxy_env`
whose `SourceDefinition(...)` (plan lines 50-55) omits `article=`, so
`source.article.enabled` is `True` (`src/fashion_radar/models/source.py:35`).
Because the test passes no `article_extractor`, `collect_configured_sources`
-> `collect_sources` builds the default extractor
(`src/fashion_radar/collectors/runner.py:73-74`) -> `FashionHttpClient`
(`src/fashion_radar/collectors/runner.py:131`) -> `httpx.Client`
(`src/fashion_radar/utils/http.py:30`), which fails under the synthetic
`ALL_PROXY=socks5h://...` env (plan lines 46-48). This is the correct RED state.

Task 2 Step 1 (plan lines 97-118), however, modifies only the `_rss_source`
helper (plan lines 99-112) and the *original*
`test_collect_configured_sources_uses_injected_collectors` (plan lines 114-116);
it never adds `article={"enabled": False}` to the *new* test. Consequently the
new test stays RED after the fix, so Task 2 Step 2's "Expected: all five tests
pass" (plan line 138) cannot hold. An implementer following the plan literally
will hit a failing 5th test at the GREEN checkpoint.

Concrete fix — pick one:
(a) Preferred: write the new test in its final GREEN form in Task 1 by adding
    `article={"enabled": False}` to its `SourceDefinition` (plan lines 50-55).
    The four existing tests already supply the RED signal, so the new test is a
    permanent seam guard, not part of RED.
(b) Add an explicit Task 2 Step 1 bullet: "Update
    `test_collect_configured_sources_with_injected_collectors_ignores_proxy_env`
    to set `article={"enabled": False}` on its source fixture" before running
    the GREEN verification.

## Minor

### M1 — `architecture.md` insertion anchor is vague
Plan lines 196-205 say "near the external/community handoff component block,"
but `docs/architecture.md` has several handoff-related blocks (lines 73, 78, 85,
96, 108, 126, 130). Pin the instruction to one block (e.g., immediately after
the `external-tool-adapters` component at `docs/architecture.md:73`).

### M2 — CHANGELOG `### Fixed` placement unspecified
`CHANGELOG.md` already has `### Added` (line 9) and `### Changed` (line 226)
under `## [Unreleased]`; the plan (lines 207-218) says only "Add a `### Fixed`
subsection." Per Keep a Changelog, insert `### Fixed` between `### Added` and
`### Changed`. State the position explicitly.

### M3 — `PROJECT_BRIEF.md` insertion point ambiguous
"Add a short section after `## Recommended First Public Version`"
(`docs/PROJECT_BRIEF.md:144`) is immediately followed by
`## Required Compliance Defaults` (`docs/PROJECT_BRIEF.md:160`). Clarify that
the new `## Current Direction Correction` section goes between line 158 and
line 160.

### M4 — Full-suite release gate under a synthetic SOCKS proxy
Task 5 Step 1 (plan lines 296-301) runs the entire suite under
`ALL_PROXY=socks5h://127.0.0.1:9 ...`. The full-project review confirms only the
four proxy-sensitive tests are affected and a dead socks port fails fast rather
than hangs, so risk is low; add a one-line note that this is intentional so
future readers do not assume it is a mistake.

### M5 — Original workflow-test monkeypatch shown only in prose
Task 2 Step 1 (plan lines 114-116) describes the original test's `monkeypatch`
proxy pinning in prose, whereas the new test shows the exact
`monkeypatch.setenv(...)` block (plan lines 46-48). For parity and to prevent
drift, show the exact snippet for the original test as well.

## Question-by-question

1. Smallest sound test-side-only path? Yes. Disabling article extraction in the
   shared `_rss_source` helper and in the workflow fixture is the minimal change
   that stops the default `FashionHttpClient` from being built when article
   extraction is not under test; no `src/` file is touched (Files list, plan
   lines 15-21; explicit guard at plan lines 87-90, 118).
2. Meaningful RED/GREEN? Yes for the four existing tests, which reproduce the
   exact C1 failure under a synthetic proxy env. The fifth test is a seam guard
   — subject to the I1 correction before its GREEN claim is valid.
3. Roadmap/docs corrections scoped and aligned? Yes. The brief/README/
   architecture/CHANGELOG/REVIEW_PROTOCOL edits directly map to the
   full-project review's recommended corrections (freeze handoff surface,
   reprioritize source coverage, source-health, matching quality, optional
   summarization) and explicitly defer the larger cleanup (disclaimer
   de-duplication, adapter consolidation), which is appropriate for a single
   correction stage.
4. Next-stage priority redirected correctly? Yes —
   `docs/PROJECT_BRIEF.md` "Current Direction Correction" and the README
   "Current Roadmap Focus" both name source breadth, source-health diagnostics,
   matching quality, and optional summarization, and freeze further handoff
   expansion.
5. No new external/community handoff features or out-of-scope behavior? Correct.
   Out-of-scope (design lines 42-48) and the Files list confirm only tests and
   docs change; no new collectors, connectors, handoff commands, matching
   expansion, summarization implementation, schema, lockfile, or dependency
   behavior.

## Verdict

Conditionally approved for implementation. Apply the I1 correction (the new
regression test must actually reach GREEN, either by writing it in final form in
Task 1 or by adding the explicit Task 2 sub-step) before starting Task 2; the
Minor items are non-blocking clarity refinements that can be folded in during
implementation.
```
