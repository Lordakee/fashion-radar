# Claude Code Stage 13 Code Review Prompt

You are reviewing the Stage 13 implementation for Fashion Radar. Run this as a
read-only code and documentation review. Do not edit files, do not commit, do
not call the network, do not run collectors, do not execute platform/social
tooling, do not create config/data/report directories, and do not create SQLite
or workflow artifacts.

Project: `/home/ubuntu/fashion-radar`

Use maximum reasoning effort. The invoking command should be:

```bash
claude -p --effort max < docs/reviews/claude-code-stage-13-code-review-prompt.md
```

## Goal

Stage 13 prepares Fashion Radar for future external community/social tools by
adding a sanitized local CSV/JSON handoff contract around the existing
`fashion-radar import-signals` command.

This is not a product-facing compliance review, audit workflow, safety
workflow, policy checklist, approval UI, platform connector, platform search
tool, scraper, crawler, browser automation flow, or account workflow.

## Plan Review Status

- Initial plan review: `docs/reviews/claude-code-stage-13-plan-review.md`
  returned `Not approved` with no Critical and 3 Important findings.
- The plan was updated for stricter schema assertions, isolated installed-wheel
  smoke, and developer-operations/runtime separation.
- Rereview: `docs/reviews/claude-code-stage-13-plan-rereview.md` returned
  `Approved for Stage 13 implementation` with no Critical or Important
  findings.

## Files Changed

Created:

- `docs/community-signal-import.md`
- `examples/community-signals.example.csv`
- `examples/community-signals.example.json`
- `schemas/community-signals.schema.json`
- `tests/test_community_signal_import_contract.py`
- `docs/superpowers/specs/2026-06-12-stage-13-community-signal-import-design.md`
- `docs/superpowers/plans/2026-06-12-stage-13-community-signal-import-plan.md`
- `docs/reviews/claude-code-stage-13-plan-review-prompt.md`
- `docs/reviews/claude-code-stage-13-plan-review.md`
- `docs/reviews/claude-code-stage-13-plan-rereview.md`
- `docs/reviews/claude-code-stage-13-code-review-prompt.md`

Modified:

- `README.md`
- `CHANGELOG.md`
- `docs/architecture.md`
- `docs/manual-signal-import.md`
- `docs/source-boundaries.md`

No production Python module, collector, source model, DB schema, dashboard,
report renderer, dependency declaration, lockfile, or source pack was changed.

## Implemented Behavior

- Added importable CSV and JSON examples for sanitized external-tool community
  signal handoff.
- Added a strict static JSON schema with:
  - top-level array or object-with-`items` forms;
  - `$ref` wiring to `#/$defs/communitySignal`;
  - required `url`, `title`, and `published_at`;
  - `additionalProperties: false` on the wrapper object and item object;
  - `source_weight` bounded to greater than `0` and less than or equal to `5`;
  - no raw/private/media/account/session/token fields.
- Added focused tests proving examples load through the existing
  `load_manual_signal_rows()` parser and that `import-signals --dry-run`
  validates both examples without creating config/data/report directories,
  SQLite files, or report/digest artifacts.
- Added docs explaining that this is a local handoff contract layered on manual
  import, not a connector or source-acquisition guide.

## Explicit Out Of Scope

Please check that Stage 13 did not add or document:

- Instagram, TikTok, X/Twitter, Xiaohongshu/RedNote, Reddit, Pinterest, Discord,
  Telegram, WeChat, or other platform connectors
- web scraping, crawler development, browser automation, Playwright, Selenium,
  MCP platform scraping servers, account automation, or platform search
- login cookies, account/session files, browser profiles, tokens, credentials,
  proxies, proxy pools, fingerprint evasion, CAPTCHA bypass, rate-limit bypass,
  access-control bypass, or paywall bypass
- official or unofficial social platform APIs
- instructions for obtaining platform exports from social platforms or
  communities
- raw comments, full post bodies, DMs, private data, account IDs, follower
  lists, profile URLs, images, videos, media downloading, reposting, or archive
  redistribution
- Google News RSS or any new source type
- complete source coverage, platform-wide coverage, community-wide coverage,
  market-wide trend proof, verified demand outside the configured source set,
  real-time social monitoring, or top social trends
- LLM scoring, embeddings, vector databases, image recognition, paid service
  requirements, or sentiment analysis
- DB migrations, persistent adapter tables, source-health changes, collector
  changes, dashboard changes, report semantics changes, or network calls
- a product-facing compliance review, audit workflow, safety workflow, approval
  UI, policy checklist, or legal review feature

## Verification Already Run

Focused RED:

```text
.venv/bin/python -m pytest tests/test_community_signal_import_contract.py -q
5 failed as expected because examples/schema did not exist yet.
```

Focused GREEN:

```text
.venv/bin/python -m pytest tests/test_community_signal_import_contract.py -q
5 passed in 0.36s
```

Full verification:

```text
git diff --check
passed

.venv/bin/python -m pytest -q
283 passed in 6.73s

.venv/bin/python -m ruff check .
All checks passed!

.venv/bin/python -m ruff format --check .
73 files already formatted

uv lock --check --default-index https://pypi.org/simple
Resolved 84 packages in 3ms

uv sync --locked --dev --check --default-index https://pypi.org/simple
Would make no changes

UV_DEFAULT_INDEX=https://pypi.tuna.tsinghua.edu.cn/simple uv sync --frozen --dev --check
Would make no changes

uv build --out-dir /tmp/fashion-radar-dist-stage13
Successfully built sdist and wheel

codegraph status
Index is up to date
```

Installed-wheel smoke:

```text
Installed just-built wheel into a fresh temp venv using the Tsinghua mirror.
Ran outside the source checkout with only copied example files.
Unset PYTHONPATH.
Set explicit temp FASHION_RADAR_CONFIG_DIR, FASHION_RADAR_DATA_DIR, and
FASHION_RADAR_REPORTS_DIR.
Ran import-signals --help.
Ran dry-run for copied CSV example: Validated 2 manual signal rows.
Ran dry-run for copied JSON example: Validated 2 manual signal rows.
Confirmed no temp config/data/report dirs, SQLite files, or report/digest
artifacts were created.
```

Documentation/scope grep:

```text
rg -n "scraper|crawler|Playwright|Selenium|cookie|session|token|proxy|CAPTCHA|fingerprint|rate-limit bypass|platform-wide|market-wide|verified demand|top social trend|real-time social monitoring|source-acquisition|platform export" docs/community-signal-import.md docs/manual-signal-import.md docs/source-boundaries.md docs/architecture.md README.md CHANGELOG.md
```

Observed matches were negative boundary wording or existing project boundary
language:

- `docs/community-signal-import.md`: source-acquisition guide, cookie/session/token
  exclusion, account/private material exclusion.
- `docs/manual-signal-import.md`: existing cookie/private-data exclusion and
  source-acquisition boundary.
- `docs/source-boundaries.md`: source-acquisition boundary, README requirements
  requiring no platform export instructions, and existing warning that trend
  deltas are not verified demand.
- `README.md`: existing generated-output/account-session artifact boundary.

No positive capability claim for platform-wide, market-wide, verified demand,
top social trend, or real-time social monitoring was added.

## Review Questions

Please focus on:

1. Whether the implementation matches the approved Stage 13 design and plan.
2. Whether examples and schema are sufficient for external tools to target the
   local handoff contract.
3. Whether the schema/runtime distinction is clear: schema strict for external
   tool outputs, runtime importer still backward-compatible for manual imports.
4. Whether tests prove examples load through the real importer and dry-run
   creates no project artifacts.
5. Whether docs avoid source-acquisition instructions and platform-wide or
   market-wide claims.
6. Whether any production code change was accidentally introduced.
7. Whether generated files, tokens, cookies, local SQLite DBs, build artifacts,
   `.codegraph`, `.venv`, or account/session artifacts are at risk of being
   committed.

## Response Format

Start with one of:

- `Approved for Stage 13 commit/push`
- `Not approved`

Then list findings in this format:

- `Critical:` issues that must be fixed before commit/push.
- `Important:` issues that should be fixed before commit/push.
- `Minor:` optional improvements.

If approved, still list any Minor improvements. If not approved, be specific
about the exact file/section and the change needed.
