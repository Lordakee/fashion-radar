You are reviewing the Stage 60 plan for the fashion-radar repository.

Model requirement for this review: zhipuai-coding-plan/glm-5.2.

Repository:
- Path: /home/ubuntu/fashion-radar
- Current HEAD: bf5cf5cfe15e5a3bab1eec718253cc2bbf6f160f
- Branch: main

Stage 60 objective:
- Add the existing read-only `imported-candidates` command to the print-only `imported-review-workflow`.
- The new step name must be `review_imported_candidate_phrases`.
- The new step must be read-only and print this existing command:
  `fashion-radar imported-candidates --config-dir <config_dir> --data-dir <data_dir> --as-of <as_of> [--source-name <source_name>]`.
- The final workflow step must remain `review_local_heat_movers`.
- The workflow builder must remain print-only and must not load configs, open SQLite, inspect paths, call `query_imported_candidates`, run subprocesses, or create artifacts.
- No new CLI command, workflow option, connector, scraper, platform API, account/session/cookie/browser automation, monitoring, scheduling, schema/migration, dependency, dashboard/report/digest write, or compliance/legal/safety-review product feature.

Files to review:
- docs/superpowers/specs/2026-06-17-stage-60-imported-candidate-workflow-step-design.md
- docs/superpowers/plans/2026-06-17-stage-60-imported-candidate-workflow-step-plan.md

Please review for:
1. Whether the design and plan satisfy the Stage 60 objective.
2. Whether the step placement/order and command flags are correct.
3. Whether the plan accidentally adds out-of-scope behavior.
4. Whether the tests and verification gates are strong enough.
5. Whether file ownership can be split safely across sequential subagents.

Return exactly:
- Verdict: APPROVED FOR STAGE 60 PLAN or CHANGES REQUIRED
- Findings grouped by severity: Critical, Important, Minor
- If approved, include one concise rationale and any recommended implementation split.
