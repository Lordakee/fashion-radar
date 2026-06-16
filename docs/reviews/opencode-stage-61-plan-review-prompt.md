You are reviewing the Stage 61 plan for the fashion-radar repository.

Model requirement for this review: zhipuai-coding-plan/glm-5.2.

Review target:
- Repository: /home/ubuntu/fashion-radar
- Current base commit: 403d092899d9f1ae27c8d3f4a1dba7cfbdd1d36f
- Review the proposed design and implementation plan only.

Files to review:
- docs/superpowers/specs/2026-06-17-stage-61-community-handoff-readiness-workflow-step-design.md
- docs/superpowers/plans/2026-06-17-stage-61-community-handoff-readiness-workflow-step-plan.md

Stage 61 objective:
- Add the existing local-only `community-handoff-check-dir` command as a read-only readiness report step inside the existing print-only `community-handoff-workflow`.
- The new step should be named `review_handoff_readiness`.
- The new step should be read-only.
- The new step should appear after `preview_candidate_phrases` and before `dry_run_directory_import`.
- The new step command should be:
  `fashion-radar community-handoff-check-dir <directory> --input-format <format> --pattern <pattern> --config-dir <config_dir> --as-of <as_of> --source-name <source_name> --strict`.
- The actual import step should remain `updates_local_imports`.
- The post-import review step should remain `print_only`.
- The workflow builder must remain print-only and must not inspect the directory, read config files, open SQLite, run commands, import rows, or create artifacts.

Out of scope:
- No new CLI command or workflow option.
- No new connector, scraper, platform API, account/session/cookie/browser automation, monitoring, scheduling, source acquisition, schema/migration, dependency, report/dashboard/digest write, or compliance/legal/safety-review product feature.

Please review for:
1. Critical or Important problems in the design or plan.
2. Any accidental scope expansion beyond the Stage 61 objective.
3. Any missing test/doc coverage needed before implementation.
4. Any mismatch with existing CLI command signatures or repository patterns.

Return exactly:
- Verdict: APPROVED FOR STAGE 61 PLAN or CHANGES REQUIRED
- Findings grouped by severity: Critical, Important, Minor
- If approved, include one concise rationale.
