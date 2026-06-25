# Stage 195 Code Review Prompt

Review the current Stage 195 code changes in `/home/ubuntu/fashion-radar`.

Scope:

- `src/fashion_radar/extract/text.py`
- `tests/test_text.py`
- `configs/sources.example.yaml`
- `src/fashion_radar/templates/configs/sources.example.yaml`
- `tests/test_config.py`
- `README.md`
- `docs/PROJECT_BRIEF.md`
- `CHANGELOG.md`
- Stage 195 plan/review artifacts

Review against:

- `docs/superpowers/plans/2026-06-25-stage-195-source-coverage-and-diacritics-plan.md`
- `AGENTS.md`

Questions:

1. Does runtime `alias_pattern(...).search(raw_text)` now match common accented/plain Latin variants while preserving existing word-boundary and multi-word whitespace behavior?
2. Does `normalize_text()` fold common Latin diacritics without new dependencies?
3. Does the default starter source config now include compact curated RSS/GDELT fashion lanes while remaining smaller than the broader public source pack?
4. Are root and packaged starter source configs byte-identical?
5. Are tests offline/deterministic and scoped correctly?
6. Did the change avoid social scraping, browser automation, platform APIs, live URL guarantees, source ranking, demand proof, and compliance-review product features?

Return:

- Verdict: APPROVED / NEEDS_WORK
- Critical findings
- Important findings
- Minor findings
- Verification commands observed or recommended
- Concrete fixes required before release
