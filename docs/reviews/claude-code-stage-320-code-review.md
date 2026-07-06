---

## Stage 320ROW ONE Homepage Daily Edit — Code Review

### Summary

No Critical issues. Two Important issues, both fixable with small targeted changes. Several Minor observations.

---

### Critical Issues

None.

---

### Important Issues

**I-1: `_localized_topic_field` raises `KeyError` on missing dict key — `templates.py` lines ~2697, ~3900**

`_localized_topic_field` uses direct key access (`topic[field]`), not `.get()`. Stage 320 calls it in `_daily_edit_topic_fallback_card`:

```python
title = _localized_topic_field(topic, "title")
```

If any `briefing_topics` entry in `app_payload` lacks a `"title"` key, this raises `KeyError` and aborts the entire `render_index_html()` call. The pre-existing `_render_briefing_topic_card` also has this exposure, but Stage 320 extends it into a new fallback code path that is supposed to be defensive (it explicitly returns `None` on unusable data). The contract data from production won't trigger this, but the function's signature gives no indication it can throw.

The fix is minimal — either change `_localized_topic_field` to use `.get()`:

```python
def _localized_topic_field(topic: dict[str, object], field: str) -> LocalizedText:
    value = topic.get(field)  # was: topic[field]
    ...
```

or add a `try/except KeyError` guard in `_daily_edit_topic_fallback_card` before calling it. The `.get()` change is safer and consistent with how `_topic_localized_card_text` already works (`card.get(field)`).

---

**I-2: Docs test anchors on `"Stage 320 adds homepage Daily Edit"` (capital D/E) — `test_row_one_docs.py` line559; plan Task 3 Step 2**

The docs test performs a case-sensitive `.index("Stage 320 adds homepage Daily Edit")` (capital D, capital E). The plan's suggested docs text writes `"Stage 320 adds homepage daily edit"` (all lowercase). If the README/docs text was authored following the plan's template verbatim, the test raises `ValueError: substring not found` at runtime.

Verification: confirm `README.md` and `docs/row-one.md` contain `"Stage 320 adds homepage Daily Edit"` (exact capitalization). If the tests are passing as reported, this is already correct — flag only if the docs were changed after verification.

---

### Minor Issues

**M-1: Double `_safe_daily_edit_href` validation in `_render_daily_edit_card` — `templates.py` line2936**

Card builders already call `_safe_daily_edit_href()` before storing the href in the card dict. The renderer then calls it again:

```python
href = _safe_daily_edit_href(card.get("href")) or "#main-content"
```

This is harmless — the renderer is the correct place to enforce the safety fallback — but the second call is logically redundant. It is worth keeping as a defence-in-depth layer since the card dict uses `dict[str, object]` typing. No change required, but worth noting for future maintainers.

---

**M-2: Signals-to-watch and read-next can both surface the read-first story in edge cases — `templates.py` lines ~2640, ~2818**

When `signal_synthesis` has no usable signals and `briefing_topics` is also empty, `_daily_edit_signals_to_watch` falls through to `_daily_edit_read_first_signal_card`, which builds a "Signals To Watch" card from the read-first block's first story. Separately, `_daily_edit_read_next` also falls back to `_daily_edit_read_first_card` when no `key_takeaways`/`signals_to_watch` blocks have usable cards. Both fallback paths can produce cards for the same story. In the minimal-payload edge case, the homepage Daily Edit section would show the same story headline twice under different card titles. Not a bug per spec (the section still renders valid content) but worth a comment.

---

**M-3: `_int_or_zero` will raise `TypeError` on a non-numeric non-None string — `templates.py` line 3836**

```python
def _int_or_zero(value: object) -> int:
    if value is None:
        return 0
    return int(value)  # raises TypeError/ValueError on e.g. "many"
```

Stage 320 calls this on `signal.get("story_count")`, `signal.get("evidence_count")`, `topic.get("story_count")`, etc. Production payloads always carry integers here, but adversarial `app_payload` input would crash. Pre-existing issue, not introduced by Stage 320. No required fix within this stage.

---

**M-4: `_daily_edit_evidence_note` embeds `signal_synthesis.boundaries` text without length guard — `templates.py` line ~2872**

```python
en=(
    f"Based on {evidence_en}; {boundary_en}; "
    "review the underlying stories before acting."
),
```

`boundary_en` is taken verbatim from `synthesis.get("boundaries")` which could be arbitrarily long. Unlike excerpts elsewhere (which pass through `_meta_description`), this body has no character cap. Purely cosmetic — the text is still safely escaped — but the card body could overflow its grid cell on long boundary strings.

---

### Positive Observations

- **Scope adherence is clean.** No new parameter on `render_index_html()`, no serialization, no new JSON artifact, no schema changes. The private builder pattern (`_daily_edit_cards` →4 named card functions → `_render_daily_edit_card`) keeps the feature fully local to `render_index_html`.
- **Escaping is consistent.** Every string reaching HTML goes through `_esc()`. The render function re-validates `href` at render time, so malformed hrefs added through any code path hit the `#main-content` fallback.
- **Link safety is conservative.** `_safe_daily_edit_href` allows only the three named in-page anchors and paths validated by the existing `validated_row_one_detail_relative_path` route validator. External URLs and `javascript:` schemes are unreachable.
- **Test coverage is strong for the intended risk surface.** The escaping test injects `<script>` tags, external URLs, and a `javascript:` href, and asserts each is neutralized. The fallback tests exercise both the briefing-topic path and the digest-block read-next path independently.
- **The JSON contract boundary tests in `test_workflows.py` correctly assert** `'"daily_edit"' not in generated_contract_payload` and `'"daily_information_layer"' not in generated_contract_payload`, protecting the non-goal boundary against regression.
- **CSS is placed correctly.** `.daily-edit-grid { grid-template-columns: 1fr; }` is inside the existing `@media (max-width: 760px)` block, consistent with every other section.

---

### Required Fixes Before Merge

1. **(I-1)** Change `_localized_topic_field` to use `topic.get(field)` instead of `topic[field]`, or add a `KeyError` guard in `_daily_edit_topic_fallback_card`. The `.get()` change is preferred for consistency with `_topic_localized_card_text`.
2. **(I-2)** Confirm `README.md` and `docs/row-one.md` spell the marker phrase as `"Stage 320 adds homepage Daily Edit"` (capital D, capital E) matching the test expectation on line 559 of `test_row_one_docs.py`.

## Claude Code Stage 320 Review Resolution

- I-1 fixed: `_localized_topic_field()` now handles missing fields with an empty `LocalizedText` instead of raising `KeyError`, and dict payloads tolerate missing `zh` / `en` values.
- Regression added: `test_render_row_one_site_daily_edit_handles_topic_fallback_without_title` covers the missing-title fallback path.
- I-2 confirmed: README.md and docs/row-one.md both use the exact `Stage 320 adds homepage Daily Edit` marker expected by tests.
- Re-verification after fixes: focused render fallback tests passed, Stage 320 focused suite passed, ruff check/format and git diff whitespace checks passed.
