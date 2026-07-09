## Stage373 Code Review

**No Critical or Important issues remain.** The four pre-implementation Critical/Important findings from the plan reviews (C1 `story` scope, C2 circular-import, I1 regex reuse, I2 monkeypatch target, plus opencode I1 filing-cue suppression) are all resolved in the implementation. What follows is a complete ordered findings list.

---

### Critical

None.

---

### Important

None.

---

### Minor

**M1 — `raising=False` in the workflow guard is weaker than necessary.**

`tests/test_workflows.py:1515` patches `build_row_one_local_article_body_section_markers` with `raising=False`. Because the function is imported at `templates.py:40–42`, the attribute exists and the patch works correctly today. But `raising=False` means a future rename of the function silently produces a no-op guard — the patch would succeed while markers flow through unblocked. Changing to `raising=True` would make the guard fail loudly if the target disappears. The project's prior Stage guards (354, 356, 357, …) also use `raising=False`, so this is a consistent pattern, not a Stage-373-specific defect, but it is a latent fragility everywhere it appears.

Resolution: fixed after review. The Stage 373 workflow guard now uses `raising=True`.

**M2 — Dead TDD shim in `test_row_one_render.py` lines 92–107 is permanently unreachable.**

The `try/except ModuleNotFoundError` fallback dataclass for `RowOneLocalArticleBodySectionMarker` was correct TDD scaffolding. The module now exists, so the `except` branch is permanently dead (covered by `pragma: no cover`). No action required — this is the established project pattern for TDD-red stubs — but the shim can be removed on any future cleanup pass.

**M3 — `_support_text` has an untested null path for valid paragraph indices.**

`local_article_body_section_markers.py:134–152`: if `section.body` is blank, all item bodies are blank, and `_paragraph_support` returns `None` (which requires `_excerpt` to produce an empty string despite the paragraph passing `paragraph.strip()`), then `_support_text` returns `None` and `_section_marker` silently skips the section. The scenario is unreachable in practice — a paragraph that passes `paragraph.strip()` will produce a non-empty `_excerpt` — but no test exercises this null return. Low risk given the double fallback in `_excerpt`, but the branch is invisible to the test suite.

**M4 — `zfill(2)` section-position badge is undocumented in the spec.**

`templates.py:17575`: `_esc(str(marker.section_position).zfill(2))` renders the position as a zero-padded two-digit string (e.g., `01`, `08`). The design doc and plan describe only "section title" and "compact support excerpt" for the header; the zero-padding decoration is an implementation addition. It is visually reasonable and consistent with the eyebrow `Section starts here / 本节从这里开始`, but the spec does not mention it. No test asserts the zero-padded form. If the padding convention ever changes, no test will catch a regression.

**M5 — Contract/artifact leakage test is slightly asymmetric across identifier forms.**

`test_row_one_render.py:4456–4468` includes the Python class name `"RowOneLocalArticleBodySectionMarker"` in the forbidden set for generated JSON contracts — a good improvement over prior stages. The denylist also covers `"Article Body Section Markers"` (title-case variant) but not `"RowOneLocalArticleBodySectionMarkers"` (pluralised class name). Both omissions are acceptable given the feature has no collection class, but the asymmetry is worth noting if a future plural form is added.
