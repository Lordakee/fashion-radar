# opencode Stage 260 Code Review

Reviewer: opencode (GLM 5.2 max), fallback reviewer after the local primary review route was unavailable
Stage: 260 (ROW ONE daily site)
Scope: uncommitted Stage 260 working-tree diff from base `7e56afe9837899cac98be057231872ad246052ac`

## Verdict

Accept.

All Stage 260 requirements are met, prior plan-review concerns are addressed,
the change stays inside the stage boundary, and the verification performed is
sufficient for this node.

## Critical Findings

None.

## Important Findings

None.

## Minor Findings

- `src/fashion_radar/cli.py`: `row-one serve --dry-run` prints the access
  message without validating `--site-dir`. This is consistent with "print URL
  without serving" semantics and is non-blocking.
- `src/fashion_radar/cli.py`: `row-one schedule` supports `cron` and `systemd`
  but no `github-actions` mode. The spec and plan only require cron and systemd,
  so this is parity awareness only.
- `src/fashion_radar/workflows.py`: the recent-items SQL query is duplicated
  between the daily HTML report path and ROW ONE generation. This is acceptable
  for two distinct outputs and can be considered later.
- `src/fashion_radar/row_one/templates.py`: the defensive section-title fallback
  constructs a localized text object via `type(edition.summary)(...)`. It works
  and is effectively unreachable with the default sections, but is slightly
  unusual style.

## Requirement Fit

- ROW ONE static generator is added and builds from existing `DailyReport` data
  and local SQLite recent items.
- `row-one build`, `row-one serve`, and `row-one schedule` are wired through the
  Typer sub-app.
- Static `index.html`, `details/*.html`, `assets/row-one.css`,
  `assets/row-one.js`, `data/edition.json`, and `.row-one-site` are emitted
  under the configurable output directory.
- Deterministic bilingual UI/fallback copy is implemented without translation
  services or LLM calls.
- Default serving stays on `127.0.0.1`; explicit `0.0.0.0` serving prints LAN
  guidance and a no-auth warning.
- 04:00 schedule snippets run `fashion-radar run` first, then
  `fashion-radar row-one build --latest-only` with one shared `AS_OF` and shared
  environment.
- `--latest-only` cleanup is bounded to known generated children and refuses
  unmarked generated-looking directories.
- Non-ASCII and long headlines produce bounded ASCII slug/hash detail paths that
  are safe as static filenames and served URLs.
- Unsafe URLs are omitted from links and dynamic HTML is escaped.

## Prior Plan-Review Concerns

Resolved:

- Children-only cleanup and preservation of unrelated files.
- Two-step refresh order for scheduled ROW ONE builds.
- Non-empty deterministic bilingual fallback copy.
- Collision-resistant detail paths.
- opencode fallback review path after Claude Code unavailability.
- Pinned temporary config/data/report directories in CLI build tests.
- Per-section story caps, default `reports/row-one/site` path, threaded serve
  smoke tests, default `127.0.0.1` host, and CSS/JS in Python strings.

## Boundary Compliance

The implementation stays inside the Stage 260 boundary. The ROW ONE package
performs no fetching, scraping, connector execution, platform API calls,
translation, LLM calls, paid API usage, deployment, demand proof, platform
coverage verification, or compliance-review product work. The server only
serves a local directory. Source attribution is preserved in stories, evidence,
and detail pages.

## Verification Sufficiency

The verification performed is sufficient for this node:

- `git diff --check`: passed
- `uv --no-config run --frozen pytest -q`: `1665 passed`
- `uv --no-config run --frozen ruff check .`: passed
- `uv --no-config run --frozen ruff format --check .`: `172 files already formatted`
- `UV_NO_CONFIG=1 uv lock --check`: passed
- `uv --no-config run --frozen python scripts/check_release_hygiene.py --repo-root .`: passed

## Recommended Next Action

Proceed to the next stage. No fixes are required for this node.
