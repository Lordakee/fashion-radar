Critical: None.

Important: None.

Minor:
- `docs/source-boundaries.md:63-64` says `community-candidates` “prints aggregate candidate phrases.” This is acceptable, but “prints aggregate candidate phrase metrics” would be slightly more precise and better aligned with the documented implementation.
- `docs/architecture.md:137-161` command-flow example does not include `community-candidates`, even though the architecture text does document it elsewhere. This is not blocking because the command is covered in the component and boundary sections plus the user-facing community docs.

Review summary:
- Stage 27B appears to stay within documentation-only scope for the intended user-facing files, with non-doc diffs matching the stated out-of-scope Stage 27A / pre-existing areas.
- The docs accurately describe `fashion-radar community-candidates PATH [OPTIONS]` as a one-file, local, read-only, in-memory pre-import preview over a supplied CSV/JSON handoff file and local config.
- The required output exclusions are documented: no supplied input file path, row URLs, row titles, summaries, raw text, normalized keys, candidate contexts, or representative item details.
- I found no blocking unsafe positive claims implying proof of demand, platform coverage, source quality/ranking, source acquisition, scraping, monitoring/watchers, scheduling, report/dashboard generation, database import/SQLite writes, entity YAML/config generation, or source connectors.
- No command mistakes or stale user-facing references appear significant enough to block completion.

APPROVED FOR STAGE 27B DOCS COMPLETION.
