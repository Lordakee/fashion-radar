You are reviewing the Stage 59 plan for the fashion-radar repository.

Model requirement for this review: zhipuai-coding-plan/glm-5.2.

Repository:
- Path: /home/ubuntu/fashion-radar
- Current HEAD: b805ddb80f89f3f47f61c45579c6ce25f6227534
- Branch: main

Stage 59 objective:
- Add machine-readable directory example discovery to existing producer contracts.
- The intended field name is `directory_example_paths`.
- Add the field to `community-signal-profile --format json` and `community-handoff-manifest --format json/table`.
- Keep existing `example_paths` as the existing single-file examples.
- Do not add commands, workflow steps, source acquisition, connectors, platform/API integrations, account/session/cookie/browser automation, monitoring, scheduling, schema/migration, dependencies, report/dashboard/digest writes, or runtime directory reads in the profile/manifest builders.

Files to review:
- docs/superpowers/specs/2026-06-17-stage-59-directory-example-discovery-design.md
- docs/superpowers/plans/2026-06-17-stage-59-directory-example-discovery-plan.md

Please review for:
1. Whether the design and plan satisfy the Stage 59 objective.
2. Whether the scope is small enough for one node.
3. Whether the plan accidentally adds out-of-scope behavior.
4. Whether the tests and verification gates are strong enough.
5. Whether file ownership can be split safely across subagents.

Return exactly:
- Verdict: APPROVED FOR STAGE 59 PLAN or CHANGES REQUIRED
- Findings grouped by severity: Critical, Important, Minor
- If approved, include one concise rationale and any recommended implementation split.
