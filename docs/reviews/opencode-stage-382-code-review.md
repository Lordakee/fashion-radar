## Stage 382 Local Article Synthesis Brief — Code Review

### Critical
None.

### Important
None.

The implementation is correct, respects every scope boundary in AGENTS.md and the plan, and is well-tested:

- **Generated-site-only boundaries hold.** No export in `row_one/__init__.py`, no entry in `pyproject.toml`, no route family in `articles.py`, no schema addition in `models.py`. The sentinel test (`tests/test_workflows.py:1826`) patches `_render_local_article_synthesis_brief` with `raising=True` and proves the renderer is only invoked from `articles/<story-id>.html`. Contract denylist extensions cover both `generated_contract_payload` and the artifact-stem tuple.
- **Anchor safety is strong.** `_safe_local_article_synthesis_href` (templates.py:17708) layers on top of `_safe_local_article_intelligence_href` and additionally cross-checks paragraph indices against `_local_article_rendered_paragraph_indices` and section numbers against `len(content_sections)`. The escape test injects `javascript:`, traversal, out-of-range, and whitespace-padded fragments — all filtered.
- **Escaping is consistent.** Every interpolated value goes through `_esc` (`escape(..., quote=True)`), including the href attribute. The render test verifies `<script>` → `&lt;script&gt;`.
- **Determinism is preserved.** `consumed_sources`/`consumed_texts` are only used for membership checks (never iterated); all candidate generators iterate sequences in defined order; dataclasses are frozen.
- **Three-card contract enforced.** `_choose_candidate` returns `None` on any missing card and the builder short-circuits to `None` (local_article_synthesis_brief.py:79-80), with a dedicated test (`test_build_local_article_synthesis_brief_requires_three_unique_cards`).
- **zh fallback is safe.** `_nonblank_localized_text` (local_article_synthesis_brief.py:314) does `en=en or zh, zh=zh or en`, so English-only inputs never produce empty zh spans. Tested at test_row_one_local_article_synthesis_brief.py:247.

### Minor

1. **Plan deviation — `_safe_local_article_synthesis_href` was added despite the plan explicitly saying not to** (Plan Task 5 Step 3: *"Do not add `_safe_local_article_synthesis_href(...)`"*). The wrapper does NOT duplicate the regex/whitespace logic (it delegates to `_safe_local_article_intelligence_href`), so the anti-duplication *intent* of the plan is honored, and the extra index cross-validation is genuinely new safety value. Still, the naming contradicts the plan; either the plan or the code should be reconciled. (templates.py:17708-17732)

2. **`_truncate` diverges from the sibling intelligence-brief `_truncate`.** Synthesis uses `clean_row_one_text` + `" ".join(...split())` with a `normalize_row_one_paragraph` fallback (local_article_synthesis_brief.py:331-337); intelligence uses only `normalize_row_one_paragraph` (local_article_intelligence_brief.py:363-367). Both yield single-space-collapsed text, so output is consistent, but the two helpers in neighboring modules drift slightly. Consider sharing one helper, or document why they differ.

3. **Parameter shadowing in `_safe_local_article_synthesis_href`.** `href: object` is reassigned to the result of `_safe_local_article_intelligence_href(href)` (templates.py:17712-17714). Python-valid, but the type narrowing is implicit; a local like `safe = _safe_local_article_intelligence_href(href)` would read more cleanly.

4. **Redundant `local_article` parameter on the renderer.** `_render_local_article_synthesis_brief(brief, *, local_article)` only uses `local_article` to re-validate anchor hrefs the builder already validated against the same object. This is defensible defense-in-depth (the render test exploits it to prove unsafe hrefs are filtered independently of the builder), but worth a one-line comment so future maintainers don't "clean it up" and lose the safety net.

5. **Asymmetric dedup keys for English-only candidates.** `_paragraph_candidates` and `_paragraph_anchor` fall back to `zh=zh or en`, so an English-only paragraph produces the key `f"{en}|{en}"` while the same text with real zh would key as `f"{en}|{zh}"`. Harmless in practice (the consumed-text set is per-build), but a subtle asymmetry.

### Maintainability notes
- CSS selector set, render-order test, escaping test, contract denylist, docs-boundary test, and the Stage 382 docs paragraph are all aligned and mutually consistent.
- The new CSS block follows the existing local-article section patterns (`.local-article-intelligence-brief-*`) and includes the required `@media (max-width: 760px)` mobile fallback for the grid.
- The docs paragraph placement (`stage_382_pos < stage_381_pos`) is asserted in both README and docs/row-one.md.

END_OF_REVIEW
