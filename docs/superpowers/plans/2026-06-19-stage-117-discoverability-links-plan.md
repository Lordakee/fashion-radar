# Stage 117 Discoverability Links Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add lightweight discoverability pointers in the summary docs so users can find the already-pinned checked-in directory preflight examples from Stage 116.

**Architecture:** Keep this as a docs/tests-only node. Do not duplicate the Stage 116 command blocks. Add short pointers in the summary docs to the existing example README and/or the `docs/community-signal-import.md#external-tool-export-directory-examples` section, then add section-scoped docs tests that prove those pointers exist.

**Tech Stack:** Python 3.11, pytest, Typer docs, markdown, uv, ruff, local opencode review with `zhipuai-coding-plan/glm-5.2 --variant max`.

---

## Files

- Modify: `README.md`
- Modify: `docs/cli-reference.md`
- Modify: `docs/first-run.md`
- Modify: `docs/github-upload-checklist.md`
- Modify: `tests/test_cli_docs.py`
- Create: `docs/reviews/opencode-stage-117-plan-review-prompt.md`
- Create later: `docs/reviews/opencode-stage-117-plan-review.md`
- Create if plan review requires changes: `docs/reviews/opencode-stage-117-plan-rereview-prompt.md`
- Create if plan review requires changes: `docs/reviews/opencode-stage-117-plan-rereview.md`
- Create later: `docs/reviews/opencode-stage-117-code-review-prompt.md`
- Create later: `docs/reviews/opencode-stage-117-code-review.md`

Do not modify `src/`, `uv.lock`, `pyproject.toml`, schemas, collectors, source
packs, entity packs, dashboard, importers, scoring, reports, CI, or GitHub
workflows.

## Task 0: Plan Review

- [ ] **Step 1: Create the plan review prompt**

Create `docs/reviews/opencode-stage-117-plan-review-prompt.md` with the
current Stage 117 design and plan review request.

- [ ] **Step 2: Run local opencode plan review**

Run:

```bash
opencode run --model zhipuai-coding-plan/glm-5.2 --variant max --dir /home/ubuntu/fashion-radar "$(cat docs/reviews/opencode-stage-117-plan-review-prompt.md)" > docs/reviews/opencode-stage-117-plan-review.md
```

Expected: review completes and states whether there are Critical or Important
blockers.

- [ ] **Step 3: Resolve Critical/Important plan findings before coding**

If the review identifies Critical or Important findings, update the design,
plan, or scope before Task 1.

- [ ] **Step 4: Run focused plan rereview if Critical/Important findings were fixed**

If Step 3 changed the plan after Critical or Important findings, create
`docs/reviews/opencode-stage-117-plan-rereview-prompt.md` and run:

```bash
opencode run --model zhipuai-coding-plan/glm-5.2 --variant max --dir /home/ubuntu/fashion-radar "$(cat docs/reviews/opencode-stage-117-plan-rereview-prompt.md)" > docs/reviews/opencode-stage-117-plan-rereview.md
```

Expected: the rereview explicitly says there are no remaining Critical or
Important blockers before implementation.

## Task 1: Write Failing Tests

- [ ] **Step 1: Add a discoverability test for summary docs**

Add a new test in `tests/test_cli_docs.py` after
`test_external_community_tool_directory_example_docs_are_linked_and_bounded`.
Use the existing helpers already defined in that file: `_read`,
`_markdown_section`, and `_normalized_text`.

Recommended test name:

```python
def test_external_community_tool_directory_preflight_examples_are_discoverable() -> None:
```

Recommended section-scoped assertions:

```python
def test_external_community_tool_directory_preflight_examples_are_discoverable() -> None:
    readme = _read(README)
    cli_reference = _read(CLI_REFERENCE)
    first_run = _read(FIRST_RUN_DOC)
    upload_checklist = _read(UPLOAD_CHECKLIST)

    def between(text: str, start: str, end: str) -> str:
        assert start in text
        assert end in text
        return text.split(start, 1)[1].split(end, 1)[0]

    readme_section = between(
        readme,
        "The external community tool export directory examples are",
        "`external-tool-adapters` is a local",
    )
    cli_reference_section = between(
        cli_reference,
        "For local/external tools that need machine-readable example discovery",
        "Print adapter registry examples:",
    )
    first_run_section = between(
        first_run,
        "The community handoff commands are also available for local directory-based handoffs:",
        "## Inspect The Sample In The Dashboard",
    )
    checklist_section = between(
        upload_checklist,
        "External community tool export directory examples docs check:",
        "External social/community tool adapter registry docs check:",
    )

    for section in (readme_section, cli_reference_section, first_run_section, checklist_section):
        normalized = _normalized_text(section).casefold()
        assert "examples/community-tool-handoff-directory.example/readme.md" in normalized
        assert "external-tool-readiness" in normalized
        assert "external-tool-workflow" in normalized
        assert "generic_community_export" in normalized
        assert "preflight examples" in normalized
        assert "checked-in" in normalized
        assert "csv" in normalized
        assert "json" in normalized
        assert "community-signal-import.md#external-tool-export-directory-examples" in normalized

    assert "community-signal-import.md#external-tool-export-directory-examples" in _normalized_text(
        cli_reference_section
    ).casefold()
```

- [ ] **Step 2: Run the focused RED test**

Run:

```bash
env -u ALL_PROXY -u all_proxy uv --no-config run --frozen pytest \
  tests/test_cli_docs.py::test_external_community_tool_directory_preflight_examples_are_discoverable \
  -q
```

Expected: the new test fails because the summary docs do not yet include the
discoverability pointers.

## Task 2: Update Summary Docs

- [ ] **Step 1: Add a pointer in `README.md`**

In the section around the checked-in directory examples, add one short sentence
after the list of example paths:

```markdown
The example README includes `external-tool-readiness` and
`external-tool-workflow` preflight examples for the checked-in
`generic_community_export` CSV and JSON directories, and the concrete command
block lives in
[docs/community-signal-import.md#external-tool-export-directory-examples](docs/community-signal-import.md#external-tool-export-directory-examples).
```

- [ ] **Step 2: Add a pointer in `docs/cli-reference.md`**

In the `Local Import And Community Handoff` section, after the `directory_example_paths`
paragraph and before `Print adapter registry examples:`, add:

```markdown
For copyable `generic_community_export` CSV/JSON `external-tool-readiness` /
`external-tool-workflow` preflight examples against the checked-in directory
examples, see
[community-signal-import.md#external-tool-export-directory-examples](community-signal-import.md#external-tool-export-directory-examples).
```

- [ ] **Step 3: Add a pointer in `docs/first-run.md`**

After the paragraph that introduces the local directory-based handoff commands,
add:

```markdown
The checked-in `generic_community_export` CSV/JSON directory preflight examples live in
[examples/community-tool-handoff-directory.example/README.md](../examples/community-tool-handoff-directory.example/README.md)
and the concrete `external-tool-readiness` / `external-tool-workflow` command
pairs for `External Community Tool` are documented in
[community-signal-import.md#external-tool-export-directory-examples](community-signal-import.md#external-tool-export-directory-examples).
```

- [ ] **Step 4: Add a pointer in `docs/github-upload-checklist.md`**

In the directory examples docs check, add this checklist item:

```markdown
- [ ] Docs point to
      [examples/community-tool-handoff-directory.example/README.md](../examples/community-tool-handoff-directory.example/README.md)
      as the checked-in `generic_community_export` CSV/JSON
      `external-tool-readiness` / `external-tool-workflow` preflight examples,
      and link the concrete command block in
      [community-signal-import.md#external-tool-export-directory-examples](community-signal-import.md#external-tool-export-directory-examples).
```

- [ ] **Step 5: Run GREEN focused tests**

Run:

```bash
env -u ALL_PROXY -u all_proxy uv --no-config run --frozen pytest \
  tests/test_cli_docs.py::test_external_community_tool_directory_preflight_examples_are_discoverable \
  -q
```

Expected: the new discoverability test passes.

## Task 3: Adjacent Verification

- [ ] **Step 1: Run adjacent docs tests**

Run:

```bash
env -u ALL_PROXY -u all_proxy uv --no-config run --frozen pytest \
  tests/test_cli_docs.py \
  -q
```

Expected: the CLI/docs suite passes.

- [ ] **Step 2: Create code review prompt**

Create `docs/reviews/opencode-stage-117-code-review-prompt.md` summarizing the
Stage 117 docs/test changes, files touched, and verification commands.

- [ ] **Step 3: Run local opencode code review**

Run:

```bash
opencode run --model zhipuai-coding-plan/glm-5.2 --variant max --dir /home/ubuntu/fashion-radar "$(cat docs/reviews/opencode-stage-117-code-review-prompt.md)" > docs/reviews/opencode-stage-117-code-review.md
```

Expected: review completes and explicitly lists no Critical or Important
blockers, or lists findings to fix before release.

- [ ] **Step 4: Fix Critical/Important review findings**

If the review identifies Critical or Important findings, fix them and rerun the
focused and adjacent tests.

## Task 4: Release Gate, Commit, Push

- [ ] **Step 1: Run full release gate**

Run:

```bash
uv --no-config run --frozen python scripts/check_release_hygiene.py
env -u ALL_PROXY -u all_proxy uv --no-config run --frozen pytest
uv --no-config run --frozen ruff check .
uv --no-config run --frozen ruff format --check .
env -u UV_DEFAULT_INDEX -u UV_INDEX_URL -u UV_EXTRA_INDEX_URL UV_NO_CONFIG=1 uv lock --check
if rg -n 'tuna|aliyun|ustc|huaweicloud|mirror|index-url|extra-index-url|find-links' uv.lock; then exit 1; fi
git diff --exit-code -- uv.lock pyproject.toml
git diff --check
```

Expected: every command exits 0, and there is no mirror URL in `uv.lock`.

- [ ] **Step 2: Stage intended files only**

Run:

```bash
git add \
  docs/superpowers/specs/2026-06-19-stage-117-discoverability-links-design.md \
  docs/superpowers/plans/2026-06-19-stage-117-discoverability-links-plan.md \
  docs/reviews/opencode-stage-117-plan-review-prompt.md \
  docs/reviews/opencode-stage-117-plan-review.md \
  docs/reviews/opencode-stage-117-plan-rereview-prompt.md \
  docs/reviews/opencode-stage-117-plan-rereview.md \
  docs/reviews/opencode-stage-117-code-review-prompt.md \
  docs/reviews/opencode-stage-117-code-review.md \
  README.md \
  docs/cli-reference.md \
  docs/first-run.md \
  docs/github-upload-checklist.md \
  tests/test_cli_docs.py
git diff --cached --name-only
git diff --cached --check
```

Expected: only intended files are staged, and staged whitespace check exits 0.

- [ ] **Step 3: Commit**

Run:

```bash
git commit -m "Link directory preflight examples from summary docs"
```

- [ ] **Step 4: Push without persisting credentials**

Use a temporary GitHub auth extraheader for the push only. After push, confirm
there is no persisted extraheader and that `git remote -v` does not expose a
token.

- [ ] **Step 5: Verify CI**

Poll the GitHub Actions run for the pushed commit until it passes or fails.

- [ ] **Step 6: Handoff Summary**

Write a short Handoff Summary with repo status, verified commands, uncommitted
files, and the next recommended stage. Do not include large diffs or logs.
