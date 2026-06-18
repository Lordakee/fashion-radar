I'll review the Stage 95 plan files. Let me read them in parallel.
Let me verify the section helper convention referenced in the prior review and check the test_cli_docs patterns.
I found a potential regression in the I1 fix. Let me verify it empirically by running the exact helper code from the plan against the real `architecture.md`.
Confirmed the regression. Now let me verify that, with the convention-correct call, all six phrases actually pass (to confirm the rest of the plan is sound).
# Stage 95 Plan Re-Review Findings

## Critical

**C1 — The I1 "fix" regressed: the section helper now fails its own assert at runtime.**
The prior review (I1) recommended matching the repo convention in `tests/test_cli_docs.py:389-392`, whose helper body is `marker = f"\n{heading}\n"`. The plan copied that helper body verbatim
(`docs/superpowers/plans/2026-06-18-stage-95-architecture-source-boundary-docs-plan.md:54-57`):

```python
def _markdown_section(text: str, heading: str) -> str:
    marker = f"\n{heading}\n"
    assert marker in f"\n{text}"
    return text.split(heading, 1)[1].split("\n## ", 1)[0]
```

but did **not** copy the corresponding call convention. The repo always passes the **full heading including the `## ` prefix** — see `tests/test_cli_docs.py:444,455,460,1301,1560` (e.g. `_markdown_section(_read(FIRST_RUN_DOC), "## Prepare A Source Checkout")`). The plan's call site omits the prefix (`plan.md:65`):

```python
section = _markdown_section(_read_architecture_doc(), "Source Boundary")
```

So `marker` becomes `"\nSource Boundary\n"`, which is **not** a substring of the markdown (the heading line is `## Source Boundary`). I verified empirically against the real `docs/architecture.md`:

```
marker repr: '\nSource Boundary\n'
marker in (newline+text): False        -> assert raises AssertionError
convention marker repr: '\n## Source Boundary\n'
convention marker in (newline+text): True
```

The test as written errors at the `assert` line, which breaks Task 3's `uv run pytest tests/test_architecture_boundary_docs.py -q` and Task 4's full suite. This is a regression from the original plan (the pre-fix `marker = f"## {heading}"` form actually passed); the incomplete fix turned a fragility issue into a hard failure.

**Fix (smallest, convention-aligned):** change `plan.md:65` to pass the full heading:

```python
section = _markdown_section(_read_architecture_doc(), "## Source Boundary")
```

I confirmed that with this one-character-class change all six assertions pass against the current `docs/architecture.md`. The design spec (`...design.md:31`) already states the intent correctly ("extracts only the `## Source Boundary` section"), so only the plan code block needs the edit. No `docs/architecture.md` or scope change required.

## Important

None beyond C1.

## Minor

None new. (Prior M1 is resolved: phrase is now `"non-core platform collection is not part of v0.1.0"` at `plan.md:73`. Prior M2 is moot since Task 1 overwrites the stale review file.)

## Review Question Answers

**1. Are the prior Critical and Important findings resolved?**
- Prior C1 (broken `test_docs_reference_existing_paths` node): **Resolved.** Verification commands in both the design (`...design.md:47-51`) and the plan (`plan.md:84-88`) now run only `tests/test_architecture_boundary_docs.py`; the non-existent node is gone.
- Prior I1 (helper anchor fragility): **Not resolved — regressed into C1 above.** The helper body was updated but the call site was not, so the test now fails outright instead of being merely fragile.
- Prior M1 (release-anchor phrase): **Resolved** (`plan.md:73`).

**2. Are all remaining proposed docs assertions present in the current `## Source Boundary` section?**
Yes. Verified empirically by extracting the section (with the convention-correct call) and normalizing — all six phrases match the current `docs/architecture.md:401-406`:

| Phrase | Present |
|---|---|
| `the core collector set is rss, rsshub-compatible feeds, and gdelt` | ✅ |
| `manual signal import is a local input path` | ✅ |
| `user-provided csv/json files` | ✅ |
| `not a connector or platform collector` | ✅ |
| `non-core platform collection is not part of v0.1.0` | ✅ |
| `source-boundaries.md` | ✅ |

**3. Are there remaining Critical or Important blockers before implementation?**
**Yes — one Critical blocker (C1 above).** Fix the call site at `plan.md:65` to pass `"## Source Boundary"` before implementing Task 2. Scope is respected (only the plan artifact changes; no disallowed file is touched). After that one-line plan edit, the stage is safe to implement.
