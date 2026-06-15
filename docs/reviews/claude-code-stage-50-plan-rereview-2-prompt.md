# Claude Code Stage 50 Plan Rereview 2 Prompt

Re-review the Stage 50 design and implementation plan in
`/home/ubuntu/fashion-radar` after the follow-up changes requested in
`docs/reviews/claude-code-stage-50-plan-rereview.md`.

Files:

- `docs/superpowers/specs/2026-06-16-stage-50-community-signal-producer-profile-design.md`
- `docs/superpowers/plans/2026-06-16-stage-50-community-signal-producer-profile-plan.md`
- Prior review:
  `docs/reviews/claude-code-stage-50-plan-rereview.md`

The prior remaining Important finding was:

- Add explicit `ManualSignalRow` `source_weight` bound checks, not only
  profile/schema/default checks.

The plan now adds direct checks that:

- omitted `source_weight` defaults to `1.0`;
- blank `source_weight` defaults to `1.0`;
- `source_weight=5` is accepted;
- `source_weight=0` is rejected;
- `source_weight=5.1` is rejected.

The plan also adds the prior Minor hardening suggestions:

- unexpected positional path argument is rejected without artifacts;
- installed-wheel `community-signal-profile --format json` smoke runs from a
  temporary cwd and asserts no config/data/report/SQLite/report artifacts are
  created.

Hard boundaries remain:

- No scraping, crawling, browser automation, account/session/cookie handling,
  platform APIs, monitoring, watch folders, scheduler behavior, source
  acquisition, database writes, report writes, dashboard state, new import
  formats, metadata sidecars, platform-specific adapters, or compliance-review
  functionality.
- The new command must print only. It should not accept path/config/data/report
  arguments, read handoff files, create directories, open SQLite, or call the
  network.

Please return:

- Critical findings
- Important findings
- Minor findings
- Missing tests or verification gaps
- Scope creep risks
- Approval status for implementation
