# Stage 188 Proxy Test Isolation And Roadmap Correction Design

## Objective

Fix the proxy-sensitive collector/workflow test gap and correct project-facing
roadmap documents so the next stages prioritize product-value work instead of
continuing low-value external-tool hardening.

## Background

The full-project review found two issues worth acting on immediately:

1. Some collector/workflow tests can fail in environments with ambient proxy
   variables because runtime HTTP client construction picks up `ALL_PROXY` /
   `HTTPS_PROXY` and can require optional `socksio` support even though the
   tests are intended to exercise injected collectors only.
2. The project brief and architecture still describe the overall product well,
   but recent work has over-invested in the external/community handoff surface
   relative to the core fashion-intelligence workflow. The next stages should
   explicitly freeze that surface and redirect effort to source coverage,
   source health, matching quality, and optional summarization.

This stage corrects both issues without adding new runtime product behavior.

## Scope

In scope:

- Update `tests/test_collectors_runner.py` so the four proxy-sensitive
  collector/workflow tests no longer depend on host proxy environment when
  article extraction is not under test.
- Update `tests/test_workflows.py` so the injected collector workflow test no
  longer depends on host proxy environment.
- Keep the fix test-side only; do not change runtime proxy behavior.
- Update roadmap-facing docs to reflect the corrected direction:
  - freeze additional external/community handoff surface expansion for now;
  - prioritize source coverage and source-health diagnostics;
  - prioritize matching quality for real fashion entities;
  - keep optional summary work ahead of further handoff hardening.
- Add Stage 188 plan and review artifacts.

Out of scope:

- New collectors, new handoff commands, or new external/social connectors.
- Matching algorithm expansion beyond wording/planning updates.
- Report summarization implementation.
- Dashboard feature changes.
- Dependency, lockfile, package archive, or database schema behavior changes.

## Technical Approach

### Test isolation fix

The failing surface is test isolation, not product logic. The minimal fix is to
keep the affected tests from constructing a default `FashionHttpClient` when
article extraction is not the behavior under test.

The root cause is current test setup:

- `SourceDefinition.article.enabled` defaults to `True`;
- `collect_sources(...)` eagerly builds the default article extractor when
  `source.article.enabled` is true and no explicit extractor is supplied;
- that path constructs `FashionHttpClient`, which constructs `httpx.Client`
  with environment-driven proxy behavior.

This stage should explicitly fix the four tests that currently fail under a
proxy-configured environment:

- `tests/test_collectors_runner.py::test_collect_sources_records_failure_and_continues_to_next_source`
- `tests/test_collectors_runner.py::test_collect_sources_passes_started_at_to_timing_aware_collectors`
- `tests/test_collectors_runner.py::test_collect_sources_stores_source_weight_and_collected_at`
- `tests/test_workflows.py::test_collect_configured_sources_uses_injected_collectors`

Use a test-only correction:

- in `tests/test_collectors_runner.py`, change the local `_rss_source(...)`
  helper so test RSS fixtures default to `article={"enabled": False}` while
  still allowing per-test overrides through payload merging;
- in `tests/test_workflows.py`, make the injected collector test explicitly set
  proxy env vars with `monkeypatch` and use
  `article={"enabled": False}` on its source fixture.

The RED proof should use the existing failing tests under a synthetic proxy
environment, plus one explicit workflow-boundary test that sets proxy vars so
the seam remains guarded in future runs.

Do not change `src/fashion_radar/utils/http.py`,
`src/fashion_radar/collectors/runner.py`, or runtime proxy behavior in this
stage. Product users may legitimately rely on environment proxies, and this
stage is only about test isolation.

### Roadmap correction

Update project-facing planning text in a small set of docs:

- `docs/PROJECT_BRIEF.md`: add a short "Current Direction Correction" section
  stating that the next implementation stages freeze additional
  external/community handoff expansion and shift to source breadth, source
  health, matching quality, and optional summarization.
- `README.md`: add a concise roadmap correction note near the roadmap/start
  sections so contributors see the current priority order quickly.
- `docs/architecture.md`: add a note in the component/boundary area that the
  existing handoff surface is considered sufficient for the current MVP and is
  not the next expansion target.
- `CHANGELOG.md`: record Stage 188 as a correction stage for test isolation and
  roadmap priority.
- `docs/REVIEW_PROTOCOL.md`: add a short reminder that review-gated stages
  should prefer unresolved product-critical capabilities over additional
  wording/parity hardening once a surface is already contract-stable.

## Acceptance Criteria

- Focused collector/workflow tests pass even when proxy-related environment
  variables are present.
- The fix is minimal and does not add new runtime product features.
- Project-facing docs clearly state that the next stages prioritize source
  coverage, source-health diagnostics, matching quality, and optional
  summarization.
- Project-facing docs clearly state that additional external/community handoff
  surface expansion is frozen for now unless a real bug is found.
- The affected test files and the full test suite both pass under a synthetic
  proxy environment before commit.
- Full release gate remains clean before commit.
