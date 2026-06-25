# Stage 199 Code Review Prompt

Review the Stage 199 implementation in `/home/ubuntu/fashion-radar`.

Goal: add aggregate match-evidence summaries to daily entity reports so users can
see why tracked entity matches are credible without exposing raw matcher
internals.

Please review these files:

- `src/fashion_radar/models/report.py`
- `src/fashion_radar/reports.py`
- `tests/test_reports.py`
- `tests/test_cli.py`
- `scripts/check_first_run_smoke.py`
- `tests/test_first_run_smoke.py`
- `docs/scoring.md`
- `CHANGELOG.md`
- `docs/superpowers/plans/2026-06-25-stage-199-aggregate-match-evidence-report-plan.md`

Check specifically:

1. The new `EntityMatchEvidence` model is additive, stable in JSON shape/order,
   and forbids extra fields.
2. `EntityReport.match_evidence` is populated from existing accepted
   `item_entities` rows joined to `items`, using `entity_name`, `entity_type`,
   the current report window, and the report `min_match_confidence`.
3. Duplicate rows for the same entity/item choose the highest confidence and,
   when tied, the lexicographically smallest reason.
4. Reason buckets match the plan: `accepted`, `context`, `parent_brand`,
   `safe_alias`, and `other`.
5. Confidence stats are rounded to four decimals in JSON and rendered to two
   decimals in Markdown, including the `min == max` range form.
6. Markdown and JSON reports expose aggregate counts/stats only, not aliases,
   context terms, item ids, normalized URLs, raw reasons, or per-row matcher
   explanations.
7. First-run smoke and CLI tests validate the new contract without brittle false
   positives.
8. Docs and changelog are accurate and do not imply demand proof, platform
   coverage verification, ranking, source/social connector expansion, scraping,
   compliance review, or external-tool behavior.

Return findings in this format:

- Critical: defects that must be fixed before commit/push.
- Important: correctness, contract, or maintainability issues that should be
  fixed in this stage.
- Minor: optional improvements or follow-up notes.

If there are no Critical or Important findings, say that clearly.
