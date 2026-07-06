# Stage 319 Focused Code Review Prompt

Review the current uncommitted diff in `/home/ubuntu/fashion-radar`.

Goal: Stage 319 adds a generated-site-only ROW ONE detail-page
`Signal Briefing / 信号简报` panel. It must be presentation-only: no generated
JSON contract/schema/runtime/manifest changes and no source collection,
fetching, scoring, connectors, LLM calls, or compliance-review behavior.

Focus files:

- `src/fashion_radar/row_one/templates.py`
- `tests/test_row_one_render.py`
- `tests/test_workflows.py`
- `tests/test_row_one_docs.py`
- `README.md`
- `docs/row-one.md`

Required behavior:

- Panel appears after `detail-information-map` and before `id="summary"`.
- Uses existing story summary/source/signal context/evidence/references.
- Uses optional existing `RowOneLocalArticle` cues.
- Dedupes references by normalized name/type/label, cap 8.
- Brief cues before content cues, cap 3.
- Paragraph links only target validated existing local article paragraph anchors.
- Text is escaped; no raw script/HTML leakage.
- New CSS selectors exist and mobile grids collapse.

Already run:

```bash
UV_NO_CONFIG=1 uv --no-config run --frozen pytest \
  tests/test_row_one_render.py \
  tests/test_workflows.py::test_write_row_one_site_files_writes_local_article_without_mutating_sqlite \
  tests/test_row_one_docs.py -q
```

Result: `149 passed`.

Return only:

- Critical findings
- Important findings
- Minor findings
- Final assessment

If no Critical or Important findings, say so clearly.
