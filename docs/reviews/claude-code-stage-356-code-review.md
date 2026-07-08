# Stage 356 Claude Code Review

Command:

```bash
claude -p --effort max --permission-mode dontAsk --add-dir /home/ubuntu/fashion-radar < docs/reviews/claude-code-stage-356-code-review-prompt.md
```

Result:

```text
Stage 356 — Saved Article Key Signals: APPROVED. No blockers or important issues.

All 12 requirements verified:

1. Generated-site-only, `articles/<story-id>.html` only.
2. Render order: after binder, before `#local-article`.
3. No app contract / schema / artifact changes.
4. Builder uses only `RowOneStory` + `RowOneLocalArticle`.
5. Why It Matters: local brief first, story fallback only with nonblank
   paragraphs, no invented evidence.
6. Brands/Products/People via reference bucket, blank-skipped, deduped by
   casefold.
7. Non-Why-It-Matters groups carry readable support statements.
8. Themes use displayed titles/labels only; no raw keys, no reference name
   repeats.
9. Paragraph index validation rejects bools, non-ints, negatives, duplicates,
   out-of-range values, and blank source paragraphs; hrefs are one-based
   `#local-article-paragraph-N`.
10. Renderer revalidates hrefs; only `#local-article-paragraph-N` and
    `#local-article-content-section-N` accepted.
11. All user-facing values escaped through `_esc()`.
12. Tests cover builder, render integration, generated-site-only scope, docs
    wording, workflow artifact/contract absence.

Residual risk: minimal. The specific render assertions inside
`test_row_one_render.py` were not fully read because the file is large, but the
workflow test monkeypatches `_render_saved_article_key_signals` and runs the
full pipeline, so any regression there would surface. Low risk.
```
