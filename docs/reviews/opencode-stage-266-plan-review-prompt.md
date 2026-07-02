Review the Stage 266 plan before implementation.

Repo: /home/ubuntu/fashion-radar
Design doc: docs/superpowers/specs/2026-07-02-stage-266-row-one-app-discovery-editorial-polish-design.md
Plan doc: docs/superpowers/plans/2026-07-02-stage-266-row-one-app-discovery-editorial-polish-plan.md

Goal:
Add a ROW ONE app discovery manifest, homepage lead story presentation,
deterministic SEO/social metadata, and source-checkout docs for opening the
local ROW ONE site.

Review criteria:
- Plan feasibility and correctness against the current codebase.
- Whether the manifest contract is small, stable, schema-validated, and does not
  duplicate edition stories/sections.
- Whether `row-one-app/v1` remains backwards compatible.
- Whether generated `data/manifest.json` and shipped
  `schemas/row-one-manifest.schema.json` boundaries are correct.
- Whether lead story and SEO/social metadata are presentation-only and do not
  alter collection, matching, scoring, ranking, scheduling, server, cleanup, or
  app payload semantics.
- Whether docs changes give a clearer GitHub/source-checkout ROW ONE path.
- Whether tests are executable as written and cover the new public behavior.
- Confirm no compliance-review product feature, new collector, LLM call, image
  generation, paid API, deployment, or system service installation is introduced.

Do not edit files. Return a concise review with Critical / Important / Minor
findings and a verdict.
