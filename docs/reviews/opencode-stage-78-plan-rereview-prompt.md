# Stage 78 Plan Rereview Prompt

Please rereview the Stage 78 plan after the first plan review found C1.

Repository: `/home/ubuntu/fashion-radar`

Files to review:

- `docs/superpowers/specs/2026-06-18-stage-78-adapter-contract-parity-design.md`
- `docs/superpowers/plans/2026-06-18-stage-78-adapter-contract-parity-plan.md`
- `docs/reviews/opencode-stage-78-plan-review.md`

First review Critical C1 said the docs drift test in Task 2 could not pass
against the planned docs prose because of phrase mismatch, case mismatch, and
distributed negation.

The plan was updated to:

- add `COMMUNITY_SIGNAL_IMPORT_DOC` unconditionally;
- use `_normalized_doc_text(...).casefold()` in the docs drift test;
- require the raw text phrase `Dry-run import guidance remains separate from
  real import guidance.`;
- update the planned docs subsection to include that exact phrase;
- split demand/ranking/coverage wording into standalone `It does not ...`
  sentences.

Please verify C1 is resolved and report any remaining Critical or Important
findings. Keep review scoped to plan correctness, determinism, boundaries, and
release safety with the dirty out-of-stage `uv.lock`.
