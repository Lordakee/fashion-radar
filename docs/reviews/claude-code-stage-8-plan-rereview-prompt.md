# Claude Code Stage 8 Plan Rereview Prompt

Review the updated Stage 8 plan for Fashion Radar after the previous Claude
Code review returned `Approved after fixes`.

Repo: `/home/ubuntu/fashion-radar`

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

Updated planning files:

- Design: `docs/superpowers/specs/2026-06-12-stage-8-candidate-discovery-design.md`
- Plan: `docs/superpowers/plans/2026-06-12-stage-8-candidate-discovery-plan.md`
- Previous review:
  `docs/reviews/claude-code-stage-8-plan-review.md`

Stage 8 goal:

Add deterministic "Untracked Candidate Signals" so users can review observed
phrases that may warrant human review for brands, designers, products, bags,
shoes, and style terms already present in locally collected RSS/GDELT items,
without adding new source collection.

Architecture and tech stack:

- No schema migration in Stage 8.
- Python 3.11+, SQLAlchemy Core, Pydantic, Typer, pytest, ruff, uv.
- Add `src/fashion_radar/discovery/candidates.py`.
- Read existing local SQLite `items` and `item_entities`.
- Extract deterministic candidate phrases from `items.title` and
  `items.summary`.
- Filter configured entity names/aliases from `entities.yaml` and stored
  `item_entities` names/aliases where
  `item_entities.confidence >= scoring.min_match_confidence`.
- Compute current/baseline metrics using existing `collected_at` semantics.
- Add report JSON/Markdown candidate section.
- Add read-only `fashion-radar candidates` CLI.
- Add dashboard tab that reads the latest generated JSON report rather than
  recomputing or writing anything on page load.

Fixes made after prior review:

- Added candidate-specific thresholds:
  `rising_growth_ratio`, `review_min_current_mentions`, and
  `review_min_distinct_sources`.
- Defined label contracts for `new_candidate`, `rising_candidate`, and
  `review`, and added planned tests for all three labels.
- Defined the output inclusion floor as the `review_*` threshold pair.
- Strengthened read-only CLI requirements:
  check `db_path.exists()` before creating any engine, avoid parent directory or
  DB creation, use read-only SQLite URI for existing DBs, inspect schema without
  `initialize_schema()`, and fail non-mutating on incompatible schema.
- Added planned tests that missing DB and missing data directory are not
  created by `fashion-radar candidates`.
- Added explicit `run` acceptance test that writes a report filtered by loaded
  `entities.yaml` even when `match_stored_items` stores no matches.
- Specified stored `item_entities` filtering predicate as confidence-based,
  matching existing entity scoring. The plan explicitly does not require
  `reason == "accepted"`.
- Added planned low-confidence/high-confidence stored-entity tests.
- Strengthened serialization safety tests to exclude `content_hash`,
  `normalized_key`, DB ids, `normalized_url`, matcher reasons, raw aliases,
  `context_terms`, and raw extraction contexts from candidate JSON/Markdown.
- Defined overlap preference for `Sandy Liang Mary Jane flats` versus `Le
  Teckel bag`.
- Defined known-entity token normalization for possessives, hyphens, and
  ampersands through `normalize_alias_key()` and token-span matching.
- Added single-token extraction and aggregate-threshold tests.
- Documented dashboard latest-report filename sort assumption and added
  malformed JSON error-metadata behavior.
- Replaced hard-coded wheel filename in package smoke with a wheel glob.

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

Please rereview only the updated Stage 8 design and plan for implementation
readiness.

Questions:

1. Do the updates fully resolve the previous Important findings?
2. Are the candidate thresholds and label contracts now unambiguous?
3. Is the read-only `candidates` CLI plan sufficient to prevent DB creation,
   schema mutation, or config mutation?
4. Is the `run` integration acceptance test strong enough to prove
   `entity_config` is passed into candidate report generation?
5. Are the stored-entity filtering predicate and tests precise enough?
6. Are the serialization safety tests sufficient for candidate output?
7. Are any remaining Stage 8 blockers present?

Return findings by severity:

- Critical
- Important
- Minor

End with exactly one of:

- Approved for Stage 8 implementation
- Approved after fixes
- Do not proceed
