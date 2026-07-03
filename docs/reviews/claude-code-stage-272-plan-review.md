Both files read. This is a review task, so I'll give the verdict directly.

## APPROVED

Both previously-remaining blockers are fixed in the plan. Implementation may start.

**Blocker 1 — edition-nav exact-substring conflict — RESOLVED.**
The plan no longer collapses both classes onto one element. `class="edition-nav"` stays alone on the `<nav>`, and `edition-rail` moves to a nested `<div>`:
- Task 2 Step 2, `plan.md:212-214` — `<nav class="edition-nav" aria-label="Edition contents">` wrapping `<div class="edition-rail">` / `<div class="edition-rail-grid">`; intent stated at `plan.md:207-209` ("the nav keeps the existing exact `edition-nav` class").
- RED regex targets that exact opening tag — `plan.md:70-72` — so the substring `class="edition-nav"` is preserved verbatim.
- CLI guard keeps `class="edition-nav"` and only *adds* the new inner hooks — `plan.md:301-307`.

**Blocker 2 — edition-status/language-toggle staged as RED — RESOLVED.**
These are now explicitly treated as green regression guards, not RED assertions:
- Task 1 Step 2, `plan.md:56-61` — "Keep the existing assertions for `edition-status`, `language-toggle`, `data-lang-toggle`, and `class="edition-nav"` in their current tests. Do not duplicate them in the RED step because they already pass."
- Reinforced in the RED-run expectation — `plan.md:113-116` — "Existing `edition-status`, `edition-nav`, and language-toggle assertions are regression guards and should remain green."
- The RED steps (`plan.md:48-54`, `67-83`, `89-103`) contain only genuinely-new hooks (`site-shell`, `edition-summary-panel`, `edition-rail*`, `story-card-*`, `story-tag-list`), so the RED failure is attributable to new behavior only.

**Non-blocking note (verify during Task 2 Step 5/6, not a gate):** The plan combines classes on the nav *item* — `class="edition-nav-item edition-rail-item"` (`plan.md:215`, `231-232`, asserted at `306`). This is the same failure mode as Blocker 1 one level deeper: if any existing test asserts the exact substring `class="edition-nav-item"` (with trailing quote), it would break. The preserved-assertion list (`plan.md:58-60`) omits it, which implies no such exact assertion exists — but I could not confirm this, since the review scope was limited to the plan and design docs. The Task 2 Step 6 CLI run will surface it immediately if present.
