## Critical

None.

## Important

None.

## Minor

1. **Invalid output `--format` is not explicitly tested before file loading.**
   The prior review used “invalid `--format`” wording, while the revised design/plan focuses on invalid `--input-format`, invalid `--as-of`, negative `--limit`, invalid config, and file reading. This matches the user’s current review focus and is not blocking. Still, adding one small CLI test for `--format xml` not reaching file loading would remove any ambiguity.

2. **CLI JSON privacy test is lighter than the module-level recursive/string privacy test.**
   The module test now performs serialized JSON and table forbidden-fragment checks for paths, URLs, titles/summaries/raw values, normalized/internal keys, contexts, representative items, source/import paths, and account fields. That resolves the previous blocker. The CLI JSON test could reuse the same forbidden-fragment loop for defense in depth, but this is not required before implementation.

3. **Planned table-sanitization fixture needs to include all required model fields.**
   The manually constructed `CommunityCandidatePreview` in the plan should include all required fields when implemented, notably `baseline_window_start`. This is a small execution detail, not a plan blocker.

## Review against requested focus

1. **Previous Critical and Important findings:** resolved. The revised plan removes `path` from the output model and table output, narrows the node, strengthens output-safety tests, adds the previously missing test categories, and clarifies validation ordering.

2. **Stage 27A scope:** sufficiently tight. The plan is now implementation plus focused module/CLI tests only. Broad docs, release verification, Claude Code review, commit, and push are explicitly out of scope.

3. **Supplied file path in output/errors:** addressed. The design says the input path is used only for reading and is never emitted in JSON/table output. The CLI plan sanitizes file-error output and tests missing-file errors without path/name echo.

4. **Avoids prohibited systems:** yes. The plan does not add source collection, scheduling, dashboard/report generation, SQLite reads/writes, stored state, config writes, entity YAML generation, directory watching, recursive discovery, or platform APIs.

5. **Validation order:** clear and tested for the key cases: invalid `--as-of`, invalid `--input-format`, negative `--limit`, invalid config, then file reading only after valid config. Invalid output `--format` could get an extra test as noted above, but this is minor.

6. **Recursive output-safety tests:** strong enough. The planned module test checks serialized JSON and table strings against forbidden values including source paths, row URLs, titles/summaries/raw text fragments, normalized/internal keys, contexts, representative items, source/import paths, and account fields.

7. **Test sufficiency:** sufficient. The plan covers current/baseline windows, missing `collected_at` using `as_of`, fallback source names, known entity suppression, thresholds, single-token thresholds, per-row duplicate suppression, disabled discovery, `limit=0`, table sanitization, CLI help, clean errors, validation ordering, and artifact absence.

8. **Scoring/label behavior:** coherent for local pre-import preview. It reuses current/baseline windows, configured entities only, candidate discovery thresholds, weighted current mentions, source diversity, and growth bonus without depending on SQLite stored matches. The local labels `new`, `rising`, and `observed` are appropriate.

APPROVED FOR IMPLEMENTATION
