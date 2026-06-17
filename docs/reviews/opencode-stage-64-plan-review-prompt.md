You are reviewing the Stage 64 implementation plan for the fashion-radar repository.

Model requirement for this review: zhipuai-coding-plan/glm-5.2.
Variant requirement: max.

Repository: /home/ubuntu/fashion-radar
Base commit: 3feb93690a81af32ed3f25e664ed0245fa98121c

Files to review:
- docs/superpowers/specs/2026-06-17-stage-64-external-tool-workflow-design.md
- docs/superpowers/plans/2026-06-17-stage-64-external-tool-workflow-plan.md
- Existing reference files:
  - src/fashion_radar/external_tool_adapters.py
  - src/fashion_radar/external_tool_templates.py
  - src/fashion_radar/community_handoff_workflow.py
  - src/fashion_radar/imported_review_workflow.py
  - src/fashion_radar/cli.py
  - scripts/check_first_run_smoke.py
  - tests/test_external_tool_adapters.py
  - tests/test_external_tool_templates.py
  - tests/test_community_handoff_workflow.py
  - tests/test_imported_review_workflow.py
  - tests/test_cli.py
  - tests/test_first_run_smoke.py
  - tests/test_cli_docs.py
  - AGENTS.md

Stage 64 objective:
- Add a local, print-only `fashion-radar external-tool-workflow` command.
- The command prints a structured workflow for user-controlled external/community
  tools that produce sanitized CSV/JSON local file handoff rows.
- It should connect `external-tool-adapters`, `external-tool-template`,
  `community-signal-profile`, `community-handoff-manifest`,
  `community-handoff-workflow`, lint/readiness, dry-run/import, and
  `imported-review-workflow`.
- It should support external/community handoff around Xiaohongshu/Rednote,
  Instagram, TikTok, X/search, media metadata, and generic community exports
  without adding built-in platform collection.

Important intended contract:
- `external-tool-workflow --format json` outputs workflow metadata, not
  importable handoff rows.
- Importable example rows remain the responsibility of
  `external-tool-template --format json/csv`.
- The workflow command must be stdout-only and print-only.
- It may instantiate static adapter/profile metadata, but it must not inspect
  the supplied directory or execute any generated command.
- It must use shell-quoted command strings, deterministic timestamps, stable
  Pydantic key order, and table-cell sanitization matching existing workflow
  commands.

Boundaries:
- No connectors.
- No scraping.
- No browser automation.
- No platform APIs.
- No account/session/cookie/token behavior.
- No media downloads.
- No reading directories or handoff files.
- No writing files or generated artifacts.
- No validation/import execution from this command.
- No SQLite access from this command.
- No monitoring or scheduling.
- No source acquisition.
- No demand proof.
- No ranking.
- No coverage verification.
- No compliance-review product feature.

Please review:
1. Does the design and plan satisfy the objective without accidentally adding
   platform collection, adapter execution, source acquisition, ranking, or
   coverage verification?
2. Is the JSON output contract clear enough as workflow metadata rather than
   importable handoff rows?
3. Are the eleven planned steps coherent, deterministic, and aligned with the
   existing external-tool and community-handoff commands?
4. Are tests sufficient to catch accidental directory reads, generated command
   execution, SQLite access, and docs boundary drift?
5. Are CLI options, first-run smoke, docs, package verification, token scanning,
   and mirror-lock checks scoped correctly?
6. Are there any Critical or Important issues that must be fixed before coding?

Return exactly:
- Verdict: APPROVED FOR STAGE 64 IMPLEMENTATION or CHANGES REQUIRED
- Findings grouped by severity: Critical, Important, Minor
- If approved, include one concise rationale.
