# Stage 82 Mirror Lockfile Recovery Design

## Goal

Document and verify the safe recovery path for a local mirror-rewritten
`uv.lock`, then restore the working tree lockfile to the public mirror-free
version.

## Problem

Local mirror-backed install workflows are supported, but a previous local
operation left `uv.lock` rewritten with mirror URLs in the working tree. The
file has been kept unstaged across releases, but leaving it dirty increases the
risk of accidental broad staging.

## Design

- Add a short "Recover A Mirror-Rewritten Lockfile" section to
  `docs/dependency-mirrors.md` after `## Project Practice` as a peer `##`
  section. The existing `## Project Practice` scan remains in place; the new
  section is additive and describes what to do after a local mirror rewrite has
  already happened.
- The section should explain that mirror installs must use frozen sync commands
  and that a locally rewritten `uv.lock` should be restored from git before
  release work.
- Include concrete commands:
  - `git restore -- uv.lock`
  - `UV_NO_CONFIG=1 uv lock --check`
  - a mirror-marker `rg` scan on `uv.lock`
  - `git diff --quiet -- uv.lock`
- Add a docs drift test in `tests/test_cli_docs.py` that pins those recovery
  commands and the "do not commit mirror URLs" boundary.
- Restore the working tree `uv.lock` from `HEAD` so the repo ends clean.

Current safety evidence: the existing dirty `uv.lock` diff has been verified as
a pure URL rewrite with identical versions, hashes, sizes, and markers. Only
registry, sdist, and wheel URLs differ.

## Non-Goals

- Do not change dependencies or regenerate `uv.lock`.
- Do not add runtime code, CLI behavior, source collection, connectors,
  scraping, platform APIs, ranking, or demand proof.
- Do not modify `AGENTS.md`, CI, or release protocol docs in this node.

## Verification

- Focused docs test for dependency mirror recovery.
- Full `tests/test_cli_docs.py`.
- `ruff check` and `ruff format --check` for the changed test file.
- `UV_NO_CONFIG=1 uv lock --check`.
- Mirror-marker scan of `uv.lock`.
- `git diff --quiet -- uv.lock` after restore.
- Full pytest/ruff/release hygiene before commit.
