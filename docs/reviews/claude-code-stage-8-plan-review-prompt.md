# Claude Code Stage 8 Plan Review Prompt

Review the proposed Stage 8 plan for Fashion Radar before implementation.

Repo: `/home/ubuntu/fashion-radar`
Planning baseline before latest plan fixes: `fdc7913`
Remote note: Git smart HTTP push times out in this environment, so Stage 7 and
the first Stage 8 planning draft were synced through the GitHub Git Database
API and verified by tree/content checks.

User rules:

- This review must use `--effort max`.
- This is a read-only planning review. Do not edit files, run collectors, add
  dependencies, access social platforms, scrape/crawl websites, mutate config,
  or perform network source collection. Return review findings only.
- Any Codex subagents used during implementation must use
  `reasoning_effort: "xhigh"`.
- Claude Code plan review must approve before implementation starts.
- After implementation, code must be reviewed by Claude Code before commit and
  next-stage planning.
- Dependencies/install checks should use mirrors where useful, without writing
  mirror URLs to `uv.lock`.

Stage 8 proposal:

- Design: `docs/superpowers/specs/2026-06-12-stage-8-candidate-discovery-design.md`
- Plan: `docs/superpowers/plans/2026-06-12-stage-8-candidate-discovery-plan.md`
- Main plan entry:
  `docs/superpowers/plans/2026-06-11-fashion-radar-implementation-plan.md`

Goal:

Add deterministic "Untracked Candidate Signals" so users can review observed
phrases that may warrant human review for brands, designers, products, bags,
shoes, and style terms already present in locally collected RSS/GDELT items,
without adding new source collection.

Recommended architecture:

- No schema migration in Stage 8.
- Add `src/fashion_radar/discovery/candidates.py`.
- Read existing SQLite `items` and `item_entities`.
- Extract deterministic candidate phrases from `items.title` and
  `items.summary`.
- Filter configured entity names/aliases from `entities.yaml` and accepted
  stored `item_entities` names/aliases.
- Compute current/baseline metrics using existing `collected_at` window
  semantics.
- Add report JSON/Markdown candidate section.
- Add read-only `fashion-radar candidates` CLI.
- Add dashboard tab that reads the latest generated JSON report rather than
  recomputing or writing anything on page load.

Tech stack:

- Python 3.11+
- SQLAlchemy Core
- Pydantic
- Typer
- pytest
- ruff
- uv
- Existing local SQLite workflow
- Existing optional Streamlit dashboard extra

Out of scope:

- No new source type or collector.
- No Instagram, TikTok, X/Twitter, Xiaohongshu/RedNote, Pinterest, Reddit,
  Google Trends, Google News RSS, static webpage monitoring, Playwright,
  browser automation, login cookies, account/session files, browser profiles,
  proxy pools, CAPTCHA bypass, paywall bypass, fingerprint evasion, anti-bot
  bypass, or private data collection.
- No paid APIs, hosted SaaS dependencies, LLM calls, embeddings, vector
  databases, or image recognition.
- No automatic mutation of `entities.yaml`.
- No claims that candidates are globally trending, viral, or confirmed brands.

Questions:

1. Does the Stage 8 design satisfy the user goal while preserving source and
   safety boundaries?
2. Is the no-schema deterministic approach appropriate for this repo?
3. Are the proposed file boundaries and interfaces coherent with existing
   scoring/report/dashboard patterns?
4. Are the tests in the plan sufficient and executable?
5. Are there correctness risks, data integrity risks, or missing acceptance
   criteria?
6. Is any part too broad for one stage?
7. Do the report, CLI, dashboard, README, and docs wording avoid implying
   viral, global, market-wide, or confirmed-brand/product claims?
8. Any blockers before implementation?

Return findings by severity:

- Critical
- Important
- Minor

End with exactly one of:

- Approved for Stage 8 implementation
- Approved after fixes
- Do not proceed
