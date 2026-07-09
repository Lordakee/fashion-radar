## Critical

None.

## Important

None. The previous companion-overlap finding is fully resolved.

The companion model's `related_items` entries carry an existing `.href` field (`saved_article_local_reading_companion.py:53`), and `_item_href(...)` produces sibling-shaped `<story-id>.html#local-article-digest` hrefs as its preferred path for items that have a local article page (`saved_article_local_reading_companion.py:299-304`). That is exactly the candidate set Stage 377 can recommend, so the exclusion is sound:

- `_companion_related_story_ids(...)` is specified identically in the spec (Co-Existence section) and plan (Task 5 Step 5): it reads each `companion.related_items` entry's `.href`, accepts only `<story-id>.html#local-article-digest` or `<story-id>.html#local-article-paragraph-N` (N>=1, no leading zeroes), extracts and safe-validates the story id, dedupes in companion order, and returns `()` for an absent companion. Rejection of `articles/...` prefixes, external URLs, absolute paths, unsafe ids, and fragment-0 is explicit in both docs and the Task 5 Step 5 assertions.
- The RED/implementation sequencing is correct: Task 4 Step 1 registers `test_companion_related_story_ids_accepts_only_safe_sibling_hrefs`, Task 5 Step 5 implements the helper and supplies the dedup, happy-path, all-reject, and `None` assertions.
- No overlap gap remains for the companion's `../...` fallback hrefs (`saved_article_local_reading_companion.py:308,315`): those items lack a local article page, so Stage 377 skips them too (it requires a `local_article_page_hrefs_by_story_id` entry). Both href maps derive from the same `page_specs` inside `_write_local_article_pages(...)` (`render.py:478-490`, plan Task 5 Step 5), so the two views cannot disagree.
- Builder-side `_safe_sibling_article_href(...)`, renderer-side `_safe_saved_article_local_related_read_href(...)`, and the companion extractor enforce consistent sibling-href rules as defense in depth. The `companion` variable is already in scope at `render.py:492`, and `edition`, `local_articles_by_story_id`, and `page_specs` are all available for the new build call.

## Minor

- The `_companion_with_hrefs` rejection-case fixture (plan Task 5 Step 5) does not include a `../`-prefixed companion fallback href (the `_item_href` fallback shape at `saved_article_local_reading_companion.py:308,315`). The validation rules already reject it via the leading-dot / path-separator / traversal checks, and it cannot cause overlap, but one explicit assertion would document that fallback-shape rejection directly.

END_OF_REVIEW
