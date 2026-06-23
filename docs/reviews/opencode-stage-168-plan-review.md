# Stage 168 Plan Review

## Summary

Stage 168 is a tightly scoped documentation/documentation-test synchronization that aligns `docs/source-packs.md` with the checked-in public source pack. It replaces the abbreviated four-theme GDELT list with the exact 10 GDELT source names and expands the example `tag_counts` to current linter output, then guards both with two new focused tests using the production `lint_source_pack(...)` as the source of truth. The plan is docs/test-only, follows TDD (RED then GREEN), respects every `AGENTS.md` scope boundary, and uses the project's mandated `uv --no-config run --frozen` and local opencode review workflow. No critical or important findings block implementation; a few minor test-strengthening suggestions follow.

## Findings

### Critical

None.

### Important

None.

### Minor

1. **GDELT lane test is unidirectional (pack -> docs only).** `test_source_packs_docs_list_current_public_pack_gdelt_lanes` asserts every pack GDELT name appears in the section, but does not catch stale doc entries left behind after a pack rename or removal. Consider adding a reverse/count guard, e.g. assert the count of backticked tokens beginning with `` `GDELT `` in the section equals `len(_public_pack_gdelt_source_names())`, so the drift signal fires in both directions.

2. **Make the "public pack lints clean" assumption self-checking.** The JSON-example test asserts `example["findings"] == []` but never asserts `result.findings == []`. I verified `_lint_sources` produces no findings for this pack (all weights explicit, all enabled, all tagged, distinct names/queries/targets, RSS `article.enabled: false`), so the assumption holds today. Adding `assert result.findings == []` would turn an implicit precondition into an explicit guard, so a future pack change that introduces a finding is caught at the test rather than only silently mismatching the doc.

3. **No schema-completeness guard on the example JSON.** The test compares six fields individually but does not assert the example object's key set equals `SourcePackLintResult`'s field set. Today the example lists all seven model fields (`path`, `source_count`, `enabled_count`, `disabled_count`, `type_counts`, `tag_counts`, `findings`) and the model is `extra="forbid"`, so drift risk is low. This is informational only; no change required for v0.1.0.

## Plan Assessment

- **Scope and safety.** Appropriately scoped and safe. No changes to `configs/source-packs/fashion-public.example.yaml`, the linter, CLI, collectors, or any runtime/network path. Blast radius is one doc plus one test module.

- **Boundary compliance.** Fully consistent with `AGENTS.md`. Stays inside the RSS/Atom + GDELT v0.1.0 core, retains the "Scores only reflect the configured source set" disclaimer, and preserves the existing Google News RSS / Google Trends / account-based access / browser automation / paywall-bypass / private-data boundary sentence (covered by the pre-existing `test_source_packs_docs_keep_public_pack_source_boundary`). No scraping, platform APIs, login/cookies, monitoring, scheduling, source acquisition, demand proof, ranking, coverage verification, or compliance-review behavior is introduced.

- **Correctness of planned values.** I independently counted tag occurrences across all 16 sources; all 22 proposed `tag_counts` keys and values match (e.g. `industry_news: 5`, `gdelt: 10`, `shoes: 2`, `luxury: 2`, singletons for `accessories`/`beauty`/`culture`/etc.). The 10 GDELT names in the spec, plan, and doc-update bullets match the YAML byte-for-byte. `type_counts` `{"gdelt": 10, "rss": 6}`, `source_count: 16`, `enabled_count: 16`, `disabled_count: 0`, and `findings: []` all reconcile with `lint_source_pack` semantics.

- **Test strength.** Sufficient to prevent the documented count/name drift. The lane-name test catches additions and renames; the count test catches any tag/type/enabled/disabled/total drift with exact-equality against live linter output. The two minor suggestions above tighten the reverse direction and the clean-pack precondition.

- **Stability choice on `path`.** Correct. `lint_source_pack` stores `path=str(path)` using whatever the caller passes; the test passes an absolute `Path`, while the doc shows a repo-relative path, so including `path` would force brittle normalization. Excluding it (and treating `findings` as an empty-list literal rather than serializing pydantic `SourcePackFinding` objects) is the right pragmatic call.

- **Workflow hygiene.** RED/GREEN expectations are accurate: the current docs lack all 10 backticked names and carry only a 2-key `tag_counts`, so both new tests fail today and pass after the planned edits. Verification commands, release gate, and opencode review/commit/push steps match `docs/REVIEW_PROTOCOL.md` and the project's frozen/`--no-config` conventions.

## Verdict

Approve. The plan is correct, boundary-compliant, and implementation-ready with no critical or important findings. Adopting Minor 1 (bidirectional/count guard for GDELT lane names) and Minor 2 (`assert result.findings == []`) during Task 1 is recommended but not required to proceed.
