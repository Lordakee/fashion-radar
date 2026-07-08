# Stage 355 Code Review

Reviewed the uncommitted Stage 355 implementation for `Saved Article Local
Section Binder`.

## Review Summary

- Initial review found no blockers, but flagged two medium issues:
  - capped section rows could cause later cited paragraphs to be mislabeled as
    unfiled;
  - paragraph excerpts were rendering full paragraph text and could duplicate
    too much body copy before the article.
- A coverage review also found missing section-row cap, unfiled cap, and
  shorthand `local-section-binder.*` artifact guards.
- Follow-up review reported no high/medium blockers after fixes. It noted one
  low-risk alignment issue for `paragraphs_zh`, which was also fixed by using
  Chinese excerpts only when `paragraphs_zh` length matches `paragraphs`.

## Fixes Applied

- Builder now scans all content sections for cited paragraph indices before
  applying the visible row cap, so unfiled paragraphs mean uncited by any
  section, not just uncited by rendered rows.
- Builder truncates paragraph excerpts with
  `SAVED_ARTICLE_LOCAL_SECTION_BINDER_EXCERPT_CHARS`.
- Tests cover section-row caps, unfiled paragraph caps, cited paragraph scanning
  beyond the row cap, excerpt truncation, invalid index filtering, dedupe, and
  language fallback on misaligned `paragraphs_zh`.
- Workflow guards now include `saved-article-local-section-binder`,
  `article-local-section-binder`, and shorthand `local-section-binder` artifact
  families.

## Final Review Result

No blocking issues remain. Stage 355 stays generated-site-only and does not
change app contracts, schemas, runtime/manifest payloads, scraping/fetching,
scoring, LLM behavior, deployment, compliance behavior, or sidecar JSON
artifacts.
