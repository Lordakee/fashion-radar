Review this Stage 53 implementation plan before any implementation begins.

Repository: `/home/ubuntu/fashion-radar`

Read these files:

- `docs/superpowers/specs/2026-06-16-stage-53-community-handoff-guardrails-design.md`
- `docs/superpowers/plans/2026-06-16-stage-53-community-handoff-guardrails-plan.md`
- `src/fashion_radar/community_signals.py`
- `src/fashion_radar/community_signal_profile.py`
- `src/fashion_radar/cli.py`
- `tests/test_community_signal_lint.py`
- `tests/test_community_signal_profile.py`
- `tests/test_cli.py`
- `tests/test_cli_docs.py`
- `docs/community-signal-import.md`
- `CHANGELOG.md`

Objective:

- Stage 53 should add quality guardrails around the existing community handoff
  contract.
- It should be test/docs-only unless the review identifies a real existing
  production bug.
- It must not add scraping, crawling, browser automation, login,
  cookies/sessions, platform APIs, source acquisition, scheduling, monitoring,
  media download, connector code, or a compliance-review feature.

Please evaluate:

1. Whether the plan matches the design and current codebase.
2. Whether the proposed tests are meaningful and not brittle.
3. Whether any proposed assertion conflicts with current intentional behavior.
4. Whether the implementation can be split safely across disjoint write scopes.
5. Whether any Critical or Important issue must be fixed before coding.

Report findings by severity:

- Critical: must fix before implementation.
- Important: should fix before implementation.
- Minor: can defer if not blocking.

If there are no Critical or Important findings, say so explicitly.
