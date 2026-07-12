
## Stage 381 Cross-Review (opencode, after Claude code rereview)

I independently re-walked the builder, the template render path, the evidence-bridge filtering, the escape test, the workflow sentinel, and the docs boundary. I agree with the Claude code rereview: **the only Important finding (I1, singular lead) is correctly fixed**, and no new Critical or Important issues are introduced.

### Verification of resolved finding

**I1 — singular `lead` at `card_count == 1`**

`src/fashion_radar/row_one/saved_article_local_related_reads.py:165`:

```python
local_read_count = f"{card_count} local {'read' if card_count == 1 else 'reads'}"
```

Both the `signal_references` branch (`:167-176`) and the context branch (`:177-184`) interpolate `local_read_count`, so `card_count == 1` produces `"1 local read"` in English on both paths. Chinese form keeps `"{card_count} 篇本地阅读"` which is invariant for singular/plural — correct.

The previously false-positive builder test `test_saved_article_local_related_read_connection_brief_uses_context_lead_without_signals` (`tests/test_row_one_saved_article_local_related_reads.py:855-876`) now asserts the corrected singular form:

```python
"This path connects 1 local read through section or source context already "
"saved in ROW ONE."
```

The render test `test_render_local_article_page_related_read_connection_brief_uses_only_safe_cards` (`tests/test_row_one_render.py:574-612`) sets up exactly one safe card and asserts `"1 local read"` and `"1 source"` in `brief_html`. Real runtime state (`card_count == 1` after unsafe-card filtering) is now covered without grammatical regression. **Fixed. ✓**

### Independent checks (no regressions)

1. **Brief derived from `renderable_cards`, not raw `related_reads.cards`** — `templates.py:9483-9497` filters each card through `_render_saved_article_local_related_read_card` (which calls `_safe_saved_article_local_related_read_href`) before building the brief. The `card_count` therefore can never include unsafe cards. ✓

2. **Evidence-bridge count consistency** — `_saved_article_local_related_read_connection_brief_cards` (`templates.py:9525-9544`) re-wraps each renderable card and strips any bridge whose `current_href` fails `_safe_saved_article_local_related_read_current_href` or whose `candidate_href` fails `_safe_saved_article_local_related_read_href`. These are the same two predicates used by `_render_saved_article_local_related_read_evidence_bridge_row` (`templates.py:9785-9795`). The summed `len(card.evidence_bridges)` therefore matches exactly the bridge rows rendered on the cards. The unsafe-bridge render test (`tests/test_row_one_render.py:4163-4177`) asserts `"0 bridges"` and `"0 条证据连接"` when all bridges are unsafe. ✓

3. **Bilingual metric values** — Each `_render_saved_article_local_related_read_connection_metric` call (`templates.py:9552-9586`) receives a `LocalizedText` with both `en` (`_count_label(...)` handles singular/plural) and `zh` (`"篇本地阅读"`, `"个来源"`, `"个信号"`, `"条证据连接"`). The render test asserts `"2 个来源"`, `"1 个信号"`, `"1 条证据连接"` in the metrics slice. ✓

4. **Escaping** — `title`, `lead`, metric `value`/`label`, lane-label chips, signal-reference `name`/`label`, and source-name chips all pass through `_esc` inside `_render_saved_article_local_related_read_connection_brief` and `_render_saved_article_local_related_read_connection_tags`. The escape test (`tests/test_row_one_render.py:3990-3992`) explicitly verifies `reference.label` is escaped within a brief chip (`"Brand &lt;script&gt;alert(&quot;label&quot;)&lt;/script&gt;"`). ✓

5. **Render order** — `{connection_brief}` interpolates before `{body_html}` in the section f-string (`templates.py:9520-9521`). `body_html` is either `lanes_html` or the flat-card grid fallback. The lanes test (`tests/test_row_one_render.py:4073-4077`) confirms the brief appears before the grid in the fallback path too. ✓

6. **Brief omitted when no renderable cards** — `_render_saved_article_local_related_reads` returns `""` at `templates.py:9488-9489` before the brief builder is ever invoked when `rendered_cards` is empty. `test_render_local_article_page_omits_related_read_connection_brief_without_safe_cards` (`tests/test_row_one_render.py:4019-4035`) covers this. ✓

7. **Workflow sentinel** — `test_stage_381_saved_local_article_related_read_connection_brief_stays_generated_site_only` (`tests/test_workflows.py:1693-1786`) monkeypatches `row_one_render.build_row_one_saved_article_local_related_reads` (resolved at call time via module global lookup at `render.py:567`) to force a real safe card into every article page, and wraps `_render_saved_article_local_related_read_connection_brief` with `raising=True`. It asserts: `calls` non-empty, brief selector present in at least one `articles/*.html` (excluding `articles/index.html`), and absent from `index.html`, all `details/*.html`, and all `data/articles/*.json`. **This proves both that the renderer is exercised and that the feature stays generated-site-only.** ✓

8. **Contract denylist** — `tests/test_workflows.py:718-730` adds Stage 381 identifiers (class name, dataclass name, snake_case stems, kebab-case stems, Chinese title `"关联阅读简报"`, English title `"Connection Brief"`) to the denylist against `generated_contract_payload` (built only from edition/manifest/runtime JSON at `:441-448`). The brief is never serialized to JSON, so these hold. ✓

9. **Docs boundary** — The Stage 381 paragraph is present verbatim in `README.md:256` and `docs/row-one.md:473`, immediately before the Stage 380 paragraph. `test_row_one_docs_describe_stage_381_related_read_connection_brief_boundary` asserts both placement and the full stale-phrase denylist. The "generated-site only" (no hyphen) wording is locked in consistently across docs and test — this is the accepted m2 cosmetic from the plan review. ✓

10. **Builder helper correctness** — `_related_read_connection_signal_references` (`:198-216`) and `_related_read_connection_sources` (`:219-235`) cap at `SAVED_ARTICLE_LOCAL_RELATED_READS_MAX_REFS == 3` via early-return/break, dedupe via `casefold()`-keyed `seen` sets, and normalize via `normalize_row_one_paragraph`. The cap-3 dedupe test (`:813-852`) confirms whitespace/case normalization and the cap. `_related_read_connection_lane_labels` (`:238-253`) emits lane labels in the stable `shared_signal → same_section → same_source` order. ✓

### Minor observations (not blocking, carried from prior reviews)

- **m1**: Render tests that slice `brief_html` between the brief opener and the lanes opener (`tests/test_row_one_render.py:3907-3912`, `:3996-4001`, `:4166-4171`) implicitly assume lanes are present. If the sole safe card had an unrecognized reason triggering grid fallback, `section_html.index('<div class="saved-article-local-related-read-lanes">', brief_start)` would raise `ValueError` instead of failing cleanly. All current test setups route into a lane by default reason, so this is robust today.
- **m3**: `reference.name.strip()` / `source_name.strip()` guards in `_render_saved_article_local_related_read_connection_tags` (`templates.py:9633, 9641`) duplicate blankness checks already enforced by the builder's `normalize_row_one_paragraph` + `if not name` path. Harmless and matches the pattern in the existing references-chip renderer.

No remaining Critical or Important findings.

END_OF_REVIEW
