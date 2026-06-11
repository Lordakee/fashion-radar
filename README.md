# Fashion Radar

Fashion Radar is a free-first, local-first fashion intelligence tool.

The goal is to collect allowed public fashion signals, match configurable fashion entities, calculate transparent heat scores, and generate daily reports and a local dashboard.

## Status

This repository is in early development. The first version focuses on:

- RSS/Atom feeds.
- GDELT metadata.
- SQLite storage.
- YAML configuration.
- Deterministic entity matching.
- Markdown/JSON reports.
- Streamlit dashboard.

## Source Boundaries

The default workflow avoids logged-in scraping, paywall bypass, CAPTCHA bypass, proxy pools, and full social-platform crawling. See [source-boundaries.md](docs/source-boundaries.md).

## Development

```bash
uv sync --locked --dev
uv run pytest
uv run ruff check .
```

For users in mainland China or slower networks, prefer the mirror-based frozen sync
commands in [dependency-mirrors.md](docs/dependency-mirrors.md). Do not regenerate the
public `uv.lock` while a mirror index is active.

Optional article text extraction uses the `article` extra:

```bash
uv sync --locked --dev --extra article
```

The core RSS/GDELT workflow does not require this extra. If `trafilatura` is not
installed, article extraction returns a conservative skipped result instead of
attempting a fallback scraper.
