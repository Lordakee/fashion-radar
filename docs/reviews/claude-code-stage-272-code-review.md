I've verified all three follow-up fixes and re-checked the constraints against the actual diff and source.

## APPROVED

All three follow-up fixes are correctly applied, and the constraints from the prior APPROVED review still hold.

**Fix 1 — bilingual story-card microcopy** (`templates.py` `_render_story_card`, lines 1042–1069)
- Date: `story-date` span wraps `data-lang="en"` (`published.en`) / `data-lang="zh"` (`published.zh`) — 1042–1045
- Evidence count: `story-evidence-count` wraps EN `1 source`/`N sources` and ZH `N 条来源` — 1060–1063
- "Read brief": `story-detail-link` wraps `data-lang="en"` "Read brief" / `data-lang="zh"` "阅读简报" — 1064–1067
- Covered by tests at `test_row_one_render.py:177–181`.

**Fix 2 — `.edition-nav-grid` removed**
- No occurrence remains in `templates.py` (markup or CSS); replaced by `.edition-rail` / `.edition-rail-grid`. Guarded by `assert ".edition-nav-grid" not in css` (`test_row_one_render.py:266`). The `.edition-nav-item` guard class is retained via the combined `.edition-nav-item, .edition-rail-item` selector, and markup still emits `edition-nav-item edition-rail-item`.

**Fix 3 — `readiness` annotation** (`_render_edition_status`, lines ~761–766)
- Signature now `readiness: RowOneReadiness | None = None` with a `build_row_one_readiness` fallback; `RowOneReadiness` is imported (line 16). Caller passes the pre-built instance (line 25), avoiding a double build. All attributes used (`story_count`, `safe_evidence_count`, `readiness.en/.zh`) exist on the frozen dataclass.

**Constraints**
- Presentation-only: changes confined to `templates.py` rendering, docs, and tests; `readiness.py` schema unchanged. ✓
- Markup guards present: `edition-nav` (753), `edition-rail` (758), `edition-nav-item edition-rail-item` (847), `article-contents` (867), `detail-panel` (168), evidence classes `--safe`/`--retained` (1161/1151). ✓
- Unsafe evidence: `_render_evidence` returns the retained row with `_esc(link.title)` and no href when `_safe_external_url` is `None`. ✓
- Docs: README (75–77) and `docs/row-one.md` (66–73) describe presentation only; the latter explicitly disclaims "acquisition, deployment, or automation expansion." ✓

No required fixes. Diff is ready for commit.
