I have all the data needed. Let me now write the review.

---

# Stage 211 Plan Review

**Verdict:** APPROVE_WITH_NITS

## Critical

None.

## Important

**I-1 — Contract list omits 5 AGENTS.md hygiene phrases required by a separate test**

`tests/test_review_protocol_docs.py:192-200` (`test_review_protocol_docs_document_capture_hygiene`) checks the *normalized text of AGENTS.md `## Review Gates`* for five phrases:

```
"completed review output", "live-capture stubs", "duplicated or truncated text",
"tool-status messages", "empty output"
```

None of these appear in the plan's **Required phrases test-contract list** (plan lines 53-63). That list names these phrases only for `docs/REVIEW_PROTOCOL.md ## Review Capture Hygiene` and `docs/github-upload-checklist.md ## Final Review`. The current AGENTS.md `## Review Gates` carries them in the sentence "ensure each local opencode record contains completed review output and no live-capture stubs, duplicated or truncated text, tool-status messages, or empty output." The plan's suggested rewrite for AGENTS.md preserves this sentence (good), but an implementer relying solely on the contract list — not the suggested wording — would have no signal that omitting or restructuring this sentence would turn the hygiene test RED. Add these 5 phrases explicitly to the AGENTS.md sub-entry of the required-phrases section.

**I-2 — No guard assertion for the new `claude-code-stage-N` artifact prefix in AGENTS.md**

The plan's suggested AGENTS.md wording adds `docs/reviews/claude-code-stage-N-...` alongside `docs/reviews/opencode-stage-N-...` to the artifact-recording line. The plan then updates no test to assert that AGENTS.md documents this prefix. `test_active_review_docs_document_local_opencode_gate` only checks `docs/reviews/opencode-stage-N` in all three docs. Since Claude Code is now declared the *primary* reviewer, its artifact prefix should also be guarded: add `assert "docs/reviews/claude-code-stage-N" in _normalized_text(agents_text)` to that test (or a targeted new assertion in the framing test). Without it, a future edit could silently drop the `claude-code-stage-N` reference from AGENTS.md and no test would catch it.

## Nits

**N-1 — `"revises"` token is too broad**

Task 1's new assertion `assert "revises" in normalized_protocol.casefold()` would pass if the word "revises" appears *anywhere* in the normalized full-file text — including an unrelated sentence. Tighten to `"opencode revises"` or `"revises the plan"` to actually pin the iron-rule relationship.

**N-2 — "Phase 1 sub-stage 1a" vs "stage-211" — undocumented duality**

The plan title and roadmap use "sub-stage 1a"; review artifacts use `stage-211`. Both are correct (one is a roadmap position label, one is the sequential artifact-naming integer), but the plan never explains the mapping. Add one line in the File Map or the Self-Review stating: *"Stage-211 is the sequential artifact ID for sub-stage 1a; both labels are in use in parallel."* This avoids the question surfacing as a code-review blocker at every future sub-stage.

**N-3 — Task 3 Step 3 uses `git diff --check` instead of `git diff --cached --check`**

Task 3 Step 3 runs `git diff --check` to detect whitespace damage. At that point the intent is to check the *staged* diff (after Task 2 edits). `git diff --check` inspects the unstaged working tree, not the index. Task 5 Step 3 already uses `git diff --cached --check` correctly; Task 3 should match it.

**N-4 — Release-review extension is an interpretation, not stated as such**

Iron rule 2 mentions plan review and code review explicitly; it is silent on release review. The plan labels its choice "minimal-churn interpretation" but conflates it with the Key Decision rationale. Worth explicitly flagging it as *"extension beyond what iron rule 2 states, accepted pending reviewer confirmation"* so the project owner has a clear audit trail for that choice.

## Résumé

Le plan est solide : portée strictement docs + guard-test, pas de fuite vers le code source/schéma/deps, ordre des tâches TDD correct (RED → GREEN), flux iron-rule respecté (Task 0 → Task 4 → Task 5). Les deux points **Important** sont de faibles risques pratiques (le wording suggéré les couvre implicitement) mais ils laissent la liste des contrats de test incomplète, ce qui pourrait piéger un implémenteur ou une révision future. Corriger la liste de phrases requises (I-1) et ajouter la guard assertion `claude-code-stage-N` (I-2) avant l'implémentation. Les nits sont sans impact sur le verdict.
