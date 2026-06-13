APPROVED FOR IMPLEMENTATION

I found no blocking Critical or Important issues in the revised Stage 25 spec/plan as written.

The revisions adequately address the prior review findings:

- The public `CandidateReport` exposure risk is handled by a dedicated `ImportedCandidateRow` / `ImportedCandidatesReview` output contract with `extra="forbid"` and only aggregate-safe fields.
- JSON/table output is explicitly constrained to omit representative items, URLs, titles, summaries, contexts, IDs, normalized keys, match internals, aliases, import paths, source files, account/private/raw fields.
- The read-only SQLite regression is now specific enough: it monkeypatches `imported_candidates_module.create_readonly_sqlite_engine`, calls `query_imported_candidates(...)`, and asserts the factory receives `db_path`.
- Compatibility coverage is broadened to include direct candidate discovery defaults, existing candidates CLI behavior, report, trends, and dashboard candidate/trend paths.
- The plan follows the existing `Literal["table", "json"]` CLI output-format pattern.
- The release/hygiene steps explicitly include `git status --short` and `git diff -- uv.lock`, and reiterate that the existing mirror URL `uv.lock` diff must remain unstaged/excluded.

Minor non-blocking note:

- The plan’s compatibility coverage depends partly on existing report/trend/dashboard tests selected by `-k`. During implementation, ensure those selected tests genuinely exercise the broad call sites affected by the `discover_candidates()` signature change; if the `-k` selection misses a path, add/adjust focused tests rather than relying on the command alone.
