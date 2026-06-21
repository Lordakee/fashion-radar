# Stage 132 Untracked Secret Hygiene Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Extend release hygiene so unignored untracked files are scanned for
secret content, not only forbidden paths.

**Architecture:** Reuse `find_secret_findings()` for `untracked_paths` in
`collect_findings()`, and add a focused regression test for an untracked file
with a valid GitHub token. Preserve existing symlink-skip behavior by keeping
the original path symlink check ahead of resolved-path containment for
untracked paths.

**Tech Stack:** Python stdlib, pytest, existing release hygiene script.

---

## Files

- Modify `scripts/check_release_hygiene.py`
  - Add untracked secret scanning in `collect_findings()`.
  - Skip original repo-relative symlink paths before resolving safe repo paths
    for untracked paths.
- Modify `tests/test_release_hygiene.py`
  - Add a regression test for an untracked file containing a valid GitHub token.
  - Add a regression test proving an untracked symlink to an ignored secret file
    is skipped rather than followed.
- Create `docs/reviews/opencode-stage-132-plan-review-prompt.md`.
- Create `docs/reviews/opencode-stage-132-plan-review.md`.
- Create `docs/reviews/opencode-stage-132-code-review-prompt.md`.
- Create `docs/reviews/opencode-stage-132-code-review.md`.

The plan-review prompt and plan-review artifact are produced before
implementation begins; the implementation tasks create only the code-review
prompt and code-review artifact.

No secret pattern changes, forbidden path policy changes, docs verification
surface changes, dependency/lockfile changes, package archive checker changes,
runtime product behavior changes, connectors, scraping, browser automation,
platform APIs, monitoring, scheduling, source acquisition, demand proof,
ranking, coverage verification, or compliance/audit product behavior is part of
this stage.

## Task 1: Add RED untracked secret test

**Files:**

- Modify: `tests/test_release_hygiene.py`

- [ ] **Step 1: Add regression test**

Add near `test_tracked_file_with_valid_github_token_is_redacted_and_reports_line`:

```python
def test_untracked_file_with_valid_github_token_is_redacted_and_reports_line(
    tmp_path: Path,
) -> None:
    repo_root = init_repo(tmp_path)
    write_file(repo_root, "notes.md", f"# Scratch\nleaked = {GITHUB_TOKEN}\n")

    result = run_checker(repo_root)

    assert result.returncode == 1
    assert "forbidden secret in untracked file: notes.md:2: GitHub token" in result.stderr
    assert GITHUB_TOKEN not in result.stderr
    assert "<redacted>" in result.stderr
```

- [ ] **Step 2: Add symlink regression test**

Add a regression test proving an untracked symlink is not followed to an ignored
target that contains a token-shaped fixture:

```python
def test_untracked_symlink_target_is_not_scanned_for_secret(tmp_path: Path) -> None:
    repo_root = init_repo(tmp_path)
    write_tracked(repo_root, ".gitignore", "ignored-secret.txt\n")
    git(repo_root, "commit", "-m", "ignore secret fixture")
    write_file(repo_root, "ignored-secret.txt", f"leaked = {GITHUB_TOKEN}\n")
    symlink = repo_root / "notes.md"
    try:
        symlink.symlink_to("ignored-secret.txt")
    except (OSError, NotImplementedError) as exc:
        pytest.skip(f"symlink unavailable: {exc}")

    result = run_checker(repo_root)

    assert result.returncode == 0
    assert result.stdout == "Release hygiene checks passed.\n"
    assert result.stderr == ""
```

- [ ] **Step 3: Run RED tests**

Run:

```bash
uv --no-config run --frozen pytest tests/test_release_hygiene.py::test_untracked_file_with_valid_github_token_is_redacted_and_reports_line -q
uv --no-config run --frozen pytest tests/test_release_hygiene.py::test_untracked_symlink_target_is_not_scanned_for_secret -q
```

Expected result: fail because untracked `notes.md` is not path-forbidden and
secret content scanning currently only checks tracked paths; the symlink test
fails after the untracked scan is added unless symlink paths are skipped before
resolved-path containment follows their targets.

## Task 2: Scan untracked files for secrets

**Files:**

- Modify: `scripts/check_release_hygiene.py`

- [ ] **Step 1: Extend `collect_findings()`**

After the existing tracked secret scan:

```python
findings.extend(find_secret_findings(repo_root, tracked_paths, "tracked"))
```

add:

```python
findings.extend(find_secret_findings(repo_root, untracked_paths, "untracked"))
```

- [ ] **Step 2: Preserve untracked symlink skip before resolved-path containment**

Update `find_secret_findings()` so it skips `(repo_root / normalized)` when the
path status is `untracked` and that original path is a symlink before calling
`safe_repo_path()`. Keep
`safe_repo_path()` on the existing resolved-path containment behavior.

- [ ] **Step 3: Run GREEN tests**

Run:

```bash
uv --no-config run --frozen pytest tests/test_release_hygiene.py -k "untracked_file_with_valid_github_token or tracked_file_with_valid_github_token or untracked_symlink_target"
uv --no-config run --frozen pytest tests/test_release_hygiene.py
```

Expected result: pass.

## Task 3: Focused verification and local code review

**Files:**

- Create: `docs/reviews/opencode-stage-132-code-review-prompt.md`
- Create: `docs/reviews/opencode-stage-132-code-review.md`

- [ ] **Step 1: Run focused verification**

Run:

```bash
uv --no-config run --frozen pytest tests/test_release_hygiene.py -k "untracked_file_with_valid_github_token or tracked_file_with_valid_github_token or untracked_symlink_target"
uv --no-config run --frozen pytest tests/test_release_hygiene.py
uv --no-config run --frozen ruff check scripts/check_release_hygiene.py tests/test_release_hygiene.py
uv --no-config run --frozen ruff format --check scripts/check_release_hygiene.py tests/test_release_hygiene.py
uv --no-config run --frozen python scripts/check_release_hygiene.py --repo-root .
git diff --check
```

Expected result: focused release hygiene tests, lint, format, live hygiene
check, and whitespace check pass.

- [ ] **Step 2: Write Stage 132 code review prompt**

Create `docs/reviews/opencode-stage-132-code-review-prompt.md` with:

```markdown
Review the Stage 132 implementation before release.

Repository: `/home/ubuntu/fashion-radar`

Stage goal:
- Extend `scripts/check_release_hygiene.py` so unignored untracked files are
  scanned for secret content, not only forbidden paths.
- Keep existing secret patterns, redaction, path policy, and runtime/product
  behavior unchanged.

Files changed:
- `scripts/check_release_hygiene.py`
- `tests/test_release_hygiene.py`
- Stage 132 design/plan/review artifacts

Review focus:
1. Does the implementation match the Stage 132 design and plan?
2. Does `collect_findings()` now scan `untracked_paths` with
   `find_secret_findings(..., "untracked")`?
3. Does the regression test prove a publishable-looking untracked file with a
   valid GitHub token is rejected, redacted, and line-numbered?
4. Does `find_secret_findings()` skip original untracked symlink paths before
   `safe_repo_path()` can resolve their targets, including an untracked symlink
   to an ignored token-bearing target, while preserving tracked-path behavior?
5. Does the stage avoid secret pattern changes, forbidden path policy changes,
   docs verification-surface changes, dependency/lockfile changes, package
   archive checker changes, runtime product behavior changes, connectors,
   scraping, browser automation, platform APIs, monitoring, scheduling, source
   acquisition, demand proof, ranking, coverage verification, and
   compliance/audit product behavior?

Return:
Start with `# Stage 132 Code Review`, then include:
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
opencode run --model zhipuai-coding-plan/glm-5.2 --variant max --dir /home/ubuntu/fashion-radar "$(cat docs/reviews/opencode-stage-132-code-review-prompt.md)" > "$tmp_review"
sed -n '1,240p' "$tmp_review"
python3 - "$tmp_review" docs/reviews/opencode-stage-132-code-review.md <<'PY'
from pathlib import Path
import re
import sys

raw = Path(sys.argv[1]).read_text(encoding="utf-8")
text = re.sub(r"\x1b\[[0-9;?]*[ -/]*[@-~]", "", raw)
start = text.find("# Stage 132 Code Review")
if start != -1:
    text = text[start:]
cut_markers = ("\n> build ", "\n$ ", "\n-> ", "\n<- ")
cut_positions = [text.find(marker) for marker in cut_markers if text.find(marker) != -1]
if cut_positions:
    text = text[: min(cut_positions)]
lines = [line.rstrip() for line in text.splitlines()]
Path(sys.argv[2]).write_text("\n".join(lines).strip() + "\n", encoding="utf-8")
PY
test -s docs/reviews/opencode-stage-132-code-review.md
rm -f "$tmp_review"
```

Expected result: review artifact is non-empty and contains no Critical or
Important blockers.

## Task 4: Full release gate, commit, push, and CI

**Files:**

- No new implementation files beyond Task 3.

- [ ] **Step 1: Run full release gate**

Run:

```bash
uv --no-config run --frozen python scripts/check_release_hygiene.py
env -u ALL_PROXY -u all_proxy uv --no-config run --frozen pytest
uv --no-config run --frozen ruff check .
uv --no-config run --frozen ruff format --check .
env -u UV_DEFAULT_INDEX -u UV_INDEX_URL -u UV_EXTRA_INDEX_URL UV_NO_CONFIG=1 uv lock --check
git diff --exit-code -- uv.lock
git diff --check
if rg -n 'ghp_[A-Za-z0-9]+' .; then echo 'GitHub token pattern found in worktree' >&2; exit 1; fi
if [ -n "$(git config --get-all http.https://github.com/.extraheader || true)" ]; then echo 'Persistent GitHub auth header found' >&2; exit 1; fi
```

Expected result: release hygiene, full pytest, ruff, format, lock check,
lockfile diff, whitespace check, token absence assertion, and persistent git
auth-header absence assertion all pass.

- [ ] **Step 2: Commit Stage 132**

Run:

```bash
git status --short --untracked-files=all
git add scripts/check_release_hygiene.py tests/test_release_hygiene.py docs/superpowers/specs/2026-06-21-stage-132-untracked-secret-hygiene-design.md docs/superpowers/plans/2026-06-21-stage-132-untracked-secret-hygiene-plan.md docs/reviews/opencode-stage-132-plan-review-prompt.md docs/reviews/opencode-stage-132-plan-review.md docs/reviews/opencode-stage-132-code-review-prompt.md docs/reviews/opencode-stage-132-code-review.md
git commit -m "Scan untracked files for release hygiene secrets"
```

Expected result: one commit containing only Stage 132 code, tests, and review
artifacts.

- [ ] **Step 3: Push with ephemeral credentials**

Use the established one-shot push pattern from the operator shell, deriving the
credential header only in process memory and passing it through `git -c` for
that single command. Do not write the token, derived header, or push command
containing credentials into files, git config, shell profile, or review
artifacts. Clear the temporary shell variable immediately after the push, then
verify no persistent GitHub credential header remains:

```bash
git config --get-all http.https://github.com/.extraheader || true
```

Expected result: push succeeds and no persistent GitHub credential header
remains.

- [ ] **Step 4: Verify remote and CI**

Run:

```bash
git ls-remote origin refs/heads/main
```

Then poll the latest GitHub Actions run for the pushed SHA until it reaches a
terminal state.

Expected result: remote `main` points at the Stage 132 commit and CI completes
successfully.
