I'll review the Stage 92 plan and design artifacts. Let me read all the relevant files in parallel.
I have all the files I need. Let me verify each proposed test phrase exists in the current doc (using the same `_normalized` = whitespace-collapse + casefold that the test applies).
All 18 proposed phrases are present in the normalized current doc, and no existing test references `source-pack-quality.md` (so the new file is non-redundant). Here is my review.

---

# Stage 92 Plan Review Findings

## Severity-Ordered Findings

**Critical:** None.

**Important:** None.

**Minor:**

- `docs/superpowers/plans/2026-06-18-stage-92-source-pack-quality-docs-boundary-plan.md:76-83` — The five phrases in `test_source_pack_quality_json_docs_keep_non_data_boundary` (`collected items`, `database state`, `source contents`, `account data`, `json output does not include fetched data`) are short tokens asserted independently. This is acceptable for a presence-only drift guard and is consistent with `tests/test_cli_docs.py:618-622`, but note these short substrings will pass even if the surrounding negation context (`does not include ...`) is later removed from the first clause only. Consider leaving as-is for parity with existing docs-drift tests, or pinning one compound phrase. Not a blocker; the design explicitly asks for phrase-level presence assertions.
- `docs/superpowers/plans/2026-06-18-stage-92-source-pack-quality-docs-boundary-plan.md:131` — Task 4 mirror scan uses `rg -n 'tuna|aliyun|ustc|huaweicloud|mirror|index-url|extra-index-url|find-links' uv.lock`. This is already the established pattern in `tests/test_cli_docs.py:712` and `docs/dependency-mirrors.md`, so it is correct. Just confirming `uv.lock` is not in the allowed-changes list and this command is a read-only verification (it is).

**Informational:**

- `docs/superpowers/specs/2026-06-18-stage-92-source-pack-quality-docs-boundary-design.md:28-46` and plan Task 2 code are mutually consistent: the test imports only `pathlib.Path`, reads the Markdown, and asserts. It does not import application modules, open SQLite, parse YAML, or execute `source-pack-lint`, satisfying the design's stated boundaries.
- `tests/test_source_pack_quality_docs.py` is not referenced by `tests/test_cli_docs.py` or `tests/test_source_packs.py`, and the reverse is also true — the new file is self-contained. Scope is safely isolated.

---

## Review Question Answers

**1. Are the proposed docs assertions present in current `docs/source-pack-quality.md`?**
Yes. I normalized the current doc with the test's exact transform (`" ".join(text.split()).casefold()`) and all 18 proposed phrases match. Coverage maps to `docs/source-pack-quality.md:8-11` (local/read-only boundary), `:98-99` (JSON non-data boundary), `:166` (article-page fetch boundary), `:203` (retail/resale demand boundary), and `:213-217` (availability non-guarantee).

**2. Are the phrases stable enough and not overly broad?**
Yes for the boundary tests; mostly yes for the JSON non-data test. The long phrases (e.g. `not a compliance, audit, policy, or source-terms review workflow`, `local configuration quality signal, not as a source availability guarantee`) are distinctive and stable. The short ones in the JSON test are intentionally enumerated sub-clauses of a single sentence and are as narrow as the source prose allows. No phrase is so broad it would match unrelated text in this specific file.

**3. Is the scope safely test-only and independent from Stages 91, 93, and 94?**
Yes within the visible artifact set. Allowed changes are limited to `tests/test_source_pack_quality_docs.py` plus review files. Disallowed list (`docs/source-pack-quality.md`, `src/`, schemas, manifests, `uv.lock`, CI, `tests/test_cli_docs.py`, runtime source-pack lint tests) matches the design's scope. The new test file does not share state, imports, fixtures, or constants with other test modules, so it cannot collide with adjacent stages' file edits. (Note: I cannot see Stages 91/93/94 specs from this prompt, but file-level disjointness holds regardless.)

**4. Are the verification commands sufficient?**
Yes. Task 3 runs the new test in isolation and alongside `tests/test_source_packs.py`, plus Ruff check and format check on the new file and `git diff --check`. Task 4 adds the full suite: release hygiene script, full `pytest`, repo-wide Ruff check/format, `UV_NO_CONFIG=1 uv lock --check`, lockfile mirror scan, `uv.lock`/`pyproject.toml` diff guard, staged-hygiene re-run, and secret/CRED-pattern scan. This exceeds the minimum needed for a test-only docs guard.

**5. Are there any Critical or Important blockers before implementation?**
No. There are no Critical or Important blockers. The two Minor notes above are optional refinements and do not block implementation.

---

**Verdict: clear to implement.** Proceed with Task 2 as written; optionally address the Minor note on short JSON-boundary phrases if you want tighter coupling to the negation framing.
