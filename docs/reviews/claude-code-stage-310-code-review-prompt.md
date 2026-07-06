# Claude Code Review Prompt: Stage 310 Saved Text Reader

You are reviewing `/home/ubuntu/fashion-radar` after Stage 310 implementation.
Use read-only review. Do not edit files.

## Goal

Add a ROW ONE generated-site detail-page saved text reader so users can scan
locally saved article content in-page instead of relying only on outbound source
links.

## Approved Architecture

- Template/static-site only.
- Use existing `RowOneLocalArticle.paragraphs` and optional aligned
  `paragraphs_zh`.
- Do not add model fields, schema fields, sidecar fields, source collection,
  browser automation, platform APIs, scheduling, network fetching, translation,
  LLM calls, or image generation.
- Preserve `row-one-app/v7`, `row-one-manifest/v1`,
  `row-one-runtime/v1`, `data/edition.json`, detail routes, schemas, and
  `#local-article-paragraph-N` anchors.
- Avoid wording that implies full external-article republication; use "saved
  text reader" / "existing saved text".

## Changed Files

- `src/fashion_radar/row_one/templates.py`
- `tests/test_row_one_render.py`
- `tests/test_row_one_docs.py`
- `README.md`
- `docs/row-one.md`
- this prompt file

## Review Focus

1. Correctness of reader rendering:
   - reader appears from saved nonblank paragraphs;
   - plain local articles get a reader without a structured map;
   - structured maps get a Reader chip in the correct order;
   - body chip says `Saved text` / `保存正文`;
   - bilingual excerpts only render when `paragraphs_zh` aligns;
   - blank aligned zh excerpt falls back to English excerpt;
   - misaligned zh paragraphs use plain monolingual excerpts;
   - blank paragraphs are skipped;
   - excerpts are escaped and truncated with `…`;
   - reader links preserve existing paragraph anchors.
2. Contract stability:
   - no reader content in `data/edition.json`;
   - no changes to app/manifest/runtime contract versions;
   - no schema or model changes.
3. Test quality:
   - tests are scoped enough to avoid reader/body false positives;
   - docs boundary tests pin the intended wording.
4. Documentation wording:
   - clear that this is a detail-page saved text reader only;
   - avoids implying full article republication.

## Verification Already Run

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_render.py tests/test_row_one_docs.py -q
# 114 passed

UV_NO_CONFIG=1 uv --no-config run --frozen pytest -q
# 2045 passed

UV_NO_CONFIG=1 uv --no-config run --frozen ruff check
# All checks passed

UV_NO_CONFIG=1 uv --no-config run --frozen ruff format --check
# 186 files already formatted

UV_NO_CONFIG=1 uv lock --check
# passed

UV_NO_CONFIG=1 uv --no-config run --frozen python scripts/check_release_hygiene.py
# Release hygiene checks passed

UV_NO_CONFIG=1 uv --no-config run --frozen fashion-radar row-one build --as-of 2026-07-06T04:00:00Z --output-dir reports/row-one/site --latest-only
# Wrote ROW ONE site; 18 stories

UV_NO_CONFIG=1 uv --no-config run --frozen fashion-radar row-one status --site-dir reports/row-one/site --json
# ok: true; app row-one-app/v7; manifest row-one-manifest/v1; runtime row-one-runtime/v1
```

## Expected Output

Return findings first, grouped by severity:

- Critical
- Important
- Minor

For each finding, include file/line references and explain why it matters.
If there are no Critical or Important findings, say so explicitly and state
whether the implementation is approved to commit.
