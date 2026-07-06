Here are my findings.

---

## No Critical issues found.

---

## Important

**1. Duplicate deduplication logic across the render/template boundary**

`_deduped_editorial_brief_items` in `render.py` already deduplicates items by truncated-body key before handing them to `render_index_html`. Then `_render_editorial_brief` in `templates.py` performs the exact same operation — same `seen_bodies: set[tuple[str, str]]`, same `_editorial_brief_body_excerpt` key. Two independent copies of the same invariant must stay in sync. If `EDITORIAL_BRIEF_BODY_EXCERPT_CHARS` is changed, or the key logic is adjusted in one place, the other silently becomes stale. The render layer should own deduplication; the template layer should trust what it receives.

**2. Triple excerpt truncation creates an unclear data invariant on `_EditorialBriefItem.body`**

Bodies are truncated in `_combined_editorial_body` (via `_editorial_brief_excerpt`), then re-truncated in `_deduped_editorial_brief_items` (same function), then truncated a third time in both `_render_editorial_brief` and `_render_editorial_brief_card` in templates (via `_editorial_brief_body_excerpt`). The three-pass chain is currently idempotent (220 → 220 → 220 chars), but it means `_EditorialBriefItem.body` carries no clear invariant: it could be raw, once-truncated, or twice-truncated depending on which constructor path ran. This becomes a latent bug if the constant is ever made call-site-specific or language-specific.

Recommendation: truncate exactly once, in the template layer when rendering, and remove the excerpt calls from `_combined_editorial_body` and `_deduped_editorial_brief_items`.

**3. Misleading test assertion obscures fragment allowlist coverage**

In `test_render_index_html_escapes_editorial_brief_and_filters_links`, 4 items are passed and the test asserts:

```python
assert (
    'href="details/the-row-signal-1234567890.html#local-article-paragraph-1"'
    not in section_html
)
```

This assertion is true because item 4 is beyond the 3-item cap — not because `#local-article-paragraph-1` is a rejected fragment. The test will stay green even if `_LOCAL_ARTICLE_PARAGRAPH_FRAGMENT_RE` is accidentally broken, as long as the cap still applies. A developer reading this test could reasonably conclude the paragraph fragment pattern is a rejected link, when it is actually valid. Acceptance of `#local-article-paragraph-N` is covered only in the integration test; the unit-level "filters links" test provides false assurance against a fragment-allowlist regression.

Fix: drop the 3-item cap situation from this test (use3 or fewer items), and add a distinct assertion that the paragraph-fragment href is present for a valid within-cap item. The cap behavior already has its own dedicated test.

---

## Minor

**4. `_render_editorial_brief_card` re-cleans already-cleaned input**

`_render_editorial_brief` constructs a new `_EditorialBriefItem` with already-excerpted title/body/meta, then passes it to `_render_editorial_brief_card`, which applies `_editorial_brief_display_text` and `_editorial_brief_body_excerpt` again. Idempotent and harmless, but it signals that the card function's contract is ambiguous about whether its input is pre-cleaned or raw. Decide one convention and enforce it.

**5. No unit-level negative test for unknown fragment rejection**

`_safe_editorial_brief_href` rejects fragments outside the two allowed patterns (e.g., `details/story.html#heading-1`, `details/story.html#summary`). This rejection is not directly tested. A short parametrized test on `_safe_editorial_brief_href` covering a rejected fragment, an accepted paragraph fragment, and an accepted content-section fragment would make the allowlist explicit and protect against regex changes.

**6. `.editorial-brief-link` span lacks `align-self: end`**

`.editorial-brief-meta` has `align-self: end` to pin the source attribution to the card bottom. `.editorial-brief-link` (the "Read locally /本地阅读" span rendered in linked cards) has no `align-self` declaration, so it follows grid flow immediately after the meta or body block rather than anchoring to the bottom. Visual-only concern, but inconsistent with the meta treatment.

**7. `_lead_story_for_editorial_brief` name vs. behavior**

The function name implies it selects the edition's lead story, but the actual behavior is "first story in iteration order that has any text in `editorial_takeaway` or `summary`." If `stories[0]` is completely empty it falls through to `stories[1]`. In practice the story list is ranked so this resolves correctly, but the name slightly overpromises. A comment clarifying the fallback intent would help.
