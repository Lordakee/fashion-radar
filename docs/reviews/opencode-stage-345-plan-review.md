# OpenCode Stage 345 Plan Review

## Important

- The first draft used raw dataclass availability to decide summary quick links. That can create dead anchors because existing renderers may filter all unsafe child cards and return an empty string. The plan should derive summary link availability from already-rendered section HTML.
- The first draft referenced `saved_signal_index.groups`, but `RowOneSavedSignalIndex` exposes entries. The implementation should use existing signal-index rendering output or the existing entry-check helper.
- The first draft referenced `safe_local_article_page_href()`, which does not exist. The implementation should reuse or extract the validation logic currently inside `_saved_article_library_entry_article_page_href()`.
- The first draft's empty-library test used an incomplete `RowOneSavedArticleLibrary(groups=[])` fixture. The test needs a complete zero-count library object.
- Section IDs must not leak onto homepage render paths. Shared render helpers should accept optional section IDs and only receive them from `render_saved_article_library_html()`.

## Approved Direction

Stage 345 is feasible after the plan corrections above. The corrected node remains generated-site-only, avoids duplicating Theme Digest, Reference Atlas, Evidence Board, Content Organization, and Organization Coverage Matrix content, and can proceed as a narrow `articles/index.html` orientation layer.
