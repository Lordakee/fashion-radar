Here is my complete plan review for Stage 325.

---

## Stage 325 Plan Review

### 1. Validity as a small follow-on stage

Valid. Stage 325 is a direct, one-function polish of Stage 324's `_render_local_article_paragraph_evidence_support()`. The three items are exactly the three non-blocking suggestions in the Stage 324 code review. No new features, no new data flows.

---

### 2. Scope containment

Clean. Only `templates.py` and `tests/test_row_one_render.py` are modified. No Pydantic models, no JSON builders, no edition/manifest/runtime contract fields, no acquisition, no LLM, no connectors, no scheduling, no deployment — nothing outside the generated-site render path. The spec's Non-Goals list mirrors every boundary defined in `AGENTS.md` and Stage 324's review. ✓

---

### 3. Failing test executability against current code

**Step 1 — map-link assertion** (strengthening existing test): correctly flagged as already-passing. No new RED expected here. ✓

**Step 2 — no-empty-ref-wrapper test**: The test asserts `"<div></div>" not in evidence_html` with `references=[]`. Current code at line 5495 always emits `<div>{refs}</div>`, which renders as `<div></div>` when `refs` is empty. This WILL be RED. ✓

**Step 3 — zh-body-fallback test**: The test supplies `zh="   "` and asserts both spans carry the English fallback. Current code at line 5478 does `body_zh = _esc(_local_article_paragraph_evidence_body(item.item_body.zh))` — calling `normalize_row_one_paragraph("   ")` returns `""`, so the zh span renders as `<span data-lang="zh"></span>`. The test's `assert '<span data-lang="zh"></span>' not in evidence_html` WILL fail on current code. RED confirmed. ✓

The XSS assertion `'<span data-lang="en">English &lt;fallback&gt; body.</span>'` is consistent with how the existing Stage 324 XSS test works (angle brackets are preserved through `normalize_row_one_paragraph` and escaped only by `_esc()` at render time). ✓

---

### 4. Implementation reasonableness and minimality

**New helper `_local_article_paragraph_evidence_body_text()`**:

```python
def _local_article_paragraph_evidence_body_text(body: LocalizedText) -> LocalizedText:
    en = _local_article_paragraph_evidence_body(body.en)
    zh = _local_article_paragraph_evidence_body(body.zh) if body.zh.strip() else en
    return LocalizedText(en=en, zh=zh)
```

`body.zh.strip()` correctly detects blank and whitespace-only zh. Fallback is to the already-normalized `en` string (not the raw input), consistent with how the reader and digest helpers handle the same scenario. `LocalizedText` is already imported at the top of the file. No new imports needed.

**Updated support renderer**: The `refs_html` guard `f"                <div>{refs}</div>\n" if refs else ""` is a minimal, clean fix — same indentation level as the existing template, consistent with surrounding whitespace.

No regressions to existing tests are expected: the body rendering path is unchanged for non-blank zh, and the refs rendering path is unchanged when references are non-empty.

---

### 5. Missing edge cases and protocol conflicts

**None critical or important.** Two minor observations:

**Minor1 — Incomplete return-statement snippet in Task 2 Step 2.** The plan shows the new `refs_html` variable and says "render `{refs_html}` instead of `                <div>{refs}</div>`", but does not show the full updated return f-string. The implementer must also remove the old `{body}                <div>{refs}</div>` line and replace it with `{body}{refs_html}`. This is clearly implied and inferrable, but the plan would be fractionally clearer with an explicit before/after of the return block.

**Minor 2 — Blank `body.en` edge case not documented.** If `body.en` is also blank, the helper returns `LocalizedText(en="", zh="")` and both spans render empty. This is harmless (model construction guarantees en has content when `item_body` is set) and is consistent with how other renderers handle it, but a brief comment in the helper acknowledging the en-blank fallthrough would make the intent self-documenting.

Neither finding is blocking.

---

### Final Verdict

**Approved to implement.**

The stage is correctly scoped, the failing tests are genuinely RED against current code (and the map-link assertion is correctly marked as already-passing), the implementation is minimal and technically sound, no JSON/model/contract/source boundaries are crossed, and the review protocol is properly followed. The two minor observations above can be incorporated at the implementer's discretion but are not required.
