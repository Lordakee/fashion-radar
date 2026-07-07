**Verdict: Safe to implement**

---

**Critical issues:** None.

---

**Important issues:**

**1. Theme ordering is implicitly assumed, not specified.**
The builder test asserts `digest.themes[0].key == "brand_momentum"` and `digest.themes[1].key == "product_heat"`, which implies themes are emitted in organization-group input order. The plan never states this. An implementer iterating over a `dict` or using a different traversal could emit them in a different order and pass linting while failing the test. The plan should say explicitly: "preserve organization group order when mapping to theme keys."

**2. Render-test fixtures `_row_one_edition_with_local_article_sections()` and `_local_articles_with_theme_digest_signals()` are referenced but not defined.**
Task 2, Step 1 adds render tests that call both helpers. The plan doesn't say whether they already exist in `tests/test_row_one_render.py` or need to be created, and doesn't give their structure. If `_row_one_edition_with_local_article_sections()` already exists from Stage 335, the plan should say so. If it doesn't, it's a silent implementation gap that will appear only when writing the test.

---

**Minor issues:**

- `_item()` and `_section()` fixture helpers referenced in the builder test are not defined in the plan snippet — the plan says "patterned after Stage 335 tests", which works but adds a lookup step. No blocker.
- The render test `assert "../details/" in html` is a coarse substring check. If the template accidentally emits `../../details/` it would pass the builder's path validation but fail this assertion with a confusing error. A more specific assertion like `assert 'href="../details/the-row-a-'` would be clearer. Not a blocker.
- Task 3, Step 1 escaping test: `assert html.count("Long lead") < 80` is correct for truncation but doesn't assert the minimum expected content is present. Minor.

---

**Required plan changes:**

One addition needed before implementation starts:

In **Task 1, Step 3** ("Implement minimal builder"), add this sentence to the deterministic ordering rules:

> Emit themes in the order their source organization groups appear in `RowOneSavedArticleContentOrganization.groups`; skip groups whose key has no mapping.

Optionally, in **Task 2, Step 1**, clarify whether `_row_one_edition_with_local_article_sections()` and `_local_articles_with_theme_digest_signals()` are new helpers to create or existing ones to reuse from Stage 335 test infrastructure.

Everything else — TDD sequencing, contract boundary, safety/dedup/cap tests, CSS selectors, docs sentinel, full-node verification, commit guard — is correct and consistent with prior stages.
