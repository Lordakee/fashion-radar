## Stage 288 Code Review — Findings

Reviewed: `src/fashion_radar/row_one/templates.py`, `tests/test_row_one_app_contract.py`, `tests/test_row_one_render.py`. Verified with full row_one suite (170 passed) and `ruff check` (clean). `mypy` is not part of this project's toolchain (only `ruff` is configured in `pyproject.toml`).

### None — no Critical or Important issues.

### Question 1 — `_signal_synthesis_meta_label()` escaping / language toggle
- **Escaping preserved.** Every interpolated value is wrapped in `_esc()` at `templates.py:1504-1511` (`label`, `story_label_en/zh`, `evidence_label_en/zh`, `heat_label_en/zh`). Counts are `int`-typed at the call site (`templates.py:1461-1468`) before being formatted, so they cannot carry markup.
- **Toggle convention matches.** Uses paired `<span data-lang="en">…</span><span data-lang="zh">…</span>`, identical to neighboring code (e.g. `templates.py:1448-1449`, `1530-1531`). Works with the existing CSS rules at `templates.py:1137-1140`.
- The `label` string comes from `_signal_reference_label()` (single-string, not localized), so duplicating it into en/zh spans is the correct way to render it under the toggle — same value in both, functionally equivalent to the previous single `<span>`.
- Bonus polish: proper pluralization (`1 story` vs `N stories`, `1 evidence link` vs `N evidence links`) — improves on the old always-plural `stories` / mass-noun `evidence`.

### Question 2 — contract test coverage
`test_row_one_app_contract_orders_signal_synthesis_within_group` at `tests/test_row_one_app_contract.py:530-636` cleanly isolates every sort criterion in `_signal_synthesis_sort_key` (`render.py:305-312`):

| Rank | Brand | (heat_sum, evidence, stories) | Criterion exercised |
|---|---|---|---|
| 1 | Sum Leader | (9, 2, 2) | **positive_heat_delta_sum** — beats Max Decoy despite lower `max_heat_delta` (5 < 8). "Max Decoy" is a deliberate decoy proving the sort key uses `positive_heat_delta_sum`, not `max_heat_delta`. |
| 2 | Max Decoy | (8, 1, 1) | heat_sum tier |
| 3 | Evidence Leader | (4, 3, 1) | **evidence_count** — same heat_sum as ranks 4-7 but more evidence |
| 4 | Story Leader | (4, 2, 2) | **story_count** — same heat_sum+evidence as Story Decoy, more stories |
| 5 | Story Decoy | (4, 2, 1) | story_count runner-up |
| 6 | Alpha Name | (4, 1, 1) | **name casefold tie-break** |
| 7 | Zeta Single | (4, 1, 1) | name casefold runner-up |

All four criteria (positive heat sum, evidence count, story count, name tie-break) are positively covered. Test also asserts `signal_count`/`group_count` aggregates and runs `_schema_validator().validate(payload)`. The 2-story "Sum Leader" case (one story with `heat_delta=0`) also confirms negative/zero deltas are clamped per-story via `max(..., 0)` in `briefing_topics.py:43-46`.

### Question 3 — minimal & schema-compatible
- Diff stat: `+169 / -5` across exactly the three in-scope files; no `pyproject.toml`/`uv.lock` touched.
- The change is render-layer only. The JSON payload fields (`story_count`, `evidence_count`, `positive_heat_delta_sum`, `max_heat_delta`, `label`) are untouched, so schema `row-one-app/v6` (`schemas/row-one-app.schema.json:25`) remains valid — confirmed by the passing schema validator inside the test.
- Helper extraction (`_signal_synthesis_meta_label`) is a pure refactor with no behavior change beyond localization/pluralization; signature uses keyword-only args (`*`), preventing positional-call drift.

### Question 4 — blockers before commit
None. Ship it.

### Minor observations (non-blocking, optional)
- **Empty `label` emits two empty spans.** If `signal.get("label")` is `""`, output contains `<span data-lang="en"></span><span data-lang="zh"></span>`. Harmless (CSS still hides one), and pre-existing behavior, but if you want a tidier render you could skip the label pair when `label` is falsy. Not required for Stage 288 scope.
- **"local delta" wording in ZH.** `+{heat_delta} 本地增量` reads naturally; just flagging that `heat_delta` here is `max_heat_delta` (per-story max), not `positive_heat_delta_sum`. The label "local delta" / "本地增量" is generic enough to cover either, and matches the pre-Stage-288 semantics, so no change needed — but worth noting if a future stage wants to distinguish "max delta" from "total delta" in the UI.

Recommended action: commit Stage 288 as-is.
