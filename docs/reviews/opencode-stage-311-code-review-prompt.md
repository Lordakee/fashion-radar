# opencode Stage 311 Code Review Prompt

You are the fallback reviewer for `/home/ubuntu/fashion-radar` on branch
`main`. Claude Code was attempted twice with `--effort max` and returned
server-side 524 timeouts, so this fallback review is required by
`docs/REVIEW_PROTOCOL.md`.

Review the pasted Stage 311 diff only. Do not run tools and do not inspect
additional files. Keep the review concise. Focus on correctness, contract
safety, test coverage, escaping/link safety, and whether the code stays within
the approved plan.

## Stage Goal

Add a generated-site detail-page saved text digest for ROW ONE. It organizes
existing locally saved article content inside generated story detail pages using
only existing `RowOneLocalArticle` sidecar fields:

- saved paragraphs and optional aligned `paragraphs_zh`
- existing `content_sections`
- existing references and paragraph indices

## Expected Scope

Expected changed files:

- `src/fashion_radar/row_one/templates.py`
- `tests/test_row_one_render.py`
- `tests/test_row_one_docs.py`
- `README.md`
- `docs/row-one.md`

Expected behavior:

- Render `#local-article-digest` inside existing `#local-article`.
- Place digest after local article map and before saved text reader, brief, content sections, and body.
- Add digest cards for read-first, people/brands, products, and source structure.
- Use first `takeaways` body when present; otherwise fall back to the first nonblank saved paragraph.
- Render only valid paragraph links to existing `#local-article-paragraph-N` anchors.
- Omit invalid or blank-paragraph indices without dropping a valid takeaway body.
- Deduplicate reference chips and cap each digest reference list at 4.
- Escape rendered text and href values.
- Add a `Digest / 整理` local article map chip only when digest exists.
- Keep plain saved-text articles useful with a digest, but still no structured local article map.
- Keep source-map count chips bilingual.
- Add static CSS only; no JavaScript changes are required.
- Update docs with Stage 311 boundary text.

## Boundaries

This stage must not:

- change `row-one-app/v7`
- change `data/edition.json`
- change `row-one-manifest/v1`
- change `row-one-runtime/v1`
- change schemas, models, sidecar fields, story IDs, detail routes, or paragraph anchors
- add source collection, scraping, browser automation, platform APIs, scheduling, scoring, LLM calls, translation services, compliance-review features, or social/community connectors
- commit generated `reports/row-one/site/**` output or `uv.lock` changes

## Reviewer Tasks

1. Inspect only the pasted diff.
2. Report Critical and Important findings first, with file/line references.
3. Include Minor findings only if they are actionable and clearly worth fixing before this stage commit.
4. If there are no Critical or Important findings, say so explicitly.
5. Do not modify files.
6. Keep the whole response under 120 lines.

## Fresh Verification Already Run

The implementation has already run these commands successfully:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest tests/test_row_one_render.py tests/test_row_one_docs.py -q
UV_NO_CONFIG=1 uv --no-config run --frozen pytest -q
UV_NO_CONFIG=1 uv --no-config run --frozen ruff check
UV_NO_CONFIG=1 uv --no-config run --frozen ruff format --check
UV_NO_CONFIG=1 uv lock --check
UV_NO_CONFIG=1 uv --no-config run --frozen python scripts/check_release_hygiene.py
UV_NO_CONFIG=1 uv --no-config run --frozen fashion-radar row-one build --as-of 2026-07-06T04:00:00Z --output-dir reports/row-one/site --latest-only
UV_NO_CONFIG=1 uv --no-config run --frozen fashion-radar row-one status --site-dir reports/row-one/site --json
```

Expected status contracts from the sample site:

- app: `row-one-app/v7`
- manifest: `row-one-manifest/v1`
- runtime: `row-one-runtime/v1`
- status: `ok: true`
