# Stage 86 Adapter Platform Label Docs Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Clarify README and CLI reference adapter registry `Platform label`
tables as advisory local provenance label guidance from
`suggested_platform_labels`, without changing runtime behavior or validation.

**Architecture:** This is a docs/test-only clarification. The existing adapter
registry remains the source of current adapter labels, while the new prose
explains that table labels are optional local provenance suggestions rather
than schema, linter, platform coverage, or demand-proof claims.

**Tech Stack:** Markdown docs, pytest docs drift tests, uv, Ruff.

---

## File Map

- Modify `README.md`.
- Modify `docs/cli-reference.md`.
- Modify `tests/test_cli_docs.py`.
- Add Stage 86 review artifacts under `docs/reviews/`.

Do not modify `src/`, schemas, lint/import behavior, adapter command behavior,
dependency manifests, `uv.lock`, CI workflows, `AGENTS.md`, or
`docs/REVIEW_PROTOCOL.md`.

## Task 1: Plan Review

- [ ] Create `docs/reviews/opencode-stage-86-plan-review-prompt.md`.
- [ ] Run local opencode plan review:

```bash
opencode run --model zhipuai-coding-plan/glm-5.2 --variant max --dir /home/ubuntu/fashion-radar "$(cat docs/reviews/opencode-stage-86-plan-review-prompt.md)" > docs/reviews/opencode-stage-86-plan-review.md
```

- [ ] Fix Critical or Important findings before implementation.

## Task 2: Add Adapter Table Docs Drift Test

- [ ] In `tests/test_cli_docs.py`, add this focused test immediately after
  `test_external_tool_adapter_registry_docs_are_linked_and_bounded`:

```python
def test_external_tool_adapter_platform_label_docs_are_advisory() -> None:
    readme_section = _markdown_section(_read(README), "## What It Does Not Do")
    cli_section = _markdown_section(
        _read(CLI_REFERENCE),
        "## Local Import And Community Handoff",
    )

    for label, section in (
        ("README.md", readme_section),
        ("docs/cli-reference.md", cli_section),
    ):
        normalized = _normalized_text(section).casefold()
        assert "known adapter ids:" in normalized
        for term in (
            "platform label column",
            "suggested_platform_labels",
            "advisory local provenance label guidance",
            "optional handoff `platform` field",
            "not a schema enum",
            "not a linter restriction",
            "not platform coverage",
            "not demand proof",
        ):
            assert term.casefold() in normalized, f"{label} missing {term!r}"
```

- [ ] Run the new test and confirm it fails before the docs prose is added:

```bash
uv --no-config run --frozen pytest tests/test_cli_docs.py::test_external_tool_adapter_platform_label_docs_are_advisory -q
```

Expected: FAIL because README and CLI reference do not yet describe the
`Platform label` column as advisory `suggested_platform_labels` guidance.

## Task 3: Add README Adapter Table Prose

- [ ] In `README.md`, find the `Known adapter ids:` table under the
  `external-tool-adapters` subsection in `## What It Does Not Do`.
- [ ] Immediately after the existing paragraph:

```markdown
The Display/source name column reflects the current registry `display_name` and
`suggested_source_name` values, which are identical for these adapters.
```

add:

```markdown
The Platform label column reflects `suggested_platform_labels` as advisory local
provenance label guidance for the optional handoff `platform` field. These
labels are local provenance suggestions only: they are not a schema enum, not a
linter restriction, not platform coverage, and not demand proof.
```

## Task 4: Add CLI Reference Adapter Table Prose

- [ ] In `docs/cli-reference.md`, find the indented `Known adapter ids:` table
  under the `external-tool-adapters` bullet.
- [ ] Immediately after the existing indented paragraph:

```markdown
  The Display/source name column reflects the current registry `display_name`
  and `suggested_source_name` values, which are identical for these adapters.
```

add:

```markdown
  The Platform label column reflects `suggested_platform_labels` as advisory local
  provenance label guidance for the optional handoff `platform` field. These
  labels are local provenance suggestions only: they are not a schema enum, not a
  linter restriction, not platform coverage, and not demand proof.
```

## Task 5: Focused Verification And Review

- [ ] Run:

```bash
uv --no-config run --frozen pytest tests/test_cli_docs.py::test_external_tool_adapter_platform_label_docs_are_advisory -q
uv --no-config run --frozen pytest tests/test_cli_docs.py -q
```

- [ ] Create `docs/reviews/opencode-stage-86-code-review-prompt.md`.
- [ ] Run local opencode code review:

```bash
opencode run --model zhipuai-coding-plan/glm-5.2 --variant max --dir /home/ubuntu/fashion-radar "$(cat docs/reviews/opencode-stage-86-code-review-prompt.md)" > docs/reviews/opencode-stage-86-code-review.md
```

- [ ] Fix Critical or Important findings before final verification.

## Task 6: Full Verification, Commit, Push

- [ ] Run:

```bash
uv --no-config run --frozen python scripts/check_release_hygiene.py
env -u ALL_PROXY -u all_proxy uv --no-config run --frozen pytest
uv --no-config run --frozen ruff check .
uv --no-config run --frozen ruff format --check .
UV_NO_CONFIG=1 uv lock --check
! rg -n 'tuna|aliyun|ustc|huaweicloud|mirror|index-url|extra-index-url|find-links' uv.lock
git diff --exit-code -- uv.lock pyproject.toml
git diff --check
```

- [ ] Stage only Stage 86 files and run staged hygiene checks:

```bash
! git diff --cached --name-only | rg -x 'uv.lock'
uv --no-config run --frozen python scripts/check_release_hygiene.py --repo-root .
git diff --cached --check
git grep --cached -n -E 'gh[pousr]_[A-Za-z0-9]{36,255}|github_pat_[A-Za-z0-9_]{82,255}|-----BEGIN [A-Z0-9 ]*PRIVATE KEY-----' -- . ':!uv.lock' && exit 1 || true
```

- [ ] Commit with:

```bash
git commit -m "Clarify adapter platform labels"
```

- [ ] Push with the stored token via temporary git extraheader only.
- [ ] Verify GitHub Actions completes successfully.
