Review the Stage 81 plan for Fashion Radar.

Goal:
- Tighten Stage 80 documentation drift tests so external import boundary
  language is asserted inside the actual README and CLI reference guidance,
  not just somewhere in each full document.

Expected scope:
- tests/test_cli_docs.py
- Stage 81 spec/plan/review artifacts

Out of scope:
- src/
- README.md and docs/cli-reference.md prose unless a scoped test exposes a real
  mismatch
- dependency manifests
- uv.lock
- AGENTS.md
- docs/REVIEW_PROTOCOL.md
- docs/github-upload-checklist.md
- any runtime connector, scraper, platform API, ranking, demand proof, or
  compliance-review product feature

Please review:
- Is the test-tightening design sufficient?
- Are there Markdown split hazards?
- Does the plan preserve the local-only handoff boundary?
- Are verification and staging guardrails adequate?

Report findings by severity: Critical, Important, Minor.
