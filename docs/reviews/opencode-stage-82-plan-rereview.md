Let me verify the existing `docs/dependency-mirrors.md` structure to ensure the placement instruction is grounded.
All three previous Important findings are resolved.

## Verification of resolved findings

1. **Drift-test exact pinned strings** — Resolved. Plan Task 2 (lines 43-52) now lists 8 exact pinned strings, including the heading `"Recover A Mirror-Rewritten Lockfile"`, the boundary phrase, all four recovery commands, and the `rg` mirror-marker scan. These are concrete enough to implement a substring drift test unambiguously.
2. **Placement of `## Recover A Mirror-Rewritten Lockfile`** — Resolved. Both spec (line 18-22) and plan (lines 29-33) now state "after `## Project Practice` as a peer `##` section". Confirmed viable: `## Project Practice` is currently the last `##` in `docs/dependency-mirrors.md` (line 54, file ends line 72), so the new section appends cleanly at the end.
3. **Relationship to `## Project Practice` mirror scan** — Resolved. Spec line 20-22 and plan lines 31-32 both state the existing scan stays in place and the new section is additive recovery guidance "for when a local mirror rewrite has already happened".

## Remaining blockers
None Critical or Important.

## Minor notes
- Plan Task 2 pins `"rg -n 'tuna|aliyun|...|find-links' uv.lock"` (line 49), but that exact string already exists in `## Project Practice` at `docs/dependency-mirrors.md:71`. As a substring test it will pass regardless of the new section, so it does not uniquely verify the new section — the heading pin (line 44) is what actually proves section presence. Harmless, just redundant for uniqueness.
- The spec's `## Verification` section (lines 46-53) is slightly looser than the plan: it doesn't enumerate the 8 pinned strings. The plan is the implementation authority and is precise, so this is acceptable, but the spec could reference the plan's pinned-string block for full parity.
- Pinned phrase `"frozen mirror install commands"` (plan line 50) is not currently in `docs/dependency-mirrors.md`, so it must be authored into the new section — worth a one-line note in Task 2 that this phrase is required prose, not pre-existing.

Plan is ready to proceed to implementation.
