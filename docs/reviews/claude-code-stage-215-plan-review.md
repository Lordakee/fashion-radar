# Stage 215Plan Review

**Verdict:** APPROVE_WITH_NITS

## Critical

None.

## Important

None.

## Nits

1. **Code block style inconsistency.** The suggested section body in the plan uses 4-space-indented code blocks for both the `docker run` one-liner and the YAML snippet. The rest of `docs/source-packs.md` uses fenced code blocks exclusively (` ```bash `, ` ```yaml `, etc.). The implementer should use fenced blocks to match the file's style.

2. **Docker image tag.** `diygod/rsshub` (untagged) pulls `latest`, which can drift silently. A nit for quick-start docs, but adding`:latest` explicitly or noting that users may want to pin a release tag would be slightly more honest. Not blocking.

3. **Docs-guard file destination is underspecified.** The plan lists three candidate files (`test_source_packs_docs.py`, `test_cli_docs.py`, or a new file) without committing to one. Implementer should check for an existing docs-guard file first and prefer extending it over adding a new file; leaving this ambiguous risks a duplicate guard module.

4. **`robots` contract phrase is minimal.** Pinning the bare word `"robots"` will match anywhere in the file, not just in the new section. It works, but pinning `"robots rules"` (matching the phrase already used in the existing preamble at line 3of `docs/source-packs.md`) would be both more specific and consistent with existing project wording.

## Résumé

The docs-only scoping is the correct call: `tests/test_source_packs.py:35` pins the public pack at exactly 20 sources of types `gdelt` and `rss`, so adding an `rsshub` entry would break the composition test without live validation. Deferring curated-feed additions is sound. The Docker guidance (`diygod/rsshub`, port 1200) is accurate. The boundary caveats (robots, no demand proof, no platform coverage verification, community-maintained routes may break) are sufficient and consistent with the existing `docs/source-packs.md` preamble and the `source-liveness` section wording. `SourceType.RSSHUB` is confirmed in `source.py:10` and the model validator at line 90 correctly requires `url`, matching the example YAML in the plan. Scope discipline is clean — no code, schema, dependency, or pack-data changes.
