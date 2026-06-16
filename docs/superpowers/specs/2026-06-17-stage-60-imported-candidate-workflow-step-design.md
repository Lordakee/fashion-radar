# Stage 60 Imported Candidate Workflow Step Design

## Goal

Add the existing local read-only `imported-candidates` command to the
print-only `imported-review-workflow`, so post-import review includes candidate
phrase review before the final local heat movement check.

## Context

The repository already has:

- `imported-candidates`, a local read-only command that reviews observed
  candidate phrases from retained `manual_import` rows.
- `imported-review-workflow`, a print-only checklist command that prints
  copyable local review commands without executing them.
- A final `review_local_heat_movers` workflow step added in Stage 58.

The current workflow can skip an important review activity: after imported rows
are matched, users can compare known imported entities and review unmatched rows,
but the workflow does not explicitly print the existing candidate phrase review
command. That makes it easier to miss new imported phrases that are not yet
tracked entities.

## Recommended Approach

Add one `ImportedReviewWorkflowStep` to `build_imported_review_workflow()`.

New step:

```python
ImportedReviewWorkflowStep(
    order=4,
    name="review_imported_candidate_phrases",
    purpose=(
        "Review observed candidate phrases from retained imported rows after "
        "stored matches are refreshed."
    ),
    command=_shell_command(
        "fashion-radar",
        "imported-candidates",
        "--config-dir",
        config_text,
        "--data-dir",
        data_text,
        "--as-of",
        as_of_text,
        *source_args,
    ),
    suggested_effect="read_only",
)
```

Resulting order:

1. `summarize_imported_sources`
2. `refresh_stored_matches`
3. `compare_imported_entities`
4. `review_imported_candidate_phrases`
5. `review_unmatched_imported_rows`
6. `review_local_heat_movers`

This preserves Stage 58’s final heat-review step while adding candidate phrase
review after stored matches are refreshed. It also keeps source-name handling
consistent with `imported-entity-deltas` and `imported-signals`: pass
`--source-name` to `imported-candidates` only when the workflow has a nonblank
source filter. The final `heat-movers` step still omits `--source-name`.

## Scope

In scope:

- Add one printed read-only workflow step for the existing `imported-candidates`
  command.
- Update direct workflow tests, CLI tests, docs drift tests, first-run smoke, and
  user docs for the six-step workflow.
- Keep `review_local_heat_movers` as the final step.
- Add release smoke assertions that installed/source checkout output includes
  the new candidate review step.

Out of scope:

- No new CLI command.
- No new workflow option such as `--candidate-limit`.
- No `--limit`, `--format`, `--current-days`, or `--baseline-days` flags on the
  printed `imported-candidates` step.
- No source/platform connector, scraping, browser automation, account login,
  cookies, sessions, platform API, source acquisition, monitoring, or scheduling.
- No schema migration, dependency change, report/dashboard/digest write, or
  workflow artifact write.
- No runtime data access in `build_imported_review_workflow()`: do not call
  `query_imported_candidates`, load configs, open SQLite, inspect paths, or run
  subprocesses from the workflow builder.

## Testing

Tests must prove:

- The workflow now has `step_count == 6`.
- The new step name is `review_imported_candidate_phrases`.
- The new step is read-only.
- The new command is exactly:
  `fashion-radar imported-candidates --config-dir <config_dir> --data-dir <data_dir> --as-of <as_of>`
  plus `--source-name <source>` only when a source filter is present.
- The final `review_local_heat_movers` step remains final and still omits
  `--source-name`.
- `imported-review-workflow` still does not run the candidate query, load
  configs, open SQLite, run subprocesses, or create artifacts.
- Current public docs mention a read-only imported candidate phrase review step
  in the workflow, not merely the standalone `imported-candidates` command.
- First-run smoke validates the new workflow shape.

## Review And Release Gates

Before implementation, submit this design and the implementation plan to local
`opencode` using model `zhipuai-coding-plan/glm-5.2`.

Before commit/push:

- Run targeted workflow/CLI/docs/first-run tests.
- Run full `pytest -q`.
- Run `ruff check .` and `ruff format --check .`.
- Run lock/sync hygiene with `UV_NO_CONFIG=1`.
- Ensure `uv.lock` and `pyproject.toml` are unchanged.
- Run release hygiene, first-run smoke, package archive smoke, and installed-wheel
  smoke.
- Run opencode release review and fix Critical/Important findings.
