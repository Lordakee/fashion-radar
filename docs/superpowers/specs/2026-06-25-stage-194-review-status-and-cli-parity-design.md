# Stage 194 Review Status And CLI Parity Design

## Objective

Close the remaining non-blocking Stage 193 CLI coverage gap and refresh the
current project direction/status documents so they no longer present completed
Stage 190 source-liveness work or completed Stage 193 trend/heat explanation
work as future work.

## Background

Stage 193 added the read-only `trend-explanations` sidecar over existing
`TrendComparison` output. The Stage 193 code and release reviews approved the
stage with no Critical or Important findings. The only remaining code-side note
was cosmetic parity: `trends` has two dedicated `--baseline-as-of` error-path
CLI tests that `trend-explanations` does not yet mirror.

The production command already contains the corresponding handling:

- invalid `--baseline-as-of` prints
  `Could not explain trend deltas: invalid --baseline-as-of`;
- `--baseline-as-of >= --as-of` prints
  `Could not explain trend deltas: baseline-as-of must be before as-of`;
- both paths exit before the missing-database branch, so they must not create
  `data_dir` or a SQLite file.

Separately, several current direction documents still use Stage 188/192-era
roadmap wording:

- `docs/reviews/opencode-full-project-review.md` names local trend/heat
  explanation as upcoming work even though Stage 193 has completed it.
- `docs/PROJECT_BRIEF.md`, `README.md`, `docs/REVIEW_PROTOCOL.md`, and
  `docs/architecture.md` still refer to source-health/feed-liveness visibility
  or `source coverage/health` as if Stage 190 had not already added the
  read-only `source-liveness` diagnostic.

The historical findings in old review/spec/plan artifacts should remain
unchanged. The current project direction should now say that the next core work
uses source-liveness evidence to broaden curated public-source coverage and
improve deterministic matching quality. Further summaries or explanations can
remain optional, local, and contract-safe.

This stage is deliberately small. It fixes coverage and planning/status drift
only. It does not add product features.

## Scope

In scope:

- Add `trend-explanations` CLI tests mirroring the existing `trends`
  `--baseline-as-of` invalid-date and ordering checks.
- Keep production `src/fashion_radar/cli.py` unchanged unless the new tests
  reveal a real regression.
- Update `tests/test_review_protocol_docs.py` so the full-project review status
  must mention Stage 192 and Stage 193 completion and must not describe the
  trend/heat explanation layer as future work.
- Update only the `Current Follow-Up Status` section of
  `docs/reviews/opencode-full-project-review.md`.
- Update current direction wording in:
  - `docs/PROJECT_BRIEF.md`
  - `README.md`
  - `docs/REVIEW_PROTOCOL.md`
  - `docs/architecture.md`
- Add a focused docs guard that pins current direction wording to
  source-liveness-backed curated public-source coverage and deterministic
  matching quality.
- Add a concise Stage 194 changelog entry.
- Record plan, code, and release review artifacts under `docs/reviews/`.

Out of scope:

- No new CLI command, flag, output field, source collector, source acquisition,
  scraping, browser automation, platform API, monitoring, scheduling, ranking,
  demand proof, platform coverage verification, or compliance-review feature.
- No changes to `TrendDelta`, `TrendComparison`, `HeatMover`,
  `HeatMoversReport`, dashboard rows, scoring, candidate scoring, matching, or
  SQLite schema.
- No changes to external-tool, community-handoff, or imported-review surfaces.
- No rewrite of the full-project review's original findings, recommendations,
  or strengths.

## Architecture

The code-side change is test-only:

```text
tests/test_cli.py
  -> invoke trend-explanations with invalid --baseline-as-of
  -> assert existing error prefix and no data-dir creation
  -> invoke trend-explanations with baseline-as-of equal to as-of
  -> assert existing ordering error and no data-dir creation
```

The planning/status change is documentation-only:

```text
tests/test_review_protocol_docs.py
  -> pin Current Follow-Up Status terms for Stages 188-193
  -> reject stale "trend/heat explanation is future work" phrasing
  -> pin current roadmap/protocol/architecture direction after Stage 190/193

docs/reviews/opencode-full-project-review.md
  -> update Current Follow-Up Status only

docs/PROJECT_BRIEF.md, README.md, docs/REVIEW_PROTOCOL.md, docs/architecture.md
  -> replace stale "build source-health" direction with "use source-liveness
     evidence for curated public-source coverage and deterministic matching"
```

Because the `trend-explanations` behavior already exists, the new CLI tests are
coverage backfill rather than RED tests for a missing implementation. If either
test fails, that failure should be treated as evidence of a real regression and
fixed at the smallest production surface.

## Acceptance Criteria

- `tests/test_cli.py` contains two `trend-explanations` tests covering invalid
  `--baseline-as-of` and `baseline-as-of >= as-of`.
- The two tests assert exit code `1`, the command-specific
  `Could not explain trend deltas` error wording, and no `data_dir` creation.
- The focused `trend-explanations` CLI test selection passes.
- `tests/test_review_protocol_docs.py` requires the full-project review status
  to mention Stage 192 and Stage 193 completion.
- The full-project review status no longer says or implies that adding a local
  trend/heat explanation layer is future work.
- Current direction docs no longer describe source-health/feed-liveness
  diagnostics as future work.
- Current direction docs prioritize source-liveness evidence, curated
  public-source coverage, and deterministic matching quality.
- Current direction docs keep further report summary or explanation refinements
  optional, local, and contract-safe.
- The historical full-project review findings and recommendations remain
  unchanged outside `Current Follow-Up Status`.
- Focused tests, lint/format checks, first-run smoke, release hygiene, lockfile
  check, mirror sync check, and full test suite pass before commit.
