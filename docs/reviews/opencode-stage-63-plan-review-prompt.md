You are reviewing the Stage 63 implementation plan for the fashion-radar repository.

Model requirement for this review: zhipuai-coding-plan/glm-5.2.
Variant requirement: max.

Repository: /home/ubuntu/fashion-radar
Base commit: cdb0535cadf9d05373b7684991d5e4ca425d48f0

Files to review:
- docs/superpowers/specs/2026-06-17-stage-63-external-tool-template-design.md
- docs/superpowers/plans/2026-06-17-stage-63-external-tool-template-plan.md
- Existing reference files:
  - src/fashion_radar/external_tool_adapters.py
  - src/fashion_radar/community_signal_profile.py
  - src/fashion_radar/community_signals.py
  - src/fashion_radar/cli.py
  - schemas/community-signals.schema.json
  - tests/test_external_tool_adapters.py
  - tests/test_cli.py
  - tests/test_cli_docs.py
  - scripts/check_first_run_smoke.py
  - AGENTS.md

Stage 63 objective:
- Add a local, print-only `fashion-radar external-tool-template` command.
- The command prints adapter-specific synthetic template rows for sanitized
  CSV/JSON local file handoff by user-controlled external/community tools.
- It should help tools such as Rednote/Xiaohongshu exporters, Instaloader,
  TikTok-Api, yt-dlp metadata exporters, X/search exports, and generic
  community exports produce the existing community signal fields:
  url, title, published_at, summary, source_name, platform, source_weight,
  collected_at.

Important intended contract:
- `--format csv` must output importable community signal CSV.
- `--format json` must output importable community signal JSON in the schema
  supported `{"items": [...]}` shape only.
- JSON/CSV rows must not include metadata fields such as `contract_version`,
  `adapter_id`, `display_name`, commands, boundaries, or field mappings.
- Metadata may exist in the internal Pydantic model and table output.
- The command must remain stdout-only and print-only.

Boundaries:
- No connectors.
- No scraping.
- No browser automation.
- No platform APIs.
- No account/session/cookie behavior.
- No media downloads.
- No reading directories or handoff files.
- No writing files or generated artifacts.
- No validation/import execution.
- No SQLite access.
- No monitoring or scheduling.
- No source acquisition.
- No demand proof.
- No ranking.
- No coverage verification.
- No compliance-review product feature.

Please review:
1. Does the design and plan satisfy the objective without accidentally
   violating the existing community signal schema?
2. Is the `--format json` plan safely importable as handoff JSON, not a
   metadata envelope?
3. Are tests sufficient to catch accidental metadata leakage into CSV/JSON rows?
4. Are CLI options, docs, smoke, and package verification scoped correctly?
5. Are there any Critical or Important issues that must be fixed before coding?

Return exactly:
- Verdict: APPROVED FOR STAGE 63 IMPLEMENTATION or CHANGES REQUIRED
- Findings grouped by severity: Critical, Important, Minor
- If approved, include one concise rationale.
