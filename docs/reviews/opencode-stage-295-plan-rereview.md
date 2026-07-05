# opencode Stage 295 Plan Rereview

GLM 5.2 max variant. Focused rereview of I-1 and M-1/M-2/M-4/M-5 only.
No files edited.

## Findings

**No Critical findings. No Important findings.**

All in-scope findings from the prior review are resolved. Details below.

### Important — prior I-1: RESOLVED

Task 2 Step 3 (plan lines 287-311) now replaces the strict list equality with the
full ordered expected list, including the previously-under-specified topic-mix
and heat-watch entries:

1. Read first: The Row signal
2. Active sections: Top Stories, Brand Moves
3. Briefing topics: The Row
4. Topic mix: 1 brand
5. Heat watch: 1 positive heat signal, highest +4
6. Follow-up path: Key Takeaways, Signals To Watch

I verified the values against the live fixture
`test_row_one_app_payload_includes_edition_brief_for_clients`
(`tests/test_row_one_app_contract.py:400`):

- The added `brand_story` carries `entity_refs=[The Row brand]` and
  `heat_delta=4`; the base `_edition()` story has no `entity_refs` and no
  `heat_delta`. That yields exactly one brand topic and exactly one positive
  heat delta of +4, matching "Topic mix: 1 brand" and
  "Heat watch: 1 positive heat signal, highest +4".
- The insertion order (topic-mix then heat-watch, before the follow-up path
  point) is consistent with the GREEN change in Task 3 Step 3.
- The sibling test at `tests/test_row_one_app_contract.py:463`
  (`..._omits_unrenderable_path_link`) uses a fixture with no entity refs and no
  heat delta, so both new points correctly stay absent and its 2-point
  expectation remains valid without modification.

### Minor — prior M-1: RESOLVED

Task 4 Step 4 (plan lines 535-549) no longer offers an either/or; it commits to
adding a single new test,
`test_row_one_docs_describe_stage_295_edition_brief_content_organization`, and
Step 5's focused command (plan lines 556-559) uses that same name.

### Minor — prior M-2: RESOLVED

Task 2 Step 4 (plan lines 325-328) now frames
`tests/test_row_one_briefing_topics.py` correctly as regression coverage that
"may already pass," distinguishing it from the genuinely-RED app-payload and
updated edition-brief expectations.

### Minor — prior M-4: RESOLVED

Task 3 Step 2 (plan lines 402-419) guards the heat-delta read with
`isinstance(heat_delta, int) and not isinstance(heat_delta, bool) and
heat_delta > 0`, excluding the `bool`-subclasses-`int` edge case.

### Minor — prior M-5: RESOLVED

Task 5 Step 3 (plan lines 611-630) now documents that `rg` may exit 1 on a
sparse-data day and directs inspecting `data/edition.json` before treating it as
a failure. (It does not add `|| true`, but the explicit note satisfies the
finding.)

## Out of scope

M-3 (explicit omission-path test) was not in the requested rereview scope and
remains an unaddressed optional suggestion. It does not block implementation.

## Verdict

The revised plan is approved for implementation. No Critical or Important
findings remain; I-1 and M-1/M-2/M-4/M-5 are all resolved.
