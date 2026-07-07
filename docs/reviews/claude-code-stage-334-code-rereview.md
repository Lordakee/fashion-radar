**Is the Important finding fixed?**

Yes. `_render_saved_article_library_snippets()` (line 4174) now iterates over `cards` with a plain list comprehension — no `[:SAVED_ARTICLE_LIBRARY_SNIPPETS_PER_CARD]` slice. The cap is applied exactly once, at line 4122 inside `_saved_article_library_snippets_by_detail_path()`, which is where the per-detail lookup is built. The comment at line 4173 accurately documents this:

```
# Snippets are deduped and capped while the per-detail lookup is built.
```

**Any new Critical or Important issues introduced by the fix?**

No. The change is minimal and correct:
- Single responsibility is now clear: dedup + cap live in the lookup builder, render just iterates what it receives.
- No logic was altered beyond removing the redundant slice.
- All relevant tests pass (26 render tests, 1 doc test).

**Verdict: Ready for full verification.**
