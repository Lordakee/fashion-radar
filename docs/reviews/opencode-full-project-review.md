# Full Project Review

## Scope

This review evaluated the repository's product direction, core implementation,
test posture, and review-gated development trajectory before Stage 188.

## Critical

### C1 - Proxy-Sensitive Collector Tests

The full test suite failed in environments with ambient proxy variables because
several collector and workflow tests accidentally constructed the default
article-extraction HTTP client while the tests were intended to exercise
injected collectors. Under a SOCKS proxy environment without optional SOCKS
support, that path raised an import error from the HTTP transport layer.

Affected tests at the time of review:

- `tests/test_collectors_runner.py::test_collect_sources_records_failure_and_continues_to_next_source`
- `tests/test_collectors_runner.py::test_collect_sources_passes_started_at_to_timing_aware_collectors`
- `tests/test_collectors_runner.py::test_collect_sources_stores_source_weight_and_collected_at`
- `tests/test_workflows.py::test_collect_configured_sources_uses_injected_collectors`

Assessment: this was a test-isolation defect, not a runtime product defect.
Stage 188 later fixed it by disabling article extraction in the relevant test
fixtures while leaving runtime proxy behavior unchanged.

## Important

### I1 - Effort Drift Into Non-Functional Handoff Surfaces

The project had accumulated a large amount of source and test code around
external tool adapters, community handoff workflows, imported review commands,
and exact wording/parity guards. That work was technically careful but had grown
larger than the core daily fashion-intelligence workflow.

The concern was allocation rather than local code quality: recent work was
hardening print-only and local handoff surfaces while the product brief still
needed source breadth, source-health visibility, matching quality, and optional
summary improvements.

Recommended correction: freeze additional `external-tool-*`,
`community-handoff-*`, and `imported-*` expansion unless a real correctness bug
is found, and redirect the next development stages to core product value.

### I2 - Repetitive Boundary Documentation

The documentation repeated long boundary disclaimers across README, architecture,
community signal, source boundary, and related docs. The repeated text made the
project safer about scope but harder to read and harder to onboard.

Recommended correction: keep one authoritative boundary explanation and avoid
adding more wording-only guardrails unless they protect a real release risk.

### I3 - Product Gaps Relative To The Brief

The original project brief prioritizes daily monitoring of fashion industry
news, celebrity styling, brand movement, emerging designers, hot products, trend
terms, and heat changes. At the time of the review, the deterministic core was
working, but the following gaps remained:

- The public source pack was still a starter set and did not prove feed
  liveness or current source productivity.
- Source-pack linting checked static YAML quality only; it did not tell a user
  whether feeds were reachable today or whether GDELT lanes returned records.
- Entity matching was deterministic and transparent, but real fashion names,
  diacritics, ambiguous aliases, product phrases, and celebrity/style contexts
  still needed quality iteration.
- Reports were deterministic and attributed, but optional summary support was
  still future work.

Recommended correction: after fixing the proxy-test issue and review-chain
hygiene, build source-liveness diagnostics, then use them to expand source
coverage with evidence.

## Strengths

- The core collect, match, score, report, and dashboard pipeline is coherent and
  free-first.
- Collector code has source health, rate limiting, robots-aware article
  extraction boundaries, and graceful failure handling.
- Matching and scoring are deterministic, inspectable, and covered by tests.
- SQLite schema management and read-only review surfaces are explicit.
- Release hygiene catches many local-state, secret, package, and review-capture
  risks before push.

## Recommended Next Steps

1. Fix the proxy-sensitive collector and workflow tests so the suite is stable
   under common developer proxy environments.
2. Correct the roadmap so near-term work prioritizes source coverage,
   source-health/feed-liveness diagnostics, matching quality, and optional
   report summaries.
3. Strengthen review-capture hygiene so committed review records contain clean,
   completed review output.
4. Build a read-only source-liveness diagnostic for configured RSS/RSSHub and
   GDELT sources before expanding the public source pack further.

## Current Follow-Up Status

- Stage 188 fixed the proxy-sensitive tests and redirected roadmap docs.
- Stage 189 is intended to fix review-capture hygiene gaps exposed by this
  review record and the Stage 188 review chain.
- The next product node should implement source-liveness diagnostics for
  configured public sources.
