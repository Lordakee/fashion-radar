# Contributing

Fashion Radar is a free-first, local-first Python project for fashion signal
monitoring. The v0.1.0 core workflow is limited to RSS/Atom,
RSSHub-compatible public feeds, and GDELT.

Do not add default social-platform scraping, login-cookie flows, proxy/account
pools, CAPTCHA bypass, paywall bypass, or private data collection.

## Setup

```bash
uv sync --locked --dev
```

Optional extras:

```bash
uv sync --locked --dev --extra article
uv sync --locked --dev --extra dashboard
```

Mirror installs are fine for local development:

```bash
UV_DEFAULT_INDEX=https://pypi.tuna.tsinghua.edu.cn/simple uv sync --frozen --dev
```

Do not commit mirror-bound URLs to `uv.lock`. See
[docs/dependency-mirrors.md](docs/dependency-mirrors.md).

## Local Workflow

```bash
uv run fashion-radar init
uv run fashion-radar doctor
uv run fashion-radar collect
uv run fashion-radar match
uv run fashion-radar report --as-of "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
uv run fashion-radar run --as-of "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
```

Dashboard:

```bash
uv sync --locked --dev --extra dashboard
uv run fashion-radar dashboard
```

## Verification

Run before opening a pull request:

```bash
uv lock --check
uv sync --locked --dev
uv run ruff check .
uv run ruff format --check .
uv run pytest
```

If packaging, templates, dashboard, or optional dependencies changed, also run
the relevant smoke checks from
[docs/github-upload-checklist.md](docs/github-upload-checklist.md).

## Connector Rules

- Core v0.1.0 sources are RSS/Atom, RSSHub-compatible feeds, and GDELT.
- Google News RSS is not a default v0.1.0 source.
- Future connectors must be disabled by default unless they are core-approved.
- Source changes must preserve attribution, conservative timeouts, rate limits,
  and robots handling for article extraction.
- Reports should store snippets/metadata and links, not republished full
  articles.

## Data Hygiene

Do not commit:

- `.venv/`
- `build/`
- `dist/`
- local SQLite databases or sidecars
- generated reports
- caches
- cookies
- tokens
- browser profiles
- account/session files
- private configs or private source exports

## Docs And Changelog

Update README/docs and `CHANGELOG.md` for user-visible behavior, CLI/config
changes, source-boundary changes, packaging changes, and security/privacy
changes.

Useful references:

- [docs/source-boundaries.md](docs/source-boundaries.md)
- [docs/scoring.md](docs/scoring.md)
- [docs/data-retention.md](docs/data-retention.md)
- [docs/REVIEW_PROTOCOL.md](docs/REVIEW_PROTOCOL.md)
- [SECURITY.md](SECURITY.md)
- [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md)
