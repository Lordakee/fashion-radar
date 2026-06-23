# Stage 179 Plan Review Prompt

Review the Stage 179 plan for Fashion Radar.

Return only the completed review body. Do not include process chatter, live tool
status, ANSI output, command logs, markdown code fences, or multiple drafts.
This is a read-only review: do not edit files, do not run `git stash`, and do
not mutate the working tree.
Start the response exactly with:

# Stage 179 Plan Review

Objective:

Add a focused regression guard that ensures the documented source-pack quality
JSON sample exposes the same top-level keys as the runtime
`SourcePackLintResult` payload.

Files to review:

- `docs/superpowers/specs/2026-06-24-stage-179-source-pack-quality-json-keyset-guard-design.md`
- `docs/superpowers/plans/2026-06-24-stage-179-source-pack-quality-json-keyset-guard-plan.md`
- `docs/reviews/opencode-stage-179-plan-review-prompt.md`
- Existing context:
  - `tests/test_source_pack_quality_docs.py`
  - `src/fashion_radar/source_packs.py`
  - `docs/source-pack-quality.md`
  - `docs/reviews/opencode-stage-176-code-review.md`

Scope boundaries:

- Test-only hardening.
- No planned runtime behavior changes.
- No planned docs changes unless the new test exposes a real documented/runtime
  key mismatch.
- No source acquisition, collector/source config changes, availability checks,
  demand proof, ranking, coverage verification features, compliance-review
  product features, dependency changes, or `uv.lock` changes.

Review questions:

1. Does the plan directly address the Stage 176 follow-up note about documenting
   the full runtime top-level JSON key set?
2. Is adding `runtime_payload = result.model_dump(mode="json")` and comparing
   `set(payload)` with `set(runtime_payload)` inside the existing JSON parity
   test sufficient and appropriately scoped?
3. Does the plan preserve the existing documented relative `path` value
   exception?
4. Are the verification, review, release, commit, and push steps sufficient for
   a small test-only stage?
5. Are there any critical or important issues to fix before implementation?

Return sections:

- Summary
- Findings
  - Critical
  - Important
  - Minor
- Verification Guidance
- Verdict
