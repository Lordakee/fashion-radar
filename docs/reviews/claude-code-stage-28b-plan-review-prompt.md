You are reviewing the Stage 28B release plan before execution.

Repository: `/home/ubuntu/fashion-radar`

Stage 28 implementation status:

- `community-candidates-dir` has been implemented locally.
- Focused verification already passed:
  - `UV_DEFAULT_INDEX=https://pypi.tuna.tsinghua.edu.cn/simple uv sync --frozen --dev --check`
  - `.venv/bin/python -m pytest tests/test_community_candidates.py tests/test_cli.py -q` -> `200 passed`
  - `.venv/bin/python -m ruff check .`
  - `.venv/bin/python -m ruff format --check .`
  - `git diff --check`
  - diff-based high-risk keyword scan
  - untracked artifact scan

Design and plan:

- `docs/superpowers/specs/2026-06-13-stage-28b-community-candidates-dir-release-design.md`
- `docs/superpowers/plans/2026-06-13-stage-28b-community-candidates-dir-release-plan.md`

Review focus:

1. Is the release node correctly scoped to Claude Code code review, verification,
   build/smoke checks, commit, and push?
2. Does the plan require Claude Code to review the Stage 28 source/tests before
   commit and push?
3. Does the plan block commit/push on Critical or Important review findings?
4. Are verification steps sufficient, including mirror-backed dependency/build
   commands, focused tests, full tests, lint/format, diff check, boundary scan,
   artifact scan, secret scan, wheel build, and installed-wheel smoke?
5. Does the plan keep `uv.lock` unstaged/uncommitted and avoid persisting GitHub
   credentials?
6. Does the plan avoid new product features, platform automation, source
   acquisition, database writes, reports, dashboards, schedulers, or entity YAML
   generation?

Output format:

- List findings by severity: Critical, Important, Minor.
- Critical and Important findings block release execution and must be fixed
  before continuing.
- If no blocking findings remain, include the exact phrase:
  `APPROVED FOR STAGE 28B RELEASE EXECUTION`.
