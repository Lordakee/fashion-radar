# Stage 191 Plan Rereview

## Critical

None. The updated excerpts stay inside the stated boundaries: no new CLI
command, no LLM/external API, no source acquisition, no social search, no
compliance-review feature, no trend/heat/dashboard contract mutation. The
canonical scope sentence, summary pluralization, and item title mappings are all
satisfiable and internally consistent.

## Important

None. The three previous Important findings are resolved:

1. **Contiguous scope phrases** - Resolved. A single canonical sentence,
   `It provides no demand proof and no platform coverage verification.`, is now
   mandated anywhere both phrases are required contiguously, and every file in
   `DAILY_BRIEF_DOCS` must contain that exact sentence. This removes the earlier
   satisfiability risk where the two phrases could be split across tokens or
   reworded.

2. **Report-level summary pluralization** - Resolved.
   `_daily_brief_summary` now routes all three counts (`tracked_count`,
   `candidate_count`, `source_caveat_count`) through
   `_count_label(count, singular, plural)`, which returns the singular form only
   when `count == 1` and the plural form otherwise, including `0`. The
   singular/plural strings are explicit per count, including the
   `needing review` participle on candidate signals.

3. **Brief item `title` mappings** - Resolved. The mappings are now fully
   explicit and field-stable: tracked entity -> `entity.entity_name`, candidate
   phrase -> `candidate.phrase`, source-health caveat -> `source.source_name`,
   collector-run caveat -> `run.source_name`. No implicit or inferred title
   derivation remains.

No new Important issue is introduced. The canonical sentence is embedded in the
summary as a contiguous substring, so an exact-match docs test will pass
wherever the summary is emitted. `_count_label` is module-level, so
definition-after-caller ordering is fine in Python.

## Minor

- `docs/trend-deltas.md` and `tests/test_trend_deltas_docs.py` are additive.
  Confirm the doc describes existing trend-delta output rather than implicitly
  specifying a new contract; documenting established behavior keeps the
  "no trend/heat/dashboard contract mutation" boundary intact.
- The new reason-code order assertions are fine, but they should assert an
  order the implementation already produces deterministically, not introduce
  ordering as a new guarantee that could flake on set/dict iteration.
- The Heat Narrative docs parity and exact first-run smoke fixture wording are
  consistent with the first finding fix; ensure the smoke fixture matches the
  summary string verbatim, including the trailing scope sentence and period.

## Verdict

Approve. All three previous Important findings are resolved by the updated
plan/spec excerpts, and the fixes introduce no new Critical or Important issue.
The Minor notes are verification reminders for implementation/tests, not
blockers.
