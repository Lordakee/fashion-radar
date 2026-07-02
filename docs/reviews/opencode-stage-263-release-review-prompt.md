# Stage 263 Release Review Prompt

You are doing the final read-only release review for Stage 263 in `/home/ubuntu/fashion-radar` before commit and push.

Work read-only. Do not edit files.

Stage 263 goal:
- Add a stable app-facing ROW ONE JSON contract at generated `data/edition.json`.
- Contract version: `row-one-app/v1`.
- Keep ROW ONE HTML rendering, collection, matching, ranking, cleanup, server, schedule, and social/platform integrations unchanged.

Review history:
- Claude Code plan/code review attempts timed out, so opencode fallback reviews were captured.
- `docs/reviews/opencode-stage-263-plan-review.md` found dependency/schema plan issues, which were addressed.
- `docs/reviews/opencode-stage-263-code-review.md` found date-format and evidence-count documentation issues, which were addressed.
- `docs/reviews/opencode-stage-263-code-rereview.md` returned `Approved with minor notes`.

Already verified in the full release gate:
- `git diff --check`
- `UV_NO_CONFIG=1 uv lock --check`
- `UV_NO_CONFIG=1 uv sync --locked --dev`
- `UV_NO_CONFIG=1 uv sync --locked --dev --check`
- `uv --no-config run --frozen ruff check .`
- `uv --no-config run --frozen ruff format --check .`
- `uv --no-config run --frozen pytest -q` -> `1703 passed`
- `uv --no-config build`
- `uv --no-config run --frozen python scripts/check_package_archives.py dist`
- `uv --no-config run --frozen python scripts/check_first_run_smoke.py --repo-root .`
- `uv --no-config run --frozen python scripts/check_release_hygiene.py --repo-root .`

Review focus:
1. Confirm release artifacts are coherent: schema, tests, docs, plan/spec, reviews, package archive requirements, lockfile.
2. Confirm no untracked required files would be missed by commit.
3. Confirm review artifacts contain coherent bodies and no empty timeout stubs.
4. Confirm no forbidden secrets, generated DB/cache files, dist artifacts, or mirror/private index URLs are staged/required.
5. Confirm no out-of-scope social/platform integration behavior was added.

Return Critical/Important/Minor findings with file/line references where useful. End with verdict: `Release approved`, `Release approved with minor notes`, or `Do not release`.
