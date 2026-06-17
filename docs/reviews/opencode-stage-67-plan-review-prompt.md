Review the Stage 67 external-tool-workflow readiness preflight spec and
implementation plan in /home/ubuntu/fashion-radar.

Files to review:
- docs/superpowers/specs/2026-06-17-stage-67-external-tool-workflow-readiness-preflight-design.md
- docs/superpowers/plans/2026-06-17-stage-67-external-tool-workflow-readiness-preflight-plan.md

Focus on:
- whether adding a printed `check_external_tool_readiness` step to
  `external-tool-workflow` is the right next-stage scope;
- whether `external-tool-workflow` correctly remains print-only even though the
  generated command is local read-only if the user runs it manually;
- whether the plan avoids connectors, scraping, browser automation, platform
  APIs, monitoring, scheduling, source acquisition, demand proof, ranking,
  coverage verification, and compliance-review product features;
- whether tests/docs/smoke updates are sufficient for stable step-count/order
  churn from 11 to 12;
- whether there are any circular-guidance, docs-drift, or CI risks that should
  be fixed before implementation.

Return only concrete Critical or Important findings, plus blocking test gaps.
