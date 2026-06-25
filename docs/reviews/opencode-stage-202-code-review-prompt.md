# Stage 202 Code Review Prompt

Review the Stage 202 implementation in `/home/ubuntu/fashion-radar`.

Goal: expose local candidate score components in daily report JSON, daily
report Markdown, and candidate CLI JSON so untracked phrase review can see the
mention, growth, and source-diversity terms behind the final candidate score.

Plan and review artifacts:

- `docs/superpowers/plans/2026-06-25-stage-202-candidate-score-components-report-plan.md`
- `docs/reviews/opencode-stage-202-plan-review.md`
- `docs/reviews/opencode-stage-202-plan-rereview.md`

Changed implementation files:

- `src/fashion_radar/discovery/candidates.py`
- `src/fashion_radar/models/report.py`
- `src/fashion_radar/reports.py`
- `src/fashion_radar/cli.py`

Changed tests/docs:

- `tests/test_candidate_scoring.py`
- `tests/test_reports.py`
- `tests/test_cli.py`
- `tests/test_candidate_discovery_docs.py`
- `tests/test_scoring_docs.py`
- `docs/candidate-discovery.md`
- `docs/scoring.md`
- `CHANGELOG.md`
- Stage 202 plan/review artifacts

Implementation summary:

- `CandidateMetric` now carries `weighted_mention_component`,
  `growth_component`, and `source_diversity_component` with default `0.0`
  values for backward-compatible direct constructors.
- `_score_candidate` splits the existing score formula into the same three
  named terms and computes `score` as their sum.
- `CandidateReport` adds the same three fields immediately after `score`, so
  JSON key order is stable.
- Daily report candidate construction and `fashion-radar candidates --format
  json` both copy the component fields from `CandidateMetric`.
- Daily Markdown candidate sections render:
  `- Score components: mentions ...; growth ...; sources ...`.
- Docs explain these are local observed review aids, not demand proof or
  platform coverage verification, and candidates intentionally omit the
  tracked-entity high-weight source term.

Unchanged by design:

- candidate ranking, thresholds, extraction, labels, representative-item
  selection, trend deltas, heat movers, tracked entity scoring, source configs,
  source packs, collectors, source-liveness, HTTP/proxy code, dashboard display,
  imported/community command outputs, database schema, dependencies, and
  lockfiles
- no source acquisition, social/platform connectors, scraping, browser
  automation, APIs, demand proof, platform coverage verification, or
  compliance-review product features

Verification already run:

- RED:
  `uv --no-config run --frozen pytest tests/test_candidate_scoring.py::test_candidate_score_exposes_components_that_sum_to_score -q`
  failed with missing `CandidateMetric.weighted_mention_component`.
- RED:
  `uv --no-config run --frozen pytest tests/test_reports.py::test_daily_report_includes_untracked_candidate_signals -q`
  failed with missing daily JSON component field.
- RED:
  `uv --no-config run --frozen pytest tests/test_cli.py::test_candidates_command_prints_json -q`
  failed because candidate CLI JSON lacked the component keys.
- RED:
  `uv --no-config run --frozen pytest tests/test_candidate_discovery_docs.py tests/test_scoring_docs.py -q`
  failed on missing docs wording.
- GREEN:
  `uv --no-config run --frozen pytest tests/test_candidate_scoring.py::test_candidate_score_exposes_components_that_sum_to_score tests/test_reports.py::test_daily_report_includes_untracked_candidate_signals tests/test_cli.py::test_candidates_command_prints_json -q`
  -> `3 passed`.
- Docs:
  `uv --no-config run --frozen pytest tests/test_candidate_discovery_docs.py tests/test_scoring_docs.py -q`
  -> `4 passed`.
- Focused candidate/report tests:
  `uv --no-config run --frozen pytest tests/test_candidate_scoring.py tests/test_reports.py -q`
  -> `30 passed`.
- Trend/imported compatibility:
  `uv --no-config run --frozen pytest tests/test_trends.py tests/test_imported_candidates.py tests/test_imported_candidate_evidence.py -q`
  -> `31 passed`.
- Focused CLI candidate/report tests:
  `uv --no-config run --frozen pytest tests/test_cli.py -q -k "candidates_command or report"`
  -> `45 passed, 274 deselected`.
- Candidate table boundary:
  `uv --no-config run --frozen pytest tests/test_cli.py::test_candidates_command_prints_json tests/test_cli.py::test_candidates_command_prints_table -q`
  -> `2 passed`.
- Touched-file lint:
  `uv --no-config run --frozen ruff check src/fashion_radar/discovery/candidates.py src/fashion_radar/models/report.py src/fashion_radar/reports.py src/fashion_radar/cli.py tests/test_candidate_scoring.py tests/test_reports.py tests/test_cli.py tests/test_candidate_discovery_docs.py tests/test_scoring_docs.py`
  -> all checks passed.
- Touched-file format:
  `uv --no-config run --frozen ruff format --check src/fashion_radar/discovery/candidates.py src/fashion_radar/models/report.py src/fashion_radar/reports.py src/fashion_radar/cli.py tests/test_candidate_scoring.py tests/test_reports.py tests/test_cli.py tests/test_candidate_discovery_docs.py tests/test_scoring_docs.py`
  -> `9 files already formatted`.

Please review:

1. Does the implementation match the Stage 202 plan and plan-rereview fixes?
2. Does `_score_candidate` preserve the existing score semantics exactly while
   exposing named components?
3. Are both copy boundaries (`reports._candidate_report` and
   `cli.candidates_command`) covered and correct?
4. Are tests strong enough to catch zeroed/stale component propagation at
   daily-report and CLI JSON boundaries?
5. Are docs/changelog accurate and scoped to local observed review aids?
6. Is there any accidental change to imported/community/dashboard/source,
   ranking, dependency, schema, social/platform, source acquisition, or
   compliance-review behavior?

Return findings as Critical, Important, and Minor. If there are no Critical or
Important findings, say that clearly.
