# Stage 197 Code Review Prompt

Review current Stage 197 changes in `/home/ubuntu/fashion-radar`.

Scope:

- `configs/source-packs/fashion-public.example.yaml`
- `docs/source-packs.md`
- `docs/source-pack-quality.md`
- `CHANGELOG.md`
- `tests/test_cli.py`
- Stage 197 plan/review artifacts

Questions:

1. Does the optional public source pack add only the intended four RSS feeds
   (Vogue, Business of Fashion, Red Carpet Fashion Awards, PurseBlog) with
   explicit weights, non-empty tags, and `article.enabled: false`?
2. Does the default compact `configs/sources.example.yaml` remain unchanged?
3. Do source-pack docs and source-pack-quality samples match current
   `source-pack-lint` output?
4. Is the public-pack CLI count assertion updated correctly?
5. Does the change avoid social/platform connectors, scraping, browser
   automation, platform APIs, access bypass, source ranking, demand proof,
   platform coverage verification, and compliance-review product features?
6. Are tests and verification adequate? Treat live `source-liveness` as advisory
   only, not a release blocker.

Return:

- Verdict: APPROVED / NEEDS_WORK
- Critical findings
- Important findings
- Minor findings
- Verification observed or recommended
- Concrete fixes required before release
