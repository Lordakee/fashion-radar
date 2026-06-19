I'll review the Stage 118 design and plan. Let me read the relevant files in parallel.
Now let me read the target docs that the plan modifies, to verify the section headings exist and the plan is consistent.
Let me read the README's `## Development` section and check the mirror-marker scan and release hygiene script context.
I've reviewed the spec, plan, and all four target docs against the existing test helpers. Here is my review.

## Review: Stage 118 Agent UV Run Hygiene

### Critical findings
None.

### Important findings

**I-1: Test assertions are not satisfiable for 2 of the 4 sections from the planned doc text alone** (`docs/superpowers/plans/...plan.md:59-78` vs `:95-140`)

The planned test requires all four sections to contain both `"mirror-backed"` and `"frozen mirror install"` (contiguous substrings). But the plan's prescribed edits only provide those phrases for README and the checklist:

- **`AGENTS.md` `## Dependencies And Mirrors`** (plan Step 1, `:95-106`): the new bullet contains `agent-run verification`, `uv --no-config run --frozen`, and `uv.lock`, but **neither** `mirror-backed` **nor** `frozen mirror install`. The existing section (AGENTS.md:30-44) also contains neither — it says "mirror-based" and "local mirror installs", not "mirror-backed" or "frozen mirror install". The follow-up sentence "Ensure the same section still says mirror-backed local installs use…" is the only thing that could introduce `mirror-backed` (via rewording the existing bullet), and it still does **not** introduce the contiguous phrase `frozen mirror install`.
- **`docs/dependency-mirrors.md` `## Project Practice`** (plan Step 3, `:118-128`): the new bullet lacks both phrases. The instruction "Keep the existing frozen mirror install bullets…" is factually wrong about this section — there are no such bullets in `## Project Practice` (dependency-mirrors.md:54-72 has "mirror-based"/"mirror-bound" only). The phrase `frozen mirror install` actually lives in a *different* section (`## Recover A Mirror-Rewritten Lockfile`, dependency-mirrors.md:89), which `_markdown_section_exact_heading(..., "Project Practice")` will not capture.

Consequence: following the plan literally, Task 2 Step 5's "Expected: the new test passes" (`:152`) will **fail** for these two sections. This directly answers review question #2 in the negative.

Resolution (pick one before coding):
1. Prescribe explicit additional prose in the AGENTS.md and dependency-mirrors.md sections that contains `mirror-backed` and `frozen mirror install` (e.g., mirror the README/checklist wording), **or**
2. Relax the loop so `mirror-backed` / `frozen mirror install` are only asserted where the added text naturally yields them (README + checklist), keeping `uv --no-config run --frozen`, `agent-run verification`, and `uv.lock` as the cross-section invariants.

### Minor findings

- **M-1**: The new test uses `_read(ROOT / "AGENTS.md")` (plan `:61`), but the file already defines `AGENTS_DOC = ROOT / "AGENTS.md"` (tests/test_cli_docs.py:27). Use the constant for consistency with the rest of the file (which uses `README`, `DEPENDENCY_MIRRORS_DOC`, `UPLOAD_CHECKLIST`).
- **M-2**: No CHANGELOG.md entry. Not test-enforced, but prior docs-only hygiene stages added one; optional.
- **M-3** (process): Design/plan invoke `opencode run --model zhipuai-coding-plan/glm-5.2 --variant max` for review (spec `:11-15`, plan `:40-42`), while AGENTS.md Review Gates (AGENTS.md:7-15) still mandate Claude Code `--effort max`. This matches recent stages (82/83), so it is established practice, but AGENTS.md Review Gates is now stale. Out of scope to fix here; flag for a future stage.

### Other review questions

1. **Mirror-backed frozen installs vs no-config frozen verification**: Correctly separated. Mirror install path (`UV_DEFAULT_INDEX=... uv sync --frozen --dev`), agent-run path (`uv --no-config run --frozen ...`), and public lockfile path (`UV_NO_CONFIG=1 uv lock --check` + marker scan) are distinct and consistent with existing docs.
3. **Headings & helpers**: All four target headings exist at the expected level (`AGENTS.md:30`, `README.md:871`, `dependency-mirrors.md:54`, `github-upload-checklist.md:9`). `_markdown_section_exact_heading`, `_normalized_text`, `_read`, and the path constants all exist (tests/test_cli_docs.py:310-421). Helper choice is appropriate; only the content matching is off (see I-1).
4. **Scope**: Remains docs/tests-only. No `src/`, `pyproject.toml`, `uv.lock`, CI, or runtime/dependency/connector/scraping/scheduling/monitoring/source-acquisition/ranking/coverage/compliance changes. Release gate even adds `git diff --exit-code -- uv.lock pyproject.toml` (plan `:200`). Clean.
5. **Verification commands**: Sufficient — focused RED, focused GREEN, adjacent docs tests, full release gate (hygiene, pytest, ruff check, ruff format, `UV_NO_CONFIG=1 uv lock --check`, marker scan, lockfile diff, `git diff --check`).

### Final statement

**There is one Important blocker (I-1).** The planned test is not internally consistent with the prescribed doc edits for `AGENTS.md` and `docs/dependency-mirrors.md`, so Task 2 Step 5 will not go green as written. Resolve I-1 (add the two missing phrases to those sections, or scope those two assertions to README/checklist) before implementation. No Critical blockers.
