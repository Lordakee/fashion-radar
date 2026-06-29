# Stage 221Plan Review

**Verdict:** APPROVE_WITH_NITS

---

## Critical

None.

---

## Important

**PROJECT_BRIEF.md "Free-First Boundary / Experimental sources" section is not in scope — but leaving it unedited creates a visible intra-document inconsistency.**

`docs/PROJECT_BRIEF.md` lines 53–59 list Xiaohongshu under "Experimental sources can be added later":
> - RedNote/Xiaohongshu MCP or crawlers.

After Stage 221/222, Xiaohongshu is no longer a future-experimental item — it is an active Phase 2 opt-in. The plan updates the "Non-Goals For MVP" section (tested) but does not mention updating this "Free-First Boundary" block (untested). No docs-guard breaks, but any reader of PROJECT_BRIEF will find the two sections contradicting each other: "opt-in Phase 2" in Non-Goals vs. "experimental, add later" in Free-First Boundary. Since Stage 221's entire purpose is an honest, internally consistent boundary evolution, this omission is out of character.

Recommended fix: add a sentence in the "Free-First Boundary" experimental list (or move the Xiaohongshu bullet to the Optional section) clarifying that Phase 2 activates Xiaohongshu as an opt-in connector. No test change needed; prose-only.

---

## Nits

**1. "Current Review-Aligned Priorities" in PROJECT_BRIEF.md ends with** "Experimental/community handoff expansion remains frozen while these remaining core gaps are addressed." Phase 2 is not community handoff, so this sentence is not technically wrong, but a one-line note that Phase 2 social acquisition is proceeding alongside core work would prevent confusion. Low priority, but a natural companion to the Important fix above.

**2. AGENTS.md lead paragraph says "fragile full social-platform scraping."** The opt-in Xiaohongshu connector is — intentionally — social-platform scraping. The plan correctly notes this paragraph needs updating. Implementer should ensure the revised wording preserves "the *core* workflow stays without login" rather than removing the sentence, since it remains true that the default pipeline needs no login cookies.

**3. The spec says "~8 assertions"; the plan says "2 assertion groups."** These count different things (spec counts all asserted phrases touched; plan counts the change groups). No implementation risk, but a future reader comparing the two will be briefly confused. Worth a parenthetical clarification in the plan's Scope section.

---

## Résumé

Framing is correct: "opt-in / user-login-required / use-at-your-own-risk" is the right register — it is not a claim that social is a core feature. All still-true caveats (no full-coverage claim, no demand proof, no coverage verification, default-workflow-excludes-broad-collection, users-respect-ToS) are correctly identified as staying. The three named docs-guard test files are the right targets; no other test file pins the ban wording that changes. Scope discipline (docs + docs-guard only, no code/schema/dep) is clean and verifiable. The one Important gap — PROJECT_BRIEF's "Free-First Boundary" section listing Xiaohongshu as future-experimental — should be patched in Task 1 alongside the Non-Goals update; it is a two-line prose fix with no test impact.
