# Claude Code Stage 15 Code Rereview Prompt

You are rereviewing Stage 15 after fixes to the first code review. Run this as a
read-only code and documentation review. Do not edit files, do not commit, do
not call the network, do not run collectors, do not create directories, do not
open SQLite, and do not execute platform/social/community tooling.

Project: `/home/ubuntu/fashion-radar`

Use maximum reasoning effort. The invoking command should be:

```bash
claude -p --effort max --permission-mode plan < docs/reviews/claude-code-stage-15-code-rereview-prompt.md
```

## Review Records

- First code review:
  `docs/reviews/claude-code-stage-15-code-review.md`
- Current implementation and docs:
  - `README.md`
  - `docs/entity-pack-quality.md`
  - `src/fashion_radar/entity_packs.py`
  - `src/fashion_radar/cli.py`
  - `tests/test_entity_pack_lint.py`
  - `tests/test_cli.py`

## Fixes Made

- Reworded `README.md` entity config summary so it no longer says broad aliases
  universally need context. It now says single-word/common aliases may need
  context unless explicitly safe with a reason, while ordinary multi-word aliases
  can match without context under current matcher rules.
- Reworded `docs/entity-pack-quality.md` opening so the command checks YAML
  before using that YAML in existing matching workflows, not as part of matching.
- Clarified dashboard wording in `README.md` so Trend Deltas local reads do not
  create trend tables or write database state.

## Verification After Fixes

Fresh commands run after the fixes:

```bash
git diff --check
.venv/bin/python -m pytest -q
.venv/bin/python -m ruff check .
.venv/bin/python -m ruff format --check .
```

Observed results:

- `pytest`: 322 passed
- `ruff check .`: all checks passed
- `ruff format --check .`: 76 files already formatted
- `git diff --check`: exit 0

## Response Format

Start with one of:

- `Approved for Stage 15 upload`
- `Not approved`

Then list findings in this format:

- `Critical:` issues that must be fixed before upload.
- `Important:` issues that should be fixed before upload.
- `Minor:` optional improvements.

Please focus on whether the previous Important finding is resolved and whether
the Minor wording updates introduced any new issue.
