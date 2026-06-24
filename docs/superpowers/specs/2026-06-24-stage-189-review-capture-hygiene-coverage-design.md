# Stage 189 Review Capture Hygiene Coverage Design

## Objective

Close the current release-hygiene blind spots so repository review artifacts are
validated consistently, including non-stage local opencode review records such
as `docs/reviews/opencode-full-project-review.md` and timeout-stub staged
records such as the current Stage 188 code review artifact.

## Background

The repository already guards staged opencode review artifacts with
`scripts/check_release_hygiene.py`, but the guard only covers
`docs/reviews/opencode-stage-N-*.md` files. The committed
`docs/reviews/opencode-full-project-review.md` still contains raw capture
noise, including ANSI escape sequences and process chatter, and therefore sits
outside the current hygiene net even though it is part of the same review
archive.

The Stage 188 review chain also contains a second false negative:
`docs/reviews/opencode-stage-188-code-review.md` records an opencode timeout and
"No partial output" instead of completed review output. Current release hygiene
passes because timeout-stub phrases are not treated as review-capture failures.
Stage 188 also has a stale release review saying the stage was not approved
before its later fixes were committed. This stage should make the checker catch
future timeout stubs and add clean follow-up review records for the existing
Stage 188 chain.

This stage fixes those gaps without changing product behavior.

This is a prerequisite maintenance stage, not the next product-value feature.
After it is committed, the next planned product stage should add source
liveness diagnostics for configured public sources so the roadmap correction
moves into source-health/feed-liveness work.

## Scope

In scope:

- Extend release-hygiene coverage to non-stage opencode review artifacts under
  `docs/reviews/`, while continuing to exclude prompt files.
- Extend release-hygiene content checks to reject timeout-stub review status
  lines without flagging ordinary prose about HTTP timeouts.
- Add tests proving the checker rejects a dirty
  `docs/reviews/opencode-full-project-review.md`, rejects staged timeout stubs,
  and still allows clean review prose.
- Clean up the committed full-project review artifact so the repository's
  review archive is internally consistent.
- Replace the Stage 188 code-review timeout record with scoped completed review
  output and add a Stage 188 release rereview that closes the stale not-approved
  release-review status.
- Update the review protocol to state that release hygiene covers both staged
  and non-staged local opencode review records.

Out of scope:

- No runtime product changes.
- No new collectors, source packs, source-health behavior, or dashboard work.
- No change to the existing staged review artifact naming scheme.
- No social-platform connector work.
- No continuation of external/community handoff hardening beyond closing the
  existing review-chain correctness gap.

## Technical Approach

The smallest safe fix is to broaden the path filter in
`scripts/check_release_hygiene.py` so it recognizes both:

- the existing staged review capture names; and
- other `docs/reviews/opencode-*.md` review records that are not prompt files.

The scanner should keep the existing content checks:

- ANSI escape/control output;
- tool-status lines;
- tool UI markers;
- process chatter at the start of the file.
- timeout-stub status lines such as `opencode code review timed out ...`.

The test suite should stay standard-library only and use the existing fixture
helpers in `tests/test_release_hygiene.py`.

## Acceptance Criteria

- A dirty `docs/reviews/opencode-full-project-review.md` fails release hygiene
  for the same reasons as a dirty staged opencode review artifact.
- A staged opencode review record that only documents a timeout fails release
  hygiene.
- A clean non-stage opencode review record passes.
- The committed `docs/reviews/opencode-full-project-review.md` no longer
  contains ANSI escape sequences, tool-status lines, or process chatter.
- The committed Stage 188 review chain has clean code-review and release
  rereview evidence.
- The full release hygiene check passes after the cleanup.
