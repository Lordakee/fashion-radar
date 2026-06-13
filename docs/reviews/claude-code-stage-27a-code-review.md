## Critical

None.

## Important

None.

## Minor

None.

## Review notes

- The new `community_candidates.py` implementation stays in-memory and reuses `load_manual_signal_rows()`, `extract_candidate_phrases()`, `configured_entity_keys()`, `ScoringSettings`, and `CandidateDiscoverySettings` as planned.
- CLI validation order is appropriate: Typer-handled option validation occurs before command execution, `--as-of` is parsed before config/file access, config loads before input read, and input-file errors are path-sanitized.
- JSON and table output are aggregate-only and do not expose local paths, row URLs, row titles/summaries/raw text, normalized keys, contexts, representative items, source/import paths, or private/account fields.
- The command does not open SQLite, initialize schema, write artifacts, touch dashboard/report state, recurse directories, collect sources, or call external services.
- Focused tests cover the required Stage 27A behaviors, including invalid option handling, invalid config ordering, clean input-file errors, privacy boundaries, thresholds, known-entity suppression, fallback source name, duplicate suppression, `limit=0`, disabled discovery, and table sanitization.
- I did not identify broad docs/release/commit/push work mixed into Stage 27A from the reviewed files.

APPROVED FOR STAGE 27A COMPLETION.
