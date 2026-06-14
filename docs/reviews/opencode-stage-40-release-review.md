I'll perform the Stage 40 release review. Let me start by examining the actual state of the repository and verifying the claims.
The diff looks clean and focused. Let me examine the new files and check for the pre-existing release-review file.
The `release-review.md` file is the streaming capture of my current output (expected per the plan's redirect). Let me verify the verification claims and read the remaining review records.
Active docs are correctly updated. Now let me run the full verification suite claimed in the prompt.
All verification passes. Let me review the plan-review trail and the release-review prompt for completeness and consistency.
I found a significant issue in the rereview-2 record. Let me verify it and check the remaining prompt files.
I have completed the investigation. Here is my Stage 40 release review.

---

# Opencode Stage 40 Release Review

Review model: GLM 5.2 via local opencode (`zhipuai-coding-plan/glm-5.2`). Mode: release review, read-only. No files were edited by this review. All verification commands were re-run independently and reproduced exit 0.

## Verification Reproduced

| Check | Result |
|---|---|
| `rg "opencode\|glm-5.2\|GLM 5.2"` in 3 active docs | present and consistent |
| `rg "Claude Code"` in 3 active docs | none (guard passes) |
| History guards (`claude-code-*`, unrelated plans/specs) | clean |
| `git diff --check` | exit 0 |
| `UV_NO_CONFIG=1 uv lock --check` | exit 0 |
| `UV_NO_CONFIG=1 uv sync --locked --dev --check` | exit 0 |
| Mirror `uv sync --frozen --dev --check` | exit 0 |
| `git diff --quiet -- uv.lock` | unchanged |

## Review Question Answers

1. **Consistent opencode/GLM 5.2 routing?** Yes. `AGENTS.md:11,13,20-24`, `docs/REVIEW_PROTOCOL.md:8,16,19,26,28,40,44,47`, and `docs/github-upload-checklist.md:174,181` all route future plan/code/release gates to `opencode run -m zhipuai-coding-plan/glm-5.2`. The `--effort max` requirement was correctly removed.
2. **Naming consistency + history preserved?** Yes. `REVIEW_PROTOCOL.md:50-66` prescribes `opencode-stage-N-{plan,release}-{review,rereview}.md` for new records and explicitly preserves `claude-code-*` as historical audit records. All 100+ `claude-code-*` files are untouched (guard confirms).
3. **Scope purely documentation-only?** Yes. No source, tests, deps, lockfile (`uv.lock` byte-identical to HEAD), CI, schema, connectors, scraping, schedulers, or monitors changed.
4. **Critical/Important blockers?** One Important blocker — see below.

## Critical Findings

None.

## Important Findings

**I-1. `docs/reviews/opencode-stage-40-plan-rereview-2.md` is corrupted and cannot serve as audit evidence.** The file that records the plan gate's final approval is garbled:

- Line 19 ends mid-sentence with an embedded tool-confirmation string: `...phrase check is nowWrote \`docs/reviews/opencode-stage-40-plan-rereview-2.md\`.` (note the `nowWrote` concatenation and the captured `Wrote \`...\`` artifact that does not belong in a review document).
- Line 21 contains a premature `**Verdict: APPROVED FOR STAGE 40 OPENCODE REVIEW WORKFLOW**` mid-document.
- Line 31 is an orphaned fragment: `the next stage."`
- Lines 49-106 then contain a *second*, complete review structure ending in a *second* `APPROVED FOR STAGE 40 OPENCODE REVIEW WORKFLOW` (line 106).

The file therefore has two verdicts, two approval phrases, a captured tool message, and broken prose. `REVIEW_PROTOCOL.md:50` and `AGENTS.md` treat these records as "audit history," and this stage's entire purpose is review-workflow integrity. Shipping a broken review record as the evidence that the plan gate passed is internally inconsistent with the stage's goal. Per the project's stated policy (`Treat Critical and Important findings as blockers`), this must be fixed before commit.

**Required fix (trivial):** regenerate `docs/reviews/opencode-stage-40-plan-rereview-2.md` with a single, clean review body (the content in lines 49-106 is already correct; remove the corrupted lines 1-48 and replace with a clean header/scope/confirmation block, or simply re-run the rereview-2 capture).

## Minor Findings

**M-1.** `docs/reviews/opencode-stage-40-plan-rereview-2.md:19` "nowWrote" corruption suggests the streaming capture (`opencode run ... > file`) is racing with tool-output telemetry. Worth a note in the plan template to render the review to a variable / `tee` with stderr separated, so future review records do not ingest `Wrote \`...\`` lines. Non-blocking once I-1 is fixed.

**M-2.** The release-review prompt's file list says the release-review file is "Added after this prompt runs" (`docs/reviews/opencode-stage-40-release-review-prompt.md:51`). This is accurate but means the prompt artifact is merged to GitHub describing a file that did not exist at prompt-write time. Acceptable for this stage; just flagging for traceability.

**M-3.** `docs/REVIEW_PROTOCOL.md:50-66` now lists four naming templates but does not show a concrete stage number example (e.g. `opencode-stage-40-plan-review.md`). The convention is clear enough; adding one concrete example would help future contributors. Non-blocking.

## Scope Compliance

- Documentation-only. No product behavior, dependency, lockfile, CI, schema, command, connector, scraping, platform-automation, source-acquisition, scheduler, watcher, or monitor changes. Aligned with `AGENTS.md` scope boundaries and the v0.1.0 free-first/local-first principle.
- Historical `claude-code-*` review records and prior `docs/superpowers/{plans,specs}/` files are preserved as audit history (guards confirm).
- The active-doc deliverable of this stage (the three modified files) is correct, consistent, and verification-clean.

## Verdict

The active-documentation deliverable is correct and fully verified. The only blocker is the integrity of one in-stage audit artifact, `docs/reviews/opencode-stage-40-plan-rereview-2.md`, which is corrupted and must be regenerated before commit. This is a one-file fix and does not require touching any active doc, source, or lockfile.

Approval phrase: **not issued** — one Important blocker (I-1) remains open.

**Required change before approval:**

1. Regenerate `docs/reviews/opencode-stage-40-plan-rereview-2.md` so it contains a single, coherent review with one verdict and one approval phrase, and contains no captured tool-confirmation (`Wrote \`...\``) artifacts or orphaned fragments. Re-run the history guards after the edit.
