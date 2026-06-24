# Stage 191 Plan Review

## Critical

None. The Stage 191 direction is coherent and the bounded contract change is
sound. No scope violations, design flaws, or blocking technical risks were
found. Findings below are specification/wording gaps and process nits that can
be resolved during implementation without changing the design.

## Important

1. Docs required-phrase set is not satisfiable by the plan's suggested wording.
   `test_daily_brief_docs_are_bounded_and_discoverable`
   requires all six phrases contiguously in every file in
   `DAILY_BRIEF_DOCS`, including CHANGELOG. The phrase
   `no platform coverage verification` is not a contiguous substring of the
   plan's recommended sentence "...provides no demand proof or platform
   coverage verification." Every one of README, docs/cli-reference.md,
   docs/architecture.md, docs/daily-digest.md,
   docs/github-upload-checklist.md, and CHANGELOG.md must therefore contain a
   distinct contiguous sentence such as "...provides no demand proof and no
   platform coverage verification." Add an explicit canonical sentence and
   require it.

2. Report-level summary pluralization is underspecified. The empty-report test
   pins the exact 0-count string:
   `"...0 tracked signals, 0 candidate signals needing review, 0 source
   caveats..."`, while the spec example shows the 1-count form
   `"...1 candidate signal needing review, 1 source caveat."` The
   `_daily_brief_summary` helper must therefore pluralize `signal->signals` and
   `caveat->caveats` based on count. Spell out the singular/plural rule and
   exact separator/punctuation for the helper.

3. Brief item `title` mapping is implicit, not stated. Tests assert
   `sections[0].items[0]["title"] == "The Row"` and
   `json_payload["brief"]["sections"][0]["items"][0]["title"] == "The Row"`,
   but the plan never says `title = entity.entity_name` for tracked items or
   `title = candidate.phrase` for candidate items. State the title source for
   each `kind` explicitly so the RED->GREEN path is unambiguous.

## Minor

1. first_run_smoke fixture edits are synchronization, not a true RED.
   `tests/test_first_run_smoke.py` calls `validate_report_outputs` with
   hand-written fixtures. Once Task 2 Step 1 updates both the fixtures and
   `validate_report_outputs` together, that test passes immediately; the
   genuine RED signal for the smoke surface comes from the real CLI subprocess
   in `scripts/check_first_run_smoke.py` and from
   `test_markdown_report_renders_daily_brief_before_top_signals`.

2. The smoke `report_markdown()` fixture update instruction is vague. The
   extended `validate_report_outputs` must require the brief to mention
   `The Row`, so the fixture's tracked-signal line must literally contain
   `The Row`. Spell out the exact fixture line to avoid a fixture/validator
   mismatch.

3. `_table_cell` is added as a new private helper in reports.py, but the design
   claims it reuses "the same table-cell style already used elsewhere in the
   repo." The existing renderer emits raw summaries without any cell
   sanitization, so there may be no shared canonical helper. Confirm there is
   no existing sanitizer to import; otherwise the brief and existing
   entity/candidate rows will follow divergent escaping rules.

4. Reason-code ordering is part of the JSON contract, but no test pins the
   order; tests only assert membership. Add an order-pinning assertion for at
   least one entity and one candidate item to lock determinism of
   `reason_codes`.

5. Adding `brief` as the second field of `DailyReport` is safe. Reports are
   write-only artifacts, the `default_factory=empty_daily_brief` preserves
   direct construction for existing tests, and existing readers access report
   JSON by key rather than by position.

6. `ruff format --check` has no Markdown risk. Ruff format only processes
   `.py`/`.pyi` files under the current configuration, so the Markdown template,
   spec, and plan are not reformatted by ruff. `git diff --check` remains the
   Markdown whitespace gate.

7. Scope is clean: no new CLI command, no scraping/browser automation/platform
   APIs/social search, no compliance-review feature, no LLM summarization, no
   mutation of `TrendDelta`/`TrendComparison`/`HeatMover`/dashboard projections,
   and no dashboard file changes. The brief is a purely additive, locally
   derived report field.

## Verdict

Approved with non-blocking minors. The design is coherent, the bounded
`DailyReport.brief` contract change is technically sound and backward-safe, the
Pydantic model shapes / key order / default factory / deterministic section
ordering / Markdown rendering are testable, the TDD core genuinely goes RED
before production, the forbidden-scope boundaries are respected, and the
release gate, review artifacts, and `git add` manifest are complete. Address
the three Important wording/specification gaps before coding.
