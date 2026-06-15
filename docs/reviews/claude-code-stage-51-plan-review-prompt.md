Please review the Stage 51 design and implementation plan for Fashion Radar.

Context:
- Repo: /home/ubuntu/fashion-radar
- Current branch: main
- Stage 51 objective: strengthen the deterministic first-run sample output gate.
- The project is local-first and free-first. Do not require paid APIs, login cookies, proxies, CAPTCHA bypass, browser automation, scraping/crawling, source/platform connectors, platform automation, or external services for this stage.
- The user explicitly does not want a compliance-review feature.

Please read:
- AGENTS.md
- docs/REVIEW_PROTOCOL.md
- docs/superpowers/specs/2026-06-16-stage-51-first-run-sample-output-quality-gate-design.md
- docs/superpowers/plans/2026-06-16-stage-51-first-run-sample-output-quality-gate-plan.md
- scripts/check_first_run_smoke.py
- tests/test_first_run_smoke.py
- examples/community-signals.example.csv
- configs/entities.example.yaml
- README.md
- docs/first-run.md
- docs/github-upload-checklist.md
- tests/test_cli_docs.py

Review focus:
1. Does the plan satisfy the staged workflow and project boundaries?
2. Is changing the two-row sample CSV to match starter entities a sound way to make first-run output useful without weakening matching rules?
3. Are the proposed smoke validators meaningful but not overly brittle?
4. Are tests and docs sufficient to prevent drift?
5. Are there any Critical or Important issues that must be fixed before implementation?

Please classify findings as Critical, Important, or Minor. If there are no Critical or Important blockers, say that implementation may proceed.
