Critical

- None.

Important

- Candidate scoring thresholds need explicit config fields or a tighter label contract before implementation. The design defines `rising_candidate` as requiring a growth-ratio threshold and says `review` is for enough evidence but not enough for `new_candidate`/`rising_candidate`, but the proposed `CandidateDiscoverySettings` has no `rising_growth_ratio`, no review-specific threshold, and no separate score/display threshold. As written, implementers may either hard-code entity scoring’s `rising_growth_ratio`, never produce `review` meaningfully beyond already-filtered candidates, or invent thresholds. Fix by specifying exactly which `ScoringSettings` fields are reused for candidates, or add candidate-specific fields such as `rising_growth_ratio` / `review_min_current_mentions` / `review_min_distinct_sources`, with tests for all three labels.

- The read-only `fashion-radar candidates` CLI has a likely implementation trap: `create_sqlite_engine(path)` currently creates the parent directory and SQLite will create a DB file on connect. The plan correctly says not to create the DB if missing, but it should also require the command to check `db_path.exists()` before creating an engine, and to use a read-only SQLite URI or another explicit non-mutating schema check for existing DBs. Otherwise an incompatible or empty DB path can still be mutated by accidental connection/initialization code.

- The report integration plan does not explicitly require `run` to pass `entity_config` into candidate discovery, even though the architecture depends on filtering configured entity aliases. The plan shows updating `report`/`run` call sites, but only spells out standalone `report` entity loading behavior. Add an acceptance/test case proving `fashion-radar run` writes a report whose candidates exclude configured entities from the just-loaded `entities.yaml`, not only stored `item_entities`.

- “Accepted stored `item_entities`” is underspecified against the actual schema. Current `item_entities` stores all rows passed to `replace_item_matches()` with `reason`, `confidence`, etc.; the plan says filter accepted stored names/aliases but does not state whether to filter all rows, only `confidence >= scoring.min_match_confidence`, only `reason == "accepted"`, or some combination. Since candidate exclusion can over-filter or under-filter, specify the exact predicate and add tests for low-confidence/rejected rows if such rows can exist.

- Representative item safety needs a sharper test. The design says public `contexts` must not contain raw text and JSON must avoid internal fields; good. But report tests explicitly assert summaries are included. If summaries are stored short snippets this is consistent with existing reports, but Stage 8 should add a negative test that candidate JSON/Markdown do not include raw extraction contexts, `normalized_key`, DB ids, `normalized_url`, matcher `reason`, raw aliases, or `context_terms`. Current planned tests only check `content_hash`.

Minor

- The extraction examples are brittle relative to the proposed simple heuristics. “Sandy Liang Mary Jane flats” could reasonably generate overlapping candidates (`Sandy Liang`, `Mary Jane flats`, possibly `Sandy Liang Mary Jane flats`). The plan should define overlap preference/deduplication more precisely, especially whether anchored product phrases may include preceding proper-name brand/designer tokens and how to avoid flooding with nested variants.

- The “contains a known entity key as a complete token span” rule should define token normalization for punctuation and possessives. For example, `The Row’s Margaux bag`, `Tory Burch-Pierced`, and ampersand aliases may otherwise leak composites or over-filter unrelated text. A few focused tests would make this deterministic.

- Dashboard latest-report selection by lexicographic filename is acceptable for current `fashion-radar-YYYY-MM-DD.json` files, but the helper should either document that assumption or parse/report-date sort. If multiple JSON reports exist with nonstandard names or suffixes later, lexicographic sorting may choose the wrong file.

- The dashboard helper plan should specify behavior for malformed latest JSON. A stale/corrupt report should render a clear message rather than crashing Streamlit. This is not a blocker for Stage 8, but it is a useful acceptance criterion for read-only dashboard behavior.

- Single-token candidates are mentioned, but extraction rules “prefer 2 to 5 word phrases” and the provided tests do not cover single-token inclusion/exclusion. Add tests proving single-token candidates are normally suppressed unless aggregate single-token thresholds are met.

- The full verification list is strong. However, the plan’s package smoke installs a hard-coded `fashion_radar-0.1.0-py3-none-any.whl`; if the version changes, this breaks for the wrong reason. Prefer globbing the built wheel in `/tmp/fashion-radar-dist-stage8`.

Answers to the review questions:

1. Yes, the Stage 8 design satisfies the user goal and preserves source/safety boundaries: it uses only retained local SQLite `items`/`item_entities`, adds no collectors or network collection, and frames output as review-only candidate signals.
2. Yes, the no-schema deterministic approach is appropriate for this repo and this stage. It avoids migration risk and is consistent with derived report/dashboard behavior, as long as retained-history limitations are documented.
3. Mostly yes. The proposed module/report/CLI/dashboard boundaries fit existing patterns. The main interface gaps are the exact candidate label thresholds, accepted-match filtering predicate, and ensuring report/run passes `EntityConfig`.
4. The tests are broadly sufficient and executable in style, with the additions above. They cover config defaults, extraction, windowing, filtering, reports, CLI read-only behavior, dashboard report-reading, docs wording, and full verification.
5. Main correctness/data integrity risks are threshold ambiguity, read-only CLI accidental DB creation/mutation, underspecified accepted stored-entity filtering, and incomplete serialization-boundary tests.
6. The stage is somewhat broad but still reasonable: one module plus report/CLI/dashboard/docs/tests. It is not too broad if implementation stays deterministic and avoids expanding extraction into ML/NLP or new collection.
7. The design and plan wording generally avoid viral/global/market-wide/confirmed claims and include explicit grep/tests to enforce this. Keep that wording discipline in report, CLI, dashboard, README, and docs.
8. No fundamental blockers, but the Important items should be fixed in the plan before implementation.

Approved after fixes
