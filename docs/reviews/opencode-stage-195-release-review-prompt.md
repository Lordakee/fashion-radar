# Stage 195 Release Review Prompt

Review whether Stage 195 is ready to commit and push.

Scope:

- Runtime diacritic-insensitive text and alias matching.
- Compact default starter RSS/GDELT source config expansion.
- Root/package starter source config parity.
- Minimal README, project brief, and changelog updates.
- Review artifacts for Stage 195.

Required verification evidence:

- `uv --no-config run --frozen pytest tests/ -q --tb=short`
- `uv --no-config run --frozen pytest tests/test_release_hygiene.py -q`
- `git diff --check`
- `cmp -s configs/sources.example.yaml src/fashion_radar/templates/configs/sources.example.yaml`
- `git diff -- configs/source-packs/fashion-public.example.yaml` has no output

Release boundaries:

- No social scraping.
- No browser automation.
- No platform APIs.
- No login/cookie/proxy behavior.
- No source ranking or demand proof.
- No platform-wide coverage claims.
- No compliance-review product feature.

Return:

- Verdict: READY / NEEDS_WORK
- Blocking findings
- Non-blocking findings
- Verification evidence summary
- Handoff Summary with repo status, verified commands, uncommitted files, and next step
