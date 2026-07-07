## Stage 340 Code Review

**APPROVED**

All tests pass (48 + 74 + 29). No correctness or contract-breaking issues found. Findings below are ranked by severity.

---

### Critical findings

None.

---

### Important findings

**1. Double normalization in `_publishable_local_article_paragraph`** (`articles.py:160`)

The private function calls `normalize_row_one_paragraph(paragraph)` on input that is already normalized by its only caller (`text_to_local_article_paragraphs` normalizes `raw_paragraph` at line 142before passing it). The function is correct (normalization is idempotent) but does redundant work on every paragraph.

This matters only as a latent hazard: if a future caller passes raw text, the guard silently rescues it, which makes the contract unclear. Since the function is private and the call-site contract is stable, the risk is low — but the double-call is confusing.

**2. `image credit:?.+` matches `"Image credits…"` without a colon**

The pattern `image credit:?.+` (IGNORECASE, fullmatch) has`:?` meaning the colon is optional, so `"Image credits have been supplied by the agency."` matches: `image credit` consumed, `s have been supplied…` consumed by `.+`. That sentence is almost certainly boilerplate, so the real-world false-positive risk is negligible — but the intent was probably to anchor on `credit:` (with colon) for the attribution-line form and let longer editorial sentences through. Worth noting for future pattern audits.

---

### Minor findings

<thinking>
Let me continue with the minor findings and recommendations.
</thinking>

**3. Overly broad workflow guard: `"quality_gate" not in generated_contract_payload`** (`test_workflows.py:507`)

The six narrower slug guards (`saved-article-paragraph-quality-gate`, etc.) already cover the artifact-name variants. The bare `"quality_gate"` guard is so broad that any legitimate future stage touching quality gating — even in a comment inside a rendered HTML attribute — would cause a spurious failure here. The guard adds no protection that the narrower checks don't already provide.

**4. `^` anchor is redundant in `LOCAL_ARTICLE_NOISE_FULL_RE`** (`articles.py:35`)

The regex opens with `^(?:…)` but is always used via `.fullmatch()`, which already anchors both ends. Harmless, but the `^` is noise that could mislead a future maintainer into thinking `re.match` / `re.search` would also work as intended.

**5. `folded` computed before the fast-exit `fullmatch` check** (`articles.py:165`)

`folded = compact.casefold()` is computed on every call but only consumed after the `fullmatch` and `prefix` checks — which return early for the majority of boilerplate paragraphs. Moving the assignment after those two guards would avoid the casefold on every filtered line. Very minor hot-path concern given typical paragraph counts, but easy to fix.

**6. No boundary test for the URL-ratio path** (`test_row_one_articles.py`)

The URL filtering has two branches: short paragraph (≤ 120 chars) and high-ratio (≥ 35% URL chars). The short-paragraph branch is exercised by the bare-URL case in `test_text_to_local_article_paragraphs_filters_extraction_boilerplate`. The high-ratio branch (> 120 chars but URL-heavy) has no dedicated test. This is not a correctness gap given the logic is simple arithmetic, but a targeted test would complete coverage of the intent.

---

### Recommended fixes before commit

Only one fix is worth making before commit; the rest are optional clean-ups.

**Fix 3— remove the bare `"quality_gate"` guard.** It is the only finding with a non-trivial future breakage risk (will cause a false test failure if any unrelated stage uses the term). Remove the single line:

```python
# remove this line from test_workflows.py
assert "quality_gate" not in generated_contract_payload
```

The six surrounding guards for `saved-article-paragraph-quality-gate`, `paragraph-quality-gate`, `Saved Article Paragraph Quality Gate`, `saved_article_paragraph_quality_gate`, `paragraph_quality_gate`, and `saved_paragraph_quality_gate` already enforce the contract precisely.

Everything else (findings1, 2, 4, 5, 6) is safe to leave as-is or address in a follow-on clean-up stage.
