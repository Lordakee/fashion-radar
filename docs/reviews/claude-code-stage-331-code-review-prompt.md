Review the current uncommitted Stage 331 changes in `/home/ubuntu/fashion-radar`.

Goal:
- Add ROW ONE local article body provenance so generated sidecars, metrics,
  readiness output, and detail pages distinguish extracted article text,
  ROW ONE summary fallback text, and skipped/unusable local article bodies.

Expected implementation:
- `RowOneLocalArticle` has a backward-compatible `body_source` field with values
  `extracted`, `summary_fallback`, and `skipped`.
- The local article builder marks successful extracted bodies as `extracted`.
- Extraction skipped/failed/empty/unusable text falls back to summary/editorial
  context as `summary_fallback` with a reason when publishable paragraphs exist.
- If no publishable fallback body exists, the builder emits a `skipped` sidecar
  with the extraction/fallback reason instead of silently dropping diagnostics.
- Metrics/readiness payloads and relevant CLI text include extracted,
  summary-fallback, and skipped local article counts.
- Detail pages render a bilingual text-source provenance chip and fallback
  reason when present.
- Docs describe the local article body provenance boundary.

Hard boundaries:
- Do not add compliance-review behavior.
- Do not change `data/edition.json`, `row-one-runtime/v1`, generated routes,
  detail anchors, source collection, scoring, connectors, or LLM behavior.
- Adding fields to `data/articles/<story-id>.json` sidecars is acceptable.

Please review for:
1. Critical or Important correctness issues, regressions, missing tests, or
   contract-boundary violations.
2. Whether the `skipped` sidecar behavior is technically consistent with the
   renderer/metrics/readiness flow.
3. Whether any changed review/doc artifacts look incomplete or unsuitable to
   commit.
4. Whether `uv.lock` appears unrelated to Stage 331 and should be excluded.

Use file/line references. Do not modify files. Report findings by severity:
Critical, Important, Minor. If no Critical/Important findings exist, say so.
