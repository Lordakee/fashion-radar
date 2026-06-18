## Stage 99 Plan Review

**Verdict: No Critical or Important blockers. The plan is approved to proceed.**

I simulated the exact planned test logic against the current `docs/manual-signal-import.md`; all 9 pinned phrases resolve to `OK` after whitespace collapse + casefold.

---

### Findings

**Critical:** None.

**Important:** None.

**Minor / Notes (informational, non-blocking):**

1. **Phrase verification confirmed.** Every planned phrase is present and uniquely resides in the `## Privacy Boundary` section:
   - `account ids` ← casefolded from `account IDs` (robust due to `casefold()`).
   - `follower lists` and `allowed to process and review locally` survive the `\n`→space join correctly.
   - `images, videos` keeps its comma because `" ".join(text.split())` only splits on whitespace, leaving punctuation attached.
   - None of the 9 phrases appear in the trailing "local input path, not a connector…" paragraph, so the deliberate non-pinning of that sentence (design lines 80-82) holds.

2. **Section scoping is correct and narrow.** `_section` splits on `## Privacy Boundary` then on the next `\n## ` heading. Since this is the last `##` section, it captures to EOF — but only the privacy paragraph is actually asserted. A `### Privacy Boundary` cannot false-match (`## Privacy Boundary` is not a substring of `### Privacy Boundary`). Scope is properly confined to privacy/material boundaries.

3. **No overlap with prior docs-boundary stages.** Existing guards (`test_architecture_boundary_docs.py`, `test_candidate_discovery_docs.py`, `test_source_pack_quality_docs.py`, etc.) target different doc files/sections. The privacy-sensitivity vocabulary (`cookies`, `follower lists`, `author profiles`, `private or sensitive material`) is distinct from architecture/source-boundary and candidate-discovery language. The architecture-flavored final sentence is intentionally excluded. No `test_manual_signal_import_docs.py` exists yet, so it's a clean addition matching the `*_docs.py` convention.

4. **Scope discipline is sound.** Allowed/disallowed lists in the prompt and plan agree. No `src/`, schema, lockfile, CI, `docs/manual-signal-import.md` source text, `test_cli_docs.py`, or runtime manual-import changes. The test is stdlib-only (`from pathlib import Path`), opens no SQLite, parses no CSV/JSON, touches no app modules.

5. **Verification commands are sufficient for a docs-only guard.** Focused run + adjacent `test_manual_signal_import.py` + `ruff check`/`ruff format --check` + `git diff --check` cover the stage; Task 4 adds the full release gate (hygiene, full pytest with proxy unset, repo ruff, `UV_NO_CONFIG=1 uv lock --check`, mirror-URL scan, `uv.lock`/`pyproject.toml` diff guard, staged hygiene, staged secret scan). Matches AGENTS.md lockfile guidance.

6. **Cosmetic only:** `_section`'s `assert marker in text` (plan line 151) has no message. On a future heading rename the failure is still clear enough given the single assertion; adding a message is optional and not required for parity with sibling `*_docs.py` tests.

---

### Review Questions (answered)

1. **Real boundary, no behavior change?** Yes — read-only docs guard; zero runtime/CLI/schema impact.
2. **Phrases present and narrowly scoped?** Yes — all 9 verified in `## Privacy Boundary` only.
3. **No overlap with recent stages?** Yes — distinct privacy vocabulary; architecture/source final sentence deliberately unpinned.
4. **Verification sufficient?** Yes — focused + adjacent + full release gate.

Proceed to Task 2.
