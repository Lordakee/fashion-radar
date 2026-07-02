# opencode Stage 262 Release Rereview Prompt

Release rereview Fashion Radar Stage 262 before push.

Repo: `/home/ubuntu/fashion-radar`

This is a read-only final release rereview. Do not edit files.

The prior fallback release review in
`docs/reviews/opencode-stage-262-release-review.md` returned "Accept with
fixes" because the plan's commit command omitted opencode review artifacts.
That commit-scoping issue has now been fixed in:

- `docs/superpowers/plans/2026-07-02-stage-262-row-one-reader-orientation-plan.md`

Review the current tree and verify there are no remaining push blockers.

Check:

- `git status --short --branch --untracked-files=all`
- `docs/superpowers/plans/2026-07-02-stage-262-row-one-reader-orientation-plan.md`
- `docs/reviews/opencode-stage-262-code-review.md`
- `docs/reviews/opencode-stage-262-release-review.md`
- `docs/reviews/opencode-stage-262-release-rereview-prompt.md`
- `docs/REVIEW_PROTOCOL.md`
- `AGENTS.md`

Also verify:

- opencode review artifacts are included by the Stage 262 commit command;
- no malformed Claude timeout stub review records are present;
- no generated CodeGraph DB/sidecar/runtime files remain in the working tree;
- no build artifacts, local data, reports, SQLite sidecars, secrets, cookies,
  or tokens are present;
- the previously passed full release gate remains sufficient.

Full release gate already passed:

```bash
UV_NO_CONFIG=1 uv lock --check
UV_NO_CONFIG=1 uv sync --locked --dev
UV_NO_CONFIG=1 uv sync --locked --dev --check
git diff --check
uv --no-config run --frozen ruff check .
uv --no-config run --frozen ruff format --check .
uv --no-config run --frozen pytest -q
rm -rf dist build
uv --no-config build
uv --no-config run --frozen python scripts/check_package_archives.py dist
uv --no-config run --frozen python scripts/check_first_run_smoke.py
rm -rf dist build
uv --no-config run --frozen python scripts/check_release_hygiene.py --repo-root .
```

Results included:

- `1685 passed`
- `All checks passed!`
- `Package archives contain required files.`
- `First-run sample smoke passed.`
- `Release hygiene checks passed.`

Return one coherent review body only:

- Verdict: accept / accept with fixes / reject
- Critical findings
- Important findings
- Minor findings
- Notes
- State whether Stage 262 is acceptable to push.

Use file and line references where possible. Do not modify files.
