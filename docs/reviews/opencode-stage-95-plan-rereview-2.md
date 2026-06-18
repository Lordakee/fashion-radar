I'll review the Stage 95 plan after the second correction. Let me read all the relevant files in parallel.
Now let me empirically verify the planned test code passes against the current `docs/architecture.md` by running the exact helper and assertions.
Let me also confirm the test file doesn't exist yet (to validate scope) and check existing patterns referenced in the prior reviews.
All checks pass. Writing findings now.

# Stage 95 Plan Second Re-Review Findings

## Critical

None.

## Important

None.

## Minor

None new.

## Review Question Answers

**1. Is the prior Critical finding resolved?**
Yes. The prior re-review's C1 (call-site regression) is fixed. The helper body uses the repo convention `marker = f"\n{heading}\n"` (`plan.md:54-57`), and the call site at `plan.md:65` now passes the full heading:

```python
section = _markdown_section(_read_architecture_doc(), "## Source Boundary")
```

This matches the established `tests/test_cli_docs.py` call convention. Verified `marker in ("\n" + text)` returns `True` against the current `docs/architecture.md:401`.

- Prior original C1 (broken `test_docs_reference_existing_paths` node): **Resolved** — `rg` confirms no reference to that non-existent test remains in the plan; Task 3 runs only `tests/test_architecture_boundary_docs.py`.
- Prior original I1 (helper anchor fragility): **Resolved** — helper now newline-anchored.
- Prior original M1 (release-anchor phrase): **Resolved** — phrase is `"non-core platform collection is not part of v0.1.0"`.

**2. Does the planned test code now pass against the current `docs/architecture.md`?**
Yes. I ran the exact helper + assertions verbatim from the plan against the current `docs/architecture.md`:

- `marker in (newline+text)`: **True**
- Section extraction ends cleanly at `## Dashboard Boundary` (next `## ` heading) — confirmed by normalized output terminating at `see [source-boundaries.md](source-boundaries.md).`
- All six phrases **PASS**:
  - `the core collector set is rss, rsshub-compatible feeds, and gdelt`
  - `manual signal import is a local input path`
  - `user-provided csv/json files`
  - `not a connector or platform collector`
  - `non-core platform collection is not part of v0.1.0`
  - `source-boundaries.md`

No `### Source Boundary` subsection exists in the file (`rg '^#+ Source Boundary'` matches only the `##` heading at line 401), so even the original fragility concern is moot in practice; the convention fix makes it moot in principle too.

**3. Are there any remaining Critical or Important blockers before implementation?**
**No.** There are no Critical or Important blockers. Scope is respected (only `tests/test_architecture_boundary_docs.py` plus review artifacts are created; `docs/architecture.md`, `src/`, `tests/test_cli_docs.py`, `uv.lock`, etc. are untouched). The stage is safe to implement.

One process note (not a blocker, not new): `AGENTS.md` / `docs/REVIEW_PROTOCOL.md` still specify plan reviews via `claude --effort max --permission-mode plan`; the plan's Task 1 uses `opencode run --model zhipuai-coding-plan/glm-5.2 --variant max` instead. This matches the model requested for this review and is consistent with the prior review notes — worth confirming the substitution is intended, but it does not affect Stage 95 implementation correctness.
