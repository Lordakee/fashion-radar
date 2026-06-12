# Stage 12 Source-Pack Quality Design

## Goal

Improve the quality of daily Fashion Radar input signals by adding a local
source-pack lint command, expanding the public fashion source pack with
additional bounded GDELT coverage lanes, and documenting how users can tune
source packs before running collection.

Stage 12 is about source quality and coverage inside the configured source set.
It is not a product-facing compliance, audit, or policy-review feature.

## Non-Goals

Stage 12 does not implement:

- Instagram, TikTok, X/Twitter, Xiaohongshu/RedNote, Reddit, Pinterest, or
  other platform connectors.
- Web scraping, crawler development, browser automation, Playwright, Selenium,
  MCP platform scraping servers, platform search, platform login/session
  handling, cookie handling, account automation, proxies, proxy pools,
  fingerprint evasion, CAPTCHA bypass, rate-limit bypass, access-control
  bypass, paywall bypass, or private data collection.
- Official or unofficial social platform APIs.
- Instructions for obtaining platform exports from Instagram, TikTok,
  X/Twitter, Xiaohongshu/RedNote, Reddit, Pinterest, or similar platforms.
- Raw comments, full post bodies, DMs, account IDs, follower lists, profile
  internals, images, videos, media downloading, or reposting.
- Google News RSS or any new source type.
- New database tables, migrations, source-health schemas, dashboard views, or
  report semantics.
- LLM scoring, embeddings, vector databases, image recognition, or paid service
  requirements.
- A user-facing compliance review, audit workflow, safety workflow, or approval
  UI.

The feature must stay local, read-only for linting, and scoped to existing
source configuration files.

## Recommended Approach

Add a focused `fashion_radar.source_packs` module that reads a source YAML file,
validates it through the existing strict `load_source_config()` path, and then
returns structured findings about source-pack quality.

Keep structural validation and linting separate:

- `load_source_config()` remains the strict schema loader.
- `source_packs.py` adds advisory and CI-friendly diagnostics.
- `fashion-radar source-pack-lint PATH` exposes the diagnostics without
  collecting sources, opening SQLite, creating directories, or making network
  calls.

Expand `configs/source-packs/fashion-public.example.yaml` conservatively by
adding GDELT lanes for important fashion information categories that are sparse
in direct RSS coverage: runway, retail/resale, footwear, handbags/accessories,
creative-director moves, designer-brand momentum, and beauty/fashion crossover.
Keep the existing RSS feeds and keep public-pack RSS article extraction
disabled.

## Public Interface

Add one flat Typer command:

```bash
fashion-radar source-pack-lint configs/source-packs/fashion-public.example.yaml
fashion-radar source-pack-lint configs/source-packs/fashion-public.example.yaml --format json
fashion-radar source-pack-lint configs/source-packs/fashion-public.example.yaml --strict
```

Options:

- `PATH`: source YAML or source-pack YAML file to lint.
- `--format table|json`: human-readable table by default, stable JSON for CI.
- `--strict`: treat warnings as failures. Errors always fail.

Default exit behavior:

- Exit `0` when there are no lint errors.
- Exit `1` when structural config loading fails or lint errors are present.
- Exit `1` under `--strict` when warnings are present.
- Informational findings do not fail unless they are promoted in a future stage.

## Lint Findings

Stage 12 should produce structured findings with:

- `severity`: `error`, `warning`, or `info`.
- `code`: stable machine-readable code.
- `message`: concise user-facing explanation.
- `source_name`: optional source name.
- `field`: optional source field.

Required Stage 12 checks:

- `invalid_config`: source YAML cannot be read, parsed, or loaded through
  `load_source_config()`.
- `duplicate_source_name`: duplicate normalized source names. This is an error
  because source health and run logs are keyed by source identity.
- `empty_enabled_pack`: no enabled sources are present. This is an error because
  collection would have no active inputs.
- `duplicate_source_target`: duplicate normalized RSS/RSSHub feed URLs.
- `duplicate_gdelt_query`: duplicate normalized GDELT queries.
- `missing_tags`: source has no tags.
- `disabled_source`: disabled sources are visible as informational findings.
- `implicit_weight`: the raw YAML omitted `weight`, so scoring uses the default.
- `article_extraction_enabled`: RSS/RSSHub source has article extraction
  enabled. This is informational for user configs and a local-pack quality
  reminder, not a compliance or policy check.

Summaries should include total sources, enabled sources, disabled sources,
source-type counts, tag counts, and finding counts.

Duplicate source-name, target, and query findings should report every source in
the collision group, not only the second occurrence. This keeps CI output clear
when three or more sources share the same normalized value.

## JSON Shape

JSON output should be stable and explicit:

```json
{
  "path": "configs/source-packs/fashion-public.example.yaml",
  "source_count": 16,
  "enabled_count": 16,
  "disabled_count": 0,
  "type_counts": {"gdelt": 10, "rss": 6},
  "tag_counts": {"industry_news": 4},
  "findings": [
    {
      "severity": "warning",
      "code": "missing_tags",
      "message": "Source has no tags.",
      "source_name": "Example Feed",
      "field": "tags"
    }
  ]
}
```

Do not include fetched data, source contents, account data, cookies, or runtime
collector state in the lint result.

## Data Flow

```text
source YAML file
  -> read raw YAML mapping
  -> load_source_config() structural validation
  -> local source-pack lint checks
  -> table or JSON stdout
```

The command does not call collectors, does not open the database, does not
create config/data/report directories, and does not fetch network resources.

## Source-Pack Expansion

The public source pack should continue using only:

- `rss`
- `gdelt`

RSS entries remain unchanged unless a later stage has verified live endpoints.
Stage 12 can add bounded GDELT entries with:

- `lookback_hours: 24`
- `max_records: 100`
- `rate_limit_per_second: 1.0`
- weights between `0.7` and `0.9`
- descriptive tags for category coverage

Recommended new GDELT lanes:

- runway and fashion week coverage
- designer-brand momentum, including relevant designer-brand wording
- retail and resale signals
- footwear and sneaker signals
- handbags and accessory signals
- creative-director and executive moves
- beauty/fashion crossover

Docs must describe this as configured-source coverage, not complete market or
platform coverage.

## Documentation

Add `docs/source-pack-quality.md` and update:

- `README.md`
- `docs/architecture.md`
- `docs/source-packs.md`
- `CHANGELOG.md`

Docs should explain:

- how to run `source-pack-lint`;
- what error, warning, and info severities mean;
- how to interpret duplicate names, duplicate URLs, duplicate queries, missing
  tags, disabled sources, and implicit weights;
- how users can tune tags and weights for daily fashion monitoring;
- that linting is local and does not check live feed availability;
- that source-pack scores and trends represent the configured local source set.

Do not document social scraping or platform extraction instructions.

## Testing

Add pure unit tests for the linter and CLI tests for:

- clean repository public pack has no errors;
- duplicate source names are detected case/space-insensitively;
- duplicate RSS/RSSHub targets are detected;
- duplicate GDELT queries are detected after whitespace normalization;
- missing tags are warnings;
- implicit weights are informational;
- invalid YAML/config is returned as an error result;
- JSON output is parseable and stable;
- `--strict` exits non-zero on warnings;
- the command does not create default or explicit config/data/report
  directories;
- the command does not create any `fashion-radar.sqlite` or `*.sqlite*` files;
- the command does not create collector, report, digest, or other workflow
  artifacts.

Extend config tests so the public source pack continues to load through
`load_source_config()`, has unique source names, has unique RSS URLs and GDELT
queries, uses only existing source types, keeps RSS article extraction disabled,
and provides tags on every source.

## Verification

Focused verification:

```bash
.venv/bin/python -m pytest tests/test_source_packs.py tests/test_config.py tests/test_cli.py -k "source_pack or public_fashion_source_pack" -q
.venv/bin/python -m ruff check src/fashion_radar/source_packs.py src/fashion_radar/cli.py tests/test_source_packs.py tests/test_config.py tests/test_cli.py
.venv/bin/python -m ruff format --check src/fashion_radar/source_packs.py src/fashion_radar/cli.py tests/test_source_packs.py tests/test_config.py tests/test_cli.py
```

Final verification:

```bash
git diff --check
.venv/bin/python -m pytest -q
.venv/bin/python -m ruff check .
.venv/bin/python -m ruff format --check .
uv lock --check --default-index https://pypi.org/simple
uv sync --locked --dev --check --default-index https://pypi.org/simple
UV_DEFAULT_INDEX=https://pypi.tuna.tsinghua.edu.cn/simple uv sync --frozen --dev --check
uv build --out-dir /tmp/fashion-radar-dist-stage12
```

Then run installed-wheel smoke tests for `fashion-radar source-pack-lint --help`
and JSON linting of the repository public pack before Claude Code code review.
