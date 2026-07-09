No remaining Critical or Important blockers.

The two previously missing pieces are now fully specified:

**companion.related_items .href extraction** — The spec (Co-Existence section) and plan (Task 5 Step 5) now agree: `_companion_related_story_ids(...)` reads the existing `.href` attribute from each `companion.related_items` entry, accepts only `<story-id>.html#local-article-digest` or `<story-id>.html#local-article-paragraph-N` (N≥ 1, no leading zeroes), extracts and safe-validates the story id, dedupes in companion order, and returns an empty tuple for absent companions. Rejection of `articles/...`, external URLs, absolute paths, and fragment-0 is explicit.

**_companion_related_story_ids tests** — Task 4 Step 1 lists `test_companion_related_story_ids_accepts_only_safe_sibling_hrefs` as a RED test; Task 5 Step 5 supplies concrete assertions covering the happy path (deduplication), all rejection cases, and the `None` companion case. The two tasks are sequenced correctly for RED-then-implement.

The renderer-side `_safe_saved_article_local_related_read_href(...)` defense-in-depth check is named, its acceptance/rejection rules are enumerated, and the builder-side `_safe_sibling_article_href(...)` mirrors them consistently.

No gaps remain in selection rules, scoring, href validation, excerpt alignment, reference chip deduplication, generated-site-only boundaries, or test coverage.

END_OF_REVIEW
