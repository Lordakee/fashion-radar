# OpenCode Stage 390 Plan Review

## Verdict

APPROVED - the plan is feasible, internally consistent, contract-safe, and
faithful to the fixed behavior; only Minor polish notes remain.

## Findings

### Critical

No findings.

### Important

No findings.

### Minor

1. `tests/test_review_protocol_docs.py:240-259` is an undeclared verification
   dependency on Worker C's `README.md` and `docs/architecture.md` changes. The
   worker should preserve its exact roadmap phrases and the coordinator should
   keep this module in the full-suite gate.
2. Task 1 Step 4 currently combines the invalid-threshold test and validation
   implementation while expecting PASS. Split it into a strict RED observation
   before the helper and a GREEN rerun afterward.
3. Rename the existing no-date RSS test when its expected classification changes
   from `live/ok` to `live/info/freshness_unknown` so its name remains accurate.
4. Make the updated-only fixture decision concrete: use a minimal Atom 1.0
   entry rather than conditionally attempting RSS 2.0 `<updated>` behavior.
5. State explicitly that a malformed feed with no entries remains a failed parse
   and leaves all three freshness fields `None`; only a successfully parsed empty
   feed reports `dated_records_seen=0`.
6. Note that the liveness timestamp helper intentionally improves on the RSS
   collector's simple `published_parsed or updated_parsed` fallback: it isolates
   conversion errors per key so malformed dates cannot fail the diagnostic.

## Feasibility

The builder signature change is keyword-only and compatible. The
`calendar.timegm` conversion matches the existing RSS collector convention, and
the exact threshold math is correct: exactly 72 hours stays fresh, 72 hours plus
one second becomes stale, ceiling display produces 72 and 73 respectively, and
future entries clamp to zero. Typer 0.26.7 was verified to return exit code 2
with an error containing `x>=1` for `min=1`. Worker write sets are disjoint, and
the final release sequence is fail-fast with archive, installed-wheel, dashboard,
and reviewed-SHA path checks. No dependency or lockfile change is needed.

## Reviewed Scope

Reviewed `AGENTS.md`, `docs/REVIEW_PROTOCOL.md`, the Stage 390 design and plan,
the source-liveness implementation and CLI command, the RSS collector timestamp
convention, and the directly related source-liveness, CLI, documentation, and
review-protocol tests. GDELT internals, collection, storage, scoring, matching,
reports, ROW ONE, frozen external/community/imported commands, dependencies, and
source-pack additions remain outside Stage 390.
