# Stage 57 Plan Rereview Prompt

You are the local planning reviewer for `/home/ubuntu/fashion-radar`.

Model requested by the project owner: `zhipuai-coding-plan/glm-5.2`.

Do not edit files. Re-review the Stage 57 planning documents after fixes to
your previous findings:

- `docs/superpowers/specs/2026-06-17-stage-57-local-heat-movers-design.md`
- `docs/superpowers/plans/2026-06-17-stage-57-local-heat-movers-plan.md`
- Previous review: `docs/reviews/opencode-stage-57-plan-review.md`

## Previous Blocking Findings To Verify

1. Critical C1: The docs forbidden-claims test globally banned phrases that
   already appear in legitimate negative boundary wording. The plan should now
   scope forbidden-claim absence to the new `heat-movers` sections and must not
   force removal of existing negated boundary docs such as "not verified demand"
   or "not platform-wide popularity".
2. Important I1: The dashboard plan added a tab but did not require a test that
   catches `main()` positional tab-routing mistakes. The plan should now require
   label-based tab routing and a fake Streamlit `main()` routing test.

## Minor Findings To Check

The revised plan should also address:

- Adding `heat-movers` to `REQUIRED_FLAGS_BY_COMMAND`.
- Clarifying that negative `--limit` is rejected by Typer parse-time validation.
- Requiring `CHANGELOG.md` to mention `heat-movers` in docs drift coverage.

## Review Scope

The intended Stage 57 feature remains:

- Create a pure `src/fashion_radar/heat_movers.py` grouping/rendering layer over
  existing `TrendComparison`.
- Add a read-only `fashion-radar heat-movers` command.
- Add a dashboard "Heat Movers" tab that reuses existing read-only trend query
  behavior.
- Update docs/tests/guardrails.

Stage 57 must still avoid platform connectors, platform APIs, scraping,
crawling, browser automation, login/accounts/cookies/sessions/proxies, media
downloads, monitoring/watch loops/scheduling/notifications/webhooks, DB schema
changes, new dependencies, report schema/template changes, generated artifacts,
new scoring formulas, demand proof, platform coverage verification,
market-wide/platform-wide popularity claims, and compliance/legal/approval/
policy/authorization/safety-review features.

## Output Format

Return:

- Critical findings
- Important findings
- Minor findings
- Whether C1 and I1 are fixed
- Final verdict

If there are no Critical or Important findings, include this exact approval line:

```text
APPROVED FOR STAGE 57 LOCAL HEAT MOVERS
```
