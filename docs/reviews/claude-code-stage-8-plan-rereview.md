Critical

- None.

Important

- The `run` acceptance test still does not strongly prove that `entity_config` is passed into candidate report generation. It only asserts that `"margaux"` is absent from `payload["candidates"]`. That can falsely pass if candidate discovery is not invoked, returns an empty list, fails to extract the configured phrase, or filters the phrase for some unrelated reason. Strengthen it by seeding both:
  - a configured phrase such as `The Row Margaux bag`, which must be absent, and
  - an unconfigured phrase such as `Le Teckel bag`, which must be present.
  
  The test should assert the report contains the unconfigured candidate while excluding the configured entity phrase. That makes the test prove both that candidate generation ran through `run` and that loaded `entities.yaml` was actually used.

- Serialization safety tests are improved but still not fully proof-oriented unless the fixture injects sentinel internal values. The current negative assertions look for strings such as `"raw reason must stay internal"`, `"raw alias must stay internal"`, and `"raw context must stay internal"`, but the shown report fixture does not appear to store those exact sentinel values in `item_entities.reason`, `item_entities.alias`, `context_terms`, or extraction internals. Without seeding those values, the test can pass even if those fields would leak in real output. Add a fixture row with sentinel alias/reason/context terms and assert those exact values are absent from candidate JSON and Markdown.

Minor

- The stored-entity filtering predicate is now unambiguous in the design and implementation requirements: filter stored `item_entities.entity_name` and `item_entities.alias` where `confidence >= scoring.min_match_confidence`, without requiring `reason == "accepted"`. The tests cover low-confidence versus high-confidence rows, which is good. One small improvement: add a high-confidence row with a non-`accepted` reason value and assert it is still filtered. This would directly lock in the “do not require reason” contract.

- The read-only `candidates` CLI plan is substantially stronger and should prevent missing DB/data-dir creation by checking `db_path.exists()` before engine creation and using a read-only SQLite URI for existing DBs. However, the test suite would be stronger with one additional case for an existing incompatible or empty SQLite file: invoke `fashion-radar candidates`, expect a non-zero user-facing schema error, and assert no `schema_metadata`/tables were created. The plan text already requires this, so this is a coverage hardening item rather than a design blocker.

Answers to the review questions:

1. The updates resolve the threshold, label-contract, read-only-connection, predicate-specification, overlap, normalization, dashboard, single-token, and wheel-glob issues at the design/plan level. Two previous Important areas are not fully resolved at the test-proof level: the `run` acceptance test can false-pass, and serialization safety needs seeded sentinel internals.

2. Yes. The candidate thresholds and label contracts are now unambiguous:
   - `review_*` is the output inclusion floor.
   - `min_current_mentions` / `min_distinct_sources` are label thresholds for `new_candidate` and `rising_candidate`.
   - `rising_growth_ratio` is candidate-specific.
   - `review` is the included-but-not-new-or-rising fallback label.

3. Yes at the plan/requirements level. The CLI now explicitly checks database existence before engine creation, avoids parent directory creation, uses a read-only SQLite URI for existing DBs, avoids `initialize_schema()`, inspects schema compatibility read-only, and fails non-mutating on incompatible schemas. Add the existing-incompatible-DB test noted above for stronger enforcement.

4. Not yet. The current `run` integration acceptance test is directionally correct but not strong enough to prove `entity_config` is passed into candidate generation because an empty candidate list would pass. Add a simultaneous positive assertion for an unconfigured candidate.

5. The predicate itself is precise enough. The tests are mostly sufficient for confidence-threshold behavior, but they should add a high-confidence/non-accepted-reason case to prove `reason` is intentionally ignored.

6. The serialization safety requirements are sufficient, but the planned tests need sentinel internal values in the fixture to be sufficient. Field-name exclusions like `normalized_key`, `content_hash`, DB ids, and `normalized_url` are useful; raw alias/reason/context leakage should be tested with actual seeded values.

7. No remaining architectural Stage 8 blockers are present. The feature remains no-schema, local-only, deterministic, report/CLI/dashboard scoped, and within the stated source/safety boundaries. The remaining issues are test-plan fixes before implementation.

Approved after fixes
