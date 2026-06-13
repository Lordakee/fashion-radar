# Stage 28B Community Candidate Directory Release Design

## Goal

Review, verify, commit, and push Stage 28 `community-candidates-dir` after
Claude Code reviews the added code and tests.

## Scope

Stage 28B is a release-control node for the already implemented Stage 28
directory preview. It may:

- create Claude Code code-review prompts/results;
- run full tests, lint, format checks, build checks, smoke checks, and scans;
- apply fixes only if Claude Code or verification finds issues in the Stage 28
  files;
- commit and push the approved Stage 28 changes.

It must not add new product features, broad docs, source collectors, platform
connectors, account automation, browser automation, watch folders, schedulers,
SQLite writes, report/dashboard writes, entity YAML generation, or `uv.lock`
changes.

## Review Target

Claude Code must review the Stage 28 source and tests:

- `src/fashion_radar/community_candidates.py`
- `src/fashion_radar/cli.py`
- `tests/test_community_candidates.py`
- `tests/test_cli.py`
- Stage 28 design/plan/review docs created during the workflow

Review must focus on:

- local, read-only, non-recursive directory behavior;
- aggregate-only JSON/table output;
- no directory path, file path, filename, row URL, row title, summary, raw text,
  normalized key, candidate context, raw validation finding, account/private
  field, or representative item leakage;
- generic error handling for invalid directory, no matching files, invalid file,
  invalid rows, and unexpected exceptions;
- validation order before config load and directory read;
- no platform automation, source acquisition, database writes, reports,
  dashboards, or entity YAML generation.

## Verification

Required verification before commit:

- mirror-backed dependency check;
- focused module and CLI tests;
- full test suite;
- ruff check;
- ruff format check;
- `git diff --check`;
- diff-based high-risk boundary scan;
- generated artifact scan;
- secret scan across files to be committed;
- build to a temporary directory;
- installed-wheel smoke for `community-candidates-dir` success and clean error.

`uv.lock` currently has a known local mirror diff from earlier mirror-backed
operations. Stage 28B must not stage or commit `uv.lock`.

## Commit And Push

Commit only after Claude Code approves with the required phrase and verification
passes. Push with a non-persistent GitHub authentication method and confirm:

- remote URL contains no token;
- no persisted `http.*extraheader` exists;
- `HEAD` matches `origin/main`;
- `uv.lock` remains unstaged/uncommitted;
- committed tree scans are clean.
