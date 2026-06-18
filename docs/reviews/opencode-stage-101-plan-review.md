# Stage 101 Plan Review

## Findings

### No Critical blockers

### No Important blockers

### Minor

**M1. Partial phrase overlap with `tests/test_cli_docs.py::test_first_run_guide_documents_paths_outputs_dashboard_reset_and_boundaries` (line 922).**
That existing test already asserts ~8 of the 10 Stage 101 phrases (in loose form, against the whole document): `does not run live collection`, `does not run \`collect\`, \`run\`, or \`dashboard\``, `should not create files under repo \`data/\` or \`reports/\``, `browser automation`, `account login`, `cookies/sessions`, `source/platform connectors`, `external services` (`tests/test_cli_docs.py:951-974`). Stage 101 adds two genuine increments: (a) **section-scoped** extraction (asserts the phrases live *inside* `## Boundary`, not just anywhere in the doc), and (b) **four new phrases** the CLI test does not cover: `candidate and trend outputs are local sample content checks from the checked-in example`, `not proof of demand`, `not platform coverage`, `not source ranking`. This is acceptable and consistent with the Stage 90-100 pattern of standalone per-doc boundary tests sitting alongside the broad CLI docs test, but the spec/plan should acknowledge the overlap so future maintainers don't see double coverage as accidental. The plan's spec `Risks` section is the natural place for this note.

**M2. Boundary-style language in `## Optional Expanded Watchlist Sample` is intentionally out of scope — worth stating.**
`docs/first-run.md:185-187` contains parallel boundary language (`does not prove demand`, `does not verify platform coverage`, `does not add connectors`). The Stage 101 guard correctly scopes only to `## Boundary` and will not catch drift in the Watchlist section. The spec's `Scope → Out of scope` list does not explicitly mention this; consider one line so it is clear the omission is deliberate rather than an oversight.

### Nit

**N1. `_section` helper behavior when `## Boundary` is the terminal heading.**
`docs/first-run.md` currently ends with `## Boundary`, so `text.split(marker, 1)[1].split("\n## ", 1)[0]` returns the trailing slice with no terminator. This is correct and robust today. If a future editor appends a new `##` section after Boundary, the helper still isolates Boundary correctly — desired behavior. No change needed; flagging only so the test author is aware the assertion is genuinely section-scoped, not file-tail-scoped.

---

## Review Question Answers

1. **Protects a real boundary without changing product behavior?** Yes. `## Boundary` in `docs/first-run.md:216-226` contains substantive local-sample boundary claims, the test pins them, and the plan's allowed-changes list (`tests/test_first_run_docs.py` + review artifacts only) plus the explicit disallowed list (`docs/first-run.md`, `src/`, `scripts/`, `examples/`, configs, schemas, `uv.lock`, CI, runtime smoke, `test_cli_docs.py`) keeps product behavior untouched.

2. **Planned phrases present and narrowly scoped to `## Boundary`?** Yes. I traced all 10 phrases through `_normalized` (whitespace collapse + `casefold`) against the actual section text — all 10 match, including the line-split phrase 7 (`"candidate and trend outputs are local sample content checks from the checked-in example"`), which concatenates correctly. The `_section(text, "Boundary")` helper restricts assertions to that one section.

3. **Avoids overlap with recent docs-boundary stages?** Yes at the stage level — each prior stage targets a different doc (`dashboard.md`, `scheduling.md`, `candidate-discovery.md`, `source-packs.md`, etc.); Stage 101 is the only one touching `docs/first-run.md`. The only overlap is with the *non-boundary* broad CLI docs test (finding M1), which is the established pattern and not a stage collision.

4. **Verification commands sufficient?** Yes. Task 2 runs focused pytest, adjacent pytest (existing `tests/test_first_run_smoke.py` + new docs test), ruff `check` + `format --check`, and `git diff --check`. Task 4 adds the full release gate: release hygiene, full pytest with proxy vars unset, repo-wide ruff, `uv lock --check`, mirror-URL scan, `uv.lock`/`pyproject.toml` diff guard, staged hygiene, and staged secret scan. This exceeds what a docs-only guard requires, in the correct direction.

---

## Verdict

**No Critical or Important blockers.** The plan is approvable as written. Addressing M1/M2 is optional (spec commentary only, no code or scope change). Proceed to Task 2.
