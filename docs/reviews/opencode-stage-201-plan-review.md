# Stage 201 Plan Review

## Verdict

Approved with one Important planning fix required before implementation.

The plan correctly scopes Stage 201 to direct RSS endpoint normalization for
existing configured public sources. It should improve `source-liveness`
evidence and first-run collection inputs without adding runtime source
acquisition behavior, social connectors, proxy pools, ranking changes, or
compliance-review features.

## Critical Findings

None.

## Important Findings

1. The initial plan did not explicitly preserve the byte-identity invariant
   between `configs/sources.example.yaml` and
   `src/fashion_radar/templates/configs/sources.example.yaml`.

   Stage 195 established that the root starter config and packaged starter
   template should stay byte-identical. The initial Stage 201 plan edited both
   files independently and did not include either a `cp`-based sync step or a
   `cmp -s` release verification command. That creates drift risk between the
   checked-in starter and what `fashion-radar init` ships.

   Required fix: update the plan to edit the root starter config first, copy it
   to the packaged template, verify with `cmp -s`, and have code/release review
   check the byte-identity invariant.

## Minor Findings

- The exact URL tests pin a point-in-time configuration decision rather than
  proving future feed liveness. This is acceptable because live liveness remains
  advisory and source availability can change.
- The plan title says "Liveness Recovery" while the body more precisely
  describes direct endpoint normalization and liveness-noise reduction.

## Review Notes

1. Direct RSS endpoint normalization is a reasonable next stage after Stage 200
   because Stage 200 unblocked source-liveness checks in this environment.
2. The plan should include both the public source pack and overlapping starter
   config/template RSS URLs.
3. The planned deterministic tests are appropriate because they verify checked-in
   YAML URL decisions without network access.
4. Live endpoint probes and `source-liveness` runs are correctly framed as
   advisory evidence, not release gates.
5. The scope boundary correctly excludes runtime code, dependencies, source
   acquisition, ranking, coverage proof, social connectors, proxy pools, and
   compliance-review behavior.
