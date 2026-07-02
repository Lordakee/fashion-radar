# Claude Code Stage 261 Code Review Prompt

You are the primary reviewer for Fashion Radar Stage 261.

Review the current uncommitted working tree in `/home/ubuntu/fashion-radar`.

## Stage

Stage 261: ROW ONE editorial synthesis

## Base

- Base commit: `1651e18c94c2059da2628c60929a242fc7da0ac9`
- Head: current uncommitted working tree

## Goal

Add deterministic ROW ONE editorial synthesis so the daily site organizes
information instead of only showing headlines, source snippets, and links.

Each generated story should expose:

- `editorial_takeaway`
- `signal_context`
- `reader_path`

The synthesis must be deterministic, local-report/item-derived, bilingual, and
presentation-only. It must not add scraping, platform APIs, translation, LLM
calls, paid APIs, deployment, demand proof, platform coverage verification, or
compliance-review product behavior.

## Relevant Files

- `docs/row-one.md`
- `docs/superpowers/specs/2026-07-02-stage-261-row-one-editorial-synthesis-design.md`
- `docs/superpowers/plans/2026-07-02-stage-261-row-one-editorial-synthesis-plan.md`
- `src/fashion_radar/cli.py`
- `src/fashion_radar/row_one/edition.py`
- `src/fashion_radar/row_one/models.py`
- `src/fashion_radar/row_one/server.py`
- `src/fashion_radar/row_one/templates.py`
- `tests/test_row_one_cli.py`
- `tests/test_row_one_docs.py`
- `tests/test_row_one_edition.py`
- `tests/test_row_one_render.py`

## Verification Already Run

Focused verification:

```bash
uv --no-config run --frozen pytest tests/test_row_one_edition.py tests/test_row_one_render.py tests/test_row_one_cli.py tests/test_row_one_docs.py -q
uv --no-config run --frozen ruff check src/fashion_radar/row_one src/fashion_radar/cli.py tests/test_row_one_edition.py tests/test_row_one_render.py tests/test_row_one_cli.py tests/test_row_one_docs.py
```

Result: `56 passed`; Ruff passed.

Full gate:

```bash
git diff --check
uv --no-config run --frozen pytest -q
uv --no-config run --frozen ruff check .
uv --no-config run --frozen ruff format --check .
UV_NO_CONFIG=1 uv lock --check
uv --no-config run --frozen python scripts/check_release_hygiene.py --repo-root .
```

Result before the final documentation/code polish: `1682 passed`; Ruff passed;
format check passed; lock check passed; release hygiene passed.

## Review Focus

Please review for:

- correctness of the new `RowOneStory` fields and `RowOneSectionKey` typing;
- deterministic synthesis behavior for entity, candidate, and recent-item
  stories;
- safe handling of `growth_ratio=None`;
- stable ordering for same-score top stories;
- homepage/detail rendering of bilingual synthesis with escaping preserved;
- JSON output compatibility and URL sanitization;
- `row-one serve --dry-run` validation behavior, including no port binding;
- documentation/spec/plan consistency with actual behavior;
- absence of new scraping/connectors/LLM/translation/deployment/compliance
  product features;
- test coverage quality and any missing high-risk edge cases.

## Output Format

Return one coherent review body only:

- Verdict: approve / approve with fixes / reject
- Critical findings
- Important findings
- Minor findings
- Required fixes before commit
- Optional follow-ups

Do not modify files.
