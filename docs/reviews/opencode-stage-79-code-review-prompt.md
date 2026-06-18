# Stage 79 Code Review Prompt

You are reviewing Stage 79 of `fashion-radar`.

Repository: `/home/ubuntu/fashion-radar`

This is a read-only code review. Do not edit files, stage changes, commit, or
run networked source-collection commands.

## Goal

Review the current uncommitted Stage 79 worktree changes before commit. This
stage improves first-time GitHub onboarding docs with a README start path,
first-run chooser table, CLI beginner roadmap, and clearer optional entity-pack
sequence.

## In Scope

- `README.md`
- `docs/first-run.md`
- `docs/cli-reference.md`
- `docs/entity-packs.md`
- `tests/test_cli_docs.py`
- `CHANGELOG.md`
- `docs/superpowers/specs/2026-06-18-stage-79-onboarding-roadmap-design.md`
- `docs/superpowers/plans/2026-06-18-stage-79-onboarding-roadmap-plan.md`
- `docs/reviews/opencode-stage-79-plan-review-prompt.md`
- `docs/reviews/opencode-stage-79-plan-review.md`
- `docs/reviews/opencode-stage-79-code-review-prompt.md`
- `docs/reviews/opencode-stage-79-code-review.md`

## Out Of Scope

- The pre-existing local mirror rewrite in `uv.lock`; it must remain unstaged
  and must not be part of Stage 79.
- `AGENTS.md`, `docs/REVIEW_PROTOCOL.md`, and
  `docs/github-upload-checklist.md`.
- Runtime CLI behavior, `src/`, dependency manifests, new commands, new flags,
  collectors, adapters, connectors, scraping, browser automation, platform APIs,
  login/session/cookie/token/proxy behavior, media downloads, monitoring,
  scheduling, source acquisition, demand proof, ranking, platform coverage
  verification, or compliance-review product features.

## Acceptance Criteria

- README has a concise `## Start Here` before `## What It Does`.
- README points first-time users to `docs/first-run.md`, names Manual
  repo-local sample as the recommended first-time path, explains smoke paths as
  verification paths, links `docs/entity-packs.md`, and keeps local-first
  boundary language.
- `docs/first-run.md` has a four-row chooser table under
  `## Choose Your First Run` with Manual repo-local sample, Automated
  source-checkout smoke, Installed-wheel smoke, and Reset repo-local sample.
- `docs/cli-reference.md` has `## Beginner Roadmap` before
  `## Shared Path Options`, using only existing commands and linking the
  first-run/entity-pack docs.
- `docs/entity-packs.md` says packs are an optional local matching layer copied
  after `init` and before first `match`/`report`, with explicit local-only
  boundary language.
- Docs drift tests pin these sections and phrases.
- No Stage 79 change adds platform/source acquisition behavior or claims demand
  proof, ranking, or platform coverage verification.

## Prior Verification

The controller already ran:

```bash
uv --no-config run --frozen pytest tests/test_cli_docs.py::test_readme_start_here_points_to_recommended_first_run_path tests/test_cli_docs.py::test_first_run_guide_has_beginner_path_chooser tests/test_cli_docs.py::test_cli_reference_has_beginner_roadmap_with_existing_commands tests/test_cli_docs.py::test_entity_pack_docs_describe_optional_matching_layer_sequence -q
uv --no-config run --frozen ruff check tests/test_cli_docs.py
uv --no-config run --frozen ruff format --check tests/test_cli_docs.py
git diff --check -- README.md docs/first-run.md docs/cli-reference.md docs/entity-packs.md CHANGELOG.md tests/test_cli_docs.py docs/superpowers/specs/2026-06-18-stage-79-onboarding-roadmap-design.md docs/superpowers/plans/2026-06-18-stage-79-onboarding-roadmap-plan.md docs/reviews/opencode-stage-79-plan-review-prompt.md docs/reviews/opencode-stage-79-plan-review.md
```

The Stage 79 plan review found that `UV_NO_CONFIG=1 uv lock --check` would fail
while the working tree contains the out-of-stage mirror-rewritten `uv.lock`.
The plan now requires temporarily restoring `git show HEAD:uv.lock > uv.lock`
before full verification, then restoring the local mirror lock backup after
verification and keeping `uv.lock` unstaged.

## Review Request

Please inspect the current worktree and report actionable issues only.

Classify findings as:

- Critical: must fix before commit.
- Important: should fix before commit.
- Minor: optional polish.

For every finding, include file and line references and explain the concrete
failure mode. If there are no Critical or Important findings, say so clearly.
