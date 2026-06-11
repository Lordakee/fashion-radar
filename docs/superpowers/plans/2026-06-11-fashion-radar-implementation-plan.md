# Fashion Radar Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a GitHub-ready free-first Fashion Radar MVP that collects allowed public fashion signals, identifies tracked entities, computes heat changes, and outputs daily reports plus a Streamlit dashboard.

**Architecture:** A local Python application with CLI commands, YAML configuration, SQLite persistence, deterministic entity matching, deterministic heat scoring, Markdown/JSON report generation, and a read-only Streamlit dashboard. Core collectors use RSS and GDELT first; Google News RSS is excluded from v0.1.0, while Google Trends, Reddit, Pinterest, TikTok, Instagram, X, and Xiaohongshu remain opt-in future connectors with explicit risk labels.

**Tech Stack:** Python 3.11+, uv, Typer, Pydantic v2, SQLAlchemy 2.x, feedparser, httpx, trafilatura, robotexclusionrulesparser, PyYAML, pandas, Streamlit, platformdirs, python-dateutil, tenacity, pytest, ruff, SQLite.

---

## Stage 0: Planning And Claude Code Review

**Status:** Completed. Initial Claude Code plan review is recorded in
`docs/reviews/claude-code-plan-review.md` and
`docs/reviews/claude-code-plan-rereview.md`.

**Files:**

- Create: `docs/PROJECT_BRIEF.md`
- Create: `docs/superpowers/specs/2026-06-11-fashion-radar-design.md`
- Create: `docs/superpowers/plans/2026-06-11-fashion-radar-implementation-plan.md`
- Create: `docs/reviews/claude-code-plan-review-prompt.md`
- Create: `docs/reviews/claude-code-plan-review.md`

**Steps:**

- [ ] Write project brief, design spec, and implementation plan.
- [ ] Ask Claude Code to review objective, stack, architecture, source boundaries, and staged implementation.
- [ ] Record Claude Code review in `docs/reviews/claude-code-plan-review.md`.
- [ ] Apply plan changes if Claude Code finds critical or important issues.
- [ ] Ask the user for approval before writing implementation code.

## Stage 1: Repository Skeleton And Core Models

**Status:** Completed. Stage 1 code review and fixes are recorded in
`docs/reviews/claude-code-stage-1-review.md`.

**Goal:** Create the Python project foundation and deterministic model/config layer.

**Planned files:**

```text
fashion-radar/
  README.md
  LICENSE
  pyproject.toml
  .env.example
  .pre-commit-config.yaml
  .gitignore
  .github/workflows/ci.yml
  configs/sources.example.yaml
  configs/entities.example.yaml
  configs/scoring.example.yaml
  data/README.md
  reports/README.md
  src/fashion_radar/__init__.py
  src/fashion_radar/__main__.py
  src/fashion_radar/cli.py
  src/fashion_radar/settings.py
  src/fashion_radar/models/__init__.py
  src/fashion_radar/models/item.py
  src/fashion_radar/models/entity.py
  src/fashion_radar/models/source.py
  src/fashion_radar/models/report.py
  src/fashion_radar/extract/__init__.py
  src/fashion_radar/extract/text.py
  src/fashion_radar/utils/__init__.py
  src/fashion_radar/utils/paths.py
  src/fashion_radar/utils/dates.py
  tests/test_config.py
  tests/test_models.py
  tests/test_text.py
  tests/test_dates.py
```

**TDD tasks:**

- [ ] Write failing tests for loading source/entity/scoring YAML into Pydantic models.
- [ ] Implement config loading.
- [ ] Write failing tests for normalized text matching primitives.
- [ ] Implement text normalization helpers.
- [ ] Write failing tests for normalized item/entity models.
- [ ] Implement models.
- [ ] Write failing tests that all model timestamps normalize to UTC.
- [ ] Implement UTC date parsing helpers.
- [ ] Write failing tests for duplicate entity aliases and unsafe common aliases.
- [ ] Implement config validation for duplicate aliases and unsafe aliases.
- [ ] Write failing tests for CLI `--help`, `init`, and `doctor`.
- [ ] Implement minimal Typer CLI skeleton.
- [ ] Run `pytest` and `ruff`.
- [ ] Ask Claude Code to review Stage 1 code.
- [ ] Fix review findings before Stage 2.

**Acceptance criteria:**

- `pytest` passes for config/model/text tests.
- `ruff check .` passes.
- Sample YAML loads without network access.
- `fashion-radar init` creates local config/report/data directories without secrets.
- Malformed entity YAML fails with helpful errors.
- Timestamps are stored as UTC-aware values.
- Claude Code review has no unfixed critical or important findings.

## Stage 2: SQLite Storage And Entity Matching

**Status:** Completed. Stage 2 plan and code reviews are recorded in
`docs/reviews/claude-code-stage-2-plan-review.md` and
`docs/reviews/claude-code-stage-2-code-review.md`.

**Goal:** Persist collected items and attach matched entities through deterministic alias matching.

**Dependency decision:** Move `sqlalchemy>=2.0.36` into core project
dependencies at the start of Stage 2 because SQLite persistence becomes part of
the MVP workflow in this stage. Keep `feedparser`, `httpx`, `trafilatura`,
`robotexclusionrulesparser`, `tenacity`, `pandas`, and `streamlit` optional
until their collector/dashboard stages.

**Matcher contract:** `alias_pattern()` is only a case-insensitive literal
word-boundary primitive. Stage 2 must add the context gate that decides whether
an alias match is accepted. Any alias whose normalized key is single-word or in
`UNSAFE_COMMON_ALIASES` must require at least one configured `context_terms`
match in the same item, unless the alias is explicitly marked
`safe_single_word: true` with a non-empty `reason`. Keep
`UNSAFE_COMMON_ALIASES` as a small, test-covered code constant seeded with
clearly ambiguous phrases such as `row`, `gap`, `coach`, `boss`, `pink`,
`ballet flat`, and `ballet flats`. Multi-word aliases that normalize to an
unsafe phrase, or include an unsafe brand-like token and can plausibly appear as
ordinary language, still need context tests. Product aliases with a
`parent_brand` should match only when the item also contains the parent brand
alias or one of that product entity's own narrow context terms. Generic shared
tokens are not enough. This prevents `the row`, `ballet flats`, `Coach`, `Gap`,
`Boss`, and `Pink` from becoming accepted matches from generic phrases alone.

**Deduplication contract:** URL normalization must have an explicit initial
tracking-parameter policy: remove `utm_*`, `fbclid`, `gclid`, `msclkid`,
`igshid`, `mc_cid`, `mc_eid`, `ref`, `ref_src`, and empty query parameters;
lowercase scheme/host; remove fragments; and keep non-tracking query
parameters. Content hashes should be computed from normalized title, publication
date, source, and summary/snippet only, not full article text.

**Schema evolution:** Stage 2 should create a tiny `schema_metadata` table with a
single integer schema version. Full Alembic migrations remain deferred, but the
database should fail clearly if a future incompatible schema version is found.

**Planned files:**

```text
src/fashion_radar/db/__init__.py
src/fashion_radar/db/engine.py
src/fashion_radar/db/schema.py
src/fashion_radar/db/repositories.py
src/fashion_radar/extract/dictionary.py
src/fashion_radar/extract/entities.py
src/fashion_radar/utils/hashing.py
tests/test_db.py
tests/test_matcher.py
tests/test_dedupe.py
```

**TDD tasks:**

- [ ] Move SQLAlchemy from optional `storage` extra to core dependencies, update `uv.lock` without mirror env vars, and verify `uv.lock` contains no mirror-bound URLs.
- [ ] Write failing tests for schema initialization.
- [ ] Implement SQLAlchemy 2.x SQLite schema initializer.
- [ ] Write failing tests for a `schema_metadata` table with schema version `1` and a clear failure for unsupported future versions.
- [ ] Implement the lightweight schema version guard.
- [ ] Write failing tests for item upsert and exact URL deduplication.
- [ ] Implement item upsert.
- [ ] Write failing tests for URL normalization, explicit tracking parameter stripping, canonical title/date deduplication, and content hash deduplication.
- [ ] Implement normalized URL and hash helpers.
- [ ] Write failing tests for alias matching across brand, celebrity, designer, product, category, and trend entities.
- [ ] Implement deterministic matcher with case-insensitive word boundaries, match confidence, and explicit accepted/rejected match reason fields.
- [ ] Write failing tests proving common phrases such as `front row seat`, `the row after the show`, `coach the team`, `mind the gap`, `boss said`, `pink room`, and generic `ballet flats` do not become accepted entity matches unless safe alias settings or context terms support them.
- [ ] Write failing tests proving positive fashion examples still match, such as `The Row Margaux handbag`, `Miu Miu ballet flats`, `Zendaya red carpet`, and `Jonathan Anderson creative director`.
- [ ] Write failing tests proving context terms are matched case-insensitively and do not rely on substring-only behavior.
- [ ] Implement context-gated deterministic matcher.
- [ ] Write failing tests for storing item/entity matches.
- [ ] Implement match persistence.
- [ ] Write failing tests that stored items keep source name, source URL, publication time, title, summary/snippet, and no full article body.
- [ ] Implement storage fields needed for attribution and future report snippets without storing republished full articles.
- [ ] Run `pytest` and `ruff`.
- [ ] Ask Claude Code to review Stage 2 code and Stage 3 plan.
- [ ] Fix review findings before Stage 3.

**Acceptance criteria:**

- SQLite database can be initialized at any configured filesystem path; tests use temp directories only as isolated fixtures.
- Duplicate URLs do not create duplicate items.
- URL normalization strips the explicit initial tracking-parameter list and supports canonical hash-based deduplication.
- Alias matching handles case, punctuation, simple whitespace differences, word boundaries, duplicate alias validation, confidence, and accepted/rejected reasons.
- Common-term false positives are tested and blocked by context gates.
- Attribution fields needed by reports are persisted, and Stage 2 storage does not introduce full-article republication.
- A lightweight schema version guard exists even though full migrations are deferred.
- `uv.lock` remains free of mirror-bound URLs after adding SQLAlchemy to core dependencies.
- Claude Code review has no unfixed critical or important findings.

## Stage 3: Public Collectors

**Status:** Next stage. Submit this plan to Claude Code before implementation.

**Goal:** Collect stable public data from RSS and GDELT, with article extraction limited to allowed pages. Google News RSS is not included in v0.1.0.

**Dependency decision:** Move `feedparser`, `httpx`,
`robotexclusionrulesparser`, and `tenacity` into core dependencies at the start
of Stage 3 because RSS/GDELT collection becomes part of the MVP workflow.
`trafilatura` may remain optional until the article extraction wrapper is
implemented in this stage; if article extraction lands in Stage 3, move
`trafilatura` into core at that point. Keep `pandas` and `streamlit` optional
until report/dashboard stages.

**Storage concurrency boundary:** Stage 3 collectors must write through
`ItemRepository` in a single local process. Do not introduce parallel database
writers in Stage 3. If later stages add concurrent collectors, first replace the
Stage 2 SELECT-then-insert upsert path with SQLite `ON CONFLICT DO UPDATE` or a
tested retry around uniqueness conflicts.

**Schema evolution decision:** Stage 3 bumps the lightweight schema version from
`1` to `2`. Because full Alembic migrations remain deferred, Stage 3 must
implement and test one explicit migration path: a version-1 database gets the
new collector status tables created and then `schema_metadata.version` is
updated to `2`. Future versions still fail clearly.

**Collector contracts:** `collectors/base.py` owns a minimal interface:
collectors receive one enabled `SourceDefinition` plus settings, return
normalized `CollectedItem` objects and a structured run status, and never write
directly to SQLite. A coordinator or CLI stage persists items through
`ItemRepository`. `utils/http.py` owns the descriptive User-Agent, timeouts,
bounded retries, and per-domain politeness delays used by RSS, article
extraction, and GDELT clients.

**GDELT query contract:** Use the public GDELT Doc API endpoint
`https://api.gdeltproject.org/api/v2/doc/doc` with JSON article-list responses.
Each `gdelt` source uses `SourceDefinition.query` as the query string, defaults
to a 24-hour lookback window, and has configurable `max_records`,
`lookback_hours`, and `rate_limit_per_second` settings under the source's
`gdelt` block. Do not derive GDELT queries from the entire entity list in Stage
3. GDELT item URLs pass through the same URL normalization and
`ItemRepository.upsert_item()` path as RSS items.

**Robots, paywalls, and politeness:** If robots.txt is unreachable, malformed,
or returns a non-200 status, the safe default is to skip article extraction for
that URL during the run. RSS feed fetching and article fetching must use
timeouts and a per-domain delay; article extraction must never bypass paywalls
and must store snippets/metadata only.

**Config ownership:** Stage 3 settings live in `sources.yaml` and Pydantic
source models. Add nested source settings for `gdelt`, `http`, `article`, and
`health` defaults. Defaults should include a descriptive User-Agent,
`http.timeout_seconds`, `http.per_domain_delay_seconds`,
`gdelt.lookback_hours`, `gdelt.max_records`, `gdelt.rate_limit_per_second`,
`health.max_failures`, and `health.retention_hours`. Manual source-health reset
is deferred to Stage 5 CLI; until then the direct database state and retention
expiry are the only reset mechanisms.

**Planned files:**

```text
src/fashion_radar/collectors/__init__.py
src/fashion_radar/collectors/base.py
src/fashion_radar/collectors/rss.py
src/fashion_radar/collectors/gdelt.py
src/fashion_radar/collectors/article.py
src/fashion_radar/collectors/robots.py
src/fashion_radar/utils/http.py
tests/fixtures/rss/sample_feed.xml
tests/fixtures/gdelt/sample_response.json
tests/test_collectors_rss.py
tests/test_collectors_gdelt.py
tests/test_collectors_article.py
tests/test_collectors_robots.py
```

**TDD tasks:**

- [ ] Write failing tests for parsing RSS fixture items.
- [ ] Move RSS/GDELT collector dependencies into core dependencies as described above, update `uv.lock` without mirror env vars, and verify `uv.lock` contains no mirror-bound URLs.
- [ ] Write failing tests for schema version `1` to `2` migration that creates collector status tables without deleting existing items.
- [ ] Implement the lightweight Stage 3 schema migration.
- [ ] Write failing tests defining the base collector result/status interface.
- [ ] Implement `collectors/base.py`.
- [ ] Write failing tests for shared HTTP User-Agent, timeout, retry, and per-domain politeness behavior.
- [ ] Implement `utils/http.py`.
- [ ] Implement RSS collector using feedparser.
- [ ] Write failing tests for parsing GDELT fixture responses.
- [ ] Write failing tests that GDELT uses the configured source query, lookback window, max records, JSON article list mode, and the same normalized URL upsert path as RSS.
- [ ] Write failing tests for GDELT request throttling and bounded retry behavior with a default of roughly 1 request per second.
- [ ] Implement GDELT collector using httpx, descriptive User-Agent, configurable rate limit, conservative default throttle, and bounded exponential backoff.
- [ ] Write failing tests proving Google News RSS source type is rejected in v0.1.0 with a clear error pointing to future experimental support.
- [ ] Write failing tests for article extraction fallback behavior.
- [ ] Write failing tests that article extraction checks robots.txt, caches robots rules per domain within a run, and skips disallowed URLs.
- [ ] Implement robots.txt checker with per-domain run cache and trafilatura article extraction wrapper.
- [ ] Write failing tests that paywalled domains are skipped for extraction.
- [ ] Implement configurable paywalled-domain skip list.
- [ ] Add per-source run status records.
- [ ] Write failing tests for source health circuit breaker after repeated failures.
- [ ] Implement configurable unhealthy-source threshold and skip unhealthy sources until manually reset or retention window expires.
- [ ] Run `pytest` and `ruff`.
- [ ] Ask Claude Code to review Stage 3 code and Stage 4 plan.
- [ ] Fix review findings before Stage 4.

**Acceptance criteria:**

- Collectors can be tested with fixtures without live network.
- A failed source does not stop other configured sources.
- Collector run status is stored.
- Collector writes are single-process and go through `ItemRepository`.
- Stage 3 migrates schema version `1` to `2` without dropping existing items.
- Collector interfaces return items and run status without writing directly to SQLite.
- GDELT uses the configured `gdelt` source query, not the whole tracked entity list.
- Google News RSS is rejected in v0.1.0.
- Article extraction respects robots.txt.
- Article extraction skips URLs when robots.txt cannot be fetched or parsed.
- GDELT uses rate limits and retries.
- All HTTP requests use descriptive User-Agent.
- RSS and article HTTP use timeouts and per-domain politeness delays.
- robots.txt rules are cached per domain within a run.
- Repeated source failures mark a source unhealthy according to config.
- Claude Code review has no unfixed critical or important findings.

## Stage 4: Heat Scoring And Reports

**Goal:** Compute daily entity metrics and generate Markdown/JSON reports.

**Planned files:**

```text
src/fashion_radar/scoring.py
src/fashion_radar/reports.py
templates/daily_report.md.j2
tests/test_scoring.py
tests/test_reports.py
```

**TDD tasks:**

- [ ] Write failing tests for weighted mention counting.
- [ ] Implement daily metrics aggregation.
- [ ] Write failing tests for heat score status labels: new, rising, hot, stable, cooling.
- [ ] Write fixture tests comparing weak-new, stable-high-volume, and rising entities.
- [ ] Implement deterministic heat scoring.
- [ ] Write failing tests for Markdown report rendering.
- [ ] Implement Markdown report renderer with source attribution footer and short snippets only.
- [ ] Write failing tests for JSON report rendering.
- [ ] Implement JSON report renderer.
- [ ] Run `pytest` and `ruff`.
- [ ] Ask Claude Code to review Stage 4 code and Stage 5 plan.
- [ ] Fix review findings before Stage 5.

**Acceptance criteria:**

- Reports are deterministic from fixture data.
- Heat score constants come from YAML.
- Report output includes rising brands, rising products, celebrity mentions, and source health.
- Every representative item has source name, source URL, and publication time.
- Reports do not reproduce full article text.
- Claude Code review has no unfixed critical or important findings.

## Stage 5: CLI And Dashboard

**Goal:** Provide a usable local command line workflow and Streamlit dashboard.

**Planned files:**

```text
src/fashion_radar/cli.py
src/fashion_radar/dashboard.py
tests/test_cli.py
```

**TDD tasks:**

- [ ] Write failing CLI tests for `fashion-radar init`.
- [ ] Implement `init` command.
- [ ] Write failing CLI tests for `collect`, `score`, `report`, and `run` against fixture/temp data.
- [ ] Implement CLI workflow commands.
- [ ] Write failing CLI tests for helpful errors on missing config and invalid YAML.
- [ ] Implement helpful CLI errors.
- [ ] Write failing tests or command construction checks proving dashboard binds to localhost by default.
- [ ] Implement `dashboard` command that launches Streamlit on localhost by default.
- [ ] Write failing tests for `clean-old-data` command behavior.
- [ ] Implement `clean-old-data` pruning command with configurable retention days.
- [ ] Build Streamlit pages for Daily Brief, Brand Heat, Product Radar, Celebrity Style, and Source Health.
- [ ] Run `pytest`, `ruff`, and a dashboard import smoke check.
- [ ] Ask Claude Code to review Stage 5 code and GitHub-readiness plan.
- [ ] Fix review findings before packaging docs.

**Acceptance criteria:**

- A user can run `fashion-radar init`, edit sample config, run `fashion-radar run`, and open dashboard.
- CLI tests pass with temporary files.
- Dashboard imports without triggering network collection.
- Dashboard shows data staleness and source failure status.
- Claude Code review has no unfixed critical or important findings.

## Stage 6: GitHub Packaging

**Goal:** Make the repository understandable and safe to publish.

**Planned files:**

```text
README.md
docs/architecture.md
docs/source-boundaries.md
docs/review-workflow.md
docs/github-upload-checklist.md
docs/scoring.md
docs/data-retention.md
CONTRIBUTING.md
CODE_OF_CONDUCT.md
SECURITY.md
CHANGELOG.md
.github/ISSUE_TEMPLATE/bug_report.yml
.github/ISSUE_TEMPLATE/feature_request.yml
.github/pull_request_template.md
```

**Tasks:**

- [ ] Write README with installation, quickstart, examples, limitations, and source boundaries.
- [ ] Write architecture documentation.
- [ ] Write compliance and platform boundary notes.
- [ ] Write scoring formula and known limitations.
- [ ] Write data retention and cleanup documentation.
- [ ] Document expected scale limits for v0.1.0.
- [ ] Write GitHub upload checklist.
- [ ] Run full test and lint suite.
- [ ] Ask Claude Code to review final code and docs before GitHub upload.
- [ ] Fix critical and important findings.
- [ ] Prepare repository for user-controlled GitHub remote creation and push.

## Stage 7: Optional Public Source Enhancements

**Goal:** Add richer opt-in sources without weakening MVP stability.

**Candidate files:**

```text
src/fashion_radar/collectors/webpage.py
tests/test_collectors_webpage.py
```

**Tasks:**

- [ ] Ask Claude Code to review a Stage 7 plan before implementation.
- [ ] Add static webpage monitoring only for explicit URL lists.
- [ ] Add Google News RSS only as disabled-by-default experimental connector with explicit use-at-your-own-risk documentation, or keep it out.
- [ ] Add Google Trends only through official API access or keep it disabled.
- [ ] Add Reddit only with user-provided API credentials and explicit API terms documentation.
- [ ] Keep Playwright, logged-in crawling, and platform scraping out of this stage.
- [ ] Ask Claude Code to review Stage 7 code.

**Acceptance criteria:**

- Fresh clone instructions are clear.
- CI passes locally.
- No secrets, cookies, accounts, or private data are committed.
- Final Claude Code review has no unfixed critical or important findings.

## Deferred Features

These are intentionally out of MVP:

- LLM-based summarization.
- Xiaohongshu logged-in crawler automation.
- Instagram/TikTok/X logged-in scraping.
- Proxy/account management.
- SaaS integrations.
- Team authentication.
- Cloud deployment.
- Automated chat-app push.
- Image recognition for outfit/product matching.
- Playwright dynamic page rendering.
- Embedding-based semantic deduplication.
- Celery/Redis background workers.

## Claude Code Review Gate Template

At each review gate, ask Claude Code:

```text
You are reviewing Fashion Radar at the end of [STAGE].

Please check:
1. Does the implementation satisfy the stage acceptance criteria?
2. Are there correctness bugs or data integrity risks?
3. Are source boundaries and platform-risk notes honest?
4. Are tests meaningful and sufficient for this stage?
5. Is the next-stage plan safe to execute?

Return findings ordered by severity:
- Critical
- Important
- Minor

Do not rewrite the project. Focus on risks, bugs, missing tests, and unclear boundaries.
```
