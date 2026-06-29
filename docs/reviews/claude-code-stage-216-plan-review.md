# Stage 216 Plan Review

**Verdict:** APPROVE_WITH_NITS

## Critical

None.

## Important

**1. `uv lock --check` form doesn't match spec §11 or the mirror-environment risk.**
The plan's Task 1 lists `uv lock --check` without the env-unset form. The spec §11 final-release gate spells out `env -u UV_DEFAULT_INDEX -u UV_INDEX_URL -u UV_EXTRA_INDEX_URL UV_NO_CONFIG=1 uv lock --check`, and the checklist uses at minimum `UV_NO_CONFIG=1 uv lock --check`. In this environment a user-level uv config or shell env can set `UV_DEFAULT_INDEX`, silently re-pinning the lock against a mirror. Task 1 should reproduce the exact form from the spec.

**2. `check_package_archives.py` coverage of new collector modules not verified.**
The plan runs `check_package_archives.py` without confirming the script asserts the presence of `collectors/html.py` and `collectors/sitemap.py`. The script predates Phase 1; if it has no entry for those new modules, a missing-module defect would pass silently. Task 1 should explicitly verify (or extend) the script to assert both new collector modules are in the wheel before treating a green run as packaging-complete. Separately, the spec §8 notes the first-run smoke fixture should include a tiny HTML source — if that was deferred from1c/1d, Task 1 should confirm the smoke actually exercises the HTML/SITEMAP code paths end-to-end before the release review fires.

## Nits

**1. `uv lock --check` mirror install step only implicit.** The checklist's mirror install check (`UV_DEFAULT_INDEX=https://pypi.tuna.../simple uv sync --frozen --dev --check`) is covered by the "per `docs/github-upload-checklist.md`" reference, but given how many distinct commands that document lists, explicitly naming it in Task 1 would reduce ambiguity.

**2. Review capture hygiene not called out.** Task 2 doesn't remind the implementer to capture the Claude Code output to a temp file first, inspect it, and then copy one coherent body — the checklist's anti-stub, anti-truncation, and anti-partial-approval rules. Worth a one-line note in Task 2 given the iron-rule status of that hygiene requirement.

**3. opencode fallback not mentioned.** Task 2 names Claude Code as the reviewer but doesn't note the fallback (`opencode run --model zhipuai-coding-plan/glm-5.2 --variant max`) if Claude Code is unavailable — already in the checklist and iron rules, but easy to overlook mid-task.

## Résumé

The plan is structurally sound: correct scope (no new code, no social/Phase 2 work, no schema/dep change), single consolidated release review is appropriate given per-stage reviews are already committed, and the roadmap-wrap (CHANGELOG note + spec Phase 1 Status) is correctly bounded. The two Important items are about execution precision, not structural gaps — fix the `uv lock --check` command form and add an explicit pre-check that `check_package_archives.py` covers the new collector modules before treating the packaging step as done.
