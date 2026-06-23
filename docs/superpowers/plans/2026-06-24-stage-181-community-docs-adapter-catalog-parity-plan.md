# Stage 181 Community Docs Adapter Catalog Parity Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make community signal docs list the current external social/community tool adapter catalog and guard that catalog against runtime registry drift.

**Architecture:** Docs/test-only parity hardening. Derive expected Markdown table rows from the existing external-tool adapter registry fixture, assert both community docs contain those rows and advisory platform-label wording, then add the same compact table already used by README/CLI reference to the two community docs.

**Tech Stack:** Python, pytest, Markdown docs, existing `build_external_tool_adapter_registry(...)`, `uv --no-config run --frozen`, local opencode review with `zhipuai-coding-plan/glm-5.2 --variant max`.

---

## Files

- Modify: `tests/test_external_tool_contract_parity.py`
  - Add `ROOT` and `COMMUNITY_SIGNAL_EXTERNAL_TOOL_DOCS`.
  - Add `_adapter_catalog_doc_row(adapter)`.
  - Add `test_community_signal_docs_list_current_external_tool_adapter_catalog`.
- Modify: `docs/community-signal-import.md`
  - Add the `Known adapter ids` table under `## External Tool Adapter Registry`.
- Modify: `docs/community-signal-quality.md`
  - Add the `Known adapter ids` table near the existing `external-tool-adapters` guidance.
- Add: `docs/superpowers/specs/2026-06-24-stage-181-community-docs-adapter-catalog-parity-design.md`
- Add: `docs/superpowers/plans/2026-06-24-stage-181-community-docs-adapter-catalog-parity-plan.md`
- Add: `docs/reviews/opencode-stage-181-plan-review-prompt.md`
- Add after plan review: `docs/reviews/opencode-stage-181-plan-review.md`
- Add after implementation: `docs/reviews/opencode-stage-181-code-review-prompt.md`
- Add after implementation: `docs/reviews/opencode-stage-181-code-review.md`
- Add after code-review minor fix: `docs/reviews/opencode-stage-181-code-rereview-prompt.md`
- Add after code-review minor fix: `docs/reviews/opencode-stage-181-code-rereview.md`
- Add before commit: `docs/reviews/opencode-stage-181-release-review-prompt.md`
- Add before commit: `docs/reviews/opencode-stage-181-release-review.md`

## Task 1: Add Failing Adapter Catalog Docs Parity Test

**Files:**

- Modify: `tests/test_external_tool_contract_parity.py`

- [ ] **Step 1: Confirm the new guard does not already exist**

Run:

```bash
uv --no-config run --frozen pytest \
  tests/test_external_tool_contract_parity.py::test_community_signal_docs_list_current_external_tool_adapter_catalog -q
```

Expected before adding the test: pytest reports the test name is not found or no
matching test is collected.

- [ ] **Step 2: Add docs constants after existing date/path constants**

Add this block after `AS_OF = "2026-06-13T12:00:00Z"`:

```python
ROOT = Path(__file__).resolve().parents[1]
COMMUNITY_SIGNAL_EXTERNAL_TOOL_DOCS = (
    ROOT / "docs" / "community-signal-import.md",
    ROOT / "docs" / "community-signal-quality.md",
)
```

- [ ] **Step 3: Add adapter-row helper**

Add this helper after the `registry` fixture:

```python
def _adapter_catalog_doc_row(adapter) -> str:
    return (
        f"| `{adapter.id}` | {adapter.display_name} | "
        f"`{adapter.platform_label}` | `{adapter.recommended_input_format}` | "
        f"`{adapter.recommended_pattern}` |"
    )
```

- [ ] **Step 4: Add the failing parity test**

Add this test after `test_every_adapter_field_mapping_matches_community_signal_profile`:

```python
def test_community_signal_docs_list_current_external_tool_adapter_catalog(registry) -> None:
    expected_rows = [_adapter_catalog_doc_row(adapter) for adapter in registry.adapters]

    for doc_path in COMMUNITY_SIGNAL_EXTERNAL_TOOL_DOCS:
        normalized = " ".join(doc_path.read_text(encoding="utf-8").split())

        assert "Known adapter ids:" in normalized
        for row in expected_rows:
            assert row in normalized, f"{doc_path.relative_to(ROOT)} missing {row!r}"

        for phrase in (
            "Display/source name column",
            "suggested_platform_labels",
            "advisory local provenance",
            "not a schema enum",
            "not a linter restriction",
            "not platform coverage",
            "not demand proof",
        ):
            assert phrase in normalized, f"{doc_path.relative_to(ROOT)} missing {phrase!r}"
```

- [ ] **Step 5: Run the test and verify RED**

Run:

```bash
uv --no-config run --frozen pytest \
  tests/test_external_tool_contract_parity.py::test_community_signal_docs_list_current_external_tool_adapter_catalog -q
```

Expected: the test fails because `docs/community-signal-import.md` and
`docs/community-signal-quality.md` do not yet contain `Known adapter ids:` and
the exact registry-derived rows.

## Task 2: Add Adapter Catalog Tables To Community Docs

**Files:**

- Modify: `docs/community-signal-import.md`
- Modify: `docs/community-signal-quality.md`

- [ ] **Step 1: Add table to `docs/community-signal-import.md`**

Under `## External Tool Adapter Registry`, after the paragraph ending with
`used elsewhere in this guide.`, add:

```markdown
Known adapter ids:

| Adapter id | Display/source name | Platform label | Format | Pattern |
| --- | --- | --- | --- | --- |
| `rednote_mcp` | Rednote MCP Export | `rednote` | `json` | `*.json` |
| `xiaohongshu_crawler` | Xiaohongshu Crawler Export | `xiaohongshu` | `csv` | `*.csv` |
| `instaloader` | Instaloader Export | `instagram` | `json` | `*.json` |
| `tiktok_api` | TikTok-Api Export | `tiktok` | `json` | `*.json` |
| `yt_dlp` | yt-dlp Metadata Export | `media` | `json` | `*.json` |
| `x_search_export` | X Search Export | `x` | `csv` | `*.csv` |
| `xpoz_mcp` | XPOZ MCP Export | `community` | `json` | `*.json` |
| `generic_community_export` | Generic Community Export | `community` | `csv` | `*.csv` |

The Display/source name column reflects the current registry `display_name` and
`suggested_source_name` values, which are identical for these adapters.

The Platform label column reflects `suggested_platform_labels` as advisory local
provenance label guidance for the optional handoff `platform` field. These
labels are local provenance suggestions only: they are not a schema enum, not a
linter restriction, not platform coverage, and not demand proof.
```

- [ ] **Step 2: Add table to `docs/community-signal-quality.md`**

After the paragraph ending with `does not run readiness or perform PATH lookup.`
and before the `external-tool-template` paragraph, add the same Markdown block
from Task 2 Step 1.

- [ ] **Step 3: Run the new test and verify GREEN**

Run:

```bash
uv --no-config run --frozen pytest \
  tests/test_external_tool_contract_parity.py::test_community_signal_docs_list_current_external_tool_adapter_catalog -q
```

Expected: the new test passes.

## Task 3: Focused Verification And Code Review

**Files:**

- Modify: `tests/test_external_tool_contract_parity.py`
- Modify: `docs/community-signal-import.md`
- Modify: `docs/community-signal-quality.md`
- Add: `docs/reviews/opencode-stage-181-code-review-prompt.md`
- Add: `docs/reviews/opencode-stage-181-code-review.md`

- [ ] **Step 1: Run focused verification**

Run:

```bash
uv --no-config run --frozen pytest tests/test_external_tool_contract_parity.py -q
uv --no-config run --frozen pytest tests/test_cli_docs.py -q
uv --no-config run --frozen ruff check tests/test_external_tool_contract_parity.py
uv --no-config run --frozen ruff format --check tests/test_external_tool_contract_parity.py
```

Expected: all focused tests and checks pass.

- [ ] **Step 2: Create code review prompt**

Create `docs/reviews/opencode-stage-181-code-review-prompt.md` with a prompt
that asks local opencode to review the Stage 181 implementation. The prompt
must require the response to start with:

```text
# Stage 181 Code Review
```

- [ ] **Step 3: Run code review**

Run:

```bash
tmp_review="$(mktemp)"
opencode run --model zhipuai-coding-plan/glm-5.2 --variant max \
  --dir /home/ubuntu/fashion-radar \
  "$(cat docs/reviews/opencode-stage-181-code-review-prompt.md)" > "$tmp_review" 2>&1
sed -n '1,320p' "$tmp_review"
cp "$tmp_review" docs/reviews/opencode-stage-181-code-review.md
rm -f "$tmp_review"
```

Expected: completed review output with no critical or important findings. Clean
the artifact so it contains only one final review body if opencode includes
process chatter, ANSI output, command logs, or multiple drafts.

## Task 4: Release Gate, Release Review, Commit, And Push

**Files:**

- Add: `docs/reviews/opencode-stage-181-release-review-prompt.md`
- Add: `docs/reviews/opencode-stage-181-release-review.md`

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

Create `docs/reviews/opencode-stage-181-release-review-prompt.md` requiring the
review body to start with:

```text
# Stage 181 Release Review
```

Then run the same temp-file `opencode run --model zhipuai-coding-plan/glm-5.2
--variant max` capture flow used for code review, copying the completed review
to `docs/reviews/opencode-stage-181-release-review.md`.

Expected: completed review output with no critical or important findings. Clean
the artifact if needed.

- [ ] **Step 3: Commit and push**

Run:

```bash
git status --short
git add \
  tests/test_external_tool_contract_parity.py \
  docs/community-signal-import.md \
  docs/community-signal-quality.md \
  docs/superpowers/specs/2026-06-24-stage-181-community-docs-adapter-catalog-parity-design.md \
  docs/superpowers/plans/2026-06-24-stage-181-community-docs-adapter-catalog-parity-plan.md \
  docs/reviews/opencode-stage-181-plan-review-prompt.md \
  docs/reviews/opencode-stage-181-plan-review.md \
  docs/reviews/opencode-stage-181-code-review-prompt.md \
  docs/reviews/opencode-stage-181-code-review.md \
  docs/reviews/opencode-stage-181-code-rereview-prompt.md \
  docs/reviews/opencode-stage-181-code-rereview.md \
  docs/reviews/opencode-stage-181-release-review-prompt.md \
  docs/reviews/opencode-stage-181-release-review.md
git commit -m "docs: list adapter catalog in community docs"
git push origin main
```

Expected: commit succeeds and `main` pushes to GitHub.

## Self-Review Notes

- Spec coverage: Task 1 adds the failing docs parity guard, Task 2 adds both
  community-doc catalog tables, Task 3 covers focused verification and code
  review, and Task 4 covers release gate, release review, commit, and push.
- Placeholder scan: no placeholders or deferred implementation notes.
- Boundary check: no runtime adapter behavior, CLI behavior, connector, source
  acquisition, scraping, browser automation, platform API, login/cookie/token,
  monitoring, scheduling, demand proof, ranking, platform coverage verification,
  compliance-review product feature, dependency, or lockfile behavior is in
  scope.
