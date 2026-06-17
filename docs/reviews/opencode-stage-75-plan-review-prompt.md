# Stage 75 Plan Review Prompt

Review the Stage 75 design and implementation plan in
`/home/ubuntu/fashion-radar`:

- `docs/superpowers/specs/2026-06-18-stage-75-adapter-docs-matrix-design.md`
- `docs/superpowers/plans/2026-06-18-stage-75-adapter-docs-matrix-plan.md`

Use a planning/code-review stance. Lead with Critical or Important findings if
present; include Minor notes after. Do not propose adding scraping, connectors,
browser automation, platform APIs, login/cookie/session/token/proxy behavior,
CAPTCHA handling, media download, monitoring/scheduling, source acquisition,
demand proof, ranking, coverage verification, or compliance-review product
behavior.

For this stage, the user explicitly directed local review through
`opencode run --model zhipuai-coding-plan/glm-5.2 --variant max`; this
stage-local review path does not change broader repository review protocol
documents.

## Goal

Add a public docs matrix for all seven external-tool adapter ids, document that
the automated first-run smoke validates the adapter registry JSON contract from
`external-tool-adapters --format json` across all seven adapters, and guard both
with `tests/test_cli_docs.py`.

## Planned Scope

- Modify `README.md`.
- Modify `docs/cli-reference.md`.
- Modify `docs/first-run.md`.
- Modify `CHANGELOG.md`.
- Modify `docs/reviews/opencode-stage-74-code-review.md` only to add a
  Stage 75 resolution note for a stale review-artifact comment.
- Modify `tests/test_cli_docs.py`.
- Keep runtime CLI and adapter registry code unchanged.
- Require the exact full adapter matrix rows in both README and CLI reference
  docs.
- Require the first-run smoke adapter-registry contract sentence in both README
  and first-run guide docs.

## Review Questions

1. Is the expected adapter matrix correct and aligned with the current registry?
2. Are README and CLI reference the right public docs to guard with full-row
   assertions?
3. Is the first-run smoke adapter-registry sentence accurate and scoped to the
   current smoke behavior?
4. Is the Stage 74 code-review resolution note appropriate as a Stage 75
   release-trail cleanup?
5. Does the plan avoid runtime behavior and external platform behavior changes?
6. Are there any Critical or Important issues to fix before implementation?
