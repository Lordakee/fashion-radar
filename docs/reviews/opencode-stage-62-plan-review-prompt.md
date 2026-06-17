You are reviewing the Stage 62 plan for the fashion-radar repository.

Model requirement for this review: zhipuai-coding-plan/glm-5.2.

Review target:
- Repository: /home/ubuntu/fashion-radar
- Current base commit: dc0c8d4cebd00c174886ebe839aec80fe9d09dab
- Review the proposed design and implementation plan only.

Files to review:
- docs/superpowers/specs/2026-06-17-stage-62-external-tool-adapter-registry-design.md
- docs/superpowers/plans/2026-06-17-stage-62-external-tool-adapter-registry-plan.md

Stage 62 objective:
- Add a local, print-only external social/community tool adapter registry.
- The registry should help user-controlled upstream tools map their sanitized
  exports into the existing community signal handoff fields:
  url, title, published_at, summary, source_name, platform, source_weight,
  collected_at.
- The registry should include known producer categories such as Rednote/
  Xiaohongshu tools, Instaloader, TikTok-Api, yt-dlp, X/search exports, and a
  generic community export.
- The CLI should be `fashion-radar external-tool-adapters`, with table/json
  output and optional adapter filtering.
- The command must remain print-only. It may build command strings but must not
  inspect the supplied directory, read configs, open SQLite, run commands,
  import rows, create files, install tools, fetch URLs, log in, store cookies,
  call platform APIs, automate browsers, monitor communities, schedule work,
  acquire sources, prove demand, rank sources, verify platform coverage, or
  perform compliance review.

Out of scope:
- No connector implementation.
- No scraper, crawler, browser automation, platform API, account/session/cookie,
  proxy, or media-download integration.
- No new dependency.
- No schema, migration, collector, scheduler, dashboard, report, digest, entity
  pack, source pack, candidate scoring, or importer behavior change.
- No compliance-review product feature.

Please review for:
1. Critical or Important problems in the design or plan.
2. Any accidental scope expansion beyond the Stage 62 objective.
3. Any missing test/doc coverage needed before implementation.
4. Any mismatch with existing CLI command signatures or repository patterns.
5. Any wording that could imply platform coverage, demand proof, ranking, or a
   real social-listening connector.

Return exactly:
- Verdict: APPROVED FOR STAGE 62 PLAN or CHANGES REQUIRED
- Findings grouped by severity: Critical, Important, Minor
- If approved, include one concise rationale.
