## Critical issues

None.

## Important issues

1. **The implementation plan’s direct commit/push step is unsafe and conflicts with the repo’s own upload boundary.**
   In `docs/superpowers/plans/2026-06-16-stage-49-first-run-onboarding-guide-plan.md`, Task 4 Step 5 instructs reading a local GitHub token, building an auth header, committing, and pushing directly to `main`. Current `docs/github-upload-checklist.md` states that the user controls remote creation, pushing, publishing, and uploads, and that those actions should not happen unless explicitly requested.
   **Recommendation:** Change the plan so implementation stops at verified commit readiness and release-review approval. Commit/push should be a separate explicitly user-authorized action, preferably without token material embedded in shell arguments.

## Minor issues

1. **The planned doc-drift tests are somewhat brittle on exact prose fragments.**
   The tests assert many full phrases such as `"temporary config, data,"` and `"report, and export directories"`. This will catch drift, but it may also fail on harmless line wrapping or wording improvements.
   **Recommendation:** Keep exact assertions for commands, paths, filenames, and success strings; use normalized or section-scoped checks for broader boundary wording.

2. **The doc-drift tests could be slightly stronger about section context.**
   The plan verifies exact source and installed smoke command substrings in README/checklist/CI/first-run guide, which is good. However, it does not ensure those commands appear in the intended “source checkout smoke” and “installed-wheel smoke” sections.
   **Recommendation:** Optional improvement: section-scope the checks so the source command is under the source smoke section and the installed-wheel command is under the installed-wheel smoke section.

3. **Reset commands are narrow enough, but the warning should explicitly mention user-edited config.**
   The proposed reset commands are specific `rm -f` commands for generated SQLite files, the two dated reports, and the three generated config files. They are not broad `rm -rf` commands and they preserve `data/README.md` and `reports/README.md`.
   **Recommendation:** Add wording like “review or copy any edits to `configs/sources.yaml`, `configs/entities.yaml`, and `configs/scoring.yaml` before running reset.”

4. **Planned file list has a small inconsistency with the requested proposed files.**
   The user’s proposed files include the Stage 49 release-review prompt/review files. The implementation plan also lists plan-review prompt/review files and includes them in the final `git add`. This may be intentional for recording this review, but it is extra relative to the proposed file list.
   **Recommendation:** Either explicitly include those plan-review files in the Stage 49 file scope or omit them from implementation/commit instructions.

## Answers to the specific review questions

1. **Does the plan give a new GitHub user a clear and accurate first-run path?**
   Yes. The planned `docs/first-run.md` chooser clearly separates source checkout smoke, installed-wheel smoke, manual repo-local sample output, dashboard inspection, and reset. The intended distinction between “verify without repo-local output” and “produce dashboard-inspectable sample output” is clear.

2. **Are the planned doc-drift tests strong enough without being too brittle?**
   Mostly yes, but they lean slightly brittle on exact prose. They are strong for command/path drift and acceptable for Stage 49, but section-scoped and normalized boundary checks would make them more maintainable.

3. **Does the plan preserve the Stage 47/48 smoke contract exactly, including source-checkout and installed-wheel commands?**
   Yes. The plan preserves:
   - `UV_NO_CONFIG=1 uv run python scripts/check_first_run_smoke.py --repo-root .`
   - `"$tmp_env/venv/bin/python" scripts/check_first_run_smoke.py --repo-root . --python "$tmp_env/venv/bin/python" --installed`

   It also preserves the contract that smokes use checked-in sample files, temporary config/data/report/export directories, verify generated dated reports, print `First-run sample smoke passed.`, and do not write repo-local `data/` or `reports/`.

4. **Are any planned reset commands risky or too broad for user-facing docs?**
   No broad destructive reset is planned. The commands are specific file removals. The only caution is that deleting generated config files may delete user edits, so the docs should explicitly warn users to review/copy local config changes first.

5. **Does the plan accidentally imply platform/social scraping, account login, browser automation, connector work, external services, or compliance-review functionality?**
   No. The design and plan explicitly exclude those areas and reinforce the boundary in README, first-run guide, and upload checklist. The dashboard mention is limited to local inspection of sample output.

6. **Is the verification plan sufficient before commit/push?**
   The verification commands are sufficient for a docs/tests-only stage: focused doc tests, full pytest, ruff, format check, lock checks, release hygiene, source smoke, build/archive check, installed-wheel smoke, and `uv.lock` unchanged.
   The issue is not verification coverage; it is the plan’s direct commit/push procedure.

## Whether any issue blocks implementation

- **Docs/tests implementation:** not blocked.
- **Commit/push phase as written:** blocked until the direct token-based push-to-main step is removed or made explicitly user-authorized and safer.

Because one Important issue remains, I am **not** including the Stage 49 implementation approval line.
