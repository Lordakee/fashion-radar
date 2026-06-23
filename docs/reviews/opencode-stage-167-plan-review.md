# Stage 167 Plan Review

## 1. Scope correctness (human-readable table error-count wording)

Confirmed correctly scoped. The objective targets exactly the two fixed plural
labels in `render_community_handoff_directory_check_table(...)`:

- `src/fashion_radar/community_handoff_check.py:190`
  `f"{result.community_signal_lint.error_count} errors"`
- `src/fashion_radar/community_handoff_check.py:208`
  `f"{result.import_dry_run.error_count} errors"`

No other renderer phrases, structured counts, models, JSON keys, or
`check_community_handoff_directory(...)` logic are touched. The design and plan
both explicitly enumerate the out-of-scope items and the `AGENTS.md`
`community-handoff-check-dir` boundary (local-only, read-only, no import, no
SQLite, no artifacts, no connectors/scraping/platform APIs) is respected: this
is a presentation-only string change.

## 2. RED test isolation

Well designed. The test builds a normal valid result through the real
`check_community_handoff_directory(...)` path, then uses Pydantic v2
`model_copy(update={...})` on the nested `community_signal_lint` and
`import_dry_run` submodels to force `error_count == 1`. This avoids
manufacturing malformed CSV to coerce exactly one error, so the test cannot
become brittle if lint/dry-run internals evolve. The assertions use
`next(line for line in lines if line.startswith("Lint: "))` /
`"...Import dry-run: "` and `endswith(", 1 error")`, which couple only to the
renderer grammar, not to CSV internals. `model_copy` does not re-run
validation, but `error_count` is a plain `int`, so direct assignment is safe.

One minor robustness note, non-blocking: the mutated state is internally
inconsistent (1 lint error but `failed_check_count == 0` and empty `findings`).
That is acceptable and intentional for a renderer-only grammar test, since the
renderer does not recompute findings. No change needed.

## 3. Reuse of `format_count_label(...)`

Appropriate and safe. `src/fashion_radar/lint_formatting.py` is a zero-import
leaf module, so importing it into `community_handoff_check.py` cannot create a
cycle. The helper signature `(count, singular, plural)` matches the use case
exactly and is already unit-tested in `tests/test_lint_formatting.py` for counts
0, 1, and 2, so the singular/plural contract is covered at the unit level. The
same helper is already consumed by `format_finding_counts(...)` elsewhere, so
this reuse is consistent with established conventions.

## 4. Avoidance of out-of-scope changes

Confirmed. The plan modifies only:

- `src/fashion_radar/community_handoff_check.py` (renderer: two phrases + one
  import line)
- `tests/test_community_handoff_check.py` (one new renderer test)

No changes to: JSON output (the `test_check_result_json_has_stable_top_level_keys`
schema test remains valid and untouched), Pydantic models, CLI flow, readiness
semantics, the `findings`/strict/warning logic in
`check_community_handoff_directory(...)`, the `files`/`rows`/`candidates`
wording, or `manual_signals.py` (correctly deferred to a separate stage per the
design).

## 5. Verification / review / release / commit / push completeness

Complete and consistent with `docs/REVIEW_PROTOCOL.md` and `AGENTS.md`.

- Focused gate: single RED test, full module, ruff check + format on the two
  touched files. Matches TDD flow.
- Release gate: full `pytest -q` (with proxy env unset), `check_first_run_smoke`,
  `check_release_hygiene`, `ruff check .`, `ruff format --check .`,
  `UV_NO_CONFIG=1 uv lock --check`, `git diff --check`, `ghp_` token scan, and
  GitHub extraheader check. This matches the established gate pattern and
  `AGENTS.md` lockfile rules (`UV_NO_CONFIG=1 uv lock --check` for public
  lockfile validation, `uv --no-config run --frozen` for test/lint runs).
- Code review and release review both use the
  `opencode run --model zhipuai-coding-plan/glm-5.2 --variant max` temp-file
  capture flow with the required `# Stage 167 Code Review` / `# Stage 167 Release
  Review` headers, and the review-capture hygiene rules in
  `docs/REVIEW_PROTOCOL.md`.
- Commit lists exactly the source, test, design, plan, and review artifacts,
  with a concise conventional-commit message.

`git push origin main` assumes the GitHub remote already exists; for Stage 167
this is consistent with prior stages and `docs/REVIEW_PROTOCOL.md`'s "let the
user create or choose the remote" is satisfied by the established remote.

## 6. Critical / important findings before implementation

None. No critical findings. No important findings.

## Minor findings (non-blocking)

- M-1 (guidance clarity): Task 2 Step 1 does not specify where to insert
  `from fashion_radar.lint_formatting import format_count_label` within the
  existing `fashion_radar.*` import block (`community_handoff_check.py:9-25`).
  Alphabetically it belongs between `fashion_radar.importers.manual_signals`
  and `fashion_radar.settings`. Ruff's import sort will enforce this
  regardless, but stating it would remove ambiguity for the implementer.
- M-2 (style, optional): The proposed
  `f"{format_count_label(result.community_signal_lint.error_count, 'error', 'errors')}"`
  wraps a bare function call in an f-string purely to stay shape-consistent with
  the adjacent implicit-concatenation f-strings. This is harmless and
  consistent; a plain `format_count_label(...)` expression would also work.
  Either is acceptable; no change required.
- M-3 (test coverage nuance): The new RED test covers only the singular (`1`)
  case. The plural contract for this renderer is covered indirectly by existing
  tests that render valid (`error_count == 0`) results and by the unit tests for
  `format_count_label`, so no additional assertion is required. Noted only for
  completeness.

## Verdict

No blocking findings. The plan is approved for implementation. Proceed with
Task 1 (RED test), confirm it fails on `1 errors`, then apply the Task 2
renderer change and run the focused + release gates and the two opencode
reviews as specified.
