You are doing a focused Stage 26 code rereview.

Repository: `/home/ubuntu/fashion-radar`

Context:

- Stage 26 was previously reviewed in
  `docs/reviews/claude-code-stage-26-code-review.md` and approved with
  `APPROVED FOR STAGE 26 COMMIT`.
- After that review, a read-only subagent found one Important issue:
  `imported-candidate-evidence` JSON exposed `normalized_phrase`, which should
  count as a normalized candidate internal.
- The current working tree contains the fix. Please review only whether the fix
  is correct and whether it introduces any new blocking Stage 26 issue.
- Treat `uv.lock` as out of scope. It has a pre-existing mirror URL diff and
  must remain unstaged/excluded.

Stage 26 goal:

Add `fashion-radar imported-candidate-evidence`, a local read-only command that
shows retained `manual_import` rows whose extracted candidate phrases match one
requested phrase.

Focused review requirements:

1. Public JSON/table/model output must not expose `normalized_phrase`,
   `normalized_key`, normalized candidate internals, extraction contexts, match
   reasons/confidence, aliases, summaries, raw comments, import paths, source
   files, account fields, cookies, sessions, or private/raw fields.
2. It is acceptable for implementation internals to compute a normalized phrase
   locally with `candidate_key()` for matching against `extract_candidate_phrases()`;
   that internal value must not be serialized.
3. Tests should lock the public JSON shape and forbid `normalized_phrase` or
   normalized key/url-style fields in output.
4. The fix should not add scraping, crawling, platform APIs, account automation,
   scheduling/watch-folder behavior, source acquisition, SQLite writes, config
   writes, reports/dashboard writes, candidate approval state, or entity YAML
   draft generation.
5. Stage 26 files may still expose `title` and `url` for one requested phrase
   because this is a local phrase-scoped evidence drilldown.

Suggested commands:

```bash
git diff -- src/fashion_radar/imported_candidate_evidence.py tests/test_imported_candidate_evidence.py tests/test_cli.py docs/superpowers/specs/2026-06-13-stage-26-imported-candidate-evidence-design.md docs/superpowers/plans/2026-06-13-stage-26-imported-candidate-evidence-plan.md
rg -n "normalized_phrase|normalized_key|normalized_url" src/fashion_radar/imported_candidate_evidence.py tests/test_imported_candidate_evidence.py tests/test_cli.py docs/superpowers/specs/2026-06-13-stage-26-imported-candidate-evidence-design.md docs/superpowers/plans/2026-06-13-stage-26-imported-candidate-evidence-plan.md
git diff --name-only
```

Verification already run after the fix:

```bash
.venv/bin/python -m pytest tests/test_imported_candidate_evidence.py::test_imported_candidate_evidence_json_shape_omits_summary_and_match_fields tests/test_cli.py::test_imported_candidate_evidence_command_prints_json_with_stable_keys -q
.venv/bin/python -m pytest tests/test_candidate_scoring.py tests/test_imported_candidate_evidence.py tests/test_cli.py -q -k "candidate_key or stored_entity_candidate_keys or imported_candidate_evidence"
.venv/bin/python -m pytest -q
.venv/bin/python -m ruff check .
.venv/bin/python -m ruff format --check .
git diff --check
git diff -U0 -- README.md docs CHANGELOG.md | rg -n "platform-wide|market-wide|verified demand|real-time monitoring|source acquisition|source-acquisition|platform search|social monitoring|authorization verifier|approval workflow|audit workflow|policy workflow|source health|source quality|source coverage|source ranking|top sources|top-sources"
```

The final `rg` command exits `1` because it finds no matches.

Output format:

- List findings by severity: Critical, Important, Minor.
- Critical and Important findings block commit/push and must be fixed.
- If no blocking findings remain, include the exact phrase:
  `APPROVED FOR STAGE 26 COMMIT`.
