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
UV_DEFAULT_INDEX=https://pypi.tuna.tsinghua.edu.cn/simple uv sync --dev
uv run pytest
uv run ruff check .
```

For users in mainland China or slower networks, prefer the mirror-based commands in [dependency-mirrors.md](docs/dependency-mirrors.md).

