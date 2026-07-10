Checking the diff directly confirms both fixes are in place:

- `border-radius: 999px` is present in `templates.py` at the `.saved-article-local-related-read-evidence-bridge-ref span, .saved-article-local-related-read-evidence-bridge-links a` rule.
- `test_saved_article_local_related_reads_omits_bridge_when_candidate_paragraph_invalid` is present in the test file, covering the symmetric out-of-range candidate paragraph path.

The opencode re-review independently confirms both resolutions. No new issues are introduced by the fix diff.

---

## Stage 380 Re-Review — Saved Local Article Related-Read Evidence Bridge

**Critical:** None

**Important:** None

The two Minor findings from the original Claude Code review (missing `border-radius: 999px` on bridge chip selectors; missing symmetric candidate-paragraph-invalid test) are both resolved. The only remaining Minor is the pre-existing harmless redundant `$` anchor inside `_LOCAL_ARTICLE_PARAGRAPH_FRAGMENT_RE`, which is not introduced by Stage 380.

END_OF_REVIEW
