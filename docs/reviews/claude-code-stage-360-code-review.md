## Stage 360 Review: Daily Local Article Capsules

### Critical

None.

---

### Important

**`None` guard evaluated after function call** — `templates.py`, `_daily_local_article_capsule_from_story`:

```python
article = local_articles_by_story_id.get(story.id)
if _usable_local_article_paragraph_count(article) <= 0 or article is None:
    return None
```

Python short-circuits `or` left-to-right, so `_usable_local_article_paragraph_count(article)` is called *before* `article is None` is tested. When a story has no saved article, `article` is `None` and the function receives it. This is safe only if `_usable_local_article_paragraph_count` handles `None` — if it does, the `or article is None` branch is dead code; if it doesn't, the guard is bypassed and the call raises. The tests appear to exercise the missing-article path, so it probably works in practice, but the ordering is fragile and inconsistent with the defensive pattern used elsewhere in this file. The guard should be:

```python
if article is None or _usable_local_article_paragraph_count(article) <= 0:
    return None
```

---

Everything else checks out: href safety is solid (story-ID round-trip validation, `articles/` prefix hardcoded, `PurePosixPath` rejects traversal), the generated-site-only boundary is enforced and tested end-to-end, caps and escaping are consistently applied, paragraph anchors delegate to the existing `_local_article_paragraph_anchor`, and test and doc coverage match the pattern of prior stages.
