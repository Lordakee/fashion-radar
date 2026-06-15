## Critical issues

None found. The Stage 52 plan stays within the intended local-only, print-only scope if implemented as written.

## Important issues / recommended fixes before implementation

### 1. Manifest may still be too thin for an external producer contract

The feature fills a real gap beyond the two existing commands, but the planned manifest fields are only partially sufficient for a producer.

`community-signal-profile` already exposes important producer-facing constraints that the manifest plan does not include:

- `prohibited_fields`
- `field_notes`
- `field_rules`, especially `source_weight`
- `unsupported_capabilities`
- possibly `supported_input_formats`

The manifest includes `producer_profile_command`, so this is not a correctness bug, but it weakens the “single machine-readable manifest” value. An external tool that consumes only the manifest could still emit prohibited fields or invalid `source_weight`.

**Recommendation:** either:

- add these profile-derived fields to the manifest, or
- make the manifest explicitly a directory wrapper and state that producers must also consume `producer_profile_command` / `community-signal-profile --format json` for full field-level validation rules.

Given the objective says “combines the target directory, filename/pattern expectations, producer contract pointers, and local command workflow,” the current shape is acceptable only if “pointers” are considered enough. If the goal is standalone producer guidance, include the missing constraints.

---

### 2. `manifest_storage_note` is directionally correct but should be stronger for JSON handoff directories

The current planned note says:

> If this manifest is saved to disk, keep it outside the matched handoff directory or use a filename excluded by the handoff pattern.

That is adequate in principle, but the highest-risk case is exactly the JSON case:

```bash
--input-format json --pattern "*.json"
```

If an external tool saves `community-handoff-manifest.json` in the handoff directory, the lint/candidates/import directory commands will likely treat it as a signal file.

**Recommendation:** make the note more explicit, for example:

> Do not save this manifest as a matched handoff file. For example, when using `--pattern "*.json"`, do not save the manifest as a `.json` file inside the handoff directory; save it outside the directory or use an excluded filename/pattern.

Also add a test asserting the note mentions the `*.json` case or “do not save as `.json` inside the handoff directory.”

---

### 3. No-side-effect test should guard all supplied paths, not only `directory`

The planned test guards `directory` against `exists`, `is_dir`, `is_file`, `iterdir`, `glob`, and `rglob`, but it leaves `config_dir` and `data_dir` unguarded.

The command is supposed to be print-only and should not inspect or create artifacts via any supplied path. The existing `community-handoff-workflow` implementation intentionally only stringifies paths, so this should be easy to enforce.

**Recommendation:** include all three supplied paths in `guarded_paths`:

```python
guarded_paths = {directory, config_dir, data_dir}
```

This would catch accidental future calls like:

```python
config_dir.exists()
data_dir.mkdir()
default_database_path(data_dir)
```

The test already monkeypatches SQLite and importer paths, which is good.

---

### 4. JSON key-order tests cover the top level but not the nested workflow

The plan says:

> The JSON key order will be tested to make this safe for downstream tools.

The proposed tests check `list(payload)` for the top-level manifest, but the nested `workflow` object is also part of the public machine-readable manifest and is reused from `CommunityHandoffWorkflow`.

**Recommendation:** add assertions for nested workflow key order, e.g.:

```python
assert list(payload["workflow"]) == [
    "directory",
    "input_format",
    "pattern",
    "as_of",
    "config_dir",
    "data_dir",
    "source_name",
    "execution_mode",
    "step_count",
    "steps",
]
assert list(payload["workflow"]["steps"][0]) == [
    "order",
    "name",
    "purpose",
    "command",
    "suggested_effect",
]
```

This matters because the manifest is explicitly intended for external tools.

---

### 5. Planned module code includes an unused import that will fail Ruff

The implementation sketch imports:

```python
COMMUNITY_SIGNAL_CONTRACT_VERSION,
```

but does not use it.

Given the verification plan includes:

```bash
UV_NO_CONFIG=1 uv run ruff check .
```

this will fail with an unused import.

**Recommendation:** remove the unused import, or intentionally expose the community signal contract version as a separate manifest field such as:

```python
producer_contract_version: str
```

If the latter is added, test it and document it. That would also improve producer usefulness.

---

### 6. `matched_file_rule` wording could be misread as this command reading files

The proposed value is:

> Read regular files directly under the supplied directory whose names match the pattern; do not recurse into subdirectories.

Because the manifest command itself must not read anything, this wording is slightly ambiguous. It is meant to describe what downstream lint/import commands do, not what the manifest command does.

**Recommendation:** rephrase to avoid any interpretation that `community-handoff-manifest` reads the directory:

> Downstream lint, preview, and import commands treat matching regular files directly under the supplied directory as handoff files; they do not recurse into subdirectories.

This aligns better with the print-only boundary.

---

### 7. Source-boundaries README requirements should be updated too

The plan updates `docs/source-boundaries.md` with a paragraph for `community-handoff-manifest`, but `docs/source-boundaries.md` also has a “README Requirements” section. The current list already includes `community-handoff-workflow`, `community-candidates-dir`, etc.

**Recommendation:** add a corresponding README requirement bullet for `community-handoff-manifest`, not just a boundary paragraph earlier in the file. This keeps the boundary policy and public README obligations synchronized.

---

## Answers to review questions

### 1. Does the manifest fill a real gap, or is it duplicative?

It fills a real gap, with caveats.

`community-signal-profile` is field/schema-oriented. `community-handoff-workflow` is command-sequence-oriented. The proposed manifest combines directory, pattern, suggested filename, profile/schema pointers, and workflow into one stable JSON shape for external local producers.

That is a legitimate producer-integration gap.

The duplication risk is acceptable as long as the manifest remains a thin composition layer over existing constants/builders and does not create a second divergent contract. The plan mostly does this by reusing `build_community_handoff_workflow()` and community signal profile constants.

### 2. Are the planned model fields stable and useful?

Mostly yes. The core fields are stable and useful:

- `contract_version`
- `execution_mode`
- `directory`
- `input_format`
- `pattern`
- `as_of`
- `config_dir`
- `data_dir`
- `source_name`
- `producer_profile_command`
- `suggested_filename`
- `matched_file_rule`
- `manifest_storage_note`
- schema/example/header/required/optional/envelope fields
- nested `workflow`
- `boundaries`

However, for an external producer, the manifest would be more useful if it also included `prohibited_fields`, `field_rules`, and possibly `field_notes` from the existing producer profile. Otherwise, external tools must call `community-signal-profile --format json` as a second step to avoid contract mistakes.

### 3. Any planned behaviors that violate `AGENTS.md` or `docs/source-boundaries.md`?

No direct violations found.

The planned command:

- does not scrape/crawl/fetch
- does not log in
- does not store cookies/sessions
- does not use platform APIs
- does not monitor/schedule/watch
- does not open SQLite
- does not inspect directories
- does not create artifacts
- does not add compliance review

The nested workflow includes an eventual import command, but it is only printed. That matches the existing `community-handoff-workflow` boundary.

### 4. Does `manifest_storage_note` adequately prevent accidental ingestion as a signal file?

Adequate but not ideal.

It gives the right instruction, but I would strengthen it for the `--pattern "*.json"` case because that is where accidental ingestion is most likely. The docs plan does mention this explicitly in `docs/community-signal-import.md`; the manifest itself should too, because external tools may only read the JSON output.

### 5. Are tests sufficient?

Good coverage overall, but I would add/adjust:

- Guard `config_dir` and `data_dir` in the no-side-effect test, not just `directory`.
- Assert nested `workflow` and `workflow.steps[]` JSON key order.
- Add a test that `manifest_storage_note` warns specifically about JSON manifests saved in `*.json` handoff directories.
- Ensure docs tests check all public docs that list commands, not only one or two references.
- Remove the planned unused import or tests/verification will fail Ruff.

The planned tests already cover:

- print-only/no artifact creation
- help visibility
- JSON output
- table output
- invalid timestamp handling
- model field order
- filename selection
- command quoting
- workflow reuse
- table sanitization

That is a strong base.

### 6. Any CLI naming, option reuse, or documentation updates missing?

CLI naming looks good:

```bash
fashion-radar community-handoff-manifest DIRECTORY
```

It is consistent with:

- `community-signal-profile`
- `community-handoff-workflow`
- `community-candidates-dir`

Option reuse is also appropriate, especially using the same `--input-format`, `--pattern`, `--config-dir`, `--data-dir`, `--as-of`, `--source-name`, and `--format` patterns.

Documentation updates are mostly covered, but add/update:

- `docs/source-boundaries.md` README Requirements bullet for the new command.
- Any centralized public command/help list if `tests/test_cli_docs.py` maintains one.
- Explicit JSON saved-manifest warning in both docs and the manifest field itself.

## Overall recommendation

Proceed after addressing the Important items above. The plan is sound, local-only, and appropriately reuses existing workflow/profile infrastructure. The main improvements are tightening the storage warning, expanding producer-contract completeness or clarifying the manifest/profile split, and strengthening no-side-effect and key-order tests.
