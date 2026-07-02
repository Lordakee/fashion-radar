# Claude Code Stage 261 Release Review Prompt

You are the primary release reviewer for Fashion Radar Stage 261.

Review the current uncommitted working tree in `/home/ubuntu/fashion-radar`
before commit and push.

## Stage

Stage 261: ROW ONE editorial synthesis

## Base

- Base commit: `1651e18c94c2059da2628c60929a242fc7da0ac9`
- Head: current uncommitted working tree

## Goal

Stage 261 upgrades ROW ONE from a link-forward static daily site into a
deterministic editorial briefing. It adds local, report-derived synthesis to
each generated story so the site explains the signal, local context, and reader
path without adding scraping, platform APIs, translation, LLM calls, image
generation, paid APIs, deployment, demand proof, platform coverage verification,
or compliance-review product behavior.

## Review Artifacts

- `docs/reviews/claude-code-stage-261-code-review.md`
- `docs/reviews/claude-code-stage-261-code-rereview.md`
- `docs/reviews/opencode-stage-261-plan-review.md`

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

```bash
git diff --check
uv --no-config run --frozen pytest -q
uv --no-config run --frozen ruff check .
uv --no-config run --frozen ruff format --check .
UV_NO_CONFIG=1 uv lock --check
uv --no-config run --frozen python scripts/check_release_hygiene.py --repo-root .
```

Result: `1682 passed`; Ruff passed; format check passed; lock check passed;
release hygiene passed.

## Review Focus

Please confirm:

- Stage 261 code review and rereview requirements are satisfied;
- implementation matches the design and plan;
- full release gate is sufficient before commit;
- no generated reports, local databases, build artifacts, tokens, cookies, or
  private data are staged or likely to be committed;
- no boundary violations were introduced;
- Stage 261 is ready to commit and push.

## Output Format

Return one coherent review body only:

- Verdict: approve / approve with fixes / reject
- Critical findings
- Important findings
- Minor findings
- Required fixes before commit
- Optional follow-ups

Do not modify files.
