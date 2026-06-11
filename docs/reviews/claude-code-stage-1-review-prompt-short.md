# Claude Code Stage 1 Focused Review Prompt

Review Stage 1 of `/home/ubuntu/fashion-radar`.

Focus files:

- `pyproject.toml`
- `README.md`
- `configs/*.example.yaml`
- `src/fashion_radar/settings.py`
- `src/fashion_radar/cli.py`
- `src/fashion_radar/models/*.py`
- `src/fashion_radar/extract/text.py`
- `src/fashion_radar/utils/*.py`
- `tests/*.py`

Stage 1 should include only project skeleton, config validation, models, text/date helpers, and CLI `init`/`doctor`.

Do not suggest Stage 2+ implementation unless needed to fix a Stage 1 bug.

Return concise findings:

- Critical
- Important
- Minor
- Recommendation: Approved for Stage 2 / Approved after fixes / Do not proceed

