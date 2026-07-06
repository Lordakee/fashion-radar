Here are the re-review findings, ordered by severity.

---

## Critical (Must Fix Before Implementation)

**C1 (new): Six "does not X" test guard phrases don't appear in the proposed docs paragraph.**

`test_row_one_docs_describe_article_readiness_boundary` asserts these exact substrings:

```python
"does not change `row-one-app/v7`",
"does not write a new generated JSON artifact",
"does not add source collection",
"does not fetch article pages",
"does not add scoring",
"does not add llm calls",
```

But the proposed docs paragraph uses a `without X-ing` construction:

```
without collecting sources, fetching article pages, mutating SQLite, changing
`row-one-app/v7`, or writing a new generated JSON artifact.
```

None of the six `"does not X"` strings appear verbatim in that text. Worse, `"scoring"` and `"llm calls"` have no counterpart in the proposed paragraph at all — they will fail regardless. `_normalized` collapses whitespace but cannot conjure missing words.

**Fix (pick one):**
- Rewrite the docs paragraph to literally include each guarded phrase, or
- Replace the test guards with phrases that actually appear in the docs (e.g., `"without collecting sources"`, `"changing \`row-one-app/v7\`"`) and add `"scoring"` and `"llm calls"` somewhere in the docs text.

---

## Important (Should Fix)

**I1: CLI text-output test is missing the `Site:` assertion.**

The design explicitly added `Site: <site-dir>` as a required output line (FR2), and the implementation emits it. But `test_row_one_article_readiness_prints_config_and_site_counts` asserts `Config:` and not `Site:`. The JSON test covers `payload["site_dir"]`, but a regression that drops the `Site:` text line would be invisible.

Add to the text-output test:
```python
assert f"Site: {output_dir}" in result.output
```

---

## No Further Critical or Important Findings

The C1 fix from the prior review (reconciling `"does not require saved article sidecars"`) is confirmed clean. The first-run docs phrase list fully matches the proposed paragraph. Analyzer logic, JSON payload, sentinel slicing code, and scope boundary are all sound.

---

## Minor / Nit

- **M1 (carried):** No test for the `ConfigError` path on missing `sources.yaml`. Acceptable to defer.
- **M3 (carried, deliberate):** Text output omits `organized_section_count` / `source_count`; plan acknowledges this as intentional.
- Confirm that `_normalized` in the existing test file collapses whitespace — if it doesn't, the `row_one_article.enabled:\ntrue` line-break in the docs is a latent phrase mismatch.

---

## Assessment

**Ready to implement? No.**

One new Critical (C1) and one Important (I1) must be addressed first. Both are in the test/docs layer, not the implementation — C1 is a phrase-form mismatch (six guards fail against the actual docs text), and I1 is a missing `Site:` assertion. Neither requires changing the analyzer or CLI logic.
