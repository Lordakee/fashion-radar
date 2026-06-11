# Claude Code Stage 6 Plan Review Prompt

You are Claude Code reviewing the Stage 6 plan for Fashion Radar before
documentation and GitHub-readiness work begins.

Repository: `/home/ubuntu/fashion-radar`

Current head:

- `3d97313 feat: add stage 5 cli and dashboard workflow`

Project goal:

- Build a free-first/local-first fashion intelligence MVP suitable for GitHub.
- It should collect allowed public fashion signals, match tracked fashion
  entities, compute heat changes, generate daily Markdown/JSON reports, and
  provide a read-only local dashboard.
- It must not implement fragile or risky social scraping in the MVP.

Approved architecture and stack:

- Python 3.11+
- uv
- Typer CLI
- Pydantic v2
- SQLAlchemy 2.x
- SQLite
- RSS/RSSHub-compatible public feeds
- GDELT Doc API
- deterministic alias/context entity matching
- deterministic scoring/report generation
- optional Streamlit dashboard extra
- pytest and ruff
- CodeGraph project tooling for Claude Code/Codex

Stage 6 goal:

- Make the repository understandable and safe to publish to GitHub.
- The agent may prepare files and local commits, but the user controls remote
  creation, pushing to GitHub, PyPI publishing, and artifact uploads.

Stage 6 plan location:

- `docs/superpowers/plans/2026-06-11-fashion-radar-implementation-plan.md`
- Review section: `## Stage 6: GitHub Packaging`

Please review whether the Stage 6 plan is concrete and safe to execute. Focus on
these requirements:

1. README explains what the tool does and does not do, the free/local-first
   positioning, source boundaries, and the workflow:
   `init -> collect -> match -> report -> dashboard`.
2. Install docs prefer `uv` and include mirror-friendly examples such as
   `UV_DEFAULT_INDEX=https://pypi.tuna.tsinghua.edu.cn/simple`, without writing
   mirror URLs into `uv.lock`.
3. Docs explicitly say MVP sources are RSS/RSSHub-compatible public feeds and
   GDELT; Instagram/TikTok/X/Xiaohongshu scraping, login cookies,
   proxy/account pools, CAPTCHA bypass, paywall bypass, and private data
   collection are out of scope.
4. Scoring docs include formula, windows, label order, `source_weight`,
   `collected_at`, stable first-seen, and known limits.
5. Data-retention docs explain `clean-old-data`, explicit matcher-row cleanup,
   stable `entity_first_seen`, and that `entity_first_seen` is not pruned while
   `last_seen_at` may refer to pruned item history.
6. Dashboard docs state read-only/local-only behavior, no collection on
   import/refresh, mention-count semantics rather than heat-score ranking, and
   no authentication if the user binds beyond `127.0.0.1`.
7. Repository hygiene docs/checklist prevent committing generated runtime data,
   SQLite sidecars, `.codegraph` DB files, browser profiles, cookies, secrets,
   reports, build artifacts, or mirror URLs in `uv.lock`.
8. CI/package readiness includes tests, ruff, locked uv sync, wheel/sdist build,
   installed wheel smoke for CLI and packaged templates, and optional dashboard
   extra resolution/import smoke.
9. GitHub templates/docs are appropriate but not overbuilt for an MVP.
10. The plan should not require implementing social scraping/connectors in
    Stage 6.

Return findings ordered by severity:

- Critical
- Important
- Minor

End with one of:

- Approved for Stage 6 implementation
- Approved after fixes
- Do not proceed
