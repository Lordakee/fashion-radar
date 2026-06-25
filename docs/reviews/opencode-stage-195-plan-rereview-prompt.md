# Stage 195 Plan Re-Review Prompt

Please re-review the revised Stage 195 plan:

`docs/superpowers/plans/2026-06-25-stage-195-source-coverage-and-diacritics-plan.md`

Prior review found:

1. The original plan changed `normalize_text()` only, which did not make runtime `alias_pattern()` matching diacritic-insensitive.
2. The original source-pack expansion premise was stale because `configs/source-packs/fashion-public.example.yaml` is already broad.
3. The original plan referenced non-existent files/tests and used arbitrary source-count assertions.

Confirm whether the revised plan now:

- covers runtime alias matching, not only normalized keys;
- correctly leaves the public source pack unchanged and targets the smaller default starter source configs;
- uses real existing files/tests;
- keeps tests offline and deterministic;
- stays within the v0.1.x RSS/GDELT boundary and avoids social scraping, source ranking, demand proof, live URL guarantees, and compliance-review product features.

Return:

- Verdict: APPROVED / NEEDS_WORK
- Critical findings
- Important findings
- Minor findings
- Concrete fixes required before implementation
