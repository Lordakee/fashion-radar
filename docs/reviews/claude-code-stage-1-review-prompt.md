# Claude Code Stage 1 Code Review Prompt

You are Claude Code reviewing Fashion Radar after Stage 1 implementation.

Repository: `/home/ubuntu/fashion-radar`

Commit under review:

- `2e9fa82 feat: scaffold fashion radar stage 1`

Stage 1 requirements:

- GitHub-ready Python project skeleton.
- `pyproject.toml`, `uv.lock`, README, LICENSE, `.gitignore`, `.env.example`, `.pre-commit-config.yaml`, CI.
- Mirror-based dependency installation guidance.
- Sample YAML configs for sources, entities, and scoring.
- Pydantic config models and validation.
- Google News RSS rejected in `v0.1.0`.
- Duplicate alias and unsafe alias validation.
- UTC date parsing helpers.
- Text normalization and alias regex helpers.
- Basic item/entity/source/report models.
- Typer CLI with `init` and `doctor`.
- `python -m fashion_radar --help` works.
- Tests for config/model/text/date/CLI skeleton.
- No database, collectors, scoring, reports, Streamlit, or social scraping implementation in Stage 1.

Fresh local verification already run:

```text
.venv/bin/python -m pytest -q
18 passed

.venv/bin/python -m ruff check .
All checks passed

.venv/bin/python -m ruff format --check .
19 files already formatted

UV_DEFAULT_INDEX=https://pypi.tuna.tsinghua.edu.cn/simple uv sync --dev
success
```

Please review:

1. Does implementation satisfy Stage 1 requirements?
2. Are there correctness bugs or future data-integrity risks?
3. Are config validations too weak or too strict for Stage 1?
4. Are source/compliance boundaries preserved?
5. Are tests meaningful and sufficient for this stage?
6. Are there issues to fix before Stage 2?

Return findings ordered by severity:

- Critical
- Important
- Minor

End with one of:

- Approved for Stage 2
- Approved after fixes
- Do not proceed

