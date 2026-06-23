# Stage 179 Source-Pack Quality JSON Key-Set Guard Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Guard the source-pack quality docs JSON sample against missing or extra top-level keys relative to the runtime `SourcePackLintResult` payload.

**Architecture:** Test-only docs hardening. Enhance the existing source-pack quality JSON parity test, compare documented JSON sample keys with `lint_source_pack(...).model_dump(mode="json")`, and keep existing value assertions unchanged so the documented relative `path` exception remains explicit.

**Tech Stack:** Python, pytest, Pydantic `model_dump(mode="json")`, existing `tests/test_source_pack_quality_docs.py` helpers, `uv --no-config run --frozen`, local opencode review with `zhipuai-coding-plan/glm-5.2 --variant max`.

---

## Files

- Modify: `tests/test_source_pack_quality_docs.py`
  - Add a runtime top-level key-set assertion to
    `test_source_pack_quality_json_sample_matches_public_pack_lint_output`.
- Add: `docs/superpowers/specs/2026-06-24-stage-179-source-pack-quality-json-keyset-guard-design.md`
- Add: `docs/superpowers/plans/2026-06-24-stage-179-source-pack-quality-json-keyset-guard-plan.md`
- Add: `docs/reviews/opencode-stage-179-plan-review-prompt.md`
- Add after plan review: `docs/reviews/opencode-stage-179-plan-review.md`
- Add after implementation: `docs/reviews/opencode-stage-179-code-review-prompt.md`
- Add after implementation: `docs/reviews/opencode-stage-179-code-review.md`
- Add before commit: `docs/reviews/opencode-stage-179-release-review-prompt.md`
- Add before commit: `docs/reviews/opencode-stage-179-release-review.md`

## Task 1: Add Runtime Key-Set Docs Guard

**Files:**

- Modify: `tests/test_source_pack_quality_docs.py`

- [ ] **Step 1: Run the existing JSON parity test before the guard**

Run:

```bash
uv --no-config run --frozen pytest \
  tests/test_source_pack_quality_docs.py::test_source_pack_quality_json_sample_matches_public_pack_lint_output -q
```

Expected before adding the guard: the existing test passes, confirming this is
a strengthening change rather than a behavior fix.

- [ ] **Step 2: Add the key-set parity assertion**

In `test_source_pack_quality_json_sample_matches_public_pack_lint_output`,
immediately after:

```python
    documented_path = PUBLIC_SOURCE_PACK.relative_to(ROOT).as_posix()
```

add:

```python
    runtime_payload = result.model_dump(mode="json")

    assert set(payload) == set(runtime_payload)
```

This intentionally compares only top-level keys. It must not replace the
existing value-level assertions, because those preserve the documented relative
path assertion and check the count/map values.

- [ ] **Step 3: Run the new key-set test**

Run:

```bash
uv --no-config run --frozen pytest \
  tests/test_source_pack_quality_docs.py::test_source_pack_quality_json_sample_matches_public_pack_lint_output -q
```

Expected: the test passes. If it fails, inspect whether the docs sample or
`SourcePackLintResult` changed; update docs only if the runtime model really has
a new or removed documented key.

## Task 2: Focused Verification And Code Review

**Files:**

- Modify: `tests/test_source_pack_quality_docs.py`
- Add: `docs/reviews/opencode-stage-179-code-review-prompt.md`
- Add: `docs/reviews/opencode-stage-179-code-review.md`

- [ ] **Step 1: Run focused source-pack quality docs checks**

Run:

```bash
uv --no-config run --frozen pytest tests/test_source_pack_quality_docs.py -q
uv --no-config run --frozen ruff check tests/test_source_pack_quality_docs.py
uv --no-config run --frozen ruff format --check tests/test_source_pack_quality_docs.py
```

Expected: all focused tests and checks pass.

- [ ] **Step 2: Create code review prompt**

Create `docs/reviews/opencode-stage-179-code-review-prompt.md` with a prompt
that asks local opencode to review the Stage 179 implementation. The prompt
must require the response to start with:

```text
# Stage 179 Code Review
```

- [ ] **Step 3: Run code review**

Run:

```bash
tmp_review="$(mktemp)"
opencode run --model zhipuai-coding-plan/glm-5.2 --variant max \
  --dir /home/ubuntu/fashion-radar \
  "$(cat docs/reviews/opencode-stage-179-code-review-prompt.md)" > "$tmp_review" 2>&1
sed -n '1,320p' "$tmp_review"
cp "$tmp_review" docs/reviews/opencode-stage-179-code-review.md
rm -f "$tmp_review"
```

Expected: completed review output with no critical or important findings. Clean
the artifact so it contains only one final review body if opencode includes
process chatter, ANSI output, command logs, or multiple drafts.

## Task 3: Release Gate, Release Review, Commit, And Push

**Files:**

- Add: `docs/reviews/opencode-stage-179-release-review-prompt.md`
- Add: `docs/reviews/opencode-stage-179-release-review.md`

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

Create `docs/reviews/opencode-stage-179-release-review-prompt.md` requiring the
review body to start with:

```text
# Stage 179 Release Review
```

Then run the same temp-file `opencode run --model zhipuai-coding-plan/glm-5.2
--variant max` capture flow used for code review, copying the completed review
to `docs/reviews/opencode-stage-179-release-review.md`.

Expected: completed review output with no critical or important findings. Clean
the artifact if needed.

- [ ] **Step 3: Commit and push**

Run:

```bash
git status --short
git add \
  tests/test_source_pack_quality_docs.py \
  docs/superpowers/specs/2026-06-24-stage-179-source-pack-quality-json-keyset-guard-design.md \
  docs/superpowers/plans/2026-06-24-stage-179-source-pack-quality-json-keyset-guard-plan.md \
  docs/reviews/opencode-stage-179-plan-review-prompt.md \
  docs/reviews/opencode-stage-179-plan-review.md \
  docs/reviews/opencode-stage-179-code-review-prompt.md \
  docs/reviews/opencode-stage-179-code-review.md \
  docs/reviews/opencode-stage-179-release-review-prompt.md \
  docs/reviews/opencode-stage-179-release-review.md
git commit -m "test: guard source pack quality json keys"
git push origin main
```

Expected: commit succeeds and `main` pushes to GitHub.

## Self-Review Notes

- Spec coverage: Task 1 adds the runtime key-set docs guard, Task 2 covers
  focused verification and code review, and Task 3 covers release gate, release
  review, commit, and push.
- Placeholder scan: no placeholders or deferred implementation notes.
- Boundary check: source-pack lint runtime behavior, docs content, source
  acquisition, availability checks, ranking, coverage verification features,
  compliance-review product features, dependencies, and lockfiles remain out of
  scope unless the strengthened test exposes a real docs/runtime key mismatch.
