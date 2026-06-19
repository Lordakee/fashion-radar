Now let me read the target docs and test file to verify the updated plan resolves the prior finding.
I'll verify each requirement against the actual target files and the updated plan.

## Review: Stage 118 Agent UV Run Hygiene (Re-review after I-1 fix)

### Verification of prior Important finding (I-1)

I traced each of the five required strings through the planned doc edits in all four scoped sections. After `_normalized_text` (which collapses whitespace including newlines to single spaces) and `.casefold()`, every planned bullet/sentence satisfies every assertion in the loop at `plan.md:85-91`:

| Section (heading) | `uv --no-config run --frozen` | `agent-run verification` | `mirror-backed` | `uv.lock` | `frozen mirror install` |
|---|---|---|---|---|---|
| AGENTS.md `## Dependencies And Mirrors` (`plan.md:113-118`) | ✓ | ✓ | ✓ "mirror-backed commands" | ✓ | ✓ "frozen mirror\ninstall commands" → normalized |
| README.md `## Development` (`plan.md:127-131`) | ✓ | ✓ | ✓ | ✓ | ✓ |
| dependency-mirrors.md `## Project Practice` (`plan.md:137-142`) | ✓ | ✓ | ✓ | ✓ | ✓ (line-wrapped, normalizes correctly) |
| github-upload-checklist.md `## Before Upload` (`plan.md:151-156`) | ✓ | ✓ | ✓ "mirror-backed local" | ✓ | ✓ |

I confirmed all four target headings exist at the expected level (`AGENTS.md:30`, `README.md:871`, `dependency-mirrors.md:54`, `github-upload-checklist.md:9`) and that `_markdown_section_exact_heading` will capture the new bullets within each section (the helper stops at the next same-or-higher level `##` heading, so e.g. `## Project Practice` will not bleed into `## Recover A Mirror-Rewritten Lockfile`). **I-1 is resolved.**

### Verification of prior Minor M-1

The test at `plan.md:75` now uses `_read(AGENTS_DOC)` instead of `_read(ROOT / "AGENTS.md")`, consistent with `tests/test_cli_docs.py:27`. All other path constants (`README`, `DEPENDENCY_MIRRORS_DOC`, `UPLOAD_CHECKLIST`) and helpers (`_read`, `_markdown_section_exact_heading`, `_normalized_text`) exist in the test file. **M-1 is resolved.**

### Scope verification

Docs/tests-only confirmed:
- Files modified: `AGENTS.md`, `README.md`, `docs/dependency-mirrors.md`, `docs/github-upload-checklist.md`, `tests/test_cli_docs.py` plus review artifacts.
- No `src/`, `pyproject.toml`, `uv.lock`, or CI workflow changes (`plan.md:27-29`).
- No runtime behavior, dependency, or lockfile changes.
- No connectors, scraping, scheduling, monitoring, source acquisition, ranking, coverage verification, or compliance/audit product behavior.
- Release gate (`plan.md:208-218`) adds `git diff --exit-code -- uv.lock pyproject.toml` as a guard.

### Critical findings
None.

### Important findings
None. Prior I-1 is resolved; the planned doc edits now explicitly introduce `mirror-backed` and `frozen mirror install` (plus the other three required strings) into all four scoped sections, and the test is internally consistent with the prescribed edits.

### Minor findings

- **M-1**: `plan.md:144` still says "Keep the existing frozen mirror install bullets and lockfile recovery section" for `## Project Practice`, but that section has no existing "frozen mirror install bullets" (the phrase lives in `## Recover A Mirror-Rewritten Lockfile` at `dependency-mirrors.md:89`). Harmless because the new bullet at `plan.md:137-142` supplies the required strings, but the preservation instruction is factually imprecise.
- **M-2**: `plan.md:120-121` instruction "Ensure the same section still says mirror-backed local installs use `UV_DEFAULT_INDEX=...`" is awkward because the existing AGENTS.md bullet says "for local mirror installs" (`AGENTS.md:35-36`), not "mirror-backed local installs". Doesn't affect test passage; suggest rewording to "Keep the existing `UV_DEFAULT_INDEX=... uv sync --frozen --dev` local mirror install bullet."
- **M-3** (carried): No `CHANGELOG.md` entry. Optional, not test-enforced.
- **M-4** (carried, out of scope): `AGENTS.md` Review Gates still mandate Claude Code `--effort max` while the stage uses opencode `zhipuai-coding-plan/glm-5.2 --variant max`. Flagged for a future stage.

### Final statement

**No Critical or Important blockers remain before implementation.** The updated plan resolves I-1 (all four scoped sections will satisfy all five assertions after the prescribed edits) and M-1 (test now uses `AGENTS_DOC`). The remaining findings are Minor and do not block implementation.
