# Stage 196 Plan Review

Verdict: **NEEDS_WORK**

Critical findings:

- The fallback-map approach is directionally sound, but the plan needs to state
  the invariant more clearly: normalization and runtime alias matching should be
  derived from the same explicit Latin character map, and only mapped
  non-decomposing Latin variants should be translated.
- The README guard should target the exact `README.md` Configuration section
  instead of loose whole-file substring checks.

Important findings:

- `_folds_to_self()` should be used only for static map derivation.
- The plan should not rely on whether the alias test already passes; it should
  define parity across normalization and runtime alias matching.

Concrete fixes required before implementation:

1. Clarify the non-decomposing Latin parity invariant.
2. Tighten the README guard to an exact offline assertion against the
   Configuration section.
3. Simplify the review/release artifact section so implementation remains
   focused.
