# Stage 187 Community Adapter Catalog Exact Table Guard Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make the community docs adapter catalog guard reject stale extra rows and row-order drift by asserting the exact `Known adapter ids` table block.

**Architecture:** Test-only docs parity hardening in `tests/test_external_tool_contract_parity.py`. Extract the contiguous Markdown table after each community doc's `Known adapter ids:` marker, compare it to a registry-derived expected table, and use a temporary doc mutation to prove the new guard fails on stale extra rows before restoring GREEN.

**Tech Stack:** Python, pytest, Markdown docs, existing `build_external_tool_adapter_registry(...)`, `uv --no-config run --frozen`, local opencode review with `zhipuai-coding-plan/glm-5.2 --variant max`.

---

## Files

- Modify: `tests/test_external_tool_contract_parity.py`
  - Add `_known_adapter_catalog_doc_table(text)`.
  - Add `test_community_signal_docs_have_exact_current_external_tool_adapter_catalog_table`.
- Read-only RED proof mutation, reverted before commit:
  - Temporarily edit `docs/community-signal-quality.md` or `docs/community-signal-import.md` to add one stale adapter row.
- Add: `docs/superpowers/specs/2026-06-24-stage-187-community-adapter-catalog-exact-table-design.md`
- Add: `docs/superpowers/plans/2026-06-24-stage-187-community-adapter-catalog-exact-table-plan.md`
- Add: `docs/reviews/opencode-stage-187-plan-review-prompt.md`
- Add after plan review: `docs/reviews/opencode-stage-187-plan-review.md`
- Add after implementation: `docs/reviews/opencode-stage-187-code-review-prompt.md`
- Add after implementation: `docs/reviews/opencode-stage-187-code-review.md`
- Add before commit: `docs/reviews/opencode-stage-187-release-review-prompt.md`
- Add before commit: `docs/reviews/opencode-stage-187-release-review.md`

## Task 1: Add Exact Adapter Catalog Table Guard

**Files:**

- Modify: `tests/test_external_tool_contract_parity.py`

- [ ] **Step 1: Confirm the new exact-table test does not already exist**

Run:

```bash
uv --no-config run --frozen pytest \
  tests/test_external_tool_contract_parity.py::test_community_signal_docs_have_exact_current_external_tool_adapter_catalog_table -q
```

Expected before adding the test: pytest reports the test name is not found or no
matching test is collected.

- [ ] **Step 2: Add the table extraction helper**

Add this helper immediately after `_adapter_catalog_doc_row(...)`:

```python
def _known_adapter_catalog_doc_table(text: str) -> list[str]:
    lines = text.splitlines()

    assert lines.count("Known adapter ids:") == 1
    marker_index = lines.index("Known adapter ids:")
    assert lines[marker_index + 1] == ""

    table_lines: list[str] = []
    for line in lines[marker_index + 2 :]:
        if not line.startswith("|"):
            break
        table_lines.append(line)

    return table_lines
```

- [ ] **Step 3: Add the exact-table test**

Add this test immediately after
`test_community_signal_docs_list_current_external_tool_adapter_catalog`:

```python
def test_community_signal_docs_have_exact_current_external_tool_adapter_catalog_table(
    registry,
) -> None:
    expected_table = [
        "| Adapter id | Display/source name | Platform label | Format | Pattern |",
        "| --- | --- | --- | --- | --- |",
        *[_adapter_catalog_doc_row(adapter) for adapter in registry.adapters],
    ]

    for doc_path in COMMUNITY_SIGNAL_EXTERNAL_TOOL_DOCS:
        actual_table = _known_adapter_catalog_doc_table(
            doc_path.read_text(encoding="utf-8")
        )

        assert actual_table == expected_table, doc_path.relative_to(ROOT)
```

- [ ] **Step 4: Run the new test on clean docs**

Run:

```bash
uv --no-config run --frozen pytest \
  tests/test_external_tool_contract_parity.py::test_community_signal_docs_have_exact_current_external_tool_adapter_catalog_table -q
```

Expected: the test passes if the existing community doc tables are already
exactly current.

## Task 2: Prove RED With Temporary Stale Row Mutation

**Files:**

- Temporarily modify and then restore: `docs/community-signal-quality.md`

- [ ] **Step 1: Add one temporary stale row**

Temporarily insert this row below the current
`generic_community_export` row in `docs/community-signal-quality.md`:

```markdown
| `removed_adapter` | Removed Adapter | `community` | `json` | `*.json` |
```

- [ ] **Step 2: Run the exact-table test and verify RED**

Run:

```bash
uv --no-config run --frozen pytest \
  tests/test_external_tool_contract_parity.py::test_community_signal_docs_have_exact_current_external_tool_adapter_catalog_table -q
```

Expected: the test fails because `docs/community-signal-quality.md` has one
extra table row that is not present in the live adapter registry.

- [ ] **Step 3: Remove the temporary stale row**

Remove the temporary `removed_adapter` row from
`docs/community-signal-quality.md`.

- [ ] **Step 4: Run the exact-table test and verify GREEN**

Run:

```bash
uv --no-config run --frozen pytest \
  tests/test_external_tool_contract_parity.py::test_community_signal_docs_have_exact_current_external_tool_adapter_catalog_table -q
```

Expected: the test passes after the temporary mutation is removed.

## Task 3: Focused Verification And Code Review

**Files:**

- Modify: `tests/test_external_tool_contract_parity.py`
- Add: `docs/reviews/opencode-stage-187-code-review-prompt.md`
- Add: `docs/reviews/opencode-stage-187-code-review.md`

- [ ] **Step 1: Run focused verification**

Run:

```bash
uv --no-config run --frozen pytest tests/test_external_tool_contract_parity.py -q -k "adapter_catalog or community_signal_docs"
uv --no-config run --frozen pytest tests/test_external_tool_contract_parity.py -q
uv --no-config run --frozen ruff check tests/test_external_tool_contract_parity.py
uv --no-config run --frozen ruff format --check tests/test_external_tool_contract_parity.py
```

Expected: all focused tests and checks pass.

- [ ] **Step 2: Create code review prompt**

Create `docs/reviews/opencode-stage-187-code-review-prompt.md` requiring the
response body to start with:

```text
# Stage 187 Code Review
```

- [ ] **Step 3: Run code review**

Run:

```bash
tmp_review="$(mktemp)"
opencode run --model zhipuai-coding-plan/glm-5.2 --variant max \
  --dir /home/ubuntu/fashion-radar \
  "$(cat docs/reviews/opencode-stage-187-code-review-prompt.md)" > "$tmp_review" 2>&1
awk 'BEGIN{copy=0} /^# Stage 187 Code Review/{copy=1} copy{print}' "$tmp_review" > docs/reviews/opencode-stage-187-code-review.md
if [ ! -s docs/reviews/opencode-stage-187-code-review.md ]; then cp "$tmp_review" docs/reviews/opencode-stage-187-code-review.md; fi
rm -f "$tmp_review"
```

Expected: completed review output with no Critical or Important findings. Clean
the artifact if opencode includes process chatter, ANSI output, command logs,
code fences, or duplicated drafts.

## Task 4: Release Gate, Release Review, Commit, And Push

**Files:**

- Add: `docs/reviews/opencode-stage-187-release-review-prompt.md`
- Add: `docs/reviews/opencode-stage-187-release-review.md`

- [ ] **Step 1: Run release gate**

Run:

```bash
env -u all_proxy -u ALL_PROXY -u http_proxy -u HTTP_PROXY -u https_proxy -u HTTPS_PROXY -u no_proxy -u NO_PROXY uv --no-config run --frozen pytest -q
uv --no-config run --frozen python scripts/check_first_run_smoke.py --repo-root .
uv --no-config run --frozen python scripts/check_release_hygiene.py --repo-root .
uv --no-config run --frozen ruff check .
uv --no-config run --frozen ruff format --check .
env -u UV_DEFAULT_INDEX -u UV_INDEX_URL -u UV_EXTRA_INDEX_URL UV_NO_CONFIG=1 uv lock --check
git diff --check
rg -n 'ghp_[A-Za-z0-9]+' .
git config --get-all http.https://github.com/.extraheader
```

Expected: all commands pass; token and extraheader checks report no persisted
secrets. For the two absence checks, exit 1 with no output is the expected clean
result.

- [ ] **Step 2: Create and run release review**

Create `docs/reviews/opencode-stage-187-release-review-prompt.md` requiring the
review body to start with:

```text
# Stage 187 Release Review
```

Run the same temp-file `opencode run --model zhipuai-coding-plan/glm-5.2
--variant max` capture flow used for code review, copying the completed review
to `docs/reviews/opencode-stage-187-release-review.md`.

Expected: completed review output with no Critical or Important findings. Clean
the artifact if needed.

- [ ] **Step 3: Commit and push**

Run:

```bash
git status --short
git add \
  tests/test_external_tool_contract_parity.py \
  docs/superpowers/specs/2026-06-24-stage-187-community-adapter-catalog-exact-table-design.md \
  docs/superpowers/plans/2026-06-24-stage-187-community-adapter-catalog-exact-table-plan.md \
  docs/reviews/opencode-stage-187-plan-review-prompt.md \
  docs/reviews/opencode-stage-187-plan-review.md \
  docs/reviews/opencode-stage-187-code-review-prompt.md \
  docs/reviews/opencode-stage-187-code-review.md \
  docs/reviews/opencode-stage-187-release-review-prompt.md \
  docs/reviews/opencode-stage-187-release-review.md
git commit -m "test: pin community adapter catalog tables"
git push origin main
```

Expected: commit succeeds and `main` pushes to GitHub.

## Self-Review Notes

- Spec coverage: Task 1 adds the exact-table guard, Task 2 proves it catches a
  stale extra row, Task 3 covers focused verification and code review, and
  Task 4 covers full release gate, release review, commit, and push.
- Placeholder scan: no placeholders or deferred implementation notes.
- Boundary check: runtime source, docs content, CLI behavior, dependencies,
  source acquisition, ranking, monitoring, scraping, platform APIs, and
  compliance-review product behavior remain out of scope.
