# Stage 91 Plan Review

Reviewer: opencode (`zhipuai-coding-plan/glm-5.2`, variant `max`), read-only.
Scope: spec + plan + current `docs/data-retention.md`, `tests/test_workflows.py`, `tests/test_cli.py`, cross-checked against the existing Stage 90 sibling `tests/test_daily_digest_docs.py` and `tests/test_cli_docs.py`.

## Verdict

**No Critical blockers. No Important blockers in the plan or proposed test.** The plan is sound, test-only, and ship-ready. One Minor framing inaccuracy and three Informational notes follow.

## Findings (ordered by severity)

### Critical
None.

### Important
None.

### Minor

1. **Plan says "Create" but the file already exists with identical content.**
   `docs/superpowers/plans/2026-06-18-stage-91-data-retention-docs-boundary-plan.md:38` ("Create `tests/test_data_retention_docs.py` with:") describes a file that already exists untracked with byte-for-byte the proposed body (`tests/test_data_retention_docs.py:1-32`). This is not a correctness defect — the proposed content and the on-disk content match exactly, and the test passes (`1 passed in 0.01s`, ruff check + format clean). The plan's "Create" checkbox should be read as "verify/land the pre-staged file." No change to the plan's substantive content is required; if you want tight bookkeeping, reword Task 2 to "Add `tests/test_data_retention_docs.py` (pre-staged) with the body below."

### Informational (non-blocking)

1. **Raw substring matching diverges from the Stage 90 sibling, intentionally.**
   The proposed test uses exact `phrase in text` checks
   (`docs/superpowers/plans/2026-06-18-stage-91-data-retention-docs-boundary-plan.md:72`),
   whereas Stage 90's `tests/test_daily_digest_docs.py:13-15` normalizes via
   `" ".join(text.split()).casefold()`. For a drift guard the stricter exact
   match is appropriate — all 14 anchors are exact-match stable today
   (verified against `docs/data-retention.md`). No change needed; recorded so
   the choice is deliberate.

2. **"config files" is the broadest anchor.**
   Of the 14 phrases, `config files`
   (`docs/superpowers/plans/...-plan.md:68` → `docs/data-retention.md:45`) is
   the least specific. It currently appears exactly once in the doc, so the
   guard is effective; the remaining anchors are backticked identifiers, a
   literal formula, or full sentences, so none can false-positive. Acceptable.

3. **Review-toolchain divergence from `AGENTS.md`.**
   Plan Task 1 / Task 3 invoke
   `opencode run --model zhipuai-coding-plan/glm-5.2 --variant max`
   (`docs/superpowers/plans/...-plan.md:31,91`), while `AGENTS.md:21-28` and
   `docs/REVIEW_PROTOCOL.md` mandate local Claude Code. This matches the
   Stage 90 sibling and your explicit direction, and
   `tests/test_review_protocol_docs.py` only enforces the rule on `AGENTS.md`,
   `docs/REVIEW_PROTOCOL.md`, and `docs/github-upload-checklist.md`, so it is
   not a Stage 91 defect. Noted for transparency.

## Answers To Review Questions

1. **Are the proposed docs assertions present in current `docs/data-retention.md`?**
   Yes — all 14. Phrase → `docs/data-retention.md` line:
   `Use \`clean-old-data\` to prune old collected items` → L14;
   `as_of - retention_days` → L24;
   `Rows in \`items\` with \`collected_at\` older than that cutoff are pruned.` → L27;
   `explicitly deletes related \`item_entities\` rows before deleting` → L31;
   `does not rely on SQLite foreign-key cascade behavior` → L32;
   `` `--dry-run` reports how many item and item/entity rows would be deleted without `` → L34;
   `The cleanup command does not prune:` → L39;
   `` `collector_runs` `` → L41;
   `` `source_health` `` → L42;
   `` `entity_first_seen` `` → L43;
   `generated Markdown or JSON report files` → L44;
   `config files` → L45;
   `` `entity_first_seen` is intentionally retained across item pruning `` → L53;
   `Back up the SQLite database before aggressive cleanup` → L69.

2. **Are the phrases stable enough and not overly broad?**
   Yes. 13 of 14 are backticked identifiers, a literal formula, or full
   sentences. `config files` is the only generic token and appears exactly
   once in the doc. None can false-positive; all are drift-resistant.

3. **Is the scope safely test-only and independent from Stages 90, 92, and 93?**
   Yes. The module imports only `from __future__ import annotations` and
   `from pathlib import Path`
   (`tests/test_data_retention_docs.py:1-3`); no application modules, no
   SQLite, no fixtures shared with `tests/test_workflows.py` or
   `tests/test_cli.py`. It is structurally a clone of Stage 90's
   `tests/test_daily_digest_docs.py`. The two runtime tests named in the
   verification command exist and are only *run*, not modified:
   `tests/test_workflows.py:155` (`test_clean_old_data_prunes_by_collected_at`)
   and `tests/test_cli.py:9594` (`test_clean_old_data_command_prunes_old_items`).
   `tests/test_cli_docs.py:54` references `docs/data-retention.md` only for
   path/flag consistency inside
   `test_repo_local_operational_examples_keep_path_flags_together`, which is
   orthogonal to the boundary-phrase content, so the two modules coexist
   without coupling. No overlap with Stages 90/92/93.

4. **Are the verification commands sufficient?**
   Yes. The plan's focused block
   (`docs/superpowers/plans/...-plan.md:80-83`) runs the new docs test plus the
   two runtime cleanup tests (so the docs guard and actual cleanup behavior
   stay in lockstep) plus `ruff check` and `ruff format --check`. Task 4 then
   layers in full `pytest`, repo-wide ruff, `uv lock --check`, release
   hygiene, and staged-secret/`uv.lock` guards. I re-ran the focused docs +
   ruff block: `1 passed`, `All checks passed!`, `1 file already formatted`.

5. **Are there any Critical or Important blockers before implementation?**
   **No Critical. No Important.** The test is shippable as-is. The only
   cosmetic action item is to optionally reword Task 2's "Create" →
   "Add (pre-staged)" to match reality.
