# Stage 297 Plan Review

**Reviewer:** Claude Code

**Verdict:** CHANGES REQUIRED

## Findings

### Critical

**C1. The planned non-enrichment test text is too short for the proposed
threshold.**

`test_build_row_one_local_articles_does_not_enrich_substantial_extracted_text`
uses extracted text that totals approximately 216 characters. With
`max_chars=500`, the planned guard checks:

```python
total_chars >= min(max_chars, LOCAL_ARTICLE_MIN_CONTEXT_CHARS)
```

That becomes `216 >= 240`, which is false. The planned implementation would
therefore append story context, and the test assertion that `"Editorial"` is not
present would fail even when the implementation follows the plan.

Fix before implementation: make the extracted text genuinely substantial,
totalling at least 240 characters, so it exercises the intended no-enrichment
path.

### Important

None reported.

## Result

The plan needs the C1 test-data correction before implementation. The captured
Claude Code output ended after the first answer section, so this record is not
treated as an approval.
