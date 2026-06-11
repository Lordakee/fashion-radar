Critical

- None found.

Important

- `src/fashion_radar/models/report.py:52-65`, `src/fashion_radar/reports.py:120-133`, `src/fashion_radar/reports.py:256-289`, `src/fashion_radar/cli.py:291-307`, `src/fashion_radar/cli.py:439-445` — Candidate outputs expose internal extraction labels via the public `contexts` field. `CandidateReport` includes `contexts`, `_candidate_report()` copies `metric.contexts`, JSON output dumps the full model, and Markdown renders `Context labels: ...`. The values originate from extraction internals such as `"proper_name_span"`, `"fashion_anchor"`, and `"single_token"` in `src/fashion_radar/discovery/candidates.py:477`, `src/fashion_radar/discovery/candidates.py:502`, and `src/fashion_radar/discovery/candidates.py:531`. This violates the Stage 8 boundary that candidate JSON/Markdown/dashboard outputs should be public-safe and free of internal DB/matcher/extraction fields. Fix by removing `contexts` from public `CandidateReport`/CLI JSON/Markdown output, or mapping them to deliberately public-safe descriptions if needed.

- `src/fashion_radar/discovery/candidates.py:195-198`, `src/fashion_radar/discovery/candidates.py:245-258` — Stored known-entity filtering is not bounded by `as_of`, so future `item_entities` rows can suppress candidates in historical/backdated reports. `discover_candidates()` correctly windows candidate item mentions by `baseline_start`/`as_of`, but `_stored_entity_keys()` selects every `item_entities` row with sufficient confidence without joining to `items` or filtering `items.collected_at <= as_of`. That makes candidate results for a fixed `as_of` change after later collection/matching, which undermines deterministic report snapshots. Fix by deriving stored known keys only from rows whose associated item was collected no later than the report `as_of`—and ideally within the same local data snapshot semantics used by candidate mentions.

Minor

- `src/fashion_radar/discovery/candidates.py:159-171`, `src/fashion_radar/models/entity.py:54-55` — Configured entity filtering ignores `active_from` / `active_until`. `configured_entity_keys()` unconditionally treats all configured entity names and aliases as known, even when an entity is inactive for the report date. This can suppress candidates outside an entity’s configured active window. If active windows are intended to affect matching/report semantics, candidate known-key filtering should use the report `as_of` when evaluating configured entities.

Approved after fixes
