# Claude Code Stage 387 Code Rereview

## Verdict

APPROVED

## Scope

Reviewed the complete Stage 387 change from `1e366aa` through the current
working-tree diff against the Stage 387 plan and design.

Stage 387 adds the Daily Local Brand, Product & People Signal Digest to
`index.html` only. The review confirmed that the builder, template rendering,
and renderer wiring do not create JSON artifacts, routes, schema changes, or
app-contract changes.

## Review Result

No critical or important findings remain.

The builder's `entity_count` and each bucket's `total_count` intentionally
retain factual pre-cap candidate totals. The template independently derives the
visible entity metric from safe, capped rendered items. This is the required
defense-in-depth behavior for manually constructed payloads and is not a
release blocker.

The root-relative `/.codegraph/**` source-distribution exclusion in
`pyproject.toml` is intentional release hygiene. It keeps the requested local
CodeGraph database out of package archives without changing runtime or wheel
packaging behavior.

The review also confirmed the specified homepage placement, local-sidecar
validation, dual href validation, escaping, sparse-edition gate, and exclusion
of all new digest content from detail pages and generated data artifacts.

## Disposition

No code changes were required from this rereview. The Stage 387 release review
remains required after the completed release gates and before commit/push.
