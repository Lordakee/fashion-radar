I'll review the Stage 84 plan by reading all the relevant files.
Now I need to find the specific test that will be modified. Let me search for it and related tests.
Let me read the exact test function being modified and its surrounding context.
I've reviewed all five files. Here is my assessment.

## Findings

**No Critical or Important blockers.** The plan is sound and safe to implement.

### Minor (informational, not blocking)

1. **`rednote_mcp` assertion stays a substring** — `tests/test_cli_docs.py:1648-1650` currently asserts only the prefix `... external-tool-readiness --adapter rednote_mcp` (no `--format json` suffix). The plan correctly preserves this as-is, which is in scope since the docs claim at `docs/github-upload-checklist.md:282-290` only names the `instaloader` table/JSON pair. A future stage could tighten `rednote_mcp` similarly, but that is out of scope here.

2. **CLI reference already satisfies the claim** — `docs/cli-reference.md:235-236` already lists both `--format table` and `--format json` for `instaloader`, so the gap is genuinely installed-wheel-smoke-only. The plan correctly leaves the CLI reference untouched (it is not in the modify list).

## Answers To Review Questions

1. **Closes the gap without runtime change?** Yes. Only `docs/github-upload-checklist.md` (smoke script text) and `tests/test_cli_docs.py` (drift test) change. No `src/` touch. The added smoke command `external-tool-readiness --adapter instaloader --format table` already exists and is documented at `docs/cli-reference.md:235`; the smoke merely exercises it under the installed wheel.

2. **Insertion point correct?** Yes. Spec lines 43-49 and plan Task 2 both insert immediately after `... external-tool-readiness --help` and before the existing JSON command. This matches the current block at `docs/github-upload-checklist.md:427-429` and keeps the existing `instaloader` JSON and `rednote_mcp` JSON commands intact.

3. **Test pins both exact commands without weakening?** Yes. The loop
   ```python
   for format_name in ("table", "json"):
       assert (
           '"$tmp_env/venv/bin/fashion-radar" external-tool-readiness '
           f"--adapter instaloader --format {format_name}"
       ) in checklist
   ```
   strictly *strengthens* coverage (was JSON-only, now table+JSON) and preserves every existing assertion listed in plan Task 3: help-loop membership, the `--help` exact command, the `rednote_mcp` substring, and `scripts/check_first_run_smoke.py`. The concatenated string yields a single space between `external-tool-readiness` and `--adapter`, matching the checklist exactly.

4. **Verification sufficient?** Yes. Task 4 runs the affected test, the broader docs test file, both `external-tool-readiness` tests, `ruff check`/`format --check`, and `git diff --check` on the two files. Task 5 adds full release hygiene, full pytest, full ruff, `UV_NO_CONFIG=1 uv lock --check`, the mirror-string scan, and `git diff --exit-code -- uv.lock pyproject.toml`. This matches the project's mirror-free lockfile discipline and is appropriate for a docs/test-only node.

5. **Blockers?** None. Scope is respected: modify list is exactly `docs/github-upload-checklist.md` + `tests/test_cli_docs.py` + Stage 84 artifacts; no `src/`, manifests, `uv.lock`, CI, `AGENTS.md`, or `docs/REVIEW_PROTOCOL.md`. No boundary-bridging behavior is introduced (no scraping, connectors, platform APIs, login/cookie/session/token, media downloads, monitoring, scheduling, source acquisition, demand proof, ranking, coverage verification, or compliance-review features). The `external-tool-readiness` boundary in `AGENTS.md` is not affected since command behavior is unchanged.

**Recommendation:** Proceed to implementation.
