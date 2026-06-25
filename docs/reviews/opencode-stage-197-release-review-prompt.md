# Stage 197 Release Review Prompt

Review Stage 197 release readiness in `/home/ubuntu/fashion-radar`.

Scope:

- Optional public source-pack expansion only.
- Four new RSS feeds in `configs/source-packs/fashion-public.example.yaml`:
  Vogue, Business of Fashion, Red Carpet Fashion Awards, and PurseBlog.
- Docs sample parity updates in `docs/source-packs.md` and
  `docs/source-pack-quality.md`.
- Changelog entry and public-pack CLI count assertion update.
- Stage 197 plan and review artifacts.

Questions:

1. Are all plan/code review Critical and Important findings resolved?
2. Did final verification include full pytest, release hygiene, deterministic
   source-pack lint/docs checks, ruff, lockfile hygiene, mirror-marker scan,
   and `git diff --check`?
3. Does the commit manifest include all intended Stage 197 files and exclude
   `uv.lock`, `pyproject.toml`, generated liveness output, build output, local
   config/data/report artifacts, and private data?
4. Is live source-liveness treated only as advisory evidence, with the current
   proxy/SOCKS environment limitation recorded honestly if observed?
5. Does the stage avoid default starter changes, new source types, social or
   platform connectors, scraping, browser automation, platform APIs, access
   bypass, demand proof, source ranking, platform coverage verification, and
   compliance-review product features?

Return:

- Verdict: READY / NEEDS_WORK
- Blocking findings
- Non-blocking findings
- Verification evidence summary
- Scope boundary confirmation
- Handoff Summary
