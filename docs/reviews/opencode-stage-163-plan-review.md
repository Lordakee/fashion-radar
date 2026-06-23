# Stage 163 Plan Review

## Summary

The Stage 163 plan is correctly scoped, internally consistent, and matches the
current code. The design's narrow fix (catch `UnicodeDecodeError` in the two
validators that own the user-facing member labels, keep `read_zip_text` strict)
is the right shape. RED tests are genuine and the verification/release gate is
complete. There are no critical or important findings; the plan is approved to
implement.

## Question 1: Scope correctness

Yes. The scope is correctly limited to invalid UTF-8 in wheel `METADATA` and
`entry_points.txt`.

Corroborating evidence from `scripts/check_package_archives.py`:

- `read_zip_text(...)` (`scripts/check_package_archives.py:408`) is the only
  decode surface and it has exactly two call sites:
  `validate_wheel_metadata(...)` (`:362`) and
  `validate_wheel_entry_points(...)` (`:378`).
- The two validators are only invoked under the presence guards at
  `scripts/check_package_archives.py:267` and `:271`, so an invalid-bytes
  member that is present will reach the decode and currently raise.
- `WHEEL` is checked for presence only (`validate_wheel_dist_info_files`,
  `:347`); it is never decoded as text, so it is correctly out of scope.
- The sdist path uses `tarfile` and never calls `read_zip_text`, so excluding
  sdist text decoding is consistent with the stated scope.

The out-of-scope list (no build config changes, no other validation semantics,
no sdist decode, no CLI product behavior, no platform/scraping features)
matches `AGENTS.md` boundaries.

## Question 2: RED test adequacy

Yes. The two RED tests genuinely exercise the decode path and fail pre-fix.

- Fixture `b"\xff\xfe\xfa"` is truly invalid UTF-8 (`\xff` is never a valid
  lead byte), so `archive.read(path).decode("utf-8")` raises
  `UnicodeDecodeError`.
- Because `METADATA`/`entry_points.txt` are present (only their bytes are
  swapped), the presence guards at `:267`/`:271` pass and the validators run,
  so the decode failure is actually reached (not short-circuited).
- Pre-fix behavior: `UnicodeDecodeError` is not caught by `validate_wheel`'s
  `except zipfile.BadZipFile` (`:276`), nor by `validate_build_dir`/`main`, so
  Python prints a traceback and exits 1. Therefore:
  - `returncode == 1` passes pre-fix (uncaught exception),
  - `"METADATA is not valid UTF-8" in stderr` fails (RED),
  - `"Traceback" not in stderr` fails (RED),
  - `"UnicodeDecodeError" not in stderr` fails (RED).
- Post-fix the same assertions go GREEN, and the stable messages do not
  substring-collide with `"Traceback"` or `"UnicodeDecodeError"`.

The `write_wheel(...)` broadening from `dict[str, str]` to
`dict[str, str | bytes]` is safe because `zipfile.ZipFile.writestr(...)`
accepts both `str` and `bytes`, and existing string fixtures are unchanged.

## Question 3: Narrowest appropriate implementation

Yes. Catching `UnicodeDecodeError` in the two validators is the narrowest
appropriate implementation.

- It catches only the decode failure, leaving `Parser().parsestr(...)` and
  `configparser` behavior untouched, and preserves the existing
  `configparser.Error` catch around `parser.read_string(...)` (`:381`).
- `UnicodeDecodeError` is a subclass of `ValueError`; the plan correctly
  catches the specific subclass and explicitly forbids widening to
  `ValueError`/`Exception`/`configparser.Error`.
- Other `archive.read(...)` failure modes (`BadZipFile`, `RuntimeError`) still
  propagate to the existing `except zipfile.BadZipFile` in `validate_wheel`,
  so the narrow catch does not mask archive corruption.
- Pushing the catch down into `read_zip_text(...)` would force a contract
  change (result object / Optional) for every caller; the design's rationale
  for not doing that is sound.

## Question 4: Verification / review / release / commit / push completeness

Yes, the steps are complete and align with `docs/REVIEW_PROTOCOL.md` and
`AGENTS.md`.

- Focused verification (Task 2 Step 4): targeted `-k` subset, full module,
  `ruff check`, `ruff format --check`. The `-k "invalid_utf8 or metadata or
  entry_points"` expression matches the two new tests plus existing
  metadata/entry-points regressions.
- Build smoke (Task 3 Step 1): real `uv build` + checker run.
- Code review (Task 3 Step 2): opencode GLM-5.2 max, captured to a temp file
  and cleaned before commit, with fix-before-continue gate.
- Release gate (Task 3 Step 3): full pytest (proxy-cleared), first-run smoke,
  release hygiene, `ruff check .`, `ruff format --check .`, frozen lockfile
  check, `git diff --check`, token scan, and GitHub extraheader check.
- Release review (Task 3 Step 4): opencode release review with fix gate.
- Final hygiene (Task 3 Step 5): re-run hygiene, diff check, token scan,
  extraheader check.
- Commit/push (Task 3 Step 6) and post-push verification (Task 3 Step 7):
  local/remote SHA parity, clean worktree, no persisted extraheader.
- The commit set includes the script, tests, design, plan, and all six review
  artifacts (plan/code/release prompt+review).

`uv --no-config run --frozen` is used consistently for tests/lint/smoke, and
`UV_NO_CONFIG=1 uv lock --check` is used for the public lockfile, matching
`AGENTS.md` mirror discipline.

## Question 5: Critical / important findings before implementation

None. No critical or important findings. The plan may proceed to
implementation after fixing (or consciously accepting) the minor notes below.

## Findings

### Critical

None.

### Important

None.

### Minor

1. Commit message precision. The proposed message
   `fix: report invalid wheel metadata encoding` covers both `METADATA` and
   `entry_points.txt`. Consider `fix: report invalid wheel text-member UTF-8`
   or mention both members so the entry-points half is not implied away. Not
   blocking.

2. RED evidence is indirect. The two new tests assert the *absence* of
   `Traceback`/`UnicodeDecodeError`, so pre-fix they fail by negation rather
   than by pinning the current traceback with a positive assertion. This is
   standard TDD and the plan's "Expected before implementation" notes state it
   explicitly, so it is acceptable. If you want bulletproof RED evidence in
   the code-review record, capture the pre-fix stderr once and quote it in
   `opencode-stage-163-code-review-prompt.md`. Observation only.

3. `dict[str, str | bytes]` invariance. Under a strict type checker (mypy),
   assigning the `dict[str, str]` literal `WHEEL_FILES` to a
   `dict[str, str | bytes]`-typed slot can draw variance noise. The project
   lints with ruff (no type check), so this has no runtime or CI impact.
   Observation only; no change required for Stage 163.

4. Combined-failure coverage. There is no test where both `METADATA` and
   `entry_points.txt` are invalid UTF-8 simultaneously. Both validators
   independently early-return, so both errors would be reported; this is not
   required by the stated scope and is noted only as optional hardening.

## Verdict

Approve. No critical or important findings. Proceed with implementation after
recording this plan review under
`docs/reviews/opencode-stage-163-plan-review.md`.
