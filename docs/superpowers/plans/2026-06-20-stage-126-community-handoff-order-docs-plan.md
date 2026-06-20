# Stage 126 Community Handoff Order Docs Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Align user-facing community handoff command sequences with the canonical local handoff order.

**Architecture:** Add one targeted docs-order regression test that extracts command names from named markdown sections, then update only affected user-facing command blocks. Runtime workflow code is already correct and stays unchanged.

**Tech Stack:** Python 3.11, pytest docs tests, Markdown documentation.

---

## Files

- Modify `tests/test_cli_docs.py`
  - Add `COMMUNITY_SIGNAL_QUALITY_DOC`.
  - Add a helper that extracts relevant `fashion-radar` command names from a
    markdown section.
  - Add a docs-order regression test for the affected README, quality,
    import, and architecture sections.
- Modify `README.md`
  - Reorder the external community tool sample's local directory sequence.
  - Add `community-candidates-dir` to the configuration directory handoff
    sample and place readiness after candidate preview.
- Modify `docs/community-signal-quality.md`
  - Add `community-handoff-check-dir` to the recommended order between
    candidate preview and dry-run import.
  - Adjust prose to describe readiness after preview and before dry-run import.
- Modify `docs/architecture.md`
  - Move `community-handoff-check-dir` after `community-signal-lint-dir` and
    `community-candidates-dir` in the command flow.
- Create `docs/reviews/opencode-stage-126-plan-review-prompt.md`.
- Create `docs/reviews/opencode-stage-126-plan-review.md`.
- Create `docs/reviews/opencode-stage-126-code-review-prompt.md`.
- Create `docs/reviews/opencode-stage-126-code-review.md`.

No runtime product code, CLI behavior, dependencies, lockfile, connectors,
scraping, platform APIs, browser automation, scheduling, source acquisition,
demand proof, ranking, coverage verification, or compliance/audit product
behavior is part of this stage.

## Task 1: Add RED docs-order regression test

**Files:**

- Modify: `tests/test_cli_docs.py`

- [ ] **Step 1: Add the quality doc path constant**

After the existing `COMMUNITY_SIGNAL_IMPORT_DOC` constant, add:

```python
COMMUNITY_SIGNAL_QUALITY_DOC = ROOT / "docs" / "community-signal-quality.md"
```

- [ ] **Step 2: Add a section command-name helper**

After `_fashion_radar_commands`, add:

```python
def _fashion_radar_command_names_from_text(
    text: str,
    *,
    allowed_names: set[str],
) -> list[str]:
    names: list[str] = []
    for block in _bash_blocks(text):
        for command in _shell_commands(block):
            match = FASHION_RADAR_COMMAND_RE.search(command)
            if match is not None and match.group("name") in allowed_names:
                names.append(match.group("name"))
    return names
```

- [ ] **Step 3: Add the targeted order test**

Near `test_community_signal_import_doc_keeps_profile_recommended_command_order`,
add:

```python
def test_user_docs_keep_community_handoff_readiness_after_preview_before_import() -> None:
    relevant = {
        "community-signal-lint-dir",
        "community-candidates-dir",
        "community-handoff-check-dir",
        "import-signals-dir",
        "imported-review-workflow",
    }

    def assert_subsequence(
        label: str,
        section: str,
        expected: tuple[str, ...],
    ) -> None:
        actual = _fashion_radar_command_names_from_text(section, allowed_names=relevant)
        position = 0
        for name in expected:
            while position < len(actual) and actual[position] != name:
                position += 1
            assert position < len(actual), (
                f"{label}: {name!r} missing or out of order in {actual!r}"
            )
            position += 1

    readme = _read(README)
    quality_doc = _read(COMMUNITY_SIGNAL_QUALITY_DOC)
    import_doc = _read(COMMUNITY_SIGNAL_IMPORT_DOC)
    architecture_doc = _read(ARCHITECTURE_DOC)

    cases = (
        (
            "README external community tools sample",
            readme.split("External community tools can target", 1)[1].split(
                "Inspect retained imported rows",
                1,
            )[0],
            (
                "community-signal-lint-dir",
                "community-candidates-dir",
                "community-handoff-check-dir",
                "import-signals-dir",
                "import-signals-dir",
            ),
        ),
        (
            "README configuration directory handoff sample",
            readme.split("Check a directory of community signal handoff files", 1)[
                1
            ].split(
                "The linters are local",
                1,
            )[0],
            (
                "community-signal-lint-dir",
                "community-candidates-dir",
                "community-handoff-check-dir",
                "import-signals-dir",
                "import-signals-dir",
            ),
        ),
        (
            "community-signal-quality recommended order",
            quality_doc.split("Recommended order:", 1)[1].split(
                "Use `community-signal-lint-dir` first",
                1,
            )[0],
            (
                "community-signal-lint-dir",
                "community-candidates-dir",
                "community-handoff-check-dir",
                "import-signals-dir",
                "import-signals-dir",
                "imported-review-workflow",
            ),
        ),
        (
            "community-signal-import canonical flow",
            import_doc.split("## Preflight Lint", 1)[1].split("## Boundary", 1)[0],
            (
                "community-signal-lint-dir",
                "community-candidates-dir",
                "community-handoff-check-dir",
                "import-signals-dir",
                "import-signals-dir",
                "imported-review-workflow",
            ),
        ),
        (
            "architecture command flow",
            architecture_doc.split("## Command Flow", 1)[1].split(
                "## Source-Pack Quality Boundary",
                1,
            )[0],
            (
                "community-signal-lint-dir",
                "community-candidates-dir",
                "community-handoff-check-dir",
                "import-signals-dir",
                "import-signals-dir",
                "imported-review-workflow",
            ),
        ),
    )

    for label, section, expected in cases:
        assert_subsequence(label, section, expected)
```

- [ ] **Step 4: Run the RED test**

Run:

```bash
uv --no-config run --frozen pytest tests/test_cli_docs.py::test_user_docs_keep_community_handoff_readiness_after_preview_before_import -q
```

Expected result: fail because the current README, quality doc, and
architecture command blocks do not keep readiness after candidate preview and
before import.

## Task 2: Align user-facing command blocks

**Files:**

- Modify: `README.md`
- Modify: `docs/community-signal-quality.md`
- Modify: `docs/architecture.md`

- [ ] **Step 1: Reorder the README external community tool sample**

In the bash block under "External community tools can target the local
community signal contract", keep `community-handoff-workflow` where it is and
move the existing local directory commands so `community-signal-lint-dir`,
both `community-candidates-dir` variants, and `community-handoff-check-dir`
appear after the external-tool readiness commands and immediately before
`import-signals-dir --dry-run`:

```bash
uv run fashion-radar community-signal-lint-dir "$tmp_run/exports" --input-format csv --pattern "*.csv" --source-name "Community Tool Export"
uv run fashion-radar community-candidates-dir "$tmp_run/exports" --input-format csv --pattern "*.csv" --config-dir "$PWD/configs" --as-of "$AS_OF" --source-name "Community Tool Export"
uv run fashion-radar community-candidates-dir "$tmp_run/exports" --input-format csv --pattern "*.csv" --config-dir "$PWD/configs" --as-of "$AS_OF" --format json
uv run fashion-radar community-handoff-check-dir "$tmp_run/exports" --input-format csv --pattern "*.csv" --config-dir "$PWD/configs" --as-of "$AS_OF" --source-name "Community Tool Export" --format json
uv run fashion-radar import-signals-dir "$tmp_run/exports" --format csv --pattern "*.csv" --source-name "Community Tool Export" --data-dir "$PWD/data" --dry-run
uv run fashion-radar import-signals-dir "$tmp_run/exports" --format csv --pattern "*.csv" --source-name "Community Tool Export" --imported-at "$AS_OF" --data-dir "$PWD/data"
```

Leave the single-file import example after that directory sequence.

- [ ] **Step 2: Reorder the README configuration directory handoff sample**

In the bash block under "Check a directory of community signal handoff files",
keep manifest and workflow first, then use:

```bash
uv run fashion-radar community-signal-lint-dir ./exports --input-format csv --pattern "*.csv" --source-name "Community Tool Export"
uv run fashion-radar community-candidates-dir ./exports --input-format csv --pattern "*.csv" --config-dir "$PWD/configs" --as-of "$AS_OF" --source-name "Community Tool Export"
uv run fashion-radar community-handoff-check-dir ./exports --input-format csv --pattern "*.csv" --config-dir "$PWD/configs" --as-of "$AS_OF" --source-name "Community Tool Export" --format json
uv run fashion-radar import-signals-dir ./exports --format csv --pattern "*.csv" --source-name "Community Tool Export" --data-dir "$PWD/data" --dry-run
uv run fashion-radar import-signals-dir ./exports --format csv --pattern "*.csv" --source-name "Community Tool Export" --imported-at "$AS_OF" --data-dir "$PWD/data"
```

- [ ] **Step 3: Add readiness to the quality recommended order**

In `docs/community-signal-quality.md`, insert this line after
`community-candidates-dir` and before `import-signals-dir --dry-run`:

```bash
uv run fashion-radar community-handoff-check-dir ./exports --input-format csv --pattern "*.csv" --config-dir "$PWD/configs" --as-of "$(date -u +%Y-%m-%dT%H:%M:%SZ)" --source-name "Community Tool Export" --format json
```

- [ ] **Step 4: Adjust the quality prose**

Replace the prose after the recommended-order block so it says:

```markdown
Use `community-signal-lint-dir` first for strict community handoff quality.
Use `community-candidates-dir` next to preview aggregate candidate phrases.
Use `community-handoff-check-dir` after preview and before importer dry-run
when you want the local readiness summary across lint, candidate preview, and
import dry-run checks. Use `community-handoff-workflow` when you want that
directory sequence printed as copyable local commands without executing
anything.
Use `import-signals-dir --dry-run` next when you want the broader manual
importer model to validate matched local files without writing rows. Then use
`import-signals-dir` without `--dry-run` to import the same local files only
after the full matched set validates.
```

Keep the following `imported-review-workflow` prose unchanged.

- [ ] **Step 5: Reorder the architecture command flow**

In `docs/architecture.md`, move `community-handoff-check-dir` so the directory
handoff lines appear as:

```bash
fashion-radar community-handoff-workflow ./exports --input-format csv --pattern "*.csv" --config-dir ./configs --data-dir ./data --as-of 2026-06-11T12:00:00Z --source-name "Manual Export"
fashion-radar community-signal-lint ./signals.csv --input-format csv --source-name "Manual Export"
fashion-radar community-signal-lint-dir ./exports --input-format csv --pattern "*.csv" --source-name "Manual Export"
fashion-radar community-candidates-dir ./exports --input-format csv --pattern "*.csv" --config-dir ./configs --as-of 2026-06-11T12:00:00Z --source-name "Manual Export"
fashion-radar community-handoff-check-dir ./exports --input-format csv --pattern "*.csv" --config-dir ./configs --as-of 2026-06-11T12:00:00Z --source-name "Manual Export"
fashion-radar import-signals-dir ./exports --format csv --pattern "*.csv" --source-name "Manual Export" --data-dir ./data --dry-run
fashion-radar import-signals-dir ./exports --format csv --pattern "*.csv" --source-name "Manual Export" --imported-at 2026-06-11T12:00:00Z --data-dir ./data
```

- [ ] **Step 6: Run the GREEN test**

Run:

```bash
uv --no-config run --frozen pytest tests/test_cli_docs.py::test_user_docs_keep_community_handoff_readiness_after_preview_before_import -q
```

Expected result: pass.

## Task 3: Focused verification and local code review

**Files:**

- Create: `docs/reviews/opencode-stage-126-code-review-prompt.md`
- Create: `docs/reviews/opencode-stage-126-code-review.md`

- [ ] **Step 1: Run focused docs and workflow tests**

Run:

```bash
uv --no-config run --frozen pytest tests/test_cli_docs.py::test_user_docs_keep_community_handoff_readiness_after_preview_before_import tests/test_cli_docs.py::test_community_handoff_check_dir_docs_are_linked_and_bounded tests/test_cli_docs.py::test_community_signal_import_doc_keeps_profile_recommended_command_order tests/test_community_handoff_workflow.py::test_build_community_handoff_workflow_returns_deterministic_steps tests/test_community_signal_profile.py::test_profile_recommended_commands_keep_directory_handoff_sequence tests/test_external_tool_adapters.py tests/test_external_tool_contract_parity.py -q
uv --no-config run --frozen ruff check tests/test_cli_docs.py
uv --no-config run --frozen ruff format --check tests/test_cli_docs.py
git diff --check
```

Expected result: selected tests, lint, format, and whitespace checks pass.

- [ ] **Step 2: Write Stage 126 code review prompt**

Create `docs/reviews/opencode-stage-126-code-review-prompt.md` with:

```markdown
Review the Stage 126 implementation before release.

Repository: `/home/ubuntu/fashion-radar`

Stage goal:
- Align user-facing community handoff command sequences with the canonical
  local order: lint directory, preview candidates, readiness check, dry-run
  import, import, and imported review.
- Keep the change docs/test-only.

Files changed:
- `README.md`
- `docs/community-signal-quality.md`
- `docs/architecture.md`
- `tests/test_cli_docs.py`
- Stage 126 design/plan/review artifacts

Review focus:
1. Does the implementation match the Stage 126 design and plan?
2. Do the named user docs show `community-handoff-check-dir` after
   `community-candidates-dir` and before `import-signals-dir`?
3. Is the regression test targeted to named sections instead of a brittle
   global command order?
4. Does the stage avoid runtime, CLI, dependency, connector, scraping, browser
   automation, platform API, monitoring, scheduling, source acquisition, demand
   proof, ranking, coverage verification, and compliance/audit product
   behavior?

Return:
- Critical findings, if any.
- Important findings, if any.
- Minor findings, if any.
- A final explicit statement whether there are any Critical or Important
  blockers before release.
```

- [ ] **Step 3: Run local opencode code review**

Run:

```bash
tmp_review="$(mktemp)"
opencode run --model zhipuai-coding-plan/glm-5.2 --variant max --dir /home/ubuntu/fashion-radar "$(cat docs/reviews/opencode-stage-126-code-review-prompt.md)" > "$tmp_review"
sed -n '1,240p' "$tmp_review"
python3 - "$tmp_review" docs/reviews/opencode-stage-126-code-review.md <<'PY'
from pathlib import Path
import re
import sys

raw = Path(sys.argv[1]).read_text(encoding="utf-8")
text = re.sub(r"\x1b\[[0-9;?]*[ -/]*[@-~]", "", raw)
start = text.find("# Stage 126 Code Review")
if start != -1:
    text = text[start:]
cut_markers = ("\n> build ", "\n$ ", "\n-> ", "\n<- ")
cut_positions = [text.find(marker) for marker in cut_markers if text.find(marker) != -1]
if cut_positions:
    text = text[: min(cut_positions)]
lines = [line.rstrip() for line in text.splitlines()]
Path(sys.argv[2]).write_text("\n".join(lines).strip() + "\n", encoding="utf-8")
PY
test -s docs/reviews/opencode-stage-126-code-review.md
rm -f "$tmp_review"
```

Expected result: review artifact is non-empty and contains no Critical or
Important blockers.

## Task 4: Full release gate, commit, push, and CI

**Files:**

- No new implementation files beyond Task 3.

- [ ] **Step 1: Run the full release gate**

Run:

```bash
uv --no-config run --frozen python scripts/check_release_hygiene.py
env -u ALL_PROXY -u all_proxy uv --no-config run --frozen pytest
uv --no-config run --frozen ruff check .
uv --no-config run --frozen ruff format --check .
env -u UV_DEFAULT_INDEX -u UV_INDEX_URL -u UV_EXTRA_INDEX_URL UV_NO_CONFIG=1 uv lock --check
git diff --exit-code -- uv.lock
git diff --check
rg -n 'ghp_[A-Za-z0-9]+' .
git config --get-all http.https://github.com/.extraheader || true
```

Expected result: release hygiene, full pytest, ruff, format, lock check,
lockfile diff, whitespace check, token scan, and git auth-header scan all pass.

- [ ] **Step 2: Commit Stage 126**

Run:

```bash
git status --short --untracked-files=all
git add README.md docs/community-signal-quality.md docs/architecture.md tests/test_cli_docs.py docs/superpowers/specs/2026-06-20-stage-126-community-handoff-order-docs-design.md docs/superpowers/plans/2026-06-20-stage-126-community-handoff-order-docs-plan.md docs/reviews/opencode-stage-126-plan-review-prompt.md docs/reviews/opencode-stage-126-plan-review.md docs/reviews/opencode-stage-126-code-review-prompt.md docs/reviews/opencode-stage-126-code-review.md
git commit -m "Align community handoff documentation order"
```

Expected result: one commit containing only Stage 126 docs/test/review
artifacts.

- [ ] **Step 3: Push with temporary auth header**

Run the established temporary-header push pattern without storing credentials in
git config or files:

```bash
AUTH_HEADER="$(printf 'x-access-token:%s' "$GITHUB_TOKEN_FOR_PUSH" | base64 -w0)"
git -c http.https://github.com/.extraheader="AUTHORIZATION: basic ${AUTH_HEADER}" push origin main
unset AUTH_HEADER
git config --get-all http.https://github.com/.extraheader || true
```

Expected result: push succeeds and no persistent GitHub auth header remains.

- [ ] **Step 4: Verify remote and CI**

Run:

```bash
git ls-remote origin refs/heads/main
```

Then poll the latest GitHub Actions run for the pushed SHA until it reaches a
terminal state.

Expected result: remote `main` points at the Stage 126 commit and CI completes
successfully.
