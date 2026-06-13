You are reviewing the Stage 26 implementation plan for this repository.

Repository: `/home/ubuntu/fashion-radar`

Review these files only:

- `docs/superpowers/specs/2026-06-13-stage-26-imported-candidate-evidence-design.md`
- `docs/superpowers/plans/2026-06-13-stage-26-imported-candidate-evidence-plan.md`

Context:

Stage 25 added:

```bash
fashion-radar imported-candidates
```

That command provides an aggregate local read-only candidate phrase list from
retained `manual_import` rows only, and intentionally omits item-level evidence.

Stage 26 proposes:

```bash
fashion-radar imported-candidate-evidence \
  --config-dir ./configs \
  --data-dir ./data \
  --as-of 2026-06-13T12:00:00Z \
  --phrase "Le Teckel bag"
```

The command should show retained local `manual_import` rows whose extracted
candidate phrases match one requested phrase. It is a phrase-scoped drilldown so
a reviewer can inspect why an imported candidate appeared.

Boundaries:

- No source acquisition, platform search, scraping, crawling, browser
  automation, account automation, scheduling, watch folders, external service
  calls, SQLite writes, config writes, report/dashboard writes, persistent
  candidate tables, candidate approval state, or entity YAML draft generation.
- The command intentionally exposes `title` and `url` for the one requested
  phrase because it is a local evidence drilldown. It must still omit summaries,
  raw comments, candidate contexts, normalized candidate internals, match
  reasons, match confidence, aliases, import paths, source files, account
  fields, cookies, sessions, and private/raw fields.
- Evidence matching must reuse the candidate extraction and candidate key
  semantics from existing candidate discovery. It must not use naive substring
  matching.
- The existing `uv.lock` mirror URL diff is pre-existing and must remain
  unstaged/excluded.

Please review for:

1. Correctness and safety of the proposed command shape.
2. Whether public helper wrappers in `discovery/candidates.py` are a reasonable
   way to avoid private helper imports and candidate matching drift.
3. Whether test coverage is sufficient for read-only behavior, missing DB,
   invalid CLI input, no DB mutation, stable JSON keys, table sanitization,
   current/baseline counters, source filtering, and known entity suppression.
4. Whether docs/release checks are adequate.
5. Any risk that the plan implies external/platform coverage, source quality or
   ranking, verified entities, demand proof, scraping, monitoring, or acquisition.

Output format:

- If approved, include the exact phrase: `APPROVED FOR IMPLEMENTATION`.
- If not approved, list findings by severity: Critical, Important, Minor.
- Treat Critical and Important findings as blocking implementation.
