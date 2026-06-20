# Stage 128 External Tool CLI Reference Option Parity Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Align the CLI reference option lists for `external-tool-workflow` and `external-tool-readiness` with actual command help.

**Architecture:** Add a targeted docs parity test that extracts each command bullet from `docs/cli-reference.md`, verifies the expected option text in that bullet, and cross-checks option names against Typer help. Then update only the stale support sentences.

**Tech Stack:** Python 3.11, pytest docs tests, Typer `CliRunner`, Markdown documentation.

---

## Files

- Modify `tests/test_cli_docs.py`
  - Add `_cli_reference_command_entry(command)`.
  - Add `test_cli_reference_external_tool_option_parity`.
- Modify `docs/cli-reference.md`
  - Update the `external-tool-workflow` support sentence.
  - Update the `external-tool-readiness` support sentence.
- Create `docs/reviews/opencode-stage-128-plan-review-prompt.md`.
- Create `docs/reviews/opencode-stage-128-plan-review.md`.
- Create `docs/reviews/opencode-stage-128-code-review-prompt.md`.
- Create `docs/reviews/opencode-stage-128-code-review.md`.

No runtime CLI behavior, dependencies, lockfile, connectors, scraping, platform
APIs, browser automation, scheduling, source acquisition, demand proof, ranking,
coverage verification, or compliance/audit product behavior is part of this
stage.

## Task 1: Add RED CLI reference option parity test

**Files:**

- Modify: `tests/test_cli_docs.py`

- [ ] **Step 1: Add command-entry extraction helper**

After `_normalized_text`, add:

```python
def _cli_reference_command_entry(command: str) -> str:
    text = _read(CLI_REFERENCE)
    match = re.search(
        rf"^- `{re.escape(command)}`:.*?(?=^- `|\n## |\Z)",
        text,
        flags=re.MULTILINE | re.DOTALL,
    )
    assert match is not None, command
    return match.group(0)
```

- [ ] **Step 2: Add the parity test**

Near the existing external tool docs tests, add:

```python
def test_cli_reference_external_tool_option_parity() -> None:
    expected_options = {
        "external-tool-workflow": (
            "--adapter",
            "--directory",
            "--config-dir",
            "--data-dir",
            "--as-of",
            "--input-format csv|json",
            "--pattern",
            "--source-name",
            "--format table|json",
        ),
        "external-tool-readiness": (
            "--adapter",
            "--directory",
            "--config-dir",
            "--data-dir",
            "--as-of",
            "--input-format csv|json",
            "--pattern",
            "--source-name",
            "--format table|json",
        ),
    }

    for command, options in expected_options.items():
        entry = _cli_reference_command_entry(command)
        help_result = CliRunner().invoke(
            app,
            [command, "--help"],
            env={"COLUMNS": "120"},
        )
        assert help_result.exit_code == 0

        for option in options:
            option_name = option.split()[0]
            assert option_name in help_result.output
            assert option in entry
```

- [ ] **Step 3: Run the RED test**

Run:

```bash
uv --no-config run --frozen pytest tests/test_cli_docs.py::test_cli_reference_external_tool_option_parity -q
```

Expected result: fail because `docs/cli-reference.md` omits the expected
workflow/readiness options.

## Task 2: Update CLI reference support sentences

**Files:**

- Modify: `docs/cli-reference.md`

- [ ] **Step 1: Update the workflow support sentence**

Replace:

```markdown
Supports `--adapter`, `--directory`, `--config-dir`, `--data-dir`, `--as-of`,
and `--format table|json`.
```

with:

```markdown
Supports `--adapter`, `--directory`, `--config-dir`, `--data-dir`, `--as-of`,
`--input-format csv|json`, `--pattern`, `--source-name`, and
`--format table|json`.
```

- [ ] **Step 2: Update the readiness support sentence**

Replace:

```markdown
Supports `--adapter` and `--format table|json`.
```

with:

```markdown
Supports `--adapter`, `--directory`, `--config-dir`, `--data-dir`, `--as-of`,
`--input-format csv|json`, `--pattern`, `--source-name`, and
`--format table|json`.
```

Keep the following local read-only wording unchanged:

```markdown
It is local read-only, not print-only, because it performs command availability
only with local PATH lookup (`shutil.which`).
```

- [ ] **Step 3: Run the GREEN test**

Run:

```bash
uv --no-config run --frozen pytest tests/test_cli_docs.py::test_cli_reference_external_tool_option_parity -q
```

Expected result: pass.

## Task 3: Focused verification and local code review

**Files:**

- Create: `docs/reviews/opencode-stage-128-code-review-prompt.md`
- Create: `docs/reviews/opencode-stage-128-code-review.md`

- [ ] **Step 1: Run focused docs/CLI tests and lint**

Run:

```bash
uv --no-config run --frozen pytest tests/test_cli_docs.py -k "external_tool_option_parity or external_tool_workflow_docs_include_examples_and_steps or external_tool_readiness_upload_checklist_help_loop_and_smoke" -q
uv --no-config run --frozen pytest tests/test_cli.py -k "external_tool_workflow_help_lists_options or external_tool_readiness_help_lists_options or external_tool_workflow_command_applies_overrides or external_tool_readiness_command_applies_overrides" -q
uv --no-config run --frozen ruff check tests/test_cli_docs.py
uv --no-config run --frozen ruff format --check tests/test_cli_docs.py
git diff --check
```

Expected result: selected docs tests, CLI tests, lint, format, and whitespace
checks pass.

- [ ] **Step 2: Write Stage 128 code review prompt**

Create `docs/reviews/opencode-stage-128-code-review-prompt.md` with:

```markdown
Review the Stage 128 implementation before release.

Repository: `/home/ubuntu/fashion-radar`

Stage goal:
- Align `docs/cli-reference.md` support sentences for
  `external-tool-workflow` and `external-tool-readiness` with actual command
  help.
- Keep the change docs/test-only.

Files changed:
- `docs/cli-reference.md`
- `tests/test_cli_docs.py`
- Stage 128 design/plan/review artifacts

Review focus:
1. Does the implementation match the Stage 128 design and plan?
2. Does the docs test parse only the relevant CLI reference bullets and
   cross-check option names against Typer help?
3. Does readiness wording remain local read-only and avoid implying directory
   inspection or file validation?
4. Does the stage avoid runtime CLI behavior, dependencies, lockfile,
   connectors, scraping, browser automation, platform API, monitoring,
   scheduling, source acquisition, demand proof, ranking, coverage
   verification, and compliance/audit product behavior?

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
opencode run --model zhipuai-coding-plan/glm-5.2 --variant max --dir /home/ubuntu/fashion-radar "$(cat docs/reviews/opencode-stage-128-code-review-prompt.md)" > "$tmp_review"
sed -n '1,240p' "$tmp_review"
python3 - "$tmp_review" docs/reviews/opencode-stage-128-code-review.md <<'PY'
from pathlib import Path
import re
import sys

raw = Path(sys.argv[1]).read_text(encoding="utf-8")
text = re.sub(r"\x1b\[[0-9;?]*[ -/]*[@-~]", "", raw)
start = text.find("# Stage 128 Code Review")
if start != -1:
    text = text[start:]
cut_markers = ("\n> build ", "\n$ ", "\n-> ", "\n<- ")
cut_positions = [text.find(marker) for marker in cut_markers if text.find(marker) != -1]
if cut_positions:
    text = text[: min(cut_positions)]
lines = [line.rstrip() for line in text.splitlines()]
Path(sys.argv[2]).write_text("\n".join(lines).strip() + "\n", encoding="utf-8")
PY
test -s docs/reviews/opencode-stage-128-code-review.md
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

- [ ] **Step 2: Commit Stage 128**

Run:

```bash
git status --short --untracked-files=all
git add docs/cli-reference.md tests/test_cli_docs.py docs/superpowers/specs/2026-06-20-stage-128-external-tool-cli-reference-option-parity-design.md docs/superpowers/plans/2026-06-20-stage-128-external-tool-cli-reference-option-parity-plan.md docs/reviews/opencode-stage-128-plan-review-prompt.md docs/reviews/opencode-stage-128-plan-review.md docs/reviews/opencode-stage-128-code-review-prompt.md docs/reviews/opencode-stage-128-code-review.md
git commit -m "Align external tool CLI reference options"
```

Expected result: one commit containing only Stage 128 docs/test/review
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

Expected result: remote `main` points at the Stage 128 commit and CI completes
successfully.
