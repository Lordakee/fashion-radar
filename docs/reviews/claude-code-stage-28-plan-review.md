## Critical

- **Out-of-scope review/documentation task blocks implementation.** The design explicitly scopes Stage 28 to implementation plus focused tests only and says docs updates, final release verification, Claude Code code review, commit, and push belong to follow-up nodes (`design.md:15-25`). The plan violates this in Task 3 by modifying `docs/reviews/claude-code-stage-28-code-review-prompt.md`, creating a code-review prompt, and running Claude Code with output written to `docs/reviews/claude-code-stage-28-code-review.md` (`plan.md:437-512`). Remove the code-review prompt creation/execution and any docs/review writes from this Stage 28 plan.

## Important

- **CLI JSON output-safety tests are not strong enough recursively.** The design requires JSON output to avoid leaking paths, filenames, row URLs, titles, summaries, raw text, normalized keys, contexts, source paths, validation findings, and representative fields (`design.md:146-153`, `design.md:186-188`). The module test recursively serializes `preview.model_dump()`, but the CLI JSON test only checks stable top-level keys and absence of top-level `directory`, `files`, and `pattern` keys (`plan.md:306-330`). Add a recursive forbidden-value scan over actual CLI JSON stdout, parallel to the module/table safety checks.

- **Validation-order tests should prove no config load as well as no directory read for early failures.** The design says invalid `--input-format`, negative `--limit`, and invalid `--as-of` must occur before config load or directory read (`design.md:71-79`, `design.md:157-161`). The plan’s validation tests focus on preventing directory reads (`plan.md:336-351`). Add assertions/patches proving config-loading functions are not called for invalid `--as-of`, invalid `--input-format`, and negative `--limit`; for invalid config, assert the directory is not read.

- **Pattern/regular-file behavior is under-specified in tests.** The design requires `--pattern` selecting regular files without recursive traversal (`design.md:176`). The planned aggregation test covers nested files ignored with `pattern="*.csv"`, but does not clearly cover a custom pattern or matching non-regular children/directories being ignored. Add a focused test with a custom pattern and a matching directory or non-regular child to lock down direct-child regular-file behavior via `load_manual_signal_directory_rows()`.

- **Scoring, label, and tie-break behavior need direct assertions.** The design requires candidate row keys to include `label` and sorting by score descending, current mentions, distinct sources, then phrase (`design.md:128-140`, `design.md:104-107`). The plan references preserving Stage 27 behavior but does not clearly assert score/label output or ordering after moving scoring into `_build_candidate_preview()` (`plan.md:94-125`, `plan.md:183-209`). Add targeted tests for label value, score semantics/parity with existing `community-candidates`, and tie-break ordering without relying on SQLite stored matches.

## Minor

- **Error-sanitization fallback wording is too narrow.** The design forbids leaking directory paths, file paths, filenames, row values, raw diagnostics, or traceback (`design.md:163-166`). The plan’s fallback for non-`ManualSignalImportError` exceptions only mentions sanitizing messages containing `str(directory)` or `directory.name` (`plan.md:424-425`). Broaden the plan language to require the generic directory-preview error for all unexpected exceptions that could expose local paths, filenames, raw loader findings, row values, or tracebacks.

- **Task 3 boundary check uses inconsistent review prompt filenames.** The plan says it will create `docs/reviews/claude-code-stage-28-code-review-prompt.md` (`plan.md:479-482`), but the diff/boundary commands reference `docs/reviews/claude-code-stage-28-plan-review-prompt.md` (`plan.md:463-465`). This appears stale. If Task 3 is removed as recommended, this inconsistency disappears.

- **The core implementation scope is otherwise tight.** Apart from Task 3, the planned source/test file map is limited to `community_candidates.py`, `cli.py`, `tests/test_community_candidates.py`, and `tests/test_cli.py`; it reuses the requested parser/extraction/config functions and avoids source collection, scheduling, reports, dashboards, SQLite writes, and entity config generation.

Blocking findings remain, so this review is **not approved for implementation** yet.
