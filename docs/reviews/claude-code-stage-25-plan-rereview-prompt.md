You are reviewing the revised Stage 25 implementation plan for this repository.

Repository: `/home/ubuntu/fashion-radar`

Review these files only:

- `docs/superpowers/specs/2026-06-13-stage-25-imported-candidates-design.md`
- `docs/superpowers/plans/2026-06-13-stage-25-imported-candidates-plan.md`

Context:

Stage 25 adds a local read-only command:

```bash
fashion-radar imported-candidates \
  --config-dir ./configs \
  --data-dir ./data \
  --as-of 2026-06-13T12:00:00Z
```

The command should surface candidate phrases from retained `manual_import` rows
only. It must not add source acquisition, platform search, scraping, crawling,
browser automation, account automation, scheduling, external service calls,
SQLite writes, config writes, report/dashboard writes, or compliance/audit/policy
workflows.

Previous Claude Code plan review found three Important issues:

1. Reusing the public `CandidateReport` output could expose representative item
   URLs, titles, summaries, contexts, item IDs, match internals, or raw/manual
   import content.
2. The read-only regression test did not prove `query_imported_candidates()`
   calls the read-only SQLite engine factory.
3. The compatibility/regression scope did not explicitly cover broad call sites
   affected by `discover_candidates()` signature changes, including report,
   trend, dashboard, and existing candidates paths.

The revised plan/spec address these by:

- defining an imported-candidate-specific `ImportedCandidateRow` aggregate with
  only `phrase`, `candidate_type`, `label`, `score`, `current_mentions`,
  `baseline_mentions`, `distinct_sources`, `growth_ratio`, and `first_seen_at`;
- requiring JSON/table output to omit `representative_items`, `source_url`,
  `title`, `summary`, `contexts`, normalized keys, item IDs, match internals,
  aliases, import paths, source files, account/private/raw fields;
- requiring a `query_imported_candidates()` test that monkeypatches
  `imported_candidates_module.create_readonly_sqlite_engine`, calls
  `query_imported_candidates(...)`, and asserts the factory was called with
  `db_path`;
- adding focused regression coverage for direct candidate discovery, existing
  `candidates` CLI behavior, report/build_daily_report, trends/build_trend_comparison,
  and dashboard candidate/trend paths;
- following the repository's existing `Literal["table", "json"]` output-format
  pattern;
- requiring final `git status --short` and `git diff -- uv.lock` checks so the
  existing mirror URL diff in `uv.lock` stays unstaged and excluded.

Please rereview the revised plan/spec for correctness, safety, implementation
completeness, test adequacy, and alignment with existing project patterns.

Output format:

- If approved, include the exact phrase: `APPROVED FOR IMPLEMENTATION`.
- If not approved, list findings by severity: Critical, Important, Minor.
- Treat Critical and Important findings as blocking implementation.
