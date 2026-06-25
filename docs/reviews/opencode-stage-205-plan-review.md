# Stage 205 Plan Review

## Verdict

No Critical findings. No Important findings. The plan is minimal,
contract-safe, and correctly scoped.

## Critical

None.

## Important

None.

## Findings

The five planned field names match `CandidateReport` exactly:
`weighted_mention_component`, `growth_component`,
`source_diversity_component`, `growth_ratio`, and `first_seen_at`.
`app.py` passes rows straight to `st.dataframe`, and no caller inspects row
keys in a way that makes adding columns unsafe.

The RED-to-GREEN mechanics are correct: the current projection in
`latest_candidate_report()` emits only the final score, mention counts,
distinct sources, and report date, so tests expecting the new fields fail until
the projection changes.

## Minor

1. Dashboard docs should mention `growth_ratio` and `first_seen_at`, not only
   the three Stage 202 score-component fields.

2. Add a partial legacy test that preserves pre-existing `growth_ratio` and
   `first_seen_at` while defaulting missing Stage 202 component fields.

3. Add config-isolated `uv lock --check` to the focused verification gate so
   accidental dependency drift is caught before code review.

4. Changelog instructions should say to prepend the Stage 205 entry under
   `### Added`.

5. `first_seen_at` display stays as raw report pass-through. Any formatting
   normalization should be future UI polish, not this stage.

## Answers To The Review Questions

1. Reasonable next stage after Stage 204: yes. It is a read-only transparency
   refinement that closes a real report-to-dashboard gap.

2. Minimal implementation: yes. Adding fields to the query projection is the
   smallest correct fix; no Streamlit rendering change is needed.

3. Legacy defaults: correct. Score components default to `0.0`;
   `growth_ratio` and `first_seen_at` default to `None`.

4. Representative items and entity match evidence should stay out of this node.
   They involve different display shapes and broader entity dashboard behavior.

5. Tests are sufficient after adding the partial legacy growth-field case.

6. Docs, changelog, and verification are sufficient with the minor additions
   above.

7. Scope is compliant: no source acquisition, connectors, scraping, demand
   proof, platform coverage verification, dependency changes, or
   compliance-review behavior.
