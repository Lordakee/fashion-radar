# Stage 51 First-Run Sample Output Quality Gate Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Strengthen the deterministic first-run smoke so it proves the checked-in sample imports, matches starter entities after the local match step, appears in reports, and produces entity trend deltas.

**Architecture:** Keep the existing smoke helper and local CLI sequence, but add semantic validators for sample CSV input, command stdout, parsed JSON payloads, generated report files, and directory handoff output. Move the smoke's matched imported-summary/imported-signals review to after `match`, because `item_entities` is populated by `match`. Update the two-row sample CSV so it matches existing starter entity config without changing default scoring or broadening entity aliases.

**Tech Stack:** Python 3.11+, Typer CLI, Pydantic models, local SQLite, pytest, ruff, uv. No new dependencies.

---

## File Structure

- Modify `examples/community-signals.example.csv`: keep the two-row local handoff fixture, but make titles/summaries match starter entities.
- Modify `tests/test_community_signal_import_contract.py`: update pinned CSV expectations.
- Modify `scripts/check_first_run_smoke.py`: add validator helpers, move matched imported review checks after `match`, and call them from `run_first_run_flow()`.
- Modify `tests/test_first_run_smoke.py`: add unit coverage for validator success/failure cases and update the command-sequence stub payloads.
- Modify `README.md`: document that the deterministic sample now yields `The Row`, `The Row Margaux`, and `Ballet Flats` report/trend signals.
- Modify `docs/first-run.md`: document the same first-run sample output contract and keep boundary wording.
- Modify `docs/github-upload-checklist.md`: mention that package smoke validates sample output content, not only command execution.
- Modify `docs/cli-reference.md`: clarify the helper's deterministic sample-output gate.
- Modify `tests/test_cli_docs.py`: pin the new docs wording without changing the smoke command strings.

## Task 1: Make The Checked-In CSV Sample Produce Starter Entity Matches

**Files:**
- Modify: `examples/community-signals.example.csv`
- Modify: `tests/test_community_signal_import_contract.py`

- [ ] **Step 1: Update the CSV fixture**

Replace the two data rows in `examples/community-signals.example.csv` with:

```csv
https://example.com/community/the-row-margaux-tote,The Row Margaux tote interest,2026-06-12T08:00:00Z,Sanitized local note about The Row Margaux handbag and tote demand,Community Tool Export,community,1.3,2026-06-12T08:30:00Z
https://example.com/community/ballet-flats-footwear,Ballet flats footwear mention,2026-06-12T09:00:00Z,Short sanitized note about ballet flats shoes and footwear styling,Community Tool Export,community,1.1,2026-06-12T09:20:00Z
```

- [ ] **Step 2: Update contract expectations**

In `tests/test_community_signal_import_contract.py::test_community_signal_csv_example_loads_through_manual_importer`, update assertions to:

```python
assert rows[0].url == "https://example.com/community/the-row-margaux-tote"
assert rows[0].title == "The Row Margaux tote interest"
assert rows[0].source_name == "Community Tool Export"
assert rows[0].platform == "community"
assert rows[0].source_weight == 1.3
assert rows[1].url == "https://example.com/community/ballet-flats-footwear"
assert rows[1].title == "Ballet flats footwear mention"
assert rows[1].summary == "Short sanitized note about ballet flats shoes and footwear styling"
```

- [ ] **Step 3: Verify the contract test**

Run:

```bash
UV_NO_CONFIG=1 uv run pytest tests/test_community_signal_import_contract.py -q
```

Expected: all tests in the file pass.

## Task 2: Add First-Run Semantic Validators

**Files:**
- Modify: `scripts/check_first_run_smoke.py`
- Modify: `tests/test_first_run_smoke.py`

- [ ] **Step 1: Add expected sample constants**

In `scripts/check_first_run_smoke.py`, add `csv` to imports and define:

```python
EXPECTED_SAMPLE_ROWS = (
    {
        "url": "https://example.com/community/the-row-margaux-tote",
        "title": "The Row Margaux tote interest",
        "published_at": "2026-06-12T08:00:00Z",
        "summary": "Sanitized local note about The Row Margaux handbag and tote demand",
        "source_name": SOURCE_NAME,
        "platform": "community",
        "source_weight": "1.3",
        "collected_at": "2026-06-12T08:30:00Z",
    },
    {
        "url": "https://example.com/community/ballet-flats-footwear",
        "title": "Ballet flats footwear mention",
        "published_at": "2026-06-12T09:00:00Z",
        "summary": "Short sanitized note about ballet flats shoes and footwear styling",
        "source_name": SOURCE_NAME,
        "platform": "community",
        "source_weight": "1.1",
        "collected_at": "2026-06-12T09:20:00Z",
    },
)
EXPECTED_SAMPLE_TITLES = tuple(row["title"] for row in EXPECTED_SAMPLE_ROWS)
EXPECTED_SAMPLE_URLS = tuple(row["url"] for row in EXPECTED_SAMPLE_ROWS)
EXPECTED_SAMPLE_ENTITIES = ("The Row", "The Row Margaux", "Ballet Flats")
EXPECTED_PLATFORM_COUNTS = {"community": 2}
EXPECTED_SOURCE_COUNTS = {SOURCE_NAME: 2}
```

- [ ] **Step 2: Add a reusable assertion helper**

Add:

```python
def assert_equal(label: str, actual: Any, expected: Any) -> None:
    if actual != expected:
        raise SmokeError(f"{label} expected {expected!r}, got {actual!r}")
```

- [ ] **Step 3: Add a sample CSV validator**

Add:

```python
def validate_sample_csv(path: Path) -> None:
    with path.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    assert_equal("sample CSV row count", len(rows), len(EXPECTED_SAMPLE_ROWS))
    for index, expected in enumerate(EXPECTED_SAMPLE_ROWS):
        if index >= len(rows):
            raise SmokeError(f"sample CSV missing row {index + 1}")
        for key, expected_value in expected.items():
            assert_equal(f"sample CSV row {index + 1} {key}", rows[index].get(key), expected_value)
```

- [ ] **Step 4: Add preview validators**

Add:

```python
def validate_community_candidates(command_name: str, payload: Any, *, directory: bool = False) -> None:
    if not isinstance(payload, dict):
        raise SmokeError(f"{command_name} output must be a JSON object")
    assert_equal(f"{command_name} input_format", payload.get("input_format"), "csv")
    assert_equal(f"{command_name} source_name", payload.get("source_name"), SOURCE_NAME)
    assert_equal(f"{command_name} row_count", payload.get("row_count"), 2)
    assert_equal(f"{command_name} candidate_count", payload.get("candidate_count"), 0)
    assert_equal(f"{command_name} candidates", payload.get("candidates"), [])
    assert_equal(f"{command_name} as_of", payload.get("as_of"), "2026-06-13T12:00:00+00:00")
    if directory:
        assert_equal(f"{command_name} file_count", payload.get("file_count"), 1)
```

- [ ] **Step 5: Add stdout validators**

Add:

```python
def assert_output_contains(command_name: str, output: str, expected_lines: Sequence[str]) -> None:
    for expected in expected_lines:
        if expected not in output:
            raise SmokeError(f"{command_name} output missing expected text: {expected}")


def validate_import_signals_dry_run(output: str) -> None:
    assert_output_contains(
        "import-signals --dry-run",
        output,
        ("Validated 2 manual signal rows", "Dry run: no rows imported"),
    )


def validate_import_signals_import(output: str) -> None:
    assert_output_contains(
        "import-signals",
        output,
        ("Validated 2 manual signal rows", "Imported 2 manual signal rows", "Items added: 2"),
    )


def validate_import_signals_dir_dry_run(output: str) -> None:
    assert_output_contains(
        "import-signals-dir --dry-run",
        output,
        (
            "Files: 1 total, 1 valid",
            "Rows: 2 import-ready",
            "Sources: Community Tool Export=2",
            "Platforms: community=2",
            "Errors: 0",
            "community-signals.csv: 2 rows, 0 errors",
            "No manual signal directory dry-run errors.",
        ),
    )
```

- [ ] **Step 6: Add imported summary and review validators**

Add:

```python
def validate_imported_summary(command_name: str, payload: Any) -> None:
    if not isinstance(payload, dict):
        raise SmokeError(f"{command_name} output must be a JSON object")
    assert_equal(f"{command_name} row_count", payload.get("row_count"), 2)
    assert_equal(f"{command_name} source_count", payload.get("source_count"), 1)
    assert_equal(f"{command_name} matched_count", payload.get("matched_count"), 2)
    assert_equal(f"{command_name} unmatched_count", payload.get("unmatched_count"), 0)
    assert_equal(f"{command_name} platform_counts", payload.get("platform_counts"), EXPECTED_PLATFORM_COUNTS)
    sources = payload.get("sources")
    if not isinstance(sources, list) or len(sources) != 1:
        raise SmokeError(f"{command_name} must report exactly one source")
    assert_equal(f"{command_name} source name", sources[0].get("source_name"), SOURCE_NAME)
    assert_equal(f"{command_name} source row_count", sources[0].get("row_count"), 2)
    assert_equal(f"{command_name} source matched_count", sources[0].get("matched_count"), 2)
```

Add:

```python
def validate_imported_signals(command_name: str, payload: Any) -> None:
    if not isinstance(payload, dict):
        raise SmokeError(f"{command_name} output must be a JSON object")
    assert_equal(f"{command_name} row_count", payload.get("row_count"), 2)
    assert_equal(f"{command_name} total_count", payload.get("total_count"), 2)
    assert_equal(f"{command_name} matched_count", payload.get("matched_count"), 2)
    assert_equal(f"{command_name} unmatched_count", payload.get("unmatched_count"), 0)
    assert_equal(f"{command_name} source_name_counts", payload.get("source_name_counts"), EXPECTED_SOURCE_COUNTS)
    assert_equal(f"{command_name} platform_counts", payload.get("platform_counts"), EXPECTED_PLATFORM_COUNTS)
    items = payload.get("items")
    if not isinstance(items, list) or len(items) != 2:
        raise SmokeError(f"{command_name} must contain exactly two sample items")
    titles = [item.get("title") for item in items if isinstance(item, dict)]
    assert_equal(f"{command_name} item titles", titles, ["Ballet flats footwear mention", "The Row Margaux tote interest"])
    matches_by_title = {
        item["title"]: {match.get("entity_name") for match in item.get("matches", [])}
        for item in items
        if isinstance(item, dict)
    }
    for title in EXPECTED_SAMPLE_TITLES:
        if title not in matches_by_title:
            raise SmokeError(f"{command_name} missing sample title: {title}")
    if "Ballet Flats" not in matches_by_title["Ballet flats footwear mention"]:
        raise SmokeError(f"{command_name} missing Ballet Flats match")
    row_matches = matches_by_title["The Row Margaux tote interest"]
    for expected_entity in ("The Row", "The Row Margaux"):
        if expected_entity not in row_matches:
            raise SmokeError(f"{command_name} missing {expected_entity} match")
```

- [ ] **Step 7: Add report, candidates, and trends validators**

Add:

```python
def validate_report_outputs(json_payload: Any, markdown_text: str) -> None:
    if not isinstance(json_payload, dict):
        raise SmokeError("report JSON output must be a JSON object")
    metadata = json_payload.get("metadata")
    if not isinstance(metadata, dict):
        raise SmokeError("report JSON missing metadata")
    assert_equal("report metadata item_count", metadata.get("item_count"), 3)
    entities = json_payload.get("entities")
    if not isinstance(entities, list):
        raise SmokeError("report JSON entities must be a list")
    entity_names = [entity.get("entity_name") for entity in entities if isinstance(entity, dict)]
    assert_equal("report entity names", entity_names, list(EXPECTED_SAMPLE_ENTITIES))
    for expected in EXPECTED_SAMPLE_ENTITIES:
        if f"### {expected} (new)" not in markdown_text:
            raise SmokeError(f"report Markdown missing sample entity section: {expected}")
    if "No entity signals in this window." in markdown_text:
        raise SmokeError("report Markdown should not contain the empty entity signal message")


def validate_candidates(command_name: str, payload: Any, report_payload: Any) -> None:
    assert_equal(f"{command_name} candidates", payload, [])
    if isinstance(report_payload, dict):
        assert_equal("report candidates", report_payload.get("candidates"), payload)


def validate_trends(command_name: str, payload: Any) -> None:
    if not isinstance(payload, dict):
        raise SmokeError(f"{command_name} output must be a JSON object")
    assert_equal(f"{command_name} as_of", payload.get("as_of"), "2026-06-13T12:00:00Z")
    deltas = payload.get("deltas")
    if not isinstance(deltas, list):
        raise SmokeError(f"{command_name} deltas must be a list")
    names = [delta.get("name") for delta in deltas if isinstance(delta, dict)]
    assert_equal(f"{command_name} entity delta names", names, list(EXPECTED_SAMPLE_ENTITIES))
```

- [ ] **Step 8: Wire validators into the existing flow**

In `run_first_run_flow()`:

- call `validate_sample_csv(example_csv)` after the file-exists check
- assign and validate the parsed `community-candidates` JSON
- validate stdout from both `import-signals` calls
- run `match` before validating matched imported summary and imported signals payloads
- parse report JSON, read Markdown, and call `validate_report_outputs`
- validate candidates payload against report payload
- validate trends payload
- validate `community-candidates-dir`
- validate stdout from `import-signals-dir --dry-run`

- [ ] **Step 9: Update unit tests**

Add tests beside the existing validator tests:

```python
def test_validate_sample_csv_requires_expected_rows(tmp_path: Path) -> None:
    sample = tmp_path / "community.csv"
    sample.write_text(
        "url,title,published_at,summary,source_name,platform,source_weight,collected_at\n"
        "https://example.com/community/the-row-margaux-tote,The Row Margaux tote interest,2026-06-12T08:00:00Z,Sanitized local note about The Row Margaux handbag and tote demand,Community Tool Export,community,1.3,2026-06-12T08:30:00Z\n"
        "https://example.com/community/ballet-flats-footwear,Ballet flats footwear mention,2026-06-12T09:00:00Z,Short sanitized note about ballet flats shoes and footwear styling,Community Tool Export,community,1.1,2026-06-12T09:20:00Z\n",
        encoding="utf-8",
    )
    smoke.validate_sample_csv(sample)
    sample.write_text("url,title,published_at\nhttps://example.com/a,Wrong,2026-06-12T08:00:00Z\n", encoding="utf-8")
    with pytest.raises(smoke.SmokeError, match="sample CSV row count"):
        smoke.validate_sample_csv(sample)
```

Add equivalent passing/failing tests for:

- `validate_community_candidates`
- `validate_import_signals_dry_run`
- `validate_import_signals_import`
- `validate_imported_summary`
- `validate_imported_signals`
- `validate_report_outputs`
- `validate_candidates`
- `validate_trends`
- `validate_import_signals_dir_dry_run`

- [ ] **Step 10: Update command-sequence test stubs**

In `test_run_first_run_flow_uses_deterministic_local_command_sequence`, write the temporary example CSV with the two expected sample rows. Update fake outputs:

- `community-candidates`: JSON object with `row_count: 2`, `candidate_count: 0`, expected windows, and `candidates: []`
- `match` runs before `imported-signals-summary` and `imported-signals`
- `imported-signals-summary`: JSON object with `row_count: 2`, `source_count: 1`, `matched_count: 2`, `unmatched_count: 0`, `platform_counts: {"community": 2}`, one source row
- `imported-signals`: JSON object with two matched sample items returned after `match`
- report JSON file: metadata `item_count: 3`, three entities, empty candidates
- report Markdown file: entity sections for `The Row`, `The Row Margaux`, and `Ballet Flats`
- `candidates`: `[]`
- `trends`: JSON object with three deltas for the expected entities
- `community-candidates-dir`: JSON object with `file_count: 1`, `row_count: 2`, `candidate_count: 0`, and `candidates: []`
- `import-signals` dry-run/import stdout and `import-signals-dir` dry-run stdout include the exact expected lines

- [ ] **Step 11: Verify focused tests**

Run:

```bash
UV_NO_CONFIG=1 uv run pytest tests/test_first_run_smoke.py tests/test_community_signal_import_contract.py -q
```

Expected: all selected tests pass.

## Task 3: Update First-Run Documentation And Drift Tests

**Files:**
- Modify: `README.md`
- Modify: `docs/first-run.md`
- Modify: `docs/github-upload-checklist.md`
- Modify: `docs/cli-reference.md`
- Modify: `tests/test_cli_docs.py`

- [ ] **Step 1: Update README first-run wording**

In the manual sample section, add that the checked-in sample is expected to
produce matched report/trend signals for `The Row`, `The Row Margaux`, and
`Ballet Flats`.

In the automated smoke section, replace the generic sentence about candidate
and trend JSON commands with:

```text
The smoke validates that the sample rows import as community signals, match the starter entities `The Row`, `The Row Margaux`, and `Ballet Flats`, appear in the dated report, produce matching entity trend deltas, and keep untracked candidates empty under the starter config.
```

- [ ] **Step 2: Update first-run guide wording**

In `docs/first-run.md`, add the same expected output contract near the manual
sample artifacts and the automated smoke description. Preserve existing
boundary terms: `temporary config, data, report, and export directories`, `does
not run collect`, `run`, or `dashboard`, `browser automation`, `account login`,
`cookies/sessions`, `source/platform connectors`, and `external services`.

- [ ] **Step 3: Update upload checklist wording**

In `docs/github-upload-checklist.md`, add one sentence after the source smoke
command:

```text
The smoke also validates the sample rows, matched starter entities, report content, trend deltas, empty untracked candidates, and directory handoff dry-run counts.
```

- [ ] **Step 4: Update CLI reference wording**

Update the compact helper description to say the script validates deterministic
sample output content, not just command execution.

- [ ] **Step 5: Pin docs drift tests**

In `tests/test_cli_docs.py`, extend existing first-run documentation tests with
terms:

```python
"The Row"
"The Row Margaux"
"Ballet Flats"
"matched starter entities"
"entity trend deltas"
"empty untracked candidates"
```

Keep the smoke command strings unchanged so
`test_first_run_smoke_command_is_documented_and_in_ci` still passes without CI
edits.

- [ ] **Step 6: Verify docs tests**

Run:

```bash
UV_NO_CONFIG=1 uv run pytest tests/test_cli_docs.py -q
```

Expected: all docs drift tests pass.

## Task 4: Stage Verification, Claude Code Review, Commit, And User-Authorized Upload

**Files:**
- Create: `docs/reviews/claude-code-stage-51-release-review-prompt.md`
- Create: `docs/reviews/claude-code-stage-51-release-review.md`
- Create if needed after fixes: `docs/reviews/claude-code-stage-51-release-rereview-prompt.md`
- Create if needed after fixes: `docs/reviews/claude-code-stage-51-release-rereview.md`
- Modify: `CHANGELOG.md`

- [ ] **Step 0: Record the accepted plan review**

Ensure these files exist and are included in the stage commit:

```text
docs/reviews/claude-code-stage-51-plan-review-prompt.md
docs/reviews/claude-code-stage-51-plan-review.md
```

If a plan rereview was required, include the corresponding
`docs/reviews/claude-code-stage-51-plan-rereview*.md` records too.

- [ ] **Step 1: Run focused verification**

Run:

```bash
UV_NO_CONFIG=1 uv run pytest tests/test_first_run_smoke.py tests/test_community_signal_import_contract.py tests/test_cli_docs.py -q
UV_NO_CONFIG=1 uv run python scripts/check_first_run_smoke.py --repo-root .
```

Expected: selected tests pass and the source first-run smoke prints
`First-run sample smoke passed.`

- [ ] **Step 2: Run full verification**

Run:

```bash
UV_NO_CONFIG=1 uv run pytest -q
UV_NO_CONFIG=1 uv run ruff check .
UV_NO_CONFIG=1 uv run ruff format --check .
UV_NO_CONFIG=1 uv lock --check
UV_DEFAULT_INDEX=https://pypi.tuna.tsinghua.edu.cn/simple uv sync --frozen --dev
UV_NO_CONFIG=1 uv sync --locked --dev --check
UV_NO_CONFIG=1 uv run python scripts/check_release_hygiene.py --repo-root .
tmp_build="$(mktemp -d)"
UV_NO_CONFIG=1 uv build --out-dir "$tmp_build"
UV_NO_CONFIG=1 uv run python scripts/check_package_archives.py "$tmp_build"
tmp_env="$(mktemp -d)"
uv venv "$tmp_env/venv"
uv pip install --python "$tmp_env/venv/bin/python" "$tmp_build"/*.whl
"$tmp_env/venv/bin/python" scripts/check_first_run_smoke.py --repo-root . --python "$tmp_env/venv/bin/python" --installed
```

Expected: all commands exit 0.

- [ ] **Step 3: Request Claude Code release review**

Create `docs/reviews/claude-code-stage-51-release-review-prompt.md` with the
stage goal, changed files, verification commands, and explicit request to find
Critical/Important/Minor issues. Run:

```bash
claude --effort max --permission-mode plan --no-session-persistence \
  --tools Read,Grep,Glob,LS,Bash \
  -p "$(cat docs/reviews/claude-code-stage-51-release-review-prompt.md)" \
  > docs/reviews/claude-code-stage-51-release-review.md
```

Expected: no Critical or Important findings. Fix any Critical/Important
findings and rerun review before committing.

- [ ] **Step 4: Final hygiene**

Run:

```bash
git diff --check
git diff --cached --check
UV_NO_CONFIG=1 uv lock --check
git diff --quiet -- uv.lock
git status --short --branch
```

Expected: no whitespace errors, lock check passes, `uv.lock` has no diff, and
only intended Stage 51 files are modified.

- [ ] **Step 5: Commit the local stage**

Run:

```bash
git add examples/community-signals.example.csv tests/test_community_signal_import_contract.py scripts/check_first_run_smoke.py tests/test_first_run_smoke.py README.md docs/first-run.md docs/github-upload-checklist.md docs/cli-reference.md tests/test_cli_docs.py CHANGELOG.md docs/superpowers/specs/2026-06-16-stage-51-first-run-sample-output-quality-gate-design.md docs/superpowers/plans/2026-06-16-stage-51-first-run-sample-output-quality-gate-plan.md docs/reviews/claude-code-stage-51-*.md
git commit -m "Strengthen first-run sample output gate"
```

Expected: commit succeeds.

- [ ] **Step 6: User-authorized GitHub upload**

This is not part of the first-run smoke helper and is not a product/runtime
external-service dependency. Run it only when the user has explicitly
authorized uploading this node to the existing remote. In the current session,
the user has authorized pushing to `origin main`.

Run:

```bash
TOKEN="$(cat /home/ubuntu/.config/fashion-radar/github-token)"
BASIC="$(printf 'x-access-token:%s' "$TOKEN" | base64 -w0)"
GIT_TERMINAL_PROMPT=0 git -c http.version=HTTP/1.1 \
  -c http.postBuffer=524288000 \
  -c http.lowSpeedLimit=0 \
  -c http.lowSpeedTime=999999 \
  -c http.extraHeader="Authorization: Basic ${BASIC}" \
  push --no-thin origin main
```

Expected: push updates `origin/main`.

- [ ] **Step 7: Confirm GitHub Actions after user-authorized upload**

This is also a post-stage upload confirmation, not a first-run smoke
requirement.

Run the stored-token Actions check without printing the token:

```bash
TOKEN="$(cat /home/ubuntu/.config/fashion-radar/github-token)"
curl -fsS -H "Authorization: Bearer ${TOKEN}" \
  -H "Accept: application/vnd.github+json" \
  -H "X-GitHub-Api-Version: 2022-11-28" \
  "https://api.github.com/repos/Lordakee/fashion-radar/actions/runs?branch=main&per_page=1" \
  | python3 -c 'import json,sys; r=json.load(sys.stdin)["workflow_runs"][0]; print(r["id"], r["status"], r["conclusion"], r["head_sha"], r["html_url"])'
```

Expected: the latest run for the pushed SHA completes with `success`.

## Self-Review Notes

- The plan covers all design requirements: sample contract, smoke validators,
  tests, docs, release review, local commit, and user-authorized upload.
- No new dependency or lockfile change is expected.
- The smoke command strings stay unchanged, so CI does not need edits.
- The matched imported-review validators are explicitly after the local `match`
  command.
- The scope excludes scraping/crawling, browser automation, platform APIs,
  account/session/cookie handling, external-service dependencies in the smoke
  helper, and compliance-review features.
- GitHub upload and Actions confirmation are separate user-authorized release
  steps after local verification, not first-run smoke requirements.
