# Claude Code Stage 299 Plan Review

**Reviewer:** Claude Code
**Verdict:** CHANGES REQUIRED

## Findings

### Critical

None.

### Important

**I1. Test body-value assertions in `_assert_local_article_brief_sections` must
be verified against actual fixtures before writing.**

Plan Task 2 Step 1 hard-codes `body.en` values `["Summary", "Important",
"Context", "Path"]` and `body.zh` values `["摘要", "重要", "背景", "路径"]`.
Those values currently match the `_edition()` fixture, but the helper is more
robust if it compares against the fixture story fields directly:

```python
assert [section.body.en for section in article.brief_sections] == [
    story.summary.en,
    story.why_it_matters.en,
    story.signal_context.en,
    story.reader_path.en,
]
```

Fix before implementation: update the plan helper to accept the fixture
`story` and compare against story fields instead of hard-coded body strings.

### Minor

**M1. `RowOneLocalArticleBriefKey` placement in `models.py` is unspecified.**

Place it with the other top-level `Literal` aliases before
`RowOneLocalArticleBriefSection`.

**M2. Proof script in Task 6 is requirements-only.**

The implementer must write the scratch script from the listed checks.

## Result

Fix I1 before implementation. No Critical findings were reported.
