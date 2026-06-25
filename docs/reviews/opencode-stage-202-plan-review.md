# Stage 202 Plan Review

**Verdict: No Critical findings. One Important finding. Several Minor notes.**

## Critical

None.

## Important

**I-1 — The `score == sum(components)` invariant is pinned at the scoring layer but not at the report/CLI boundary.**

The whole value proposition is "components explain the surfaced score." Task 1
Step 1 asserts the sum on a synthetic `CandidateMetric` in
`test_candidate_scoring.py`, and Task 1 Steps 2-3 assert each component's sign
in the report-JSON and CLI-JSON paths, but neither asserts:

```python
parsed["candidates"][0]["score"] == (
    weighted_mention_component
    + growth_component
    + source_diversity_component
)
```

Because the three component values travel from `CandidateMetric` to
`CandidateReport` through two independent copy sites (`reports._candidate_report`
and `cli.candidates_command`), a future bug that passes a stale or zeroed
component into one path would leave the score looking explained while breaking
the explanation. Add explicit sum-equality assertions in both
`tests/test_reports.py::test_daily_report_includes_untracked_candidate_signals`
and `tests/test_cli.py::test_candidates_command_prints_json`.

## Minor

**M-1 — Markdown example numbers diverge from default-derived reality, and the test only checks a prefix.**

The Component Contract shows an illustrative line with `mentions 2.40` and
`sources 0.30`, but with default `ScoringSettings` the two-item/two-source
fixture produces `mentions 2.00; sources 1.00`. Lock the full expected line in
the report test, including `sources 1.00`, to pin ordering and two-decimal
formatting exactly.

**M-2 — Candidate CLI table format is not covered for components.**

The JSON path should receive component fields. The table is a compact summary,
so omitting components is defensible, but the plan should state this explicitly
so the omission is not read as accidental.

**M-3 — `imported_candidate_evidence.py` imports from `discovery.candidates` but is not in the named regression list.**

The added `CandidateMetric` fields are defaulted at the end of the dataclass,
so keyword and positional consumers stay compatible. Add
`tests/test_imported_candidate_evidence.py` to the regression sweep for
completeness.

**M-4 — Note the entity/candidate shape asymmetry in docs.**

`EntityReport` has a fourth `high_weight_component`; candidates correctly have
only three components because `_score_candidate` has no high-weight-source term.
Add a one-line scoring docs note that candidate and entity component sets differ
intentionally.

## Question-by-Question Answers

1. **Reasonable next stage?** Yes. Stage 199 established the component
   transparency precedent for tracked entities; extending the same explainability
   to untracked candidates is natural parity and matches the full-project-review
   direction toward core report value over handoff expansion.
2. **Formula preserved exactly?** Yes. The Component Contract maps one-to-one
   onto the existing `_score_candidate` formula, including the
   `if growth_ratio else 0.0` condition. Ranking keys and thresholds remain
   untouched.
3. **Same `CandidateReport` fields everywhere?** Yes. The shared model should
   be used by daily reports and candidate CLI JSON. `imported_candidates.py` and
   `community_candidates.py` use separate row models and should remain
   untouched.
4. **RED tests sufficient?** Yes after fixing I-1. Component math,
   sum-at-scoring-layer, report JSON/Markdown, CLI stable keys, docs wording,
   and the existing internal-leakage loop cover the stage.
5. **Avoids forbidden scope?** Yes. The plan adds no source acquisition,
   connectors, scraping, APIs, dashboard changes, dependency or schema changes,
   demand proof, coverage verification, or compliance-review behavior.
6. **Release verification sufficient?** Yes. The release verification set is
   appropriate for an additive reporting-model change with no dependency or
   schema deltas.
