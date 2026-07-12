Now I have everything I need. Let me compile the full review.

---

## Stage 381 Code Review — Saved Local Article Related-Read Connection Brief

**Scope:** `saved_article_local_related_reads.py`, `templates.py`, all four test files, README.md, docs/row-one.md, plan, plan review records. All 421 tests pass; ruff clean on all modified files.

---

## Important

**I1— Lead sentence always uses plural "local reads", producing grammatically incorrect copy at `card_count=1`**

The builder hard-codes `f"{card_count} local reads"` in both lead branches. With `card_count=1`, the rendered lead reads:

```
This path connects1 local reads through section or source context already saved in ROW ONE.
```

`_count_label(count, singular, plural)` (`templates.py:15749`) handles singular correctly and is used for all four metrics chips — but the `lead` field is composed at build time in the builder, not via `_count_label`. The builder test `test_saved_article_local_related_read_connection_brief_uses_context_lead_without_signals` (`test_row_one_saved_article_local_related_reads.py:841–844`) explicitly asserts the wrong string, making it a false-positive test that locks in the defect:

```python
assert brief.lead.en == (
    "This path connects 1 local reads through section or source context already "
    "saved in ROW ONE."
)
```

`card_count=1` is a real runtime state: a3-card model where2 cards have unsafe hrefs produces exactly 1 renderable card. The render test fixes (plan C1) targeted only the metrics assertion (`"1 local read"` via `_count_label`) — the lead was not addressed.

Fix: Replace the lead format string with a sentence that uses `_count_label`-equivalent pluralisation, e.g.:

```python
count_phrase = f"{card_count} local {'read' if card_count == 1 else 'reads'}"
lead_en_signals = f"This path connects {count_phrase} through shared signals,..."
lead_en_context = f"This path connects {count_phrase} through section or source ..."
```

Update the builder test to assert the singular form correctly.

---

## Minor

**m1 — `test_render_local_article_page_related_read_connection_brief_uses_only_safe_cards` assumes lanes are present without asserting it**

The test (`test_row_one_render.py:3928–3935`) slices `brief_html` by searching for `<div class="saved-article-local-related-read-lanes">` as the end marker. This works because `_related_read_card` defaults to `reason=LocalizedText(en="Shared signal: The Row", ...)`, which routes into a lane. If the sole safe card had an unrecognised reason, `section_html.index('<div class="saved-article-local-related-read-lanes">', brief_start)` would raise `ValueError` rather than produce a useful test failure. There is no assertion that the test setup produces a lanes div. The assumption is correct but implicit. A comment or a fallback slice end (`saved-article-local-related-reads-grid`) would make the test more robust.

**m2 — Docs "generated-site only" missing hyphen is locked in by both docs and test**

README.md:256, docs/row-one.md:473, and `test_row_one_docs.py:4962` all carry `"generated-site only"` (two words) while the stage title and plan goal say `"generated-site-only"`. Since docs and test match, no test fails — this is cosmetic. It was identified as m5 in the plan review and accepted.

**m3 — `.strip()` guards in `_render_saved_article_local_related_read_connection_tags` are redundant**

`templates.py:9589` (`reference.name.strip()`) and `templates.py:9597` (`source_name.strip()`) re-check blankness that `_related_read_connection_signal_references` and `_related_read_connection_sources` already exclude via `normalize_row_one_paragraph` + `if not name`. The guards are harmless and match the pattern in the existing `_render_saved_article_local_related_read_references` helper (also has `.strip()` there), but they are not meaningful safety logic.

---

## No Critical Findings

**Checked and confirmed correct:**

- **href safety boundary**: `renderable_cards` is derived from `_render_saved_article_local_related_read_card(card)` which calls `_safe_saved_article_local_related_read_href` — unsafe cards never reach the brief builder at `templates.py:9490–9493`. ✓
- **Brief computed from `renderable_cards`, not `related_reads.cards`**: `templates.py:9490` computes `renderable_cards` first, then passes it to both `build_row_one_saved_article_local_related_read_connection_brief` and `build_row_one_saved_article_local_related_read_lanes`. ✓
- **HTML escaping**: all card-derived text (source names, reference names/labels, lead, title, metric labels) goes through `_esc`. The escape test confirms `<script>` → `&lt;script&gt;` and `"` → `&quot;`. ✓
- **Omit brief when no renderable cards**: `_render_saved_article_local_related_reads` returns `""` before ever calling the brief builder when `not rendered_cards`. `test_render_local_article_page_omits_related_read_connection_brief_without_safe_cards` covers this path. ✓
- **Render order (brief before lanes/grid)**: the `{connection_brief}` interpolation appears before `{body_html}` in the section f-string (`templates.py:9517–9518`), and the order test confirms index ordering. ✓
- **No new routes, links, or hrefs in the brief**: no `<a>` tags in any brief helper. The brief is copy, metrics, and tag chips only. ✓
- **Builder returns `None` for empty input**: `test_saved_article_local_related_read_connection_brief_returns_none_without_cards` covers this. ✓
- **Signal/source count consistency**: `signal_count = len(signal_references)` and `source_count = len(source_names)` — both are counts of the displayed (capped) sets. The dedup/caps test confirms at lines 811–821. ✓
- **`dek` field not present on the dataclass**: `assert not hasattr(brief, "dek")` at line 750 guards against the draft-spec regression. ✓
- **Lane label stable ordering** (`shared_signal` → `same_section` → `same_source`): confirmed by test at lines 757–766. ✓
- **Normalization deduplication** (whitespace, case): the caps test uses `" TheRow "` / `"the row"` inputs to confirm `normalize_row_one_paragraph` + `casefold` dedup produces `"The Row"` once. ✓
- **CSS positioned correctly** (after `.saved-article-local-related-read-lane-header p`, before `.saved-article-local-related-read-card`): `templates.py:2676–2711` is between lines 2672 and 2712 — confirmed. ✓
- **CSS selector coverage test**: `test_row_one_render.py:18002–18005` asserts `.saved-article-local-related-read-connection-brief`, `-copy`, `-metrics`, `-tags` all appear. ✓
- **No contract leakage**: workflow denylist (`test_workflows.py:720–730`) covers all class names, dataclass names, Chinese text, and artifact stems. Denylist targets the JSON contract payload, not the generated HTML, so no false-positive from the brief rendering in article pages. ✓
- **Workflow sentinel**: `test_stage_381_saved_local_article_related_read_connection_brief_stays_generated_site_only` monkeypatches `_render_saved_article_local_related_read_connection_brief` with `raising=True` and proves the site-generation pipeline runs clean without it. ✓
- **Docs boundary test**: paragraph appears before "Stage 380adds" in both README.md and docs/row-one.md, and all stale-phrase negations pass. ✓
- **Plan review records**: all four records are present with complete output and no remaining Critical or Important findings per both rereviewers. ✓
- **Full suite**:421 tests pass, ruff clean. ✓

---

**One fix needed before commit:** Important finding I1 (singular grammar in the lead sentence). The test for the no-signals lead branch must be updated to assert the corrected string after the fix.

END_OF_REVIEW
