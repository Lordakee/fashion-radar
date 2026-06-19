# Stage 122 Sdist Internal Artifact Exclusion Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Exclude internal review and superpowers planning artifacts from source distributions and make package archive checks reject them if they appear.

**Architecture:** Use a two-layer release guard. Hatch sdist excludes keep `docs/reviews/**` and `docs/superpowers/**` out of normal source distributions, while `scripts/check_package_archives.py` rejects those paths if any built archive contains them. Tests cover both the checker behavior and the build configuration.

**Tech Stack:** Python 3.11, Hatchling build configuration, standard-library archive validation, pytest, ruff, uv.

---

## Files

- Modify `tests/test_package_archives.py`
  - Add a failing regression test that injects internal review/plan members into
    the synthetic sdist.
- Modify `scripts/check_package_archives.py`
  - Add `FORBIDDEN_RELEASE_PATH_PREFIXES`.
  - Teach `is_forbidden_release_member()` to reject exact prefix paths and
    child paths.
- Modify `tests/test_package_metadata.py`
  - Add a failing regression test for Hatch sdist exclude configuration.
- Modify `pyproject.toml`
  - Add `[tool.hatch.build.targets.sdist]` with exclude entries.

No product code, CLI commands, connector behavior, scraping, source acquisition,
ranking, demand proof, coverage verification, dependencies, or CI workflow
files are part of this stage.

## Task 1: Add RED checker test for internal sdist artifacts

**Files:**

- Modify: `tests/test_package_archives.py`

- [ ] **Step 1: Add the failing test**

Insert this test near the existing sdist forbidden-member tests, after
`test_rejects_sdist_with_generated_source_config`:

```python
@pytest.mark.parametrize(
    "forbidden_path",
    [
        "docs/reviews/opencode-stage-1-code-review.md",
        "docs/superpowers/plans/2026-06-20-stage-122-plan.md",
        "docs/superpowers/specs/2026-06-20-stage-122-design.md",
    ],
)
def test_rejects_sdist_with_internal_review_or_plan_artifacts(
    tmp_path: Path,
    forbidden_path: str,
) -> None:
    build_dir = tmp_path / "dist"
    build_dir.mkdir()
    write_wheel(build_dir)
    write_sdist(build_dir, files=SDIST_FILES + [forbidden_path])

    result = run_checker(build_dir)

    assert result.returncode == 1
    assert (
        f"sdist archive contains forbidden release member: {forbidden_path}"
        in result.stderr
    )
```

- [ ] **Step 2: Run the RED test**

Run:

```bash
uv --no-config run --frozen pytest tests/test_package_archives.py::test_rejects_sdist_with_internal_review_or_plan_artifacts -q
```

Expected result: fail because the checker currently accepts those archive
members.

## Task 2: Add checker guard for internal artifact paths

**Files:**

- Modify: `scripts/check_package_archives.py`

- [ ] **Step 1: Add path-prefix constant**

Add this constant after `FORBIDDEN_RELEASE_GENERATED_CONFIGS`:

```python
FORBIDDEN_RELEASE_PATH_PREFIXES = (
    "docs/reviews",
    "docs/superpowers",
)
```

- [ ] **Step 2: Add prefix rejection**

In `is_forbidden_release_member()`, after the `lower_path in
FORBIDDEN_RELEASE_GENERATED_CONFIGS` check, add:

```python
    if any(
        lower_path == prefix or lower_path.startswith(f"{prefix}/")
        for prefix in FORBIDDEN_RELEASE_PATH_PREFIXES
    ):
        return True
```

- [ ] **Step 3: Run the focused checker test**

Run:

```bash
uv --no-config run --frozen pytest tests/test_package_archives.py::test_rejects_sdist_with_internal_review_or_plan_artifacts -q
```

Expected result: pass.

- [ ] **Step 4: Run all package archive tests**

Run:

```bash
uv --no-config run --frozen pytest tests/test_package_archives.py -q
```

Expected result: all tests in `tests/test_package_archives.py` pass.

## Task 3: Add RED pyproject sdist exclude test

**Files:**

- Modify: `tests/test_package_metadata.py`

- [ ] **Step 1: Add the failing test**

Add this test after `test_package_script_and_wheel_package_are_declared`:

```python
def test_sdist_excludes_internal_agent_artifacts() -> None:
    data = tomllib.loads(PYPROJECT.read_text(encoding="utf-8"))

    assert data["tool"]["hatch"]["build"]["targets"]["sdist"]["exclude"] == [
        "/docs/reviews/**",
        "/docs/superpowers/**",
    ]
```

- [ ] **Step 2: Run the RED test**

Run:

```bash
uv --no-config run --frozen pytest tests/test_package_metadata.py::test_sdist_excludes_internal_agent_artifacts -q
```

Expected result: fail with a missing `sdist` key.

## Task 4: Add Hatch sdist excludes

**Files:**

- Modify: `pyproject.toml`

- [ ] **Step 1: Add the Hatch sdist target**

Add this block immediately after the existing wheel target:

```toml
[tool.hatch.build.targets.sdist]
exclude = [
  "/docs/reviews/**",
  "/docs/superpowers/**",
]
```

- [ ] **Step 2: Run the pyproject metadata test**

Run:

```bash
uv --no-config run --frozen pytest tests/test_package_metadata.py::test_sdist_excludes_internal_agent_artifacts -q
```

Expected result: pass.

## Task 5: Verify a real sdist omits internal artifacts

**Files:**

- No source edits.

- [ ] **Step 1: Build into a temporary directory**

Run:

```bash
tmp_build="$(mktemp -d)"
uv --no-config build --out-dir "$tmp_build"
```

Expected result: one `.whl` and one `.tar.gz` are created under `$tmp_build`.

- [ ] **Step 2: Run package archive checker against the real build**

Run:

```bash
uv --no-config run --frozen python scripts/check_package_archives.py "$tmp_build"
```

Expected result:

```text
Package archives contain required files.
```

- [ ] **Step 3: Scan the real sdist members**

Run:

```bash
if tar -tzf "$tmp_build"/*.tar.gz | grep -E '/docs/(reviews|superpowers)(/|$)'; then
  exit 1
fi
```

Expected result: no output and exit code 0.

- [ ] **Step 4: Remove the temporary build directory**

Run:

```bash
rm -rf "$tmp_build"
```

Expected result: no temporary build directory remains.

## Task 6: Focused verification and local code review

**Files:**

- Create: `docs/reviews/opencode-stage-122-code-review-prompt.md`
- Create: `docs/reviews/opencode-stage-122-code-review.md`

- [ ] **Step 1: Run focused tests**

Run:

```bash
uv --no-config run --frozen pytest tests/test_package_archives.py tests/test_package_metadata.py -q
```

Expected result: all focused tests pass.

- [ ] **Step 2: Run focused lint and format checks**

Run:

```bash
uv --no-config run --frozen ruff check scripts/check_package_archives.py tests/test_package_archives.py tests/test_package_metadata.py
uv --no-config run --frozen ruff format --check scripts/check_package_archives.py tests/test_package_archives.py tests/test_package_metadata.py
```

Expected result: both commands pass.

- [ ] **Step 3: Write the Stage 122 code review prompt**

Create `docs/reviews/opencode-stage-122-code-review-prompt.md` with:

```markdown
Review the Stage 122 implementation before release.

Repository: `/home/ubuntu/fashion-radar`

Stage goal:
- Exclude internal review and superpowers planning artifacts from source
  distributions.
- Make package archive checks reject those paths if they appear in any built
  archive.

Files changed:
- `pyproject.toml`
- `scripts/check_package_archives.py`
- `tests/test_package_archives.py`
- `tests/test_package_metadata.py`
- Stage 122 design/plan/review artifacts

Review focus:
1. Does the implementation match the Stage 122 design and plan?
2. Do Hatch sdist excludes cover `docs/reviews/**` and `docs/superpowers/**`
   without removing required public docs, examples, schemas, or source files?
3. Does `scripts/check_package_archives.py` reject exact internal artifact
   directory paths and child paths after archive path normalization?
4. Do the tests prove both the checker guard and the pyproject build
   configuration?
5. Does the stage avoid runtime, CLI, dependency, connector, scraping,
   platform API, monitoring, scheduling, source acquisition, demand proof,
   ranking, coverage verification, and compliance/audit product behavior?

Return:
- Critical findings, if any.
- Important findings, if any.
- Minor findings, if any.
- A final explicit statement whether there are any Critical or Important
  blockers before release.
```

- [ ] **Step 4: Run local opencode code review**

Run:

```bash
tmp_review="$(mktemp)"
opencode run --model zhipuai-coding-plan/glm-5.2 --variant max --dir /home/ubuntu/fashion-radar "$(cat docs/reviews/opencode-stage-122-code-review-prompt.md)" > "$tmp_review"
sed -n '1,220p' "$tmp_review"
python3 - "$tmp_review" docs/reviews/opencode-stage-122-code-review.md <<'PY'
from pathlib import Path
import re
import sys

raw = Path(sys.argv[1]).read_text(encoding="utf-8")
text = re.sub(r"\x1b\[[0-9;?]*[ -/]*[@-~]", "", raw)
drop_prefixes = ("→ ", "← ", "$ ", "> build ")
lines = [
    line.rstrip()
    for line in text.splitlines()
    if not any(line.startswith(prefix) for prefix in drop_prefixes)
]
Path(sys.argv[2]).write_text("\n".join(lines).strip() + "\n", encoding="utf-8")
PY
test -s docs/reviews/opencode-stage-122-code-review.md
rm -f "$tmp_review"
```

Expected result: review artifact is non-empty, contains one coherent review
body, and contains no Critical or Important blockers. If the captured output
contains live tool status lines or multiple drafts, replace the final artifact
with one cleaned review body before committing. If Critical or Important
findings appear, fix them and run a rereview before continuing.

## Task 7: Full release gate, commit, push, and CI

**Files:**

- No new implementation files beyond Task 6.

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
```

Expected result: every command exits 0.

- [ ] **Step 2: Check secrets and temporary auth state**

Run:

```bash
rg -n 'ghp_[A-Za-z0-9]+' .
git config --get-all http.https://github.com/.extraheader || true
```

Expected result: no token matches in the repository and no persistent GitHub
extraheader output.

- [ ] **Step 3: Stage the Stage 122 files**

Run:

```bash
git add pyproject.toml \
  scripts/check_package_archives.py \
  tests/test_package_archives.py \
  tests/test_package_metadata.py \
  docs/superpowers/specs/2026-06-20-stage-122-sdist-internal-artifact-exclusion-design.md \
  docs/superpowers/plans/2026-06-20-stage-122-sdist-internal-artifact-exclusion-plan.md \
  docs/reviews/opencode-stage-122-plan-review-prompt.md \
  docs/reviews/opencode-stage-122-plan-review.md \
  docs/reviews/opencode-stage-122-code-review-prompt.md \
  docs/reviews/opencode-stage-122-code-review.md
```

- [ ] **Step 4: Verify staged diff and commit**

Run:

```bash
git diff --cached --stat
git diff --cached | rg -n 'ghp_[A-Za-z0-9]+'
git commit -m "Exclude internal artifacts from sdist"
```

Expected result: commit succeeds and no token scan output appears.

- [ ] **Step 5: Push with temporary GitHub auth header**

Run:

```bash
AUTH_HEADER=$(printf 'x-access-token:%s' '<token supplied by user>' | base64 -w0)
git -c http.https://github.com/.extraheader="AUTHORIZATION: basic ${AUTH_HEADER}" push origin main
unset AUTH_HEADER
git config --get-all http.https://github.com/.extraheader || true
```

Expected result: push succeeds and no persistent GitHub extraheader output
appears.

- [ ] **Step 6: Verify remote SHA and CI**

Run:

```bash
git rev-parse HEAD
git ls-remote origin refs/heads/main
```

Expected result: both SHAs match. Then poll GitHub Actions for the pushed SHA
and require a successful CI conclusion before reporting completion.

## Self-Review

- Spec coverage: the plan covers build-time exclusion, checker rejection,
  tests, real archive verification, local review, release gate, commit, push,
  and CI.
- Marker scan: no unresolved implementation markers remain. The push command
  intentionally uses `<token supplied by user>` as a non-secret stand-in; the
  actual token must not be stored in repository files or Git config.
- Type consistency: test names, constants, paths, and command names match the
  existing files and planned edits.
